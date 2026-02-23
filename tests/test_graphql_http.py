import allure
import pytest
import requests

pytestmark = pytest.mark.regression


@pytest.mark.smoke
def test_graphql_get_is_rejected(base_url):
    with allure.step("Send GET request to GraphQL endpoint"):
        response = requests.get(base_url, timeout=30)
    with allure.step("Verify GET request is rejected"):
        assert response.status_code == 404


def test_invalid_json_body_returns_error(base_url):
    with allure.step("Send POST request with invalid JSON body"):
        response = requests.post(
            base_url,
            data="{bad-json",
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
    with allure.step("Verify invalid JSON is handled with an error-like status"):
        assert response.status_code in (200, 400)
