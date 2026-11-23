Typography
==========

The opening paragraph of a page introduces it, so it is drawn a little larger. Everything after it
is body text at a comfortable measure, with **strong text**, *emphasis*, ``inline code``,
:kbd:`Ctrl+Shift+P`, :guilabel:`Save as`, :menuselection:`File --> Export --> PDF`, a
`link to daisyUI <https://daisyui.com>`_, a reference to :doc:`admonitions`, a cross-reference to
:py:func:`textwrap.dedent`, an abbreviation :abbr:`WCAG (Web Content Accessibility Guidelines)`,
subscript H\ :sub:`2`\ O and superscript E = mc\ :sup:`2`.

A second paragraph shows how body text reads at length. Documentation is read in short bursts by
people who arrived from a search or a link, so the first sentence of each paragraph should carry
its point, and the rest should support it. Line length, line height and the space between
paragraphs matter more than the typeface.

Second-level heading
--------------------

Text under a second-level heading.

Third-level heading
~~~~~~~~~~~~~~~~~~~

Text under a third-level heading.

Fourth-level heading
^^^^^^^^^^^^^^^^^^^^

Text under a fourth-level heading.

Fifth-level heading
"""""""""""""""""""

Text under a fifth-level heading.

Quotes
------

    Simple things should be simple, complex things should be possible.

    -- Alan Kay

.. epigraph::

   An epigraph opens a section with somebody else's words.

   -- An attribution

.. pull-quote::

   A pull quote repeats a line from the text to draw the eye.

Line blocks
-----------

| These lines are
| broken exactly
| as they were written.

Rubrics and topics
------------------

.. rubric:: A rubric labels a short run of text.

.. topic:: A topic

   A topic is a self-contained block, set apart from the text around it.

.. sidebar:: A sidebar

   A sidebar floats beside the text that refers to it.

Text beside the sidebar. It wraps around it on a wide screen and sits under it on a narrow one.
Enough words are needed here to show the wrap, so this paragraph keeps going for a few more lines
to give the float something to sit beside.

Glossary
--------

.. glossary::

   Theme
      A named set of colours, radii and borders in daisyUI.

   Token
      A CSS variable a theme sets, such as ``--color-primary``.

The word :term:`Theme` links to its definition.

Version notes
-------------

.. versionadded:: 0.1
   Search as you type.

.. versionchanged:: 0.1
   The navbar holds the brand instead of the sidebar.

.. deprecated:: 0.1
   ``top_of_page_button``, singular. Use ``top_of_page_buttons``.

Footnotes and citations
-----------------------

A claim with a footnote [#f1]_ and another [#f2]_, and a citation [Bringhurst2004]_.

.. [#f1] The first footnote.
.. [#f2] The second footnote, which is longer so that it wraps onto a second line in the
   footnote list at the end of the page.

.. [Bringhurst2004] Robert Bringhurst, *The Elements of Typographic Style*, 2004.
