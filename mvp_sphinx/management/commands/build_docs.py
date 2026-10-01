"""Management command that runs the Sphinx build for the project's documentation apps."""

import subprocess
import sys
from importlib.util import find_spec
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser
from mvp.mounted import MountedApp

from mvp_sphinx.mounted import DocumentationApp


class Command(BaseCommand):
    """Build the docs build of each mounted documentation app that names its source.

    The command runs ``sphinx-build -b json`` from an app's ``source_dir`` into
    its ``build_dir``, as a process of its own. Nothing here imports Sphinx, so
    the site that serves the pages still needs none.
    """

    help = (
        "Build the Sphinx documentation of the project's documentation apps: "
        "every app that has a source_dir, or only the ones named."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        """Take the namespaces of the apps to build."""
        parser.add_argument(
            "namespaces",
            nargs="*",
            metavar="namespace",
            help=(
                "The namespace of a documentation app to build. "
                "Leave out to build every app that has a source_dir."
            ),
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Build each chosen app in turn, stopping at the first build that fails."""
        apps = self.apps_to_build(options["namespaces"])
        if find_spec("sphinx") is None:
            raise CommandError(
                "Sphinx is not installed here. Install it where you build the "
                "docs: the site that serves them does not need it."
            )

        quiet = options["verbosity"] == 0
        for app in apps:
            if not quiet:
                self.stdout.write(f"Building {app.namespace} from {app.source_dir}")
                self.stdout.flush()
            # Sphinx runs as its own process, as it does from a shell, so this
            # one never imports it. Both paths are the project's own settings.
            status = subprocess.run(  # noqa: S603
                [
                    sys.executable,
                    "-m",
                    "sphinx",
                    "-b",
                    "json",
                    *(["-q"] if quiet else []),
                    str(app.source_dir),
                    str(app.build_dir),
                ],
                check=False,
            ).returncode
            if status != 0:
                raise CommandError(
                    f'Sphinx could not build "{app.namespace}" from {app.source_dir}.'
                )
        if not quiet:
            self.stdout.write(self.style.SUCCESS(f"Built {len(apps)} docs build(s)."))

    def apps_to_build(self, namespaces: list[str]) -> list[DocumentationApp]:
        """Return the documentation apps to build, in the order they are mounted.

        Args:
            namespaces: The namespaces asked for, or an empty list for every
                mounted app that has a ``source_dir``.

        Returns:
            The chosen apps, each with a ``source_dir``.

        Raises:
            CommandError: A namespace belongs to no mounted documentation app,
                a named app has no ``source_dir``, or no mounted app has one.
        """
        mounted = {
            mount.app.namespace: mount.app
            for mount in MountedApp.mounts()
            if isinstance(mount.app, DocumentationApp)
        }
        unknown = [name for name in namespaces if name not in mounted]
        if unknown:
            raise CommandError(
                f"No documentation app is mounted with the namespace "
                f"{', '.join(unknown)}. Mounted: {', '.join(mounted) or 'none'}."
            )
        if namespaces:
            apps = [mounted[name] for name in mounted if name in namespaces]
            without = [app.namespace for app in apps if app.source_dir is None]
            if without:
                raise CommandError(
                    f"{', '.join(without)} has no source_dir. Pass the Sphinx "
                    "source directory to its DocumentationApp as source_dir."
                )
            return apps
        apps = [app for app in mounted.values() if app.source_dir is not None]
        if not apps:
            raise CommandError(
                "No mounted documentation app has a source_dir. Pass the Sphinx "
                "source directory to a DocumentationApp as source_dir."
            )
        return apps
