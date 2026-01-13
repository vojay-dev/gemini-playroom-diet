from airflow.configuration import AIRFLOW_HOME
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk import dag, chain

_POSTGRES_CONN_ID = "postgres_playroom_diet"

@dag(
    template_searchpath=f"{AIRFLOW_HOME}/include/sql"
)
def process_scans():

    _get_new_scans = SQLExecuteQueryOperator(
        task_id="get_new_scans",
        conn_id=_POSTGRES_CONN_ID,
        sql="SELECT * FROM public.scans WHERE status = 'processing';",
    )

process_scans()
