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


class BoundingBox(BaseModel):
    x: float  # 0-1 normalized, left edge
    y: float  # 0-1 normalized, top edge
    w: float  # 0-1 normalized, width
    h: float  # 0-1 normalized, height

class Toy(BaseModel):
    category: str
    item_name: str
    count: int
    play_mode: str
    bbox: BoundingBox  # Location in image (normalized 0-1 coordinates)

class ToyInventory(BaseModel):
    items: list[Toy]

class SkillScores(BaseModel):
    cognitive: int  # 0-100: problem solving, reasoning, memory
    motor_fine: int  # 0-100: finger dexterity, precision
    motor_gross: int  # 0-100: coordination, balance, strength
    social_emotional: int  # 0-100: empathy, cooperation, expression
    creative: int  # 0-100: imagination, artistic, open-ended play
    language: int  # 0-100: communication, vocabulary, storytelling

class RoadmapItem(BaseModel):
    timeframe: str  # "now", "3_months", "6_months"
    priority: int  # 1, 2, or 3
    missing_skill: str  # O*NET ability name
    skill_id: str  # O*NET ID like "1.A.1.f.2"
    skill_category: str  # One of: cognitive, motor_fine, motor_gross, social_emotional, creative, language
    recommended_toy: str
    reasoning: str

class AnalysisResult(BaseModel):
    status_quo: str
    skill_scores: SkillScores
    roadmap: list[RoadmapItem]  # Exactly 3 items

class ToyRecommendationItem(BaseModel):
    timeframe: str
    decision: str  # "APPROVED" or "SUBSTITUTED"
    recommended_toy: str
    safety_context: str
    amazon_search: str

class ToyRecommendation(BaseModel):
    items: list[ToyRecommendationItem]

class PlayQuest(BaseModel):
    title: str
    target_skill: str
    skill_id: str
    duration_minutes: int
    toys_needed: list[str]
    setup: str
    instructions: list[str]
    parent_tip: str

def get_image_bytes(image_path: str) -> bytes:
    image_url = f"{supabase_project_url}/storage/v1/object/public/playroom-images/{image_path}"
    with httpx.Client() as client:
        response = client.get(image_url)
        response.raise_for_status()
        return response.content


