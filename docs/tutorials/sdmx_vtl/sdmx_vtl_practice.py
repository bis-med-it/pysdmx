"""Define a VTL program with SDMX 3.2 artefacts and run it.

This script shows how pysdmx can define a VTL program (Eurostat's GDP
check) with the VTL artefacts of SDMX 3.2, exchange the definitions and,
with vtlengine, run the program on real data. The notebook
sdmx_vtl_practice.ipynb is the exercise on the same steps, and
sdmx_vtl.ipynb explains them.

SDMX 3.2 is a draft: the script needs pysdmx 1.24.0rc1, with the all
extras, and access to the Internet.
"""

import json

import pandas as pd
from helpers import EUROSTAT, retrieve
from msgspec.structs import replace
from vtlengine import run, semantic_analysis

from pysdmx.io import read_sdmx, write_sdmx
from pysdmx.io.format import Format
from pysdmx.io.pd import PandasDataset
from pysdmx.model import (
    ItemReference,
    QueryExtraction,
    QueryParameter,
    Reference,
    Transformation,
    TransformationScheme,
    VtlDatasetMapping,
    VtlExecution,
    VtlMappingScheme,
)
from pysdmx.toolkit.vtl import (
    convert_dataset_to_sdmx,
    convert_dataset_to_vtl,
    generate_vtl_script,
    model_validations,
)
from pysdmx.util import parse_urn

# Part 1: The input: a real Dataflow

# Step 1: Read the Dataflow of GDP and its Data Structure Definition from
# Eurostat.
# Note: The Dataflow is ESTAT:NAMA_10_GDP(1.0) (GDP and main components). Its
# Data Structure Definition is attached to it, because the next steps need its
# components.
message = read_sdmx(
    f"{EUROSTAT}/structure/dataflow/ESTAT/NAMA_10_GDP/1.0"
    "?references=descendants"
)
dsd_gdp = message.get_data_structure_definitions()[0]
df_gdp = replace(message.get_dataflows()[0], structure=dsd_gdp)
print(df_gdp.short_urn, [(c.id, c.role.name) for c in dsd_gdp.components])

# Part 2: Structural part: the program and its mappings

# Step 2: Define the mapping of the input.
# Note: The VTL Mapping Scheme defines the VTL Data Sets of the program: each
# VtlDatasetMapping has the alias used in VTL, the SDMX artefact and is_input.
# The input, with the alias gdp, is the Dataflow of Step 1.
gdp_mapping = VtlDatasetMapping(
    id="GDP",
    name="GDP",
    vtl_alias="gdp",
    sdmx_artefact=df_gdp,
    is_input=True,
)

# Step 3: Define the mapping of the output and the VTL Mapping Scheme.
# Note: The output, with the alias gdp_check, is the Dataflow
# ESTAT:ES_NAMA_10_GDP(1.0), which is not defined beforehand: its data
# structure is derived from the program, so a Reference to it is enough.
check_mapping = VtlDatasetMapping(
    id="GDP_CHECK",
    name="Validation results",
    vtl_alias="gdp_check",
    sdmx_artefact=Reference("Dataflow", "ESTAT", "ES_NAMA_10_GDP", "1.0"),
    is_input=False,
)
mappings = VtlMappingScheme(
    id="VTL_MAP_GDP",
    agency="ESTAT",
    name="VTL mappings of the GDP check",
    items=[gdp_mapping, check_mapping],
)
for m in mappings.items:
    print(m.vtl_alias, m.sdmx_urn, m.is_input)

# Step 4: Define the Transformation of the annual growth of GDP.
# Note: The Transformation Scheme is the VTL program. Its first Transformation
# gives the annual growth of GDP, in percentage, as the result growth. It is
# not persistent: it is not an output of the program.
growth_transformation = Transformation(
    id="GROWTH",
    name="Annual growth of GDP (%)",
    result="growth",
    is_persistent=False,
    expression="(gdp / timeshift(gdp, 1) - 1) * 100",
)

