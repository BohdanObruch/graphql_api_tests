import allure
import pytest

pytestmark = pytest.mark.regression


def test_account_current_with_invalid_token_returns_error(gql):
    with allure.step("Query accountCurrent with invalid access token"):
        response = gql.post(
            """
            query ($accessToken: String) {
              accountCurrent(accessToken: $accessToken) {
                resource { login }
              }
            }
            """,
            variables={"accessToken": "invalid-token"},
        )
    with allure.step("Verify invalid token is rejected"):
        assert response.status_code in (200, 400)
        body = gql.parse_json(response)
        assert "errors" in body
        assert body["errors"]


def test_accounts_with_inactive_true_returns_paging(gql):
    with allure.step("Query accounts list with withInactive=true"):
        response = gql.post(
            """
            query {
              accounts(withInactive: true) {
                users { login }
                paging { totalPagesCount currentPage pageSize }
              }
            }
            """
        )
    with allure.step("Verify accounts response contract"):
        assert response.status_code == 200
        body = gql.parse_json(response)
        assert "errors" not in body
        assert body["data"]["accounts"]["paging"]["totalPagesCount"] >= 0


def test_login_account_with_invalid_credentials_returns_error(gql):
    with allure.step("Attempt login with invalid credentials"):
        response = gql.post(
            """
            mutation ($credentials: LoginCredentialsInput) {
              loginAccount(login: $credentials) {
                token
              }
            }
            """,
            variables={
                "credentials": {
                    "login": "unknown-user",
                    "password": "wrong-password",
                    "rememberMe": False,
                }
            },
        )
    with allure.step("Verify invalid credentials are rejected"):
        assert response.status_code in (200, 400)
        body = gql.parse_json(response)
        assert "errors" in body
        assert body["errors"]


def test_logout_with_invalid_token_returns_error(gql):
    with allure.step("Attempt logoutAccount with invalid token"):
        response = gql.post(
            """
            mutation ($accessToken: String) {
              logoutAccount(accessToken: $accessToken)
            }
            """,
            variables={"accessToken": "invalid-token"},
        )
    with allure.step("Verify invalid token is rejected"):
        assert response.status_code in (200, 400, 500)
        if response.status_code != 500:
            body = gql.parse_json(response)
            assert "errors" in body
            assert body["errors"]


def test_update_account_with_invalid_token_returns_error(gql):
    with allure.step("Attempt updateAccount using invalid token"):
        response = gql.post(
            """
            mutation {
              updateAccount(accessToken: "invalid-token", userData: {name: "name"}) {
                resource { login }
              }
            }
            """
        )
    with allure.step("Verify invalid token is rejected"):
        assert response.status_code in (200, 400)
        body = gql.parse_json(response)
        assert "errors" in body
        assert body["errors"]
