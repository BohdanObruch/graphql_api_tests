import json

import requests


class GraphQLClient:
    def __init__(self, base_url: str, timeout: int = 30) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def post(self, query: str, variables: dict | None = None) -> requests.Response:
        payload = {"query": query}
        if variables is not None:
            payload["variables"] = variables
        return requests.post(
            self.base_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=self.timeout,
        )

    @staticmethod
    def parse_json(response: requests.Response) -> dict:
        return json.loads(response.text)

