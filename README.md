# GraphQL API Test Suite

Automated test project for validating a GraphQL API endpoint with focus on contract stability, protocol validation, and
operation-level negative checks.

## Purpose

This repository verifies that the runtime GraphQL API matches documented behavior and schema expectations.

Primary goals:

- detect schema drift between runtime API and `schema.graphql`,
- validate GraphQL transport/protocol behavior,
- ensure all documented root operations are covered by tests,
- provide fast smoke checks and full regression checks,
- generate step-by-step Allure reports for debugging and traceability.

## What Is Covered

- HTTP/transport checks:
    - GET rejection behavior,
    - invalid JSON handling,
    - missing `Content-Type` behavior consistency,
    - large payload handling.
- GraphQL validation checks:
    - unknown field/argument,
    - wrong argument types,
    - required argument enforcement,
    - required selection-set validation,
    - variable declaration/use validation,
    - invalid UUID format handling.
- Schema contract checks:
    - runtime `Query`/`Mutation` root names,
    - root operation names/args/return types vs snapshot,
    - `MutationResult` enum contains `OK`,
    - input object fields/types match SDL snapshot.
- Operation coverage checks:
    - all runtime root operations are mapped in `INVALID_TYPE_CASES`.
- Business-flow oriented negative checks:
    - invalid token/credentials behavior for account operations.

## Project Structure

```text
src/
  clients/graphql_client.py
  services/schema_service.py
  data/operations_contract.py
tests/
  conftest.py
  test_graphql_contract.py
  test_graphql_http.py
  test_graphql_operations.py
  test_graphql_validation.py
  test_graphql_business_flows.py
schema.graphql
TESTING_GRAPHQL_API.md
```

## Requirements

- Python 3.14+
- Dependencies from `pyproject.toml`
- `.env` with:

```env
BASE_URL=""
```

## Run Tests

All tests:

```powershell
pytest -q
```

Smoke only:

```powershell
pytest -q -m smoke
```

Regression only:

```powershell
pytest -q -m regression
```

Lint:

```powershell
ruff check .
```

## Allure Reporting

All tests use `allure.step(...)` markers for step-level reporting.

Generate results with pytest (configured in `pyproject.toml`):

- output directory: `test-result/allure-results`

Open report (example):

```powershell
allure serve test-result/allure-results
```

## Documentation Sources

The suite is aligned with:

- `schema.graphql` (SDL snapshot),

---

# Набор тестов GraphQL API

Проект автоматизированного тестирования GraphQL API с фокусом на стабильность контракта, валидацию протокола и
негативные проверки операций.

## Назначение

Этот репозиторий проверяет, что runtime API соответствует документированному поведению и ожиданиям схемы.

Основные цели:

- выявлять расхождения между runtime API и `schema.graphql`,
- проверять транспортный и протокольный уровень GraphQL,
- гарантировать покрытие всех документированных root-операций,
- иметь быстрый smoke-прогон и полный regression-прогон,
- формировать пошаговые отчеты Allure для отладки и трассировки.

## Что покрыто

- HTTP/transport проверки:
    - поведение при GET,
    - обработка невалидного JSON,
    - консистентность поведения без `Content-Type`,
    - обработка больших payload.
- Проверки валидации GraphQL:
    - неизвестное поле/аргумент,
    - неверные типы аргументов,
    - обязательные аргументы,
    - обязательный selection set,
    - валидация переменных запроса,
    - невалидный UUID.
- Проверки контрактов схемы:
    - root-типы `Query`/`Mutation`,
    - имена операций/аргументы/типы возврата против snapshot,
    - наличие `OK` в enum `MutationResult`,
    - соответствие input-типов SDL snapshot.
- Проверка полноты покрытия операций:
    - все runtime root-операции присутствуют в `INVALID_TYPE_CASES`.
- Негативные checks по бизнес-потокам:
    - поведение с невалидным токеном/кредами в account-операциях.

## Структура проекта

```text
src/
  clients/graphql_client.py
  services/schema_service.py
  data/operations_contract.py
tests/
  conftest.py
  test_graphql_contract.py
  test_graphql_http.py
  test_graphql_operations.py
  test_graphql_validation.py
  test_graphql_business_flows.py
schema.graphql
```

## Требования

- Python 3.14+
- Зависимости из `pyproject.toml`
- `.env` с:

```env
BASE_URL=""
```

## Запуск тестов

Все тесты:

```powershell
pytest -q
```

Только smoke:

```powershell
pytest -q -m smoke
```

Только regression:

```powershell
pytest -q -m regression
```

Линт:

```powershell
ruff check .
```

## Allure отчеты

Во всех тестах используются `allure.step(...)` для пошаговой отчетности.

Результаты формируются через pytest (настроено в `pyproject.toml`):

- директория результатов: `test-result/allure-results`

Открыть отчет (пример):

```powershell
allure serve test-result/allure-results
```

## Источники документации

Набор тестов синхронизирован с:

- `schema.graphql` (SDL snapshot),
