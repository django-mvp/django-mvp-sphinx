Sharing and copying links
=========================

Every page of this guide has an address of its own, and so does every heading on
it. That makes the guide easy to point someone at: copy the address from the
browser and send it. This page explains what the addresses look like, how to reach
a heading directly, and how to check them from a script.

What an address looks like
--------------------------

The guide lives under ``/docs/``. The front page is ``/docs/``, and every other
page adds its place in the sidebar to that: the page called *Signing in*, which sits
inside *Your first visit*, is at ``/docs/first-visit/signing-in/``.

Addresses end in a slash. An address typed without the slash is sent on to the
one with it, so both work, and the one the browser shows afterwards is the one to
copy.

Addresses do not change when the guide is edited and rebuilt, unless a page is
moved or renamed. A link to a page that no longer exists leads to the site's
not-found page, the same as any other address under ``/docs/`` with nothing behind
it.

Pictures and files the guide links to, such as the picture on
:doc:`notices` and the accounts file on :doc:`accounts`, have addresses under
``/docs/`` as well. They are served by the same guide, so a link to one works for
anyone who can open the guide.

Linking to a heading
--------------------

Hover over any heading to reveal the link beside it, or tab to it with the
keyboard. Following that link adds the heading's name to the address, after a ``#``,
and puts the heading at the top of the page, clear of the top bar. Copy the address
after following it, and whoever opens it lands on the same section.

The panel called *On this page* does the same thing from the side: every entry in
it is a link to a heading, and the entries of sub-headings sit under their parent.

Copying from the browser
~~~~~~~~~~~~~~~~~~~~~~~~

Copy the address from the address bar once the page has scrolled to the heading.
Most browsers also offer *Copy link address* when you right-click a link, which is
the quickest way to take the address of a heading from the *On this page* panel
without scrolling to it first.

On a phone the address bar may hide part of the address. Choose the share button
of the browser instead, which sends the whole of it.

Copying from a script
~~~~~~~~~~~~~~~~~~~~~

A script that needs a page can ask for it like any other address. The simplest way
is ``curl``, and because the guide answers with ordinary pages, its output is a page
of the site:

.. code-block:: console

   $ curl --silent --include --location http://127.0.0.1:8000/docs/first-visit/signing-in/

The same thing from Python, checking only that the page is there:

.. code-block:: python
   :caption: check_page.py
   :linenos:
   :emphasize-lines: 4, 5

   from urllib.request import urlopen

   address = "http://127.0.0.1:8000/docs/first-visit/signing-in/"
   with urlopen(address) as response:
       print(response.status)

.. code-block:: console

   $ python check_page.py
   200

Long addresses
~~~~~~~~~~~~~~

Some addresses are long, and a line of code that holds one runs past the edge of
the page. It scrolls sideways inside its own box instead of pushing the page
sideways:

.. code-block:: console

   $ curl --silent --location --header "Accept: text/html" --output /tmp/page.html --write-out "%{http_code}\n" http://127.0.0.1:8000/docs/first-visit/finding-your-way/

When a heading moves
--------------------

A heading keeps the same name in the address for as long as its words do not
change. Reword a heading and its old address still loads the page, but the browser
stays at the top of it, because the section it named is called something else now.

That is the one time a shared link to a heading goes stale. A link to the page
itself, without the ``#``, keeps working.

Checking that a link works
--------------------------

The quickest check of a link is to open it in a private window, where nothing you
have signed in to follows you. A link to a page of this guide opens the same whether
or not you are signed in.

A link to the staff guide is different. It opens the staff guide for staff, asks
everyone else who has not signed in to sign in, and shows the forbidden page to a
regular account. See :doc:`/staff-guide` for who can open it.

Sending the link
~~~~~~~~~~~~~~~~

When you send a link to a page of this guide, nothing else needs to go with it. The
page brings its own sidebar, so whoever opens it can move on to the pages around it.
If you are sending a link to the staff guide instead, say so, so that the person
opening it knows to sign in as staff first.

A link that sends more than one place
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want someone to read two pages in order, send the address of the first. Its
*Next* link at the foot of the page leads to the second, when the second follows the
first in the sidebar. When it does not, send both addresses, each with a word about
why.
