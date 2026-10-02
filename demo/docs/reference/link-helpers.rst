Link helpers
============

.. module:: demo.links

The demo ships a small Python module, ``demo.links``, for building the addresses
this guide describes on :doc:`sharing-links`. This page lists everything in it. It
is written for whoever looks after the site, and you do not need any of it to read
the guide.

.. autosummary::

   page_address
   check_address
   SharedLink
   NotAGuideAddress

Building an address
-------------------

.. autofunction:: page_address

.. autodata:: GUIDE_PREFIX

Checking an address
-------------------

.. autofunction:: check_address

.. autoexception:: NotAGuideAddress

.. autofunction:: strip_heading

Links to send
-------------

.. autoclass:: SharedLink
   :members:
   :member-order: bysource

Older helpers
-------------

.. autofunction:: old_address
