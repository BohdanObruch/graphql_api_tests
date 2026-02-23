from src.clients.graphql_client import GraphQLClient

INTROSPECTION_QUERY = """
query {
  __schema {
    queryType { name }
    mutationType { name }
    types {
      name
      kind
      inputFields {
        name
        type {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
            }
          }
        }
      }
      fields(includeDeprecated: true) {
        name
        args {
          name
          type {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
              }
            }
          }
        }
        type {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
            }
          }
        }
      }
    }
  }
}
"""


def fetch_schema(client: GraphQLClient) -> dict:
    response = client.post(INTROSPECTION_QUERY)
    return client.parse_json(response)


def unwrap_type(type_node: dict) -> str:
    kind = type_node.get("kind")
    if kind == "NON_NULL":
        return f"{unwrap_type(type_node['ofType'])}!"
    if kind == "LIST":
        return f"[{unwrap_type(type_node['ofType'])}]"
    if type_node.get("name"):
        return type_node["name"]
    of_type = type_node.get("ofType")
    return unwrap_type(of_type) if of_type else "Unknown"
