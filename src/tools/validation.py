from __future__ import annotations

from dataclasses import dataclass

FORBIDDEN_SQL_TOKENS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "pragma",
    "attach",
    "detach",
    "replace",
    "vacuum",
}


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    sql: str | None = None
    error_code: str | None = None
    error: str | None = None
    hint: str | None = None


def validate_select_sql(sql: object) -> ValidationResult:
    if not isinstance(sql, str) or not sql.strip():
        return ValidationResult(
            ok=False,
            error_code="invalid_args",
            error="query.args.sql must be a non-empty string.",
            hint="Return a query tool call with a SELECT statement.",
        )

    stripped = sql.strip()
    if ";" in stripped.rstrip(";"):
        return ValidationResult(
            ok=False,
            error_code="unsafe_sql",
            error="Only one SQL statement is allowed.",
            hint="Use a single SELECT statement against sales_metrics_enriched.",
        )
    stripped = stripped.rstrip(";").strip()
    lowered = stripped.lower()
    tokens = _tokens(lowered)

    if not lowered.startswith("select "):
        return ValidationResult(
            ok=False,
            error_code="unsafe_sql",
            error="Only read-only SELECT queries are allowed.",
            hint="Rewrite the request as a SELECT against sales_metrics_enriched.",
        )
    if "sales_metrics_enriched" not in tokens:
        return ValidationResult(
            ok=False,
            error_code="unsafe_sql",
            error="Queries may only read from sales_metrics_enriched.",
            hint="Use FROM sales_metrics_enriched and the documented columns.",
        )
    if FORBIDDEN_SQL_TOKENS.intersection(tokens):
        return ValidationResult(
            ok=False,
            error_code="unsafe_sql",
            error="Write/admin SQL keywords are not allowed.",
            hint="Use a read-only SELECT query.",
        )
    if "*" in tokens:
        return ValidationResult(
            ok=False,
            error_code="invalid_args",
            error="SELECT * is not allowed in this demo.",
            hint="Choose the specific columns needed for the answer.",
        )

    guarded_sql = stripped
    if "limit" not in tokens:
        guarded_sql = f"{guarded_sql} LIMIT 100"
    return ValidationResult(ok=True, sql=guarded_sql)


def _tokens(sql: str) -> set[str]:
    normalized = sql
    for char in ",()[]{}+-/%\n\r\t":
        normalized = normalized.replace(char, " ")
    return {part for part in normalized.split(" ") if part}
