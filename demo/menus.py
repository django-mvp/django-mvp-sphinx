"""Sidebar navigation for the demo project, registered by ``DemoConfig.ready``."""

# A menu entry whose view_name will not resolve is dropped without an error, so a
# page missing from the sidebar is usually a name that does not match the route.
from flex_menu import MenuItem
from mvp.menus import AppMenu

from demo.mounted import docs, staff_guide

AppMenu.extend(
    [
        MenuItem(
            name="overview",
            view_name="overview",
            extra_context={"label": "Overview", "icon": "overview"},
        ),
        docs.menu_item(),
        staff_guide.menu_item(),
    ]
)

# The project's own entry in the guide's sidebar. It follows the contents, stays
# there when the docs are rebuilt, and is drawn for staff only.
docs.menu.append(staff_guide.menu_item())
