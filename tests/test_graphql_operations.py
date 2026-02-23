import allure
import pytest

from src.data.operations_contract import INVALID_TYPE_CASES
from src.services.schema_service import fetch_schema

pytestmark = pytest.mark.regression


@pytest.mark.parametrize(
    ("operation_name", "query"),
    list(INVALID_TYPE_CASES.items()),
)
def test_every_documented_operation_rejects_invalid_argument_types(gql, operation_name, query):
    with allure.step(f"Execute operation {operation_name} with invalid argument types"):
        response = gql.post(query)
    with allure.step(f"Verify operation {operation_name} returns validation error status"):
        assert response.status_code in (200, 400), operation_name
    with allure.step(f"Verify operation {operation_name} response contains GraphQL errors"):
        body = gql.parse_json(response)
        assert "errors" in body, operation_name
        assert body["errors"], operation_name


def test_required_arguments_are_enforced(gql):
    query = """
    mutation {
      activateAccount {
        resource { login }
      }
    }
    """
    with allure.step("Execute mutation without required activationToken argument"):
        response = gql.post(query)
    with allure.step("Verify response status indicates validation handling"):
        assert response.status_code in (200, 400)
    with allure.step("Verify missing required argument is reported in errors"):
        body = gql.parse_json(response)
        assert "errors" in body
        assert body["errors"]


def test_all_runtime_operations_have_coverage_cases(gql):
    with allure.step("Fetch runtime GraphQL schema via introspection"):
        runtime_data = fetch_schema(gql)
        assert "errors" not in runtime_data
        schema = runtime_data["data"]["__schema"]
    with allure.step("Collect runtime query and mutation operation names"):
        types = {t["name"]: t for t in schema["types"]}
        query_root = types[schema["queryType"]["name"]]
        mutation_root = types[schema["mutationType"]["name"]]
        runtime_operations = {field["name"] for field in (query_root["fields"] or [])}
        runtime_operations.update({field["name"] for field in (mutation_root["fields"] or [])})
    with allure.step("Verify every runtime operation has a negative coverage case"):
        assert runtime_operations == set(INVALID_TYPE_CASES.keys())


def test_accounts_requires_with_inactive_argument(gql):
    with allure.step("Execute accounts query without required withInactive argument"):
        response = gql.post(
            """
            query {
              accounts {
                paging { totalPagesCount }
              }
            }
            """
        )
    with allure.step("Verify GraphQL reports missing required argument"):
        assert response.status_code in (200, 400)
        body = gql.parse_json(response)
        assert "errors" in body
        assert body["errors"]


def test_login_account_requires_remember_me(gql):
    with allure.step("Execute loginAccount mutation without required rememberMe field"):
        response = gql.post(
            """
            mutation {
              loginAccount(login: { login: "user", password: "pass" }) {
                token
              }
            }
            """
        )
    with allure.step("Verify GraphQL reports missing required rememberMe field"):
        assert response.status_code in (200, 400)
        body = gql.parse_json(response)
        assert "errors" in body
        assert body["errors"]
