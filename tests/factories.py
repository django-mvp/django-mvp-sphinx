"""Factories for the models the suite creates."""

import factory
from django.contrib.auth.models import Group, User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"reader{n}")
    password = factory.PostGenerationMethodCall("set_password", "password")


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: f"Group {n}")
