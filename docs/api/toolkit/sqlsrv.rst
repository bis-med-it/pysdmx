.. _sql-toolkit-api:

SQL Server Toolkit
==================

The SQL Server Toolkit provides functions to help using pysdmx with SQL Server.

Create a SQL table out of structural metadata
---------------------------------------------

.. autofunction:: pysdmx.toolkit.sqlsrv.create_table

Create prepared statements from pysdmx queries
----------------------------------------------

.. autofunction:: pysdmx.toolkit.sqlsrv.get_select_statement

Lower-level functions
---------------------

There are also lower-level functions available, if necessary, but they are
typically abstracted via the `get_select_statement` function described above.

.. autofunction:: pysdmx.toolkit.sqlsrv.get_select_columns
.. autofunction:: pysdmx.toolkit.sqlsrv.get_sort_clause
.. autofunction:: pysdmx.toolkit.sqlsrv.get_pagination_clause
.. autofunction:: pysdmx.toolkit.sqlsrv.get_where_clause
.. autofunction:: pysdmx.toolkit.sqlsrv.get_sql_data_type
    