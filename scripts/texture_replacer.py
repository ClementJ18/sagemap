"""Script to replace textures in a map file.

Usage:
1. Run the script with a map file path
2. It will generate texture_mapping.json with all unique textures
3. Edit the JSON file to specify replacements
4. Press Enter to apply the changes
"""

import json
import sys
from pathlib import Path

from sagemap import parse_map_from_path, write_map_to_path


def extract_textures(map_path: str) -> dict[str, str]:
    """Extract all unique texture names from a map file."""
    print(f"Loading map from: {map_path}")
    sage_map = parse_map_from_path(map_path)

    if not sage_map.blend_tile_data:
        print("Warning: No BlendTileData found in map")
        return {}

    textures = {}
    for texture in sage_map.blend_tile_data.textures:
        # Initialize with empty string (user will fill in replacement)
        textures[texture.name] = ""

    print(f"Found {len(textures)} unique textures:")
    for texture_name in sorted(textures.keys()):
        print(f"  - {texture_name}")

    return textures


def create_mapping_file(textures: dict[str, str], output_path: str = "texture_mapping.json"):
    """Create a JSON file with texture mappings."""
    with open(output_path, "w") as f:
        json.dump(textures, f, indent=2)
    print(f"\nCreated {output_path}")
    print("Edit this file to specify texture replacements.")
    print('Leave values empty ("") to keep the original texture.')


def load_mapping_file(mapping_path: str = "texture_mapping.json") -> dict[str, str]:
    """Load texture mappings from JSON file."""
    with open(mapping_path, "r") as f:
        return json.load(f)


def apply_replacements(map_path: str, mapping: dict[str, str], output_path: str = None):
    """Apply texture replacements to a map file."""
    print(f"\nApplying replacements to: {map_path}")
    sage_map = parse_map_from_path(map_path)

    if not sage_map.blend_tile_data:
        print("Error: No BlendTileData found in map")
        return

    # Filter out empty replacements
    active_replacements = {k: v for k, v in mapping.items() if v and v.strip()}

    if not active_replacements:
        print("No replacements specified. Aborting.")
        return

    print(f"\nApplying {len(active_replacements)} replacement(s):")
    replaced_count = 0

    for texture in sage_map.blend_tile_data.textures:
        if texture.name in active_replacements:
            old_name = texture.name
            new_name = active_replacements[old_name]
            texture.name = new_name
            print(f"  {old_name} -> {new_name}")
            replaced_count += 1

    if replaced_count == 0:
        print("Warning: No textures were replaced (mapping names may not match)")
        return

    # Save the modified map
    if output_path is None:
        output_path = map_path

    print(f"\nSaving modified map to: {output_path}")
    write_map_to_path(sage_map, output_path, compress=True)
    print(f"Successfully replaced {replaced_count} texture(s)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python texture_replacer.py <map_file_path> [output_map_path]")
        print("\nExample:")
        print("  python texture_replacer.py Mission.json")
        print("  python texture_replacer.py Mission.json Mission_Modified.json")
        sys.exit(1)

    map_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(map_path).exists():
        print(f"Error: Map file not found: {map_path}")
        sys.exit(1)

    # Step 1: Extract textures
    textures = extract_textures(map_path)
    if not textures:
        print("No textures found to replace")
        sys.exit(0)

    # Step 2: Create mapping file
    mapping_file = "texture_mapping.json"
    create_mapping_file(textures, mapping_file)

    # Step 3: Wait for user to edit
    print("\n" + "=" * 60)
    print("Please edit texture_mapping.json with your replacements.")
    print("Press Enter when ready to apply changes...")
    print("=" * 60)
    input()

    # Step 4: Load mappings
    try:
        mapping = load_mapping_file(mapping_file)
    except FileNotFoundError:
        print(f"Error: {mapping_file} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {mapping_file}: {e}")
        sys.exit(1)

    # Step 5: Apply replacements
    apply_replacements(map_path, mapping, output_path)


if __name__ == "__main__":
    main()
