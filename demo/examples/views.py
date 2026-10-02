"""The views behind the guide's live examples."""

import time

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from mvp.views import MVPFormView, MVPTemplateView

from demo.examples.forms import ContactForm


class ContactView(MVPFormView):
    """Take a message, thank the sender, and show the empty form again."""

    form_class = ContactForm
    template_name = "demo/examples/contact.html"
    page_title = "Contact us"

    def form_valid(self, form):
        name = form.cleaned_data["name"]
        messages.success(self.request, f"Thanks, {name}. Nothing was sent.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path


class StatusView(MVPTemplateView):
    """A page with no form: what the site says about an order."""

    template_name = "demo/examples/status.html"
    page_title = "Order status"


class SlowView(StatusView):
    """The same page, three seconds late."""

    def get(self, request, *args, **kwargs):
        time.sleep(3)
        return super().get(request, *args, **kwargs)


class StaffNoteView(UserPassesTestMixin, MVPTemplateView):
    """A page only staff may open."""

    template_name = "demo/examples/staff_note.html"
    page_title = "A note for staff"

    def test_func(self):
        return self.request.user.is_staff


class BrokenView(MVPTemplateView):
    """A page that fails every time."""

    template_name = "demo/examples/status.html"

    def get(self, request, *args, **kwargs):
        raise RuntimeError("This example fails on purpose.")
