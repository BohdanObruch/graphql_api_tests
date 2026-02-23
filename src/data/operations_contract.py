INVALID_TYPE_CASES = {
    "accountCurrent": """
        query {
          accountCurrent(accessToken: 123) {
            resource { login }
          }
        }
    """,
    "accounts": """
        query {
          accounts(withInactive: "false") {
            users { login }
            paging { totalPagesCount }
          }
        }
    """,
    "registerAccount": """
        mutation {
          registerAccount(registration: "bad") {
            id
            login
          }
        }
    """,
    "activateAccount": """
        mutation {
          activateAccount(activationToken: 123) {
            resource { login }
          }
        }
    """,
    "changeAccountEmail": """
        mutation {
          changeAccountEmail(changeEmail: "bad") {
            resource { login }
          }
        }
    """,
    "resetAccountPassword": """
        mutation {
          resetAccountPassword(resetPassword: "bad") {
            resource { login }
          }
        }
    """,
    "changeAccountPassword": """
        mutation {
          changeAccountPassword(changePassword: "bad") {
            resource { login }
          }
        }
    """,
    "updateAccount": """
        mutation {
          updateAccount(accessToken: 123, userData: "bad") {
            resource { login }
          }
        }
    """,
    "loginAccount": """
        mutation {
          loginAccount(login: "bad") {
            token
          }
        }
    """,
    "logoutAccount": """
        mutation {
          logoutAccount(accessToken: 123)
        }
    """,
    "logoutAllAccount": """
        mutation {
          logoutAllAccount(accessToken: 123)
        }
    """,
}