# Step 5: Define the Transformation of the check and the Transformation Scheme.
# Note: The second Transformation keeps the data points whose growth is above
# 20% in absolute value, as the result gdp_check. It is persistent: it is the
# output of the program.
check_transformation = Transformation(
    id="GDP_CHECK",
    name="Growth of GDP within 20%",
    result="gdp_check",
    is_persistent=True,
    expression='check(abs(growth) <= 20 errorcode "GDP_GROWTH" invalid)',
)
ts = TransformationScheme(
    id="TS_GDP_CHECK",
    agency="ESTAT",
    name="GDP check",
    vtl_version="2.2",
    vtl_mapping_scheme=mappings,
    items=[growth_transformation, check_transformation],
)

# Part 3: Execution model: where the input data come from


# Step 6: Define the execution of the program by Eurostat.
# Note: A VtlExecution references the Transformation Scheme and has at most one
# data extraction for each input. It is maintained independently of the
# program.
# Note: The extraction queries a web service (SDMX REST 2.0). The key is fixed.
# The period is a parameter with a default value, which can be changed at run
# time. Eurostat queries its own web service for all countries.
def gdp_check_execution(agency, entry_point, key):
    """Returns an execution of the GDP check."""
    return VtlExecution(
        id="EXEC_GDP_CHECK",
        agency=agency,
        name=f"Execution of the GDP check by {agency}",
        transformation_scheme=ts,
        extractions=[
            QueryExtraction(
                dataset_mapping=ItemReference(
                    "VtlDatasetMapping", "ESTAT", "VTL_MAP_GDP", "1.0", "GDP"
                ),
                entry_point=entry_point,
                sdmx_api_version="2.0",
                parameters=[
                    QueryParameter(name="key", value=key, is_fixed=True),
                    QueryParameter(
                        name="c[TIME_PERIOD]", value="ge:2015", is_fixed=False
                    ),
                ],
            )
        ],
    )


execution = gdp_check_execution("ESTAT", EUROSTAT, "A.CP_MEUR.B1GQ.*")

# Part 4: Checking and exchanging the definitions

# Step 7: Check the definitions and write them in SDMX-ML 3.2.
# Note: model_validations checks the rules that involve several artefacts (e.g.
# the outputs are persistent results, the extractions apply to inputs). It
# raises an error when a rule is not met.
# Note: In the SDMX-ML message, the VtlExecution has the reference to the
# Transformation Scheme, and the query extraction with its entry point and its
# parameters.
vtl_artefacts = [mappings, ts, execution]
for artefact in vtl_artefacts:
    model_validations(artefact, [df_gdp, *vtl_artefacts])
sdmx_ml = write_sdmx(vtl_artefacts, Format.STRUCTURE_SDMX_ML_3_2)
print(sdmx_ml)

# Part 5: At run time

# Step 8: Generate the VTL script and get the data structure of the output,
# without any data.
# Note: The engine needs only the reference to the VtlExecution and, possibly,
# some parameter values. The VTL script is generated from its Transformation
# Scheme.
# Note: The semantic analysis of the engine gets the SDMX artefact and the
# alias of the input, and gives the data structure of every result. The one of
# the output is converted into SDMX: these are the components of the Dataflow
# ESTAT:ES_NAMA_10_GDP(1.0).
script = generate_vtl_script(ts, model_validation=True)
print(script)

analysis = semantic_analysis(
    script=ts,
    data_structures=df_gdp,
    sdmx_mappings={df_gdp.short_urn: gdp_mapping.vtl_alias},
)
schema_check = convert_dataset_to_sdmx(
    analysis[check_mapping.vtl_alias],
    reference=parse_urn(check_mapping.sdmx_urn),
).structure
print(
    pd.DataFrame(
        [(c.id, c.role.name, str(c.dtype)) for c in schema_check.components],
        columns=["component", "role", "data type"],
    )
)


