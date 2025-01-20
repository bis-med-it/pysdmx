# Open Source Software Licence Compliance Note

The BIS has independently authored the software program: `pysdmx`. It relies on multiple third-party software modules listed in `poetry.lock`.

`pysdmx` is licensed under the Apache License Version 2.0 and is therefore provided with no warranty. To comply with the terms of the licences covering the third-party components, `pysdmx` must be installed with the considerations below, any other installation method may not be compliant with the relevant third-party licences.

## Installation considerations

For a licence compliant installation, `pysdmx` must be installed using the package installer for Python (pip) using the `--no-binary` flag. An example installation command is:

`pip install pysdmx --no-binary :all:`

## Further information

1. Please note that usage of the `--no-binary` flag will increase the complexity of the installation (such as requiring building modules for some components from source). Please refer to third-party documentation for additional guidance; and
2. Please be aware that compliance materials may be placed into temporary directories by pip; and
3. When resolving dependencies for `pysdmx`, pip may automatically use a later version of a dependency. To prevent this behaviour, poetry can be used to generate a `verified-requirements.txt` which contains fixed version numbers: `poetry export -f requirements.txt -o verified-requirements.txt`. An example installation using this file is: `pip install -r verified-requirements.txt --no-binary :all:`
