# Code

Code blocks sit on daisyUI's neutral colour, as its mockup-code component does, and their
highlighting is drawn from the theme's tokens. Hover a block to copy it.

```python
from dataclasses import dataclass


@dataclass
class Theme:
    """A daisyUI theme, by name."""

    name: str
    dark: bool = False

    def css_selector(self) -> str:
        # Every theme is a data attribute on the root element.
        return f'[data-theme="{self.name}"]'


themes = [Theme("light"), Theme("dark", dark=True)]
print({t.name: t.css_selector() for t in themes if not t.dark})
```

## With a caption, line numbers and emphasised lines

```{code-block} javascript
:caption: theme.js
:linenos:
:emphasize-lines: 3,4

const root = document.documentElement;
const mode = localStorage.getItem("daisy-mode") || "auto";
const dark = mode === "dark" ||
  (mode === "auto" && matchMedia("(prefers-color-scheme: dark)").matches);
root.dataset.theme = dark ? "dark" : "light";
```

## A console session

```console
$ pip install sphinx-daisyui
Successfully installed sphinx-daisyui-0.1.0
$ sphinx-build -b html docs docs/_build/html
build succeeded.
```

## Other languages

```css
@plugin "daisyui" {
  themes: light --default, dark --prefersdark;
}
```

```toml
[project]
name = "my-docs"
dependencies = ["sphinx-daisyui"]
```

```diff
- html_theme_options = {}
+ html_theme_options = {"navigation_with_keys": True}
```

```html
<button class="btn btn-primary">daisyUI button</button>
```

## A very long line

```python
result = some_function_with_a_long_name(
    first_argument="a value",
    second_argument="another value",
    third_argument=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
)
```

## A literal include

```{literalinclude} conf-snippet.py
:language: python
```