@dag(max_active_runs=1)  # each Dag run processes ALL new scans, no parallelism on Dag level needed
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
            5. "bbox": Bounding box location in the image using NORMALIZED coordinates (0-1 range):
               - "x": Left edge position (0 = left side, 1 = right side)
               - "y": Top edge position (0 = top, 1 = bottom)
               - "w": Width of the bounding box (0-1)
               - "h": Height of the bounding box (0-1)
               Example: A toy in the center would have bbox: {"x": 0.4, "y": 0.4, "w": 0.2, "h": 0.2}

            You can define your own categories and play modes based on the toys you see.
            If the image provided is not a playroom or no toys are visible, respond with an empty "items" list.
        """,
        max_active_tis_per_dag=2
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
        output_type=PlayQuest,
        system_prompt="""
            You are a creative Play Coach who designs fun, engaging activities for children using their existing toys.

            **Your task:**
            Create ONE "Play Quest" - a structured play activity that:
            1. Uses 2-4 toys from the provided inventory (no new purchases needed)
            2. Targets a specific O*NET cognitive or physical ability
            3. Is age-appropriate, fun, and takes 10-30 minutes
            4. Includes clear instructions parents can follow

            **Output format:**
            - title: A fun, adventure-style name (e.g., "The Tower Challenge", "Treasure Hunt Adventure")
            - target_skill: The O*NET ability name being developed
            - skill_id: The O*NET ID (e.g., "1.A.1.f.2")
            - duration_minutes: Estimated time (10-30)
            - toys_needed: List of 2-4 toys from the inventory to use
            - setup: One paragraph on how to prepare the activity
            - instructions: 3-5 clear steps for the activity
            - parent_tip: One sentence on how to make it more engaging or educational
        """,
        max_active_tis_per_dag=2
    )
    def generate_play_quest(zipped_input: tuple):
        toy_inventory, scan_record = zipped_input
        child_age = scan_record[2]
        return json.dumps({"toys": toy_inventory.get("items", []), "child_age": child_age})

    zipped_quest_input = toy_inventories.zip(_get_new_scans.output)
    play_quests = generate_play_quest.expand(zipped_input=zipped_quest_input)

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
            1. **Audit:** Analyze the provided inventory and assess current skill development.
            2. **Score:** Rate the child's current development in 6 categories (0-100 scale):
               - cognitive: problem solving, reasoning, memory
               - motor_fine: finger dexterity, precision, hand-eye coordination
               - motor_gross: body coordination, balance, strength
               - social_emotional: empathy, cooperation, emotional expression
               - creative: imagination, artistic expression, open-ended play
               - language: communication, vocabulary, storytelling
            3. **Roadmap:** Create a 3-item development roadmap with priorities:
               - Priority 1 (timeframe: "now"): Most critical gap to address immediately
               - Priority 2 (timeframe: "3_months"): Second priority for near-term
               - Priority 3 (timeframe: "6_months"): Third priority for longer-term growth

            **Requirements:**
            - In status_quo, summarize the dominant O*NET Ability clusters present.
            - In skill_scores, provide realistic scores based on the toy inventory analysis.
            - In roadmap, provide exactly 3 items. Each must include:
              - The specific O*NET Ability Name in missing_skill
              - The O*NET ID Code in skill_id (e.g., "1.A.1.f.2")
              - Which of the 6 categories it maps to in skill_category
              - A specific toy recommendation in recommended_toy
              - Scientific reasoning citing the O*NET ability
        """,
        max_active_tis_per_dag=2
    )
    def analyze_playroom(toy_inventory: dict):
        return json.dumps(toy_inventory)

    analysis_results = analyze_playroom.expand(toy_inventory=toy_inventories)

    @task.llm(
        model="gemini-3-flash-preview",
        output_type=ToyRecommendation,
        system_prompt="""
            You are a dual-role agent: CPSC Safety Auditor and Personal Shopper.

            **Input:** A development roadmap with 3 recommended toys and the child's age.

            **For EACH of the 3 toys in the roadmap:**

            **Step 1: Safety Audit**
            Check the toy against CPSC guidelines for the child's age.
            - If safe: Keep the recommendation (decision: "APPROVED").
            - If unsafe: Select a safer alternative that achieves the same developmental goal (decision: "SUBSTITUTED").

            **Step 2: Shopping Prep**
            Generate a specific 'amazon_search' for the FINAL toy.
            - Include brand names if they matter for safety.
            - Exclude generic terms that lead to low-quality knock-offs.

            **Requirements:**
            - Return exactly 3 items, one for each roadmap entry.
            - Preserve the timeframe ("now", "3_months", "6_months") from the input.
            - Decision must be "APPROVED" or "SUBSTITUTED".
            - Provide a clear 'safety_context' explaining your decision for each toy.
        """,
        max_active_tis_per_dag=2
    )
    def safety_check(zipped_input: tuple):
        analysis_result, scan_record = zipped_input
        child_age = scan_record[2]
        return json.dumps({"roadmap": analysis_result.get("roadmap", []), "child_age": child_age})

    zipped_input_safety = analysis_results.zip(_get_new_scans.output)
    recommendations = safety_check.expand(zipped_input=zipped_input_safety)

    @task
    def print_result(zipped_input: tuple):
        toy_inventory, analysis_result, toy_recommendation = zipped_input
        print("=" * 50)
        print("TOY INVENTORY:")
        print(json.dumps(toy_inventory, indent=2))
        print("=" * 50)
        print("SKILL SCORES:")
        print(json.dumps(analysis_result.get("skill_scores", {}), indent=2))
        print("=" * 50)
        print("DEVELOPMENT ROADMAP:")
        for item in analysis_result.get("roadmap", []):
            print(f"  [{item.get('timeframe')}] {item.get('recommended_toy')} - {item.get('missing_skill')}")
        print("=" * 50)
        print("SAFETY RECOMMENDATIONS:")
        for item in toy_recommendation.get("items", []):
            print(f"  [{item.get('timeframe')}] {item.get('decision')}: {item.get('recommended_toy')}")

    zipped_input_print = toy_inventories.zip(analysis_results, recommendations)
    print_result.expand(zipped_input=zipped_input_print)

    @task(max_active_tis_per_dag=2)
    def save_result(zipped_input: tuple):
        toy_inventory, play_quest, analysis_result, toy_recommendation, scan_record = zipped_input
        scan_id = str(scan_record[0])
        roadmap_items = analysis_result.get("roadmap", [])
        safety_items = toy_recommendation.get("items", [])

        merged_roadmap = []
        for i, roadmap_item in enumerate(roadmap_items):
            safety_item = safety_items[i] if i < len(safety_items) else {}
            merged_roadmap.append({
                **roadmap_item,
                "decision": safety_item.get("decision", "APPROVED"),
                "final_toy": safety_item.get("recommended_toy", roadmap_item.get("recommended_toy")),
                "safety_context": safety_item.get("safety_context", ""),
                "amazon_search": safety_item.get("amazon_search", "")
            })

        payload = {
            "status_quo": analysis_result.get("status_quo", ""),
            "skill_scores": analysis_result.get("skill_scores", {}),
            "roadmap": merged_roadmap,
            "toy_inventory": toy_inventory.get("items", []),
            "play_quest": play_quest
        }
        supabase = create_client(supabase_project_url, supabase_secret_key)

        supabase.table("scans").update({
            "status": "done",
            "results_json": payload
        }).eq("id", scan_id).execute()

    zipped_input_save = toy_inventories.zip(play_quests, analysis_results, recommendations, _get_new_scans.output)
    save_result.expand(zipped_input=zipped_input_save)

process_scans()
