How long a page takes to read
=============================

Some pages of this guide are a minute's reading and one is a good deal longer. This
page shows the sums behind a reading-time estimate, for anyone deciding how to split
a long page.

The estimate
------------

A page of :math:`w` words, read at :math:`r` words a minute, takes
:math:`t = w / r` minutes. Most people read a guide like this one at about
:math:`r = 230`, so the page on :doc:`sharing-links`, at roughly 700 words, takes
:math:`700 / 230 \approx 3` minutes.

Code slows a reader down. Counting each line of code as :math:`c` words gives a
better estimate for a page with :math:`n` lines of it:

.. math::
   :label: reading-time

   t = \frac{w + c\,n}{r}

With :math:`c = 12`, the 9 lines of code on that page add about half a minute.

A whole guide
-------------

The time to read every page is the sum over the pages. For pages
:math:`1, \dots, N`, using :eq:`reading-time` for each:

.. math::
   :label: guide-time

   T = \sum_{i=1}^{N} \frac{w_i + c\,n_i}{r}
     = \frac{1}{r} \left( \sum_{i=1}^{N} w_i + c \sum_{i=1}^{N} n_i \right)

Equation :eq:`guide-time` is why the reading rate can be changed last: it is one
division at the end.

Pictures and tables
-------------------

A fuller estimate gives every kind of content its own weight. Written out in full
it is wider than most screens, and scrolls sideways inside its own area:

.. math::

   T = \frac{1}{r}\sum_{i=1}^{N} w_i + \frac{c}{r}\sum_{i=1}^{N} n_i + s_{\text{picture}}\sum_{i=1}^{N} p_i + s_{\text{table}}\sum_{i=1}^{N} b_i + s_{\text{admonition}}\sum_{i=1}^{N} a_i + s_{\text{heading}}\sum_{i=1}^{N} h_i + s_{\text{link}}\sum_{i=1}^{N} l_i

The weights can be kept together as a table of rates:

.. math::

   \begin{pmatrix} t_{\text{words}} \\ t_{\text{code}} \\ t_{\text{pictures}} \end{pmatrix}
   =
   \begin{pmatrix} 1/r & 0 & 0 \\ 0 & c/r & 0 \\ 0 & 0 & s \end{pmatrix}
   \begin{pmatrix} w \\ n \\ p \end{pmatrix}

.. note::

   Maths works inside a note too. A reader who skims covers the page in about
   :math:`t / 2`.

.. list-table:: Rates used on this page
   :header-rows: 1

   * - Symbol
     - Meaning
     - Value
   * - :math:`r`
     - Words read in a minute
     - :math:`230`
   * - :math:`c`
     - Words one line of code counts as
     - :math:`12`
   * - :math:`s`
     - Minutes spent on a picture
     - :math:`\tfrac{1}{5}`

When the sum goes wrong
-----------------------

A formula with a mistake in it does not stop the others on the page. This one has
an unknown command in it:

.. math::

   t = \frak{w}{r} + \notacommand{n}
