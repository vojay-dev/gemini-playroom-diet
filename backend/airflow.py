import requests

class AirflowClient:

    def __init__(self, host: str, username: str, password: str, token: str | None = None):
        self.host = host
        self.username = username
        self.password = password
        self.session = requests.Session()

        self._static_token = token is not None
        self.token = token if self._static_token else self.get_jwt_token()
        self._update_session_auth()

    def get_jwt_token(self) -> str:
        url = f"{self.host}/auth/token"
        response = requests.post(url, json={"username": self.username, "password": self.password})
        response.raise_for_status()
        return response.json().get("access_token")

    def trigger_dag(self, dag_id: str, payload: dict | None = None) -> str:
        url = f"{self.host}/api/v2/dags/{dag_id}/dagRuns"
        payload = payload or {"logical_date": None}
        response = self.session.post(url, json=payload)

        if response.status_code == 401 and not self._static_token:
            self.token = self.get_jwt_token()
            self._update_session_auth()
            response = self.session.post(url, json=payload)

        response.raise_for_status()
        return response.json().get("dag_run_id")

    def _update_session_auth(self):
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

if __name__ == "__main__":
    client = AirflowClient("http://localhost:8080", "airflow", "airflow")
    dag_run_id = client.trigger_dag("process_scans")
    print(f"Triggered DAG run with ID: {dag_run_id}")
