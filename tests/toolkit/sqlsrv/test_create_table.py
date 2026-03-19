import pytest

from pysdmx.model import (
    Component,
    Components,
    Concept,
    DataflowInfo,
    DataType,
    Facets,
    Role,
)
from pysdmx.toolkit.sqlsrv import Column, create_table


@pytest.fixture
def dsi():
    f1 = Component(
        "FREQ",
        True,
        Role.DIMENSION,
        Concept("FREQ", dtype=DataType.STRING),
        DataType.ALPHA,
        Facets(min_length=1, max_length=1),
        "Frequency",
    )
    f2 = Component(
        "INDICATOR",
        True,
        Role.DIMENSION,
        Concept("IND"),
        DataType.STRING,
        Facets(min_length=6, max_length=6),
    )
    f3 = Component(
        "PERIOD", True, Role.DIMENSION, Concept("PERIOD"), DataType.PERIOD
    )
    f4 = Component(
        "VALUE", False, Role.MEASURE, Concept("VALUE"), DataType.INTEGER
    )
    f5 = Component(
        "CONF",
        True,
        Role.ATTRIBUTE,
        Concept("CONF"),
        DataType.STRING,
        Facets(min_length=1, max_length=1),
        attachment_level="O",
    )
    return DataflowInfo("TEST", Components([f1, f2, f3, f4, f5]), "SDMX")


def test_default_schema_name(dsi):
    sta = create_table(dsi)

    assert sta.startswith("CREATE TABLE dbo.")


def test_specific_schema_name(dsi):
    sn = dsi.agency

    sta = create_table(dsi, sn)

    assert sta.startswith(f"CREATE TABLE {dsi.agency}.")


def test_default_table_name(dsi):
    sta = create_table(dsi)

    assert sta.startswith(f"CREATE TABLE dbo.{dsi.id}")


def test_specific_table_name(dsi):
    tn = "TEST42"

    sta = create_table(dsi, table_name=tn)

    assert sta.startswith(f"CREATE TABLE dbo.{tn}")


def test_full_statement_default_idx(dsi):
    expected = "CREATE TABLE dbo.TEST (\n"
    expected += "    FREQ CHAR(1) NOT NULL, -- Frequency\n"
    expected += "    INDICATOR CHAR(6) NOT NULL,\n"
    expected += "    PERIOD VARCHAR(50) NOT NULL,\n"
    expected += "    VALUE INT NULL,\n"
    expected += "    CONF CHAR(1) NOT NULL,\n"
    expected += (
        "    CONSTRAINT PK_dbo_TEST PRIMARY KEY (FREQ,INDICATOR,PERIOD)\n"
    )
    expected += ");\n"
    expected += "CREATE INDEX IDX_dbo_TEST_FREQ ON dbo.TEST (FREQ);\n"
    expected += (
        "CREATE INDEX IDX_dbo_TEST_INDICATOR ON dbo.TEST (INDICATOR);\n"
    )
    expected += "CREATE INDEX IDX_dbo_TEST_PERIOD ON dbo.TEST (PERIOD);\n"

    sta = create_table(dsi)

    assert sta == expected


def test_full_statement_specific_idx(dsi):
    expected = "CREATE TABLE dbo.TEST (\n"
    expected += "    FREQ CHAR(1) NOT NULL, -- Frequency\n"
    expected += "    INDICATOR CHAR(6) NOT NULL,\n"
    expected += "    PERIOD VARCHAR(50) NOT NULL,\n"
    expected += "    VALUE INT NULL,\n"
    expected += "    CONF CHAR(1) NOT NULL,\n"
    expected += (
        "    CONSTRAINT PK_dbo_TEST PRIMARY KEY (FREQ,INDICATOR,PERIOD)\n"
    )
    expected += ");\n"
    expected += (
        "CREATE INDEX IDX_dbo_TEST_INDICATOR ON dbo.TEST (INDICATOR);\n"
    )
    expected += "CREATE INDEX IDX_dbo_TEST_PERIOD ON dbo.TEST (PERIOD);\n"

    sta = create_table(dsi, index_fields=["INDICATOR", "PERIOD"])

    assert sta == expected


