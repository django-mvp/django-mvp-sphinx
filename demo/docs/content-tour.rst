Content tour
============

A page of every construct the guide's styling covers, for looking at the pages
under the light and dark themes. Ordinary text reads as it does elsewhere on
the site: **bold**, *emphasis*, a `link <https://www.djangoproject.com>`_ and
``inline code``, then a list:

* the first item
* the second item

Admonitions
-----------

Each admonition is told apart by what it means.

.. note::

   Notes are informational.

.. tip::

   Tips are helpful.

.. hint::

   Hints look like tips.

.. important::

   Important notices ask for attention.

.. warning::

   Warnings are cautionary.

.. caution::

   Cautions look like warnings.

.. attention::

   So do attention notices.

.. danger::

   Dangers are the strongest.

.. error::

   Errors look like dangers.

A generic admonition, with a title of its own, is informational:

.. admonition:: A title of the author's choosing

   A generic admonition names no kind, so it takes the informational look.

Admonitions nest, and each keeps its own meaning:

.. warning::

   The outer warning.

   .. tip::

      A tip inside it.

.. seealso::

   :doc:`getting-started`, for the same construct in another page.

Version notes
-------------

.. versionadded:: 1.2

   A way to do it was added.

.. versionchanged:: 1.3

   How it is done changed.

.. deprecated:: 2.0

   Do it the other way instead.

Code
----

Code is highlighted in the site's colours, in each theme.

.. code-block:: python

   from dataclasses import dataclass


   @dataclass
   class Page:
       """A page of the guide."""

       title: str
       number: int = 1

       def heading(self) -> str:
           # Build the heading text.
           return f"{self.number}. {self.title}"

.. code-block:: console

   $ python manage.py collectstatic --noinput
   $ python manage.py runserver

.. code-block:: json

   {"title": "Content tour", "pages": [1, 2, 3], "draft": false, "owner": null}

A block with a caption, line numbers and emphasised lines:

.. code-block:: python
   :caption: settings.py
   :linenos:
   :emphasize-lines: 2, 4

   INSTALLED_APPS = [
       "django.contrib.staticfiles",
       "mvp",
       "mvp_sphinx",
   ]

Code in a language Pygments cannot highlight is plain text in the same box:

.. code-block:: text

   Nothing here is highlighted.
   It reads as ordinary code text.