# Step 9: Query the data of the input.
# Note: retrieve (in helpers.py) builds the query from the extraction: the
# artefact of the mapping, the key and the other parameters, which take the
# run-time values unless they are fixed. It prints the address of the query.
def input_dataset(execution, values):
    """Returns the SDMX data set of the input of an execution."""
    return PandasDataset(
        structure=replace(
            dsd_gdp.to_schema(),
            context="dataflow",
            id=df_gdp.id,
            version=df_gdp.version,
        ),
        data=retrieve(execution.extractions[0], gdp_mapping.sdmx_urn, values),
    )


gdp = input_dataset(execution, {"c[TIME_PERIOD]": "ge:2015"})
print(len(gdp.data), "observations of", gdp.data["geo"].nunique(), "areas")

# Step 10: Execute the program.
# Note: The SDMX data set is converted into a VTL Data Set, named after its
# alias, and the engine runs the script on it.
# Note: The result growth is not persistent, so the engine only returns it when
# all the results are requested.
gdp_vtl = convert_dataset_to_vtl(gdp, gdp_mapping.vtl_alias)
results = run(
    script=script,
    data_structures=json.loads(gdp_vtl.to_json_datastructure()),
    datapoints={gdp_vtl.name: gdp_vtl.data},
    return_only_persistent=False,
)
growth = results["growth"].data
print(growth.loc[growth["OBS_VALUE"].abs().nlargest(5).index].round(1))

# Step 11: Store the result.
# Note: The persistent result gdp_check is the output of the program: its data
# are converted into SDMX, as data of the Dataflow ESTAT:ES_NAMA_10_GDP(1.0).
# The conversion checks that its data structure is the one obtained in Step 8.
# Note: The output has the data points whose growth is above 20% in absolute
# value, with their error code.
checked = convert_dataset_to_sdmx(
    results[check_mapping.vtl_alias], schema=schema_check
)
print(write_sdmx(checked, Format.DATA_SDMX_CSV_2_0_0))

# Bonus: Reuse and change the program

# Bonus 1: Reuse the program with another execution.
# Note: A national institute reuses the program of Eurostat with its own
# execution, which only queries the data of its country. The program and its
# mappings do not change.
# Note: An empty output means that every data point passes the check.
other_execution = gdp_check_execution("CSO", EUROSTAT, "A.CP_MEUR.B1GQ.IE")
model_validations(other_execution, [df_gdp, mappings, ts, other_execution])

other_gdp = convert_dataset_to_vtl(
    input_dataset(other_execution, {"c[TIME_PERIOD]": "ge:2000"}),
    gdp_mapping.vtl_alias,
)
other_results = run(
    script=script,
    data_structures=json.loads(other_gdp.to_json_datastructure()),
    datapoints={other_gdp.name: other_gdp.data},
)
other_checked = convert_dataset_to_sdmx(
    other_results[check_mapping.vtl_alias], schema=schema_check
)
print(write_sdmx(other_checked, Format.DATA_SDMX_CSV_2_0_0))

# Bonus 2: Change the threshold of the check.
# Note: A stricter check is another program: a Transformation Scheme with the
# same mappings and another expression.
strict = replace(
    ts,
    id="TS_GDP_CHECK_10",
    name="GDP check (10%)",
    items=[
        growth_transformation,
        replace(
            check_transformation,
            name="Growth of GDP within 10%",
            expression=(
                'check(abs(growth) <= 10 errorcode "GDP_GROWTH" invalid)'
            ),
        ),
    ],
)
strict_results = run(
    script=generate_vtl_script(strict, model_validation=True),
    data_structures=json.loads(gdp_vtl.to_json_datastructure()),
    datapoints={gdp_vtl.name: gdp_vtl.data},
)
print(
    len(results["gdp_check"].data),
    "data points do not pass the check of 20%, and",
    len(strict_results["gdp_check"].data),
    "the check of 10%",
)
