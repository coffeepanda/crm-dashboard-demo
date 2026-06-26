from __future__ import annotations

from pathlib import Path

from aethergraph import start_server

from crm_dashboard_demo.db.connection import ensure_database


def main() -> None:
    ensure_database()
    project_root = Path(__file__).resolve().parent
    url = start_server(
        load_modules=["crm_dashboard_demo.agent"],
        project_root=str(project_root),
    )
    print(f"CRM dashboard demo server running at {url}")


if __name__ == "__main__":
    main()
