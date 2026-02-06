import multiprocessing
from map_parser import parse_map, Map

# path = "C:\\Users\\Clement\\Documents\\Edain\\Edain-Mod\\_mod\\maps\\map edain oldforest II\\map edain oldforest II.map"

# map: Map = parse_map(path)

def _process_single_map(file_info):
    """Helper function to process a single map file. Used for multiprocessing."""
    file_path, filename = file_info
    try:
        print(f"Processing file: {filename}")
        map_obj = parse_map(file_path)
        map_name = filename.split(".")[0]
        return (map_name, map_obj)
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return (filename.split(".")[0], None)

def process_directory(root_dir: str, num_processes: int = None) -> dict[str, Map]:
    """Recursively process all files in a directory using multiprocessing.
    
    Args:
        root_dir: Directory to process
        num_processes: Number of processes to use. If None, uses CPU count - 1.
    
    Returns:
        Dictionary mapping map names to Map objects
    """
    if num_processes is None:
        num_processes = min(3, multiprocessing.cpu_count() - 2)
    
    # Collect all map files first
    file_list = []
    for root, _, files in os.walk(root_dir):
        for filename in files:
            if filename.lower().endswith((".map", ".bse")):
                file_path = os.path.join(root, filename)
                file_list.append((file_path, filename))
    
    if not file_list:
        print("No map files found.")
        return {}
    
    print(f"Found {len(file_list)} map files. Processing with {num_processes} processes...")
    
    # Process files using multiprocessing
    maps = {}
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(_process_single_map, file_list)
    
    # Collect results, filtering out None values (failed parses)
    for map_name, map_obj in results:
        if map_obj is not None:
            maps[map_name] = map_obj
    
    print(f"Successfully processed {len(maps)} out of {len(file_list)} map files.")
    return maps

if __name__ == "__main__":
    import os
    import time

    root_directory = "C:\\Users\\Clement\\Documents\\Edain\\Edain-Mod\\_mod\\maps"
    
    start_time = time.time()
    maps = process_directory(root_directory)
    end_time = time.time()
    
    print(f"Processed {len(maps)} maps in {end_time - start_time:.2f} seconds.")