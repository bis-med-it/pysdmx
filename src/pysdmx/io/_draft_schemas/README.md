# Draft schemas of SDMX-ML 3.2 and SDMX-JSON 2.2

SDMX 3.2 is not released yet. These files are copies of the draft
schemas with the VTL changes of SDMX 3.2, used to validate SDMX-ML 3.2 and
SDMX-JSON 2.2 structure messages until the `sdmxschemas` package has them.

| Folder | Source | Branch | Commit |
| --- | --- | --- | --- |
| `sdmx_ml_3_2` | https://github.com/sdmx-twg/sdmx-ml (`schemas`) | `cr-76-vtl-changes` (sdmx-twg/sdmx-ml#77) | `89edf65` |
| `sdmx_json_2_2` | https://github.com/sdmx-twg/sdmx-json (`schemas/structure_message`) | `cr-197-vtl-changes` (sdmx-twg/sdmx-json#198) | `84c87b6` |

The SDMX-JSON schema has one change: its `$id` and `description` are those of
the `2.2` branch of sdmx-json (SDMX-JSON 2.2.0), as the branch of the pull
request does not have the 2.2 namespace yet.

To update them, copy the files again from the two repositories. Once
`sdmxschemas` has the 3.2 and 2.2 schemas, this package can be removed.
