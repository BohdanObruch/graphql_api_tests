import time

import allure
import pytest
import requests

pytestmark = pytest.mark.regression


def _assert_graphql_error_response(gql, response):
    assert response.status_code in (200, 400)
    body = gql.parse_json(response)
    assert "errors" in body
    assert body["errors"]


@pytest.mark.smoke
def test_post_valid_query_returns_json(gql):
    with allure.step("Send valid GraphQL POST query"):
        response = gql.post("query { __typename }")
    with allure.step("Verify successful HTTP status and GraphQL data payload"):
        assert response.status_code == 200
        body = gql.parse_json(response)
        assert "errors" not in body
        assert body["data"]["__typename"] == "Query"


@pytest.mark.smoke
def test_smoke_query_response_time_under_sla(gql):
    with allure.step("Measure response time for smoke __typename query"):
        started_at = time.perf_counter()
        response = gql.post("query { __typename }")
        elapsed = time.perf_counter() - started_at
    with allure.step("Verify response is within SLA threshold"):
        assert response.status_code == 200
        assert elapsed < 15


def test_missing_content_type_behavior_is_consistent(base_url):
    with allure.step("Send POST without Content-Type header"):
        response = requests.post(base_url, data='{"query":"query { __typename }"}', timeout=30)
    with allure.step("Verify API handles missing Content-Type without server error"):
        assert response.status_code in (200, 400, 404, 415)
        assert response.status_code < 500


def test_large_payload_handling(base_url):
    with allure.step("Send oversized but valid GraphQL request payload"):
        large_padding = " " * 200_000
        payload = {"query": f"query {{ __typename }}{large_padding}"}
        response = requests.post(base_url, json=payload, timeout=30)
    with allure.step("Verify large payload does not cause server-side failure"):
        assert response.status_code in (200, 400, 413)
        assert response.status_code < 500


def test_unknown_query_field_returns_error(gql):
    with allure.step("Send query with unknown root field"):
        response = gql.post("query { totallyUnknownField }")
    with allure.step("Verify GraphQL validation error is returned"):
        _assert_graphql_error_response(gql, response)


def test_unknown_argument_returns_error(gql):
    with allure.step("Send valid operation with unknown argument"):
        response = gql.post(
            """
            query {
              accountCurrent(accessToken: "token", unknownArg: 1) {
                resource { login }
              }
            }
            """
        )
    with allure.step("Verify GraphQL validation error is returned"):
        _assert_graphql_error_response(gql, response)


def test_field_without_selection_set_returns_error(gql):
    with allure.step("Send query for object-returning field without selection set"):
        response = gql.post('query { accountCurrent(accessToken: "token") }')
    with allure.step("Verify selection-set validation error is returned"):
        _assert_graphql_error_response(gql, response)


def test_unused_variable_returns_error(gql):
    with allure.step("Send query that declares but does not use a variable"):
        response = gql.post(
            """
            query ($withInactive: Boolean!) {
              __typename
            }
            """,
            variables={"withInactive": True},
        )
    with allure.step("Verify variable validation error is returned"):
        _assert_graphql_error_response(gql, response)


def test_missing_declared_variable_returns_error(gql):
    with allure.step("Send query requiring variable but omit variables payload"):
        response = gql.post(
            """
            query ($withInactive: Boolean!) {
              accounts(withInactive: $withInactive) {
                paging { totalPagesCount }
              }
            }
            """
        )
    with allure.step("Verify missing variable validation error is returned"):
        assert response.status_code in (200, 400, 500)
        if response.status_code != 500:
            body = gql.parse_json(response)
            assert "errors" in body
            assert body["errors"]


def test_invalid_uuid_format_returns_error(gql):
    with allure.step("Send mutation with invalid UUID format"):
        response = gql.post(
            """
            mutation {
              activateAccount(activationToken: "not-a-uuid") {
                resource { login }
              }
            }
            """
        )
    with allure.step("Verify UUID validation error is returned"):
        _assert_graphql_error_response(gql, response)
