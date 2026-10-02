A working form
==============

Some things are easier to try than to read about. This page shows two pages of
the site running right here, each beside the code that makes it.

The contact form
----------------

Fill the form in and send it. Leave a field empty first, or write a very short
message, to see what the site says. Nothing you send goes anywhere.

.. live-example:: /examples/contact/
   :title: The contact form

   ../../examples/forms.py
   ../../examples/views.py 12-25
   ../../templates/demo/examples/contact.html

"Start again" puts the form back to how it was when you opened this page.
"Open on its own" takes you to the form as an ordinary page of the site.

An order's status
-----------------

An example doesn't need a form. This one is a page that only shows something,
and its source is the part of one template that draws it.

.. live-example:: /examples/status/
   :title: An order's status

   ../../templates/demo/examples/status.html 3-9

Using one example never changes the other.
