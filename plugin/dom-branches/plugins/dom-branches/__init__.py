"""dom-branches: read-only DOM claim branches pane.

The pane's data comes from dashboard/plugin_api.py (mounted by the gateway under
/api/plugins/dom-branches) and the desktop half in desktop-plugins/dom-branches.
This module registers no tools or hooks; register() exists only so Hermes'
plugin loader accepts the package.
"""


def register(ctx) -> None:
    return None
