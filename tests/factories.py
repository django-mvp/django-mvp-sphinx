"""Factories for the models the suite creates."""

import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"reader{n}")
    password = factory.django.Password("password")


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: f"Group {n}")
