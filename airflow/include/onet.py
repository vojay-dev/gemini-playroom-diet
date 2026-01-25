import os
from airflow.providers.postgres.hooks.postgres import PostgresHook
from supabase import create_client

_POSTGRES_CONN_ID = "postgres_playroom_diet"


def get_careers_for_skill(skill_name: str) -> list[str]:
    """
    Queries the O*NET database to find jobs that require a specific skill at a high level.
    """

    try:
        url = os.getenv("SUPABASE_PROJECT_URL")
        key = os.getenv("SUPABASE_SECRET_KEY")
        supabase = create_client(url, key)

        response = supabase.rpc("get_careers_for_skill", {"skill_name": skill_name}).execute()
        return [item['job_title'] for item in response.data]

    except Exception as e:
        print(f"Tool Error: {e}")
        return []
