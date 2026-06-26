"""CRM dashboard demo agent package."""

from __future__ import annotations

__all__ = ["crm_dashboard_agent"]


def __getattr__(name: str):
    if name == "crm_dashboard_agent":
        from .agent import crm_dashboard_agent

        return crm_dashboard_agent
    raise AttributeError(name)
