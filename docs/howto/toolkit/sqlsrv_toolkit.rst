.. _sqlsrv_toolkit:

SQL Server Toolkit
==================

The SQL Server Toolkit provides functions to help using pysdmx with SQL Server.

Creating a SQL Server table based on SDMX Structures
----------------------------------------------------

The :meth:`pysdmx.toolkit.sqlsrv.create_table` function returns a SQL CREATE TABLE
statement out of structural metadata. 

.. code-block:: python

    from pysdmx.api.fmr import RegistryClient
    from pysdmx.toolkit.sqlsrv import create_table

    client = RegistryClient("https://registry.sdmx.org/sdmx/v2")
    dfi = client.get_dataflow_details("SDMX", "NAMAIN_IDC_N", "1.0")
    cs = create_table(dfi)

    print(cs)

    # Outputs
    # CREATE TABLE dbo.NAMAIN_IDC_N (
    #    FREQ CHAR(1) NOT NULL, -- Frequency
    #    ADJUSTMENT NVARCHAR(2) NOT NULL, -- Adjustment indicator
    #    REF_AREA NVARCHAR(5) NOT NULL, -- Reference area
    #    COUNTERPART_AREA NVARCHAR(5) NOT NULL, -- Counterpart area
    #    REF_SECTOR NVARCHAR(7) NOT NULL, -- Reporting institutional sector
    #    COUNTERPART_SECTOR NVARCHAR(7) NOT NULL, -- Counterpart institutional sector
    #    ACCOUNTING_ENTRY NVARCHAR(2) NOT NULL, -- Accounting Entry
    #    STO NVARCHAR(9) NOT NULL, -- Stocks, Transactions, Other Flows
    #    INSTR_ASSET NVARCHAR(7) NOT NULL, -- Instrument and Assets Classification
    #    ACTIVITY NVARCHAR(9) NOT NULL, -- Activity classification
    #    EXPENDITURE NVARCHAR(12) NOT NULL, -- Expenditure (COFOG, COICOP, COPP or COPNI)
    #    UNIT_MEASURE NVARCHAR(15) NOT NULL, -- Unit
    #    PRICES NVARCHAR(2) NOT NULL, -- Prices
    #    TRANSFORMATION NVARCHAR(5) NOT NULL, -- Transformation
    #    TIME_PERIOD NVARCHAR(50) NOT NULL, -- Time period
    #    OBS_VALUE FLOAT NULL, -- Observation value
    #    COMMENT_OBS NVARCHAR(4000) NULL, -- Comments to the observation value
    #    CONF_STATUS CHAR(1) NOT NULL, -- Confidentiality status
    #    EMBARGO_DATE DATETIME2 NULL, -- Embargo date
    #    OBS_STATUS CHAR(1) NOT NULL, -- Observation status
    #    PRE_BREAK_VALUE FLOAT NULL, -- Pre-break value
    #    COMMENT_TS NVARCHAR(1050) NULL, -- Series comment
    #    COMPILING_ORG NVARCHAR(4) NULL, -- Compiling organisation
    #    CURRENCY NVARCHAR(15) NULL, -- Currency code used for compilation
    #    DATA_COMP NVARCHAR(4000) NULL, -- Underlying compilation
    #    DECIMALS NVARCHAR(2) NOT NULL, -- Decimals
    #    DISS_ORG NVARCHAR(MAX) NULL, -- Dissemination organisation
    #    LAST_UPDATE DATETIME2 NULL, -- Last Update Date
    #    REF_PERIOD_DETAIL NVARCHAR(3) NULL, -- Reference period detail
    #    REF_YEAR_PRICE INT NULL, -- Reference year (price)
    #    TABLE_IDENTIFIER NVARCHAR(12) NULL, -- Table identifier
    #    REF_PERIOD_DETAIL NVARCHAR(3) NULL, -- Reference period detail
    #    REF_YEAR_PRICE INT NULL, -- Reference year (price)
    #    TABLE_IDENTIFIER NVARCHAR(12) NULL, -- Table identifier
    #    TIME_FORMAT NVARCHAR(4) NOT NULL, -- Time format
    #    TIME_PER_COLLECT CHAR(1) NULL, -- Time period collection
    #    TITLE NVARCHAR(200) NULL, -- Title
    #    UNIT_MULT NVARCHAR(2) NOT NULL, -- Unit multiplier
    #    CONSTRAINT PK_dbo_NAMAIN_IDC_N PRIMARY KEY (FREQ,ADJUSTMENT,REF_AREA,COUNTERPART_AREA,REF_SECTOR,COUNTERPART_SECTOR,ACCOUNTING_ENTRY,STO,INSTR_ASSET,ACTIVITY,EXPENDITURE,UNIT_MEASURE,PRICES,TRANSFORMATION,TIME_PERIOD)
    # );
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_FREQ ON dbo.NAMAIN_IDC_N (FREQ);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_ADJUSTMENT ON dbo.NAMAIN_IDC_N (ADJUSTMENT);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_REF_AREA ON dbo.NAMAIN_IDC_N (REF_AREA);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_COUNTERPART_AREA ON dbo.NAMAIN_IDC_N (COUNTERPART_AREA);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_REF_SECTOR ON dbo.NAMAIN_IDC_N (REF_SECTOR);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_COUNTERPART_SECTOR ON dbo.NAMAIN_IDC_N (COUNTERPART_SECTOR);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_ACCOUNTING_ENTRY ON dbo.NAMAIN_IDC_N (ACCOUNTING_ENTRY);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_STO ON dbo.NAMAIN_IDC_N (STO);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_INSTR_ASSET ON dbo.NAMAIN_IDC_N (INSTR_ASSET);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_ACTIVITY ON dbo.NAMAIN_IDC_N (ACTIVITY);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_EXPENDITURE ON dbo.NAMAIN_IDC_N (EXPENDITURE);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_UNIT_MEASURE ON dbo.NAMAIN_IDC_N (UNIT_MEASURE);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_PRICES ON dbo.NAMAIN_IDC_N (PRICES);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_TRANSFORMATION ON dbo.NAMAIN_IDC_N (TRANSFORMATION);
    # CREATE INDEX IDX_dbo_NAMAIN_IDC_N_TIME_PERIOD ON dbo.NAMAIN_IDC_N (TIME_PERIOD);

