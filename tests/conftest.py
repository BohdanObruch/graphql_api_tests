import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from src.clients.graphql_client import GraphQLClient

ROOT = Path(__file__).resolve().parent.parent


load_dotenv()


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL")


@pytest.fixture(scope="session")
def gql(base_url: str) -> GraphQLClient:
    return GraphQLClient(base_url=base_url)


@pytest.fixture(scope="session")
def schema_snapshot_path() -> Path:
    return ROOT / "schema.graphql"
