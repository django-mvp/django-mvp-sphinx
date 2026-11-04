"""A project chooses a documentation app's build for each request."""

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse

from mvp_sphinx.mounted import DocumentationApp

GUIDE_HOST = "guide.example.test"
SEARCH_HOST = "search.example.test"


@pytest.fixture
def chosen_app(guide_build, search_build, monkeypatch, settings):
    # The demo's docs app, serving the guide on one host and the search
    # fixture on any other, as a project serving one build per site would.
    from demo.mounted import docs

    settings.ALLOWED_HOSTS = [GUIDE_HOST, SEARCH_HOST, "testserver"]

    def build_for(request):
        return guide_build if request.get_host() == GUIDE_HOST else search_build

    monkeypatch.setattr(docs, "build_dir", build_for)
    return docs


def page(client, host, path="/docs/", **query):
    return client.get(path, query, HTTP_HOST=host)


class TestPagesFollowTheChosenBuild:
    def test_each_host_gets_its_own_front_page(self, client, db, chosen_app) -> None:
        assert "The guide front page" in page(client, GUIDE_HOST).content.decode()
        assert "The search fixture" in page(client, SEARCH_HOST).content.decode()

    def test_a_page_only_one_build_has_is_not_found_on_the_other(
        self, client, db, chosen_app
    ) -> None:
        assert page(client, SEARCH_HOST, "/docs/lanterns/").status_code == 200
        assert page(client, GUIDE_HOST, "/docs/lanterns/").status_code == 404

    def test_a_file_is_served_from_the_chosen_build_only(
        self, client, db, chosen_app, guide_build
    ) -> None:
        image = next((guide_build / "_images").iterdir()).name

        assert page(client, GUIDE_HOST, f"/docs/_images/{image}").status_code == 200
        assert page(client, SEARCH_HOST, f"/docs/_images/{image}").status_code == 404

    def test_a_chosen_build_that_does_not_exist_answers_not_found(
        self, client, db, chosen_app, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.setattr(chosen_app, "build_dir", lambda request: tmp_path / "none")

        assert page(client, GUIDE_HOST).status_code == 404


class TestTheSidebarFollowsTheChosenBuild:
    def test_the_sidebar_is_rebuilt_for_each_hosts_build_in_turn(
        self, rf, chosen_app
    ) -> None:
        def addresses(host):
            def leaves(items):
                found = []
                for item in items:
                    if item.is_parent:
                        found += leaves(item.visible_children)
                    else:
                        found.append(item.url)
                return found

            request = rf.get("/docs/", HTTP_HOST=host)
            return leaves(chosen_app.menu.process(request).visible_children)

        for _ in range(2):
            guide = addresses(GUIDE_HOST)
            search = addresses(SEARCH_HOST)

            assert "/docs/page/" in guide
            assert "/docs/lanterns/" not in guide
            assert "/docs/lanterns/" in search
            assert "/docs/page/" not in search


class TestSearchFollowsTheChosenBuild:
    def test_search_reads_the_chosen_build(self, client, db, chosen_app) -> None:
        path = reverse("docs:search")

        assert "Lanterns and lamps" in (
            page(client, SEARCH_HOST, path, q="quetzal").content.decode()
        )
        assert "Lanterns and lamps" not in (
            page(client, GUIDE_HOST, path, q="quetzal").content.decode()
        )


class TestPageExtractsFollowTheChosenBuild:
    def test_an_extract_is_read_from_the_requests_build(
        self, rf, db, chosen_app
    ) -> None:
        def request_for(host):
            request = rf.get("/", HTTP_HOST=host)
            request.user = AnonymousUser()
            return request

        assert chosen_app.page_extract("lanterns/", request_for(SEARCH_HOST))
        assert chosen_app.page_extract("lanterns/", request_for(GUIDE_HOST)) is None


class TestTheBuildCommand:
    @pytest.fixture
    def chosen_source(self, chosen_app, monkeypatch, tmp_path):
        monkeypatch.setattr(chosen_app, "source_dir", tmp_path)
        return chosen_app

    def test_naming_an_app_whose_build_is_chosen_per_request_is_an_error(
        self, chosen_source
    ) -> None:
        with pytest.raises(CommandError, match="each request"):
            call_command("build_docs", chosen_source.namespace, verbosity=0)

    def test_an_app_whose_build_is_chosen_per_request_is_left_out(
        self, chosen_source, monkeypatch
    ) -> None:
        from demo.mounted import staff_guide

        monkeypatch.setattr(staff_guide, "source_dir", None)

        with pytest.raises(CommandError, match="source_dir"):
            call_command("build_docs", verbosity=0)


class TestAFunctionIsAccepted:
    def test_an_app_takes_a_function_as_its_build_dir(self, tmp_path) -> None:
        DocumentationApp(build_dir=lambda request: tmp_path, namespace="chosen")
