When an example cannot run
==========================

An example is a page of the site, and pages come and go. This page shows what
you see when one is slow, missing, closed to you, or broken. In every case the
source is still here to read.

A slow example
--------------

This one takes three seconds to answer. Its place is held while you wait.

.. live-example:: /examples/slow/
   :title: A slow page

   ../../examples/views.py 35-40

An example that is gone
-----------------------

The site no longer has a page at the address this one names.

.. live-example:: /examples/retired/
   :title: A page the site no longer has

   ../../templates/demo/examples/status.html 3-9

An example for staff only
-------------------------

Only staff accounts may open this one. Signed out, you are asked to sign in.
Signed in without a staff account, you are told you may not see it. Sign in as
``staff.user@example.com`` to see it run.

.. live-example:: /examples/staff/
   :title: A note for staff

   ../../examples/views.py 43-50
   ../../templates/demo/examples/staff_note.html

An example that fails
---------------------

This one raises an error every time. The rest of this page is unaffected.

.. live-example:: /examples/broken/
   :title: A page that fails

   ../../examples/views.py 53-59