By default:

* The name of the table is the structure ID.
* The table is created in the `dbo` schema.
* The primary key is a composite key based on the dimensions.
* Indexes are created for every dimension.

However, additional parameters are available to tweak this behavior. Also, should
additional columns be required beyond the components already defined in the structure,
they can be passed using the `extra_columns` parameters.

Creating prepared statements from pysdmx queries
------------------------------------------------

If you use :ref:`pysdmx query model <dc_query_model>`, you can use the
:meth:`pysdmx.toolkit.sqlsrv.get_select_statement` function returns a SQL SELECT
prepared statement for your query. 

.. code-block:: python
    
    from pysdmx.api.dc.query import Operator, SortBy, TextFilter
    from pysdmx.toolkit.sqlsrv import get_select_statement

    schema_name = "SDMX"
    table_name = "BOP"
    cols = ["SKEY", "TIME_PERIOD", "OBS_VALUE", "OBS_STATUS"]
    flt = TextFilter("PRV", Operator.EQUALS, "UY2")
    offset = 0
    limit = 42
    srt = SortBy("TIME_PERIOD", "desc")

    select, values = get_select_statement(
        table_name, schema_name, flt, cols, [srt], offset, limit
    )

    print(select)
    print(values)

    # PRINT1: SELECT "SKEY", "TIME_PERIOD", "OBS_VALUE", "OBS_STATUS" FROM SDMX.BOP WHERE "PRV" = ? ORDER BY "TIME_PERIOD" DESC OFFSET 0 ROWS FETCH NEXT 42 ROWS ONLY
    # PRINT2: ['UY2']

