API
===

.. py:module:: demo.links

Functions
---------

.. py:function:: page_address(path: str, heading: str | None = None, *, strict: bool = False) -> str

   Return the address of a page. See also :py:func:`check_address`.

   :param path: The page's place in the sidebar.
   :param heading: A heading on the page.
   :param strict: Whether an empty path is an error.
   :returns: The address, ending in a slash.
   :raises ValueError: The path is empty.

.. py:function:: check_address(address: str) -> bool

   Say whether an address belongs to the guide.

.. py:function:: lonely_address()

Classes
-------

.. py:class:: Link(address: str, note: str = '')

   A link to a page.

   .. py:method:: render(style: str = 'plain') -> str

      Return the link as text.

   .. py:attribute:: address
      :type: str

      The address the link opens.

   .. py:property:: is_empty
      :type: bool

      Whether the link holds no address.

   .. py:class:: Reader

      Who a link is sent to.

      .. py:method:: can_open(address: str) -> bool

         Say whether this reader can open an address.

.. py:class:: Shortcut

   Another link.

   .. py:method:: render(style: str = 'plain') -> str

      Return the shortcut as text.

Errors and data
---------------

.. py:exception:: NotAGuideAddress

   Raised when an address is outside the guide.

.. py:data:: GUIDE_PREFIX
   :type: str
   :value: '/docs/'

   The prefix every address starts with.

Older helpers
-------------

.. py:function:: old_address(page: str) -> str

   Return an address in the older form.

   .. deprecated:: 0.4
      Use :py:func:`page_address`.

Other languages
---------------

.. js:function:: buildAddress(path, heading)

   Build the address of a page.

   :param path: The page's place in the sidebar.
   :param heading: A heading on the page.
