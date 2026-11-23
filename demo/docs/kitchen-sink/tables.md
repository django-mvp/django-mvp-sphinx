# Tables

A table sits in a bordered box that scrolls sideways when it is wider than the page.

| Theme | Mode | Primary | Rounded |
|---|---|---|---|
| light | Light | Indigo | Yes |
| dark | Dark | Indigo | Yes |
| corporate | Light | Blue | Slightly |
| business | Dark | Blue | Slightly |
| retro | Light | Red | Yes |

```{list-table} A list table with a stub column
:header-rows: 1
:stub-columns: 1

* - Option
  - Navbar
  - Sidebar
  - Footer
* - Logo for each mode
  - `logo.image_light`, `logo.image_dark`
  - `logo.image_light`
  - No
* - Edit link
  - `use_edit_page_button`
  - `secondary_sidebar_items`
  - No
* - Version switcher
  - `switcher`
  - No
  - Yes
```

## A wide table

| Name | Type | Default | Since | Description | Example |
|---|---|---|---|---|---|
| `light_theme` | `str` | `"light"` | 0.1 | The daisyUI theme for light mode, by name | `"corporate"` |
| `dark_theme` | `str` | `"dark"` | 0.1 | The daisyUI theme for dark mode, by name | `"business"` |
| `theme_picker` | `bool` or `list` | `False` | 0.1 | Offers themes to the reader in the navbar menu | `["nord", "dracula"]` |
| `navigation_depth` | `int` | `4` | 0.1 | How many levels of pages the sidebar holds | `3` |

## A grid table

```{eval-rst}
+------------+------------+-----------+
| Header 1   | Header 2   | Header 3  |
+============+============+===========+
| body row 1 | column 2   | column 3  |
+------------+------------+-----------+
| body row 2 | Cells may span columns.|
+------------+------------+-----------+
```
