"""The demo project's documentation app, serving the guide in demo/docs/."""

from demo.settings import BASE_DIR
from mvp_sphinx.mounted import DocumentationApp

docs = DocumentationApp(build_dir=BASE_DIR / "demo" / "docs" / "_build" / "json")
