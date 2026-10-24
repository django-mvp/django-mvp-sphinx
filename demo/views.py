"""The demo project's pages."""

# MVPTemplateView, not TemplateView: it supplies the page title, subtitle and
# breadcrumbs the application shell draws around the content.
from django.utils.translation import gettext_lazy as _
from mvp.views import MVPTemplateView

from demo.mounted import docs, staff_guide
from mvp_sphinx.extracts import PageExtract


class OverviewView(MVPTemplateView):
    """What this package is, and what it puts on a page."""

    template_name = "demo/overview.html"
    page_title = "Overview"
    page_subtitle = "What this package puts on a page"
    breadcrumbs = [{"text": "Overview"}]


class InPageView(MVPTemplateView):
    """A screen whose template places a section of the guide in the page itself."""

    template_name = "demo/in_page.html"
    page_title = _("Searching")
    page_subtitle = _("A section of the guide, placed in the page by its template")
    breadcrumbs = [{"text": _("Searching")}]


class InfoDialogView(MVPTemplateView):
    """A screen of the site whose info dialog holds a page of the documentation.

    Attributes:
        app: The documentation app the page comes from.
        address: The page's address in that app, with a section's anchor or not.
        intro: What the screen says about the dialog beside its title.
    """

    template_name = "demo/info_dialog.html"
    app = docs
    address = ""
    intro = ""

    def get_extract(self) -> PageExtract | None:
        """Return the page or section, once per request."""
        if not hasattr(self, "extract"):
            self.extract = self.app.page_extract(self.address, self.request)
        return self.extract

    def get_page_info(self):
        """Show the page in the dialog, or no icon when it can't be had."""
        return self.get_extract() or ""

    def get_page_info_actions(self):
        """Offer the full page from the foot of the dialog."""
        extract = self.get_extract()
        if extract is None:
            return []
        return [
            {
                "text": _("Open the full page"),
                "href": extract.url,
                "icon": "document",
                "variant": "primary",
            }
        ]

    def get_context_data(self, **kwargs):
        """Add what the screen says about its dialog."""
        context = super().get_context_data(**kwargs)
        context["intro"] = self.intro
        return context

    def get_breadcrumbs(self):
        """Return the trail: the info dialogs, then this screen."""
        return [{"text": _("Info dialogs")}, {"text": self.get_page_title()}]


class WholePageView(InfoDialogView):
    """The info dialog holds a whole page of the guide."""

    page_title = _("Getting around")
    page_subtitle = _("The info dialog holds a whole page of the guide")
    address = "first-visit/finding-your-way/"
    intro = _(
        "This screen stands in for one of your own. Its explanation is the guide's "
        "page on finding your way, shown whole in the info dialog."
    )


class SectionView(InfoDialogView):
    """The info dialog holds one section of a page."""

    page_title = _("Search")
    page_subtitle = _("The info dialog holds one section of a page")
    address = "first-visit/finding-your-way/#searching-the-guide"
    intro = _(
        "The guide covers searching in one section of a longer page. The info dialog "
        "holds that section and nothing else."
    )


class NoticesView(InfoDialogView):
    """The info dialog holds a page of notices, tables and a picture."""

    page_title = _("Notices")
    page_subtitle = _("Notices, tables and a picture in the info dialog")
    address = "reference/notices/"
    intro = _(
        "The guide's page of notices has every kind of notice, a picture and a "
        "table, so this dialog shows how each looks outside the guide."
    )


class StaffOnlyView(InfoDialogView):
    """The info dialog holds a page of the staff guide, for staff only."""

    page_title = _("Staff accounts")
    page_subtitle = _("A page of the staff guide, shown to staff only")
    app = staff_guide
    address = "accounts/"
    intro = _(
        "The explanation comes from the staff guide, which only staff may read. "
        "Signed in as staff, the info icon is beside the title. Anyone else sees "
        "no icon at all."
    )


class MissingPageView(InfoDialogView):
    """The info dialog names a page the guide doesn't have."""

    page_title = _("A moved page")
    page_subtitle = _("The guide has no page at the address this screen names")
    address = "first-visit/a-page-that-moved/"
    intro = _(
        "This screen asks for a page the guide doesn't have, as if it had been "
        "moved. There is no info icon, the screen works as usual, and the server "
        "log has a warning naming the address."
    )
