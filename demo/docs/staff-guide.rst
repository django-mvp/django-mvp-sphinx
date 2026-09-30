About the staff guide
=====================

The staff guide is a second, smaller guide that lives next to this one, at
``/staff-guide/``. It is for people with a staff account, and it covers what the
staff accounts are and what sets them apart.

Who can open it
---------------

Only staff accounts can. What happens to everyone else depends on who they are:

* Someone who has not signed in is asked to sign in.
* Someone signed in with a :term:`regular account` is shown the site's forbidden
  page.
* Someone signed in with a :term:`staff account` or the :term:`superuser account`
  reads it.

The sidebar follows the same rule. The staff guide's entry appears only while
you are signed in as staff, so a regular account never sees a link it cannot use.

.. warning::

   Not seeing the entry is not a fault. If you expect to see it, check which
   account you signed in with: :doc:`reference/accounts` lists what each one can
   open.

Trying it
---------

#. Sign in with ``staff.user@example.com`` and the password ``password``. See
   :doc:`first-visit/signing-in` if you need the steps.
#. Choose *Staff guide* in the sidebar, or open the
   `staff guide </staff-guide/>`_ directly.
#. Sign out and sign in as ``regular.user@example.com``, then open the address
   again to see the forbidden page.

.. caution::

   The demo's accounts share one password, and anyone who can reach the site can
   sign in as staff. Run it only where you would trust everyone who can open it.

.. versionadded:: 0.1

   The staff guide's entry in the sidebar, shown to staff accounts only.
