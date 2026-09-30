The demo accounts
=================

``seed_demo`` creates three accounts, and all three use the password ``password``.
Run it again at any time: it resets each account to this state.

.. list-table:: What each account can open
   :header-rows: 1

   * - Email
     - Password
     - Role
     - Staff guide in the sidebar
     - Opens the staff guide
     - Sees the guide you are reading
   * - ``regular.user@example.com``
     - ``password``
     - A :term:`regular account`, signed in but not staff
     - No
     - No: shown the forbidden page
     - Yes
   * - ``staff.user@example.com``
     - ``password``
     - A :term:`staff account`
     - Yes
     - Yes
     - Yes
   * - ``super.user@example.com``
     - ``password``
     - The :term:`superuser account`, which is also staff
     - Yes
     - Yes
     - Yes

Someone who has not signed in sees this guide and the overview page, and is asked
to sign in when they open the staff guide.

.. important::

   The accounts are for the demo only. Nothing on this page is a secret, so never
   reuse the password.

Comparing the accounts
----------------------

To see the difference yourself:

* Sign in as ``regular.user@example.com`` and look at the sidebar. It holds two
  entries, the overview and this guide:

  .. list-table::
     :header-rows: 1

     * - Account
       - Entries in the sidebar
       - What the staff entry would lead to, if it were there for this account
     * - Regular
       - Overview, this guide
       - The forbidden page, because the account is not staff
     * - Staff or superuser
       - Overview, this guide, staff guide
       - The staff guide's front page

* Sign out, sign in as ``staff.user@example.com``, and look again. The staff guide
  has joined the list.

For a script
------------

The same accounts as JSON, for a test that has to sign in:

.. code-block:: json

   [
     {"email": "regular.user@example.com", "password": "password", "staff": false},
     {"email": "staff.user@example.com", "password": "password", "staff": true},
     {"email": "super.user@example.com", "password": "password", "staff": true}
   ]

And as a file to take away: :download:`the accounts as a spreadsheet
</accounts.csv>`.

What the command prints
-----------------------

Running ``seed_demo`` prints one line per account, then a last line. The first run
says *created*, and later runs say *updated*:

.. code-block:: text

     created  regular.user@example.com
     created  staff.user@example.com
     created  super.user@example.com

   All three sign in with the password 'password'.
