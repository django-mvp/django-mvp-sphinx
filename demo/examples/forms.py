"""The form behind the contact example."""

from django import forms


class ContactForm(forms.Form):
    """A message to the people who run the site."""

    name = forms.CharField(label="Your name", max_length=80)
    email = forms.EmailField(label="Email address")
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"rows": 3}),
        min_length=10,
        help_text="At least ten characters.",
    )
