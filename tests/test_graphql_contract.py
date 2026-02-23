import json
import re

import allure
import pytest

from src.services.schema_service import fetch_schema, unwrap_type

pytestmark = pytest.mark.regression


def _read_json_snapshot(snapshot_path):
    for encoding in ("utf-8", "cp1251", "latin-1", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return json.loads(snapshot_path.read_text(encoding=encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return None


def _extract_type_body(sdl: str, type_name: str) -> str:
    match = re.search(rf"\btype\s+{type_name}\b", sdl)
    if not match:
        return ""
    start = sdl.find("{", match.end())
    if start == -1:
        return ""

    depth = 0
    for index in range(start, len(sdl)):
        char = sdl[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return sdl[start + 1 : index]
    return ""


def _parse_sdl_fields(type_body: str) -> dict[str, dict]:
    fields: dict[str, dict] = {}
    buffer = ""
    paren_depth = 0

    for raw_line in type_body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        buffer = f"{buffer} {line}".strip()
        paren_depth += line.count("(") - line.count(")")

        if paren_depth != 0 or ":" not in buffer:
            continue

        signature = " ".join(buffer.split())
        parsed = re.match(
            r"^([_A-Za-z][_0-9A-Za-z]*)\s*(?:\((.*)\))?\s*:\s*([!\[\]_A-Za-z][_0-9A-Za-z!\[\]]*)",
            signature,
        )
        buffer = ""
        if not parsed:
            continue

        field_name, args_raw, return_type = parsed.groups()
        args: dict[str, str] = {}
        if args_raw:
            for arg_name, arg_type in re.findall(
                r"([_A-Za-z][_0-9A-Za-z]*)\s*:\s*([!\[\]_A-Za-z][_0-9A-Za-z!\[\]]*)",
                args_raw,
            ):
                args[arg_name] = arg_type

        fields[field_name] = {"type": return_type, "args": args}

    return fields


def _read_sdl_snapshot(snapshot_path) -> dict | None:
    try:
        raw = snapshot_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return None

    sdl_without_descriptions = re.sub(r'""".*?"""', "", raw, flags=re.S)
    sdl = re.sub(r"#.*", "", sdl_without_descriptions)
    return {
        "queryType": {"name": "Query"},
        "mutationType": {"name": "Mutation"},
        "sdl": sdl,
        "roots": {
            "Query": _parse_sdl_fields(_extract_type_body(sdl, "Query")),
            "Mutation": _parse_sdl_fields(_extract_type_body(sdl, "Mutation")),
        },
    }


def _runtime_root_operations(runtime_schema: dict) -> dict[str, dict]:
    types = {t["name"]: t for t in runtime_schema["types"] if t["name"]}
    operations: dict[str, dict] = {}
    for root_name in (runtime_schema["queryType"]["name"], runtime_schema["mutationType"]["name"]):
        fields_map = {}
        for field in types[root_name]["fields"] or []:
            fields_map[field["name"]] = {
                "type": unwrap_type(field["type"]),
                "args": {arg["name"]: unwrap_type(arg["type"]) for arg in field["args"]},
            }
        operations[root_name] = fields_map
    return operations


def _snapshot_root_operations(snapshot_path) -> dict:
    json_snapshot = _read_json_snapshot(snapshot_path)
    if json_snapshot is not None:
        snapshot_schema = json_snapshot["data"]["__schema"]
        return {
            "queryType": snapshot_schema["queryType"],
            "mutationType": snapshot_schema["mutationType"],
            "roots": _runtime_root_operations(snapshot_schema),
        }

    sdl_snapshot = _read_sdl_snapshot(snapshot_path)
    if sdl_snapshot is not None:
        return sdl_snapshot

    raise ValueError(f"Cannot decode snapshot file: {snapshot_path}")


def _parse_sdl_input_objects(sdl: str) -> dict[str, dict[str, str]]:
    input_objects: dict[str, dict[str, str]] = {}
    for input_name, input_body in re.findall(r"\binput\s+([_A-Za-z][_0-9A-Za-z]*)\s*\{(.*?)\}", sdl, flags=re.S):
        fields: dict[str, str] = {}
        for field_name, field_type in re.findall(
            r"([_A-Za-z][_0-9A-Za-z]*)\s*:\s*([!\[\]_A-Za-z][_0-9A-Za-z!\[\]]*)",
            input_body,
        ):
            fields[field_name] = field_type
        input_objects[input_name] = fields
    return input_objects


@pytest.mark.smoke
def test_graphql_smoke_typename(gql):
    with allure.step("Send __typename smoke query"):
        response = gql.post("query { __typename }")
    with allure.step("Verify successful response status"):
        assert response.status_code == 200
    with allure.step("Verify response data contains Query typename"):
        body = gql.parse_json(response)
        assert "errors" not in body
        assert body["data"]["__typename"] == "Query"


def test_runtime_root_operations_match_snapshot(gql, schema_snapshot_path):
    with allure.step("Fetch runtime GraphQL schema via introspection"):
        runtime_data = fetch_schema(gql)
        assert "errors" not in runtime_data
        runtime_schema = runtime_data["data"]["__schema"]
    with allure.step("Load schema snapshot from schema.graphql or json snapshot"):
        snapshot = _snapshot_root_operations(schema_snapshot_path)
    with allure.step("Verify root type names match"):
        assert runtime_schema["queryType"]["name"] == snapshot["queryType"]["name"]
        assert runtime_schema["mutationType"]["name"] == snapshot["mutationType"]["name"]
    with allure.step("Verify root operations, return types, and argument types match snapshot"):
        runtime_roots = _runtime_root_operations(runtime_schema)
        assert runtime_roots == snapshot["roots"]


def test_mutation_result_enum_contains_ok(gql):
    query = """
    query {
      __type(name: "MutationResult") {
        kind
        enumValues {
          name
        }
      }
    }
    """
    with allure.step("Send introspection query for MutationResult enum"):
        response = gql.post(query)
    with allure.step("Verify successful response status"):
        assert response.status_code == 200
    with allure.step("Verify MutationResult enum contains OK value"):
        body = gql.parse_json(response)
        assert "errors" not in body
        assert body["data"]["__type"]["kind"] == "ENUM"
        assert "OK" in [v["name"] for v in body["data"]["__type"]["enumValues"]]


def test_input_object_fields_match_schema_snapshot(gql, schema_snapshot_path):
    with allure.step("Load input object definitions from SDL snapshot"):
        snapshot = _read_sdl_snapshot(schema_snapshot_path)
        assert snapshot is not None
        expected_inputs = _parse_sdl_input_objects(snapshot["sdl"])
        assert expected_inputs
    with allure.step("Fetch runtime GraphQL schema for input object verification"):
        runtime_data = fetch_schema(gql)
        assert "errors" not in runtime_data
        runtime_schema = runtime_data["data"]["__schema"]
        runtime_types = {t["name"]: t for t in runtime_schema["types"] if t["name"]}
    with allure.step("Verify input field names and types are unchanged"):
        for input_name, expected_fields in expected_inputs.items():
            assert input_name in runtime_types, input_name
            runtime_input_fields = runtime_types[input_name]["inputFields"] or []
            runtime_fields = {field["name"]: unwrap_type(field["type"]) for field in runtime_input_fields}
            assert runtime_fields == expected_fields, input_name
