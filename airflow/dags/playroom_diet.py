import json
import os
from airflow.configuration import AIRFLOW_HOME
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk import dag, task
from airflow_ai_sdk import BaseModel
import httpx
from supabase import create_client
from pydantic_ai import BinaryContent

_POSTGRES_CONN_ID = "postgres_playroom_diet"


supabase_project_url = os.getenv("SUPABASE_PROJECT_URL")
supabase_secret_key = os.getenv("SUPABASE_SECRET_KEY")


class Toy(BaseModel):
    category: str
    item_name: str
    count: int
    play_mode: str

class ToyInventory(BaseModel):
    items: list[Toy]

class AnalysisResult(BaseModel):
    status_quo: str
    missing_skill: str
    recommended_toy: str
    reasoning: str

class ToyRecommendation(BaseModel):
    decision: str
    recommended_toy: str
    safety_context: str
    amazon_search: str

def get_image_bytes(image_path: str) -> bytes:
    image_url = f"{supabase_project_url}/storage/v1/object/public/playroom-images/{image_path}"
    with httpx.Client() as client:
        response = client.get(image_url)
        response.raise_for_status()
        return response.content


@dag
def process_scans():

    _get_new_scans = SQLExecuteQueryOperator(
        task_id="get_new_scans",
        conn_id=_POSTGRES_CONN_ID,
        sql="SELECT id, image_path, child_age FROM public.scans WHERE status = 'processing';",
    )

    @task.llm(
        model="gemini-3-flash-preview",
        output_type=ToyInventory,
        system_prompt="""
            You are an expert Inventory AI for a child development app.

            Your goal is to categorize the inventory to help a parent declutter.

            Please extract the following for EVERY distinct group of toys you see:
            1. "category": Broad type (e.g., Vehicle, Construction, Doll, Puzzle, Art, Active).
            2. "item_name": Specific description (e.g., "Hot Wheels Cars", "Duplo Blocks").
            3. "count": An estimated count (e.g., 1, 2, 5).
            4. "play_mode": The primary type of interaction (e.g., "Passive", "Constructive", "Pretend Play", "Gross Motor", "Fine Motor").

            You can define your own categories and play modes based on the toys you see.
            If the image provided is not a playroom or no toys are visible, respond with an empty "items" list.
        """
    )
    def analyze_image(scan_record: tuple):
        image_path = scan_record[1]
        image_bytes = get_image_bytes(image_path)

        return [
            "Analyze the playroom image provided, which contains a collection of children's toys.",
            BinaryContent(data=image_bytes, media_type='image/jpeg')
        ]

    toy_inventories = analyze_image.expand(scan_record=_get_new_scans.output)

    @task.llm(
        model="gemini-3-flash-preview",
        output_type=AnalysisResult,
        system_prompt="""
            You are an expert Child Development Specialist who uses the US Dept of Labor's O*NET database to scientifically validate play.

            **The core logic:**
            You treat "play" as the child's "job". Your goal is to map toy interactions to official O*NET abilities.
            - Example: "Stacking Blocks" = "Visualization (1.A.1.f.2)" and "Finger Dexterity (1.A.2.a.2)".
            - Example: "Riding a Bike" = "Gross Body Coordination (1.A.3.c.3)".

            **Your task:**
            1. **Audit:** Analyze the provided inventory. Identify which O*NET Ability clusters are heavily represented (e.g., "High Social Perceptiveness") and which are MISSING (e.g., "Zero Structural Visualization").
            2. **Gap:** Identify the most critical developmental blind spot.
            3. **Fix:** Recommend ONE toy that specifically trains the missing O*NET Ability.

            **Requirements:**
            - In status_quo, summarize the dominant O*NET Ability clusters present.
            - In missing_skill, specify the most critical missing O*NET Ability.
            - In recommended_toy, suggest ONE toy that effectively trains the missing ability.
            - In your reasoning, you MUST cite the specific O*NET Ability Name and ID Code (e.g. 'Deductive Reasoning 1.A.1.b.5') to justify your recommendation.
        """
    )
    def analyze_playroom(toy_inventory: dict):
        return json.dumps(toy_inventory)

    analysis_results = analyze_playroom.expand(toy_inventory=toy_inventories)

    @task.llm(
        model="gemini-3-flash-preview",
        output_type=ToyRecommendation,
        system_prompt="""
            You are a dual-role agent: CPSC Safety Auditor and Personal Shopper.

            **Input:** A 'recommended toy' and 'child age'.

            **Step 1: safety audit**
            Check the toy against CPSC guidelines for the age.
            - If safe: Keep the recommendation.
            - If unsafe : You MUST select a safer alternative that achieves the same developmental goal.

            **Step 2: Shopping prep**
            Generate a specific 'amazon_search' for the FINAL toy.
            - Include brand names if they matter for safety.
            - Exclude generic terms that lead to low-quality knock-offs.

            **Requirements:**
            - Decison can be "APPROVED" or "SUBSTITUTED".
            - Provide a clear 'safety_context' explaining your decision.
        """
    )
    def safety_check(analysis_result: dict, scan_record: tuple):
        child_age = scan_record[2]
        return json.dumps({**analysis_result, "child_age": child_age})

    recommendations = safety_check.expand(
        analysis_result=analysis_results,
        scan_record=_get_new_scans.output
    )

    @task
    def print_result(
        toy_inventory: dict,
        analysis_result: dict,
        toy_recommendation: dict
    ):
        print("Toy Inventory:", json.dumps(toy_inventory, indent=2))
        print("Analysis Result:", json.dumps(analysis_result, indent=2))
        print("Toy Recommendation:", json.dumps(toy_recommendation, indent=2))

    print_result.expand(
        toy_inventory=toy_inventories,
        analysis_result=analysis_results,
        toy_recommendation=recommendations
    )

    @task
    def save_result(
        analysis_result: dict,
        toy_recommendation: dict,
        scan_record: tuple
    ):
        scan_id = str(scan_record[0])

        payload = {
            "analysis_result": json.dumps(analysis_result),
            "toy_recommendation": json.dumps(toy_recommendation)
        }
        supabase = create_client(supabase_project_url, supabase_secret_key)

        supabase.table("scans").update({
            "status": "done",
            "results_json": payload
        }).eq("id", scan_id).execute()

    save_result.expand(
        analysis_result=analysis_results,
        toy_recommendation=recommendations,
        scan_record=_get_new_scans.output
    )

process_scans()
