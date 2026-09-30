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

Wide content
------------

Content wider than the page scrolls or scales inside it, and never pushes the
page sideways. Try this page at the width of a phone.

A table wider than a phone screen scrolls sideways inside its own area, which
takes keyboard focus:

.. list-table:: Supported environments
   :header-rows: 1

   * - Python
     - Django
     - Operating system
     - Database
     - Web server
     - Cache
     - Task queue
     - Status
   * - 3.12
     - 5.2
     - Ubuntu 24.04 with the distribution's own packages installed
     - PostgreSQL 16 with the PostGIS extension enabled
     - gunicorn behind nginx
     - Redis 7
     - Celery with a Redis broker
     - Supported
   * - 3.13
     - 6.0
     - Debian 13 with the distribution's own packages installed
     - PostgreSQL 17 with the PostGIS extension enabled
     - uvicorn behind Caddy
     - Valkey 8
     - Celery with an AMQP broker
     - Supported

A table inside a list item:

* The first step, with its own table:

  .. list-table::
     :header-rows: 1

     * - Setting
       - Value
       - What it does when it is set to something long enough to need room
     * - ``DEBUG``
       - ``False``
       - Keeps error details from readers of the site in production and sends them to the log

* The second step needs no table.

A code line longer than the reading area scrolls inside its own box:

.. code-block:: console

   $ python manage.py collectstatic --noinput --clear --link --ignore "*.map" --ignore "*.scss" --ignore "node_modules" --verbosity 2

An image wider than the reading area scales down to fit, keeping its ratio:

.. image:: shell.png
   :width: 2400px
   :alt: A terminal prompt

A figure keeps its caption with the image:

.. figure:: shell.png
   :width: 2400px
   :alt: A terminal prompt

   The caption stays inside the figure, under the image.


Glossaries and interface references
-----------------------------------

A glossary sets each term apart from its definition:

.. glossary::

   documentation app
      The part of a project that serves a Sphinx build as pages of the site.

   docs build
      The JSON output of ``sphinx-build -b json``, which the documentation app
      reads on every request.

   front page
      The page a guide opens on. It links to every other page of the guide.

A term is referenced from running text like this: the :term:`documentation app`
reads the :term:`docs build`, and readers arrive at the :term:`front page`. A
page is referenced the same way, as in :doc:`getting-started`.

Keys, labels and menu paths sit inside a line of text. Press
:kbd:`Ctrl+K` to search, choose :guilabel:`Save changes` to keep an edit, or
open :menuselection:`Settings --> Appearance --> Theme` to change the theme.


Headings
--------

Hover over a heading to reveal the link beside it, or tab to it with the keyboard. Following the link puts the section at the top of the page, clear of the top bar.

Each section below is long enough that the page has to scroll to reach the next, so following one of its links shows the heading landing below the top bar instead of behind it.

Choosing a name
~~~~~~~~~~~~~~~

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Using ``BodyRewriter`` in your own views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Sharing a link
~~~~~~~~~~~~~~

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Checking the result
~~~~~~~~~~~~~~~~~~~

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.

Reading a page is easier when a reader can copy the address of the part they mean. Every heading on this page carries a link to itself, and a reader who wants to share the section sends that address instead of describing where to scroll. The paragraph runs long on purpose so the sections take room.
