"""Sidebar navigation for the demo project, registered by ``DemoConfig.ready``."""

# A menu entry whose view_name will not resolve is dropped without an error, so a
# page missing from the sidebar is usually a name that does not match the route.
from flex_menu import MenuItem
from mvp.menus import AppMenu, MenuGroup

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
        MenuGroup(
            name="info_dialogs",
            extra_context={"label": "Info dialogs"},
            children=[
                MenuItem(
                    name=name, view_name=f"info_{name}", extra_context={"label": label}
                )
                for name, label in [
                    ("whole_page", "A whole page"),
                    ("section", "One section"),
                    ("notices", "Notices and pictures"),
                    ("staff", "Staff only"),
                    ("moved", "A moved page"),
                ]
            ],
        ),
    ]
)

# The project's own entry in the guide's sidebar. It follows the contents, stays
# there when the docs are rebuilt, and is drawn for staff only.
docs.menu.append(staff_guide.menu_item())
