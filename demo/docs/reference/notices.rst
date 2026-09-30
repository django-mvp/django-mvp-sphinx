How this guide marks notices
============================

The guide sets a few kinds of notice apart from the text around them. This page
shows each one once, so you can tell what a notice means by how it looks.

Notices
-------

Ordinary advice and warnings come in pairs that look alike.

.. note::

   A note holds something worth knowing.

.. tip::

   A tip holds a shortcut or a better way.

.. hint::

   A hint looks like a tip, and means the same.

.. important::

   An important notice asks you to read it before going on.

.. warning::

   A warning says something can go wrong.

.. caution::

   A caution looks like a warning, and means the same.

.. attention::

   An attention notice looks like a warning too.

.. danger::

   A danger is the strongest: it says something cannot be undone.

.. error::

   An error looks like a danger.

Some notices carry a title of their own, and look like a note:

.. admonition:: A title of the guide's choosing

   A titled notice names no kind, so it reads as information.

A notice can hold another, and each keeps its own meaning:

.. warning::

   The outer warning.

   .. tip::

      A tip inside it.

.. seealso::

   :doc:`/first-visit/signing-in`, where the accounts are introduced.

Version notes
-------------

When something changed on the site, a note says in which version. These three are
examples.

.. versionadded:: 0.1

   A way to do something was added.

.. versionchanged:: 0.2

   How it is done changed.

.. deprecated:: 0.3

   Do it the other way instead.

Pictures
--------

A picture that is wider than the text scales down to fit, keeping its shape:

.. image:: /shell.png
   :width: 2400px
   :alt: A striped picture standing in for a screenshot

A figure keeps its caption with its picture:

.. figure:: /shell.png
   :width: 2400px
   :alt: A striped picture standing in for a screenshot

   The caption stays under the picture it describes.
