# sphinx-design

sphinx-design's components take their colours from the daisyUI theme.

## Cards

::::{grid} 1 2 3 3
:gutter: 3

:::{grid-item-card} A card
:footer: A footer

Body text of the card.
:::

:::{grid-item-card} A linked card
:link: https://daisyui.com

The whole card is a link.
:::

:::{grid-item-card} {octicon}`zap` With an icon
:class-card: sd-border-primary

A card with a coloured border.
:::
::::

## Tabs

::::{tab-set}

:::{tab-item} Python
```python
html_theme = "daisyui"
```
:::

:::{tab-item} Logo options
```python
html_theme_options = {"logo": {"image_light": "logo.svg"}}
```
:::

:::{tab-item} Layout options
```python
html_theme_options = {"layout": "hHh LpR lff"}
```
:::
::::

## Dropdowns

:::{dropdown} A dropdown
Hidden until opened.
:::

:::{dropdown} An open dropdown with a colour
:open:
:color: primary
:icon: info

Open from the start.
:::

## Buttons and badges

```{button-link} https://daisyui.com
:color: primary
:shadow:

A primary button
```

```{button-link} https://daisyui.com
:color: secondary
:outline:

An outlined button
```

{bdg-primary}`primary` {bdg-secondary}`secondary` {bdg-success}`success` {bdg-info}`info`
{bdg-warning}`warning` {bdg-danger}`danger` {bdg-light}`light` {bdg-dark}`dark`
{bdg-primary-line}`primary line` {bdg-success-line}`success line`

## Icons

{octicon}`heart;1.5em;sd-text-danger` {octicon}`star;1.5em;sd-text-warning`
{octicon}`check-circle;1.5em;sd-text-success` {octicon}`info;1.5em;sd-text-info`

## An article info line

```{article-info}
:author: Sam Jennings
:date: November 2026
:read-time: 5 min read
```