def test_extra_columns(dsi):
    expected = "CREATE TABLE dbo.TEST (\n"
    expected += "    FREQ CHAR(1) NOT NULL, -- Frequency\n"
    expected += "    INDICATOR CHAR(6) NOT NULL,\n"
    expected += "    PERIOD VARCHAR(50) NOT NULL,\n"
    expected += "    VALUE INT NULL,\n"
    expected += "    CONF CHAR(1) NOT NULL,\n"
    expected += "    PRV CHAR(3) NOT NULL, -- Provider\n"
    expected += "    LAST_UPD DATETIME2 NOT NULL,\n"
    expected += (
        "    CONSTRAINT PK_dbo_TEST PRIMARY KEY (FREQ,INDICATOR,PERIOD,PRV)\n"
    )
    expected += ");\n"
    expected += "CREATE INDEX IDX_dbo_TEST_FREQ ON dbo.TEST (FREQ);\n"
    expected += (
        "CREATE INDEX IDX_dbo_TEST_INDICATOR ON dbo.TEST (INDICATOR);\n"
    )
    expected += "CREATE INDEX IDX_dbo_TEST_PERIOD ON dbo.TEST (PERIOD);\n"
    expected += "CREATE INDEX IDX_dbo_TEST_PRV ON dbo.TEST (PRV);\n"
    extra_cols = [
        Column(
            "PRV",
            DataType.ALPHA_NUM,
            3,
            3,
            True,
            True,
            True,
            False,
            "Provider",
        ),
        Column("LAST_UPD", DataType.DATE_TIME, required=True),
    ]

    sta = create_table(dsi, extra_columns=extra_cols)

    assert sta == expected


def test_extra_columns_no_double_index(dsi):
    expected = "CREATE TABLE dbo.TEST (\n"
    expected += "    FREQ CHAR(1) NOT NULL, -- Frequency\n"
    expected += "    INDICATOR CHAR(6) NOT NULL,\n"
    expected += "    PERIOD VARCHAR(50) NOT NULL,\n"
    expected += "    VALUE INT NULL,\n"
    expected += "    CONF CHAR(1) NOT NULL,\n"
    expected += "    PRV CHAR(3) NOT NULL, -- Provider\n"
    expected += "    LAST_UPD DATETIME2 NOT NULL,\n"
    expected += (
        "    CONSTRAINT PK_dbo_TEST PRIMARY KEY (FREQ,INDICATOR,PERIOD,PRV)\n"
    )
    expected += ");\n"
    expected += (
        "CREATE INDEX IDX_dbo_TEST_INDICATOR ON dbo.TEST (INDICATOR);\n"
    )
    expected += "CREATE INDEX IDX_dbo_TEST_PERIOD ON dbo.TEST (PERIOD);\n"
    expected += "CREATE INDEX IDX_dbo_TEST_PRV ON dbo.TEST (PRV);\n"
    extra_cols = [
        Column(
            "PRV",
            DataType.ALPHA_NUM,
            3,
            3,
            True,
            True,
            True,
            False,
            "Provider",
        ),
        Column("LAST_UPD", DataType.DATE_TIME, required=True),
    ]

    sta = create_table(
        dsi,
        index_fields=["INDICATOR", "PERIOD", "PRV"],
        extra_columns=extra_cols,
    )

    assert sta == expected


def test_extra_columns_none_in_pk(dsi):
    expected = "CREATE TABLE dbo.TEST (\n"
    expected += "    FREQ CHAR(1) NOT NULL, -- Frequency\n"
    expected += "    INDICATOR CHAR(6) NOT NULL,\n"
    expected += "    PERIOD VARCHAR(50) NOT NULL,\n"
    expected += "    VALUE INT NULL,\n"
    expected += "    CONF CHAR(1) NOT NULL,\n"
    expected += "    PRV CHAR(3) NOT NULL, -- Provider\n"
    expected += "    LAST_UPD DATETIME2 NOT NULL,\n"
    expected += (
        "    CONSTRAINT PK_dbo_TEST PRIMARY KEY (FREQ,INDICATOR,PERIOD)\n"
    )
    expected += ");\n"
    expected += "CREATE INDEX IDX_dbo_TEST_FREQ ON dbo.TEST (FREQ);\n"
    expected += (
        "CREATE INDEX IDX_dbo_TEST_INDICATOR ON dbo.TEST (INDICATOR);\n"
    )
    expected += "CREATE INDEX IDX_dbo_TEST_PERIOD ON dbo.TEST (PERIOD);\n"
    extra_cols = [
        Column(
            "PRV",
            DataType.ALPHA_NUM,
            3,
            3,
            required=True,
            documentation="Provider",
        ),
        Column("LAST_UPD", DataType.DATE_TIME, required=True),
    ]

    sta = create_table(dsi, extra_columns=extra_cols)

    assert sta == expected
