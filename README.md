# sagemap

A python library for reading BFME .map files. Can potentially work with the map files of other SAGE games but might need to be adjusted. This implementation is not complete.

All the credit for the parsing logic goes to: https://github.com/OpenSAGE/OpenSAGE. I simply "translated" it to Python and simplified it.

## Installing
The package is available on pip

```
python -m pip install sagemap
```

## Example

```python
from sagemap import parse_map_from_path

# Load a BFME .map file
map = parse_map_from_path('path/to/your/file.map')

# Access map properties
print(map.world_info)
print(map.height_map_data)
print(map.objects_list)
```

## Map Linter

sagemap includes a command-line linter for validating BFME map files. The linter checks for common issues such as terrain flatness, object counts, resource placement, and camera settings.

### Usage

Run the linter from the command line:

```
python -m sagemap.linter <path-to-map-folder>
```

You can list all available error codes or exclude specific checks using command-line options. For more details, run:

```
python -m sagemap.linter --help
```

### Using the Linter Programmatically

You can also use the linter in your own Python scripts:

```python
from sagemap.linter import lint_map
from sagemap import parse_map_from_path

map = parse_map_from_path('path/to/your/file.map')
errors = lint_map(map)

for error in errors:
	print(f"{error.code}: {error.message}")
```