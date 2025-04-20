import os
import json
import sys
from pathlib import Path
import pandas as pd
from collections import defaultdict

def load_character_data():
    """
    Load character data from the cloned Ultimate Hitboxes repository.
    Assumes the repo is already cloned locally.
    """
    # Define the path to the ultimate-hitboxes data directory
    repo_path = Path(os.path.expanduser("~")) / "Documents" / "GitHub" / "ultimate-hitboxes" / "server" / "data"
    
    # Print the path we're checking to help with debugging
    print(f"Looking for repository at: {repo_path}")
    
    # Ensure the path exists
    if not repo_path.exists():
        print(f"Error: Repository path '{repo_path}' not found.")
        print("Please provide the correct path to the ultimate-hitboxes repository:")
        user_path = input("Path to repository: ")
        repo_path = Path(user_path)
        if not repo_path.exists():
            print("Path still not found. Exiting.")
            sys.exit(1)
    
    # Get a list of all character data files
    character_files = list(repo_path.glob("*.json"))
    
    if not character_files:
        print("No character data files found in the repository.")
        sys.exit(1)
    
    print(f"Found {len(character_files)} character data files.")
    
    # Load each character's data
    character_data = {}
    character_attributes = None
    
    for file_path in character_files:
        character_name = file_path.stem
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Special handling for characterData.json
                if character_name == 'characterData':
                    character_attributes = data
                    print(f"Loaded character attributes data")
                else:
                    character_data[character_name] = data
                    print(f"Loaded data for {character_name}")
                    
        except json.JSONDecodeError:
            print(f"Error: Could not parse JSON in {file_path}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return character_data, character_attributes

def analyze_data_structure(character_data, character_attributes):
    """
    Analyze the structure of the character data to determine fields for CSV files.
    """
    print("\nAnalyzing character data structure...")
    
    # Character overview data
    character_fields = set()
    for char_name, char_data in character_data.items():
        # Skip non-character data files
        if char_name in ['items', 'todo'] or not isinstance(char_data, dict):
            continue
            
        for field in char_data.keys():
            if field != "moves":  # We'll handle moves separately
                character_fields.add(field)
    
    # Add character attribute fields
    attribute_fields = set()
    if character_attributes:
        for char_id, attr in character_attributes.items():
            if isinstance(attr, dict):
                for field in attr.keys():
                    attribute_fields.add(field)
    
    # Move data
    move_fields = set()
    hitbox_fields = set()
    throw_fields = set()
    
    for char_name, char_data in character_data.items():
        # Skip non-character data files
        if char_name in ['items', 'todo'] or not isinstance(char_data, dict):
            continue
            
        if "moves" in char_data and isinstance(char_data["moves"], list):
            for move in char_data["moves"]:
                if not isinstance(move, dict):
                    continue
                    
                # Collect move-level fields
                for field in move.keys():
                    if field not in ["hitboxes", "throws"]:
                        move_fields.add(field)
                
                # Collect hitbox-level fields
                if "hitboxes" in move and isinstance(move["hitboxes"], list):
                    for hitbox in move["hitboxes"]:
                        if not isinstance(hitbox, dict):
                            continue
                        for field in hitbox.keys():
                            hitbox_fields.add(field)
                
                # Collect throw-level fields
                if "throws" in move and isinstance(move["throws"], list):
                    for throw in move["throws"]:
                        if not isinstance(throw, dict):
                            continue
                        for field in throw.keys():
                            throw_fields.add(field)
    
    print(f"Character fields: {len(character_fields)}")
    print(f"Character attribute fields: {len(attribute_fields)}")
    print(f"Move fields: {len(move_fields)}")
    print(f"Hitbox fields: {len(hitbox_fields)}")
    print(f"Throw fields: {len(throw_fields)}")
    
    return {
        "character_fields": sorted(list(character_fields)),
        "attribute_fields": sorted(list(attribute_fields)),
        "move_fields": sorted(list(move_fields)),
        "hitbox_fields": sorted(list(hitbox_fields)),
        "throw_fields": sorted(list(throw_fields))
    }

def prepare_data_for_csv(character_data, character_attributes, structure):
    """
    Prepare the data for CSV export.
    """
    print("\nPreparing data for CSV export...")
    
    # Prepare character overview data
    character_rows = []
    
    # Create a mapping of character IDs to their file names
    char_id_mapping = {}
    if character_attributes:
        for char_file in character_data.keys():
            if char_file in ['items', 'todo']:
                continue
                
            # Try to find a matching character ID in characterData
            for char_id, attr in character_attributes.items():
                if isinstance(attr, dict) and 'name' in attr:
                    # Match by name or filename (with number prefix removed)
                    file_name_without_prefix = char_file.split('_', 1)[1] if '_' in char_file else char_file
                    if (attr['name'].lower() == file_name_without_prefix.lower() or 
                        attr['name'].lower().replace(' ', '-') == file_name_without_prefix.lower() or
                        attr['name'].lower().replace(' & ', '-') == file_name_without_prefix.lower()):
                        char_id_mapping[char_file] = char_id
                        break
    
    for char_name, char_data in character_data.items():
        # Skip non-character data files
        if char_name in ['items', 'todo'] or not isinstance(char_data, dict):
            continue
            
        char_row = {
            "character_id": char_name,
            "file_name": char_name
        }
        
        # Add character data fields
        for field in structure["character_fields"]:
            if field in char_data:
                char_row[field] = char_data[field]
            else:
                char_row[field] = None
        
        # Add attribute data if available
        char_id = char_id_mapping.get(char_name)
        if char_id and character_attributes and char_id in character_attributes:
            char_row["internal_id"] = char_id
            attr = character_attributes[char_id]
            if isinstance(attr, dict):
                for field in structure["attribute_fields"]:
                    if field in attr:
                        char_row[f"attr_{field}"] = attr[field]
                    else:
                        char_row[f"attr_{field}"] = None
        
        character_rows.append(char_row)
    
    # Prepare move data
    move_rows = []
    hitbox_rows = []
    throw_rows = []
    
    for char_name, char_data in character_data.items():
        # Skip non-character data files
        if char_name in ['items', 'todo'] or not isinstance(char_data, dict):
            continue
            
        if "moves" in char_data and isinstance(char_data["moves"], list):
            for move_idx, move in enumerate(char_data["moves"]):
                if not isinstance(move, dict):
                    continue
                    
                # Add move data
                move_row = {
                    "character_id": char_name,
                    "internal_id": char_id_mapping.get(char_name, ""),
                    "move_index": move_idx
                }
                for field in structure["move_fields"]:
                    if field in move:
                        move_row[field] = move[field]
                    else:
                        move_row[field] = None
                move_rows.append(move_row)
                
                # Add hitbox data
                if "hitboxes" in move and isinstance(move["hitboxes"], list):
                    for hitbox_idx, hitbox in enumerate(move["hitboxes"]):
                        if not isinstance(hitbox, dict):
                            continue
                            
                        hitbox_row = {
                            "character_id": char_name,
                            "internal_id": char_id_mapping.get(char_name, ""),
                            "move_index": move_idx,
                            "hitbox_index": hitbox_idx,
                            "move_name": move.get("name", "")
                        }
                        for field in structure["hitbox_fields"]:
                            if field in hitbox:
                                hitbox_row[field] = hitbox[field]
                            else:
                                hitbox_row[field] = None
                        hitbox_rows.append(hitbox_row)
                
                # Add throw data
                if "throws" in move and isinstance(move["throws"], list):
                    for throw_idx, throw in enumerate(move["throws"]):
                        if not isinstance(throw, dict):
                            continue
                            
                        throw_row = {
                            "character_id": char_name,
                            "internal_id": char_id_mapping.get(char_name, ""),
                            "move_index": move_idx,
                            "throw_index": throw_idx,
                            "move_name": move.get("name", "")
                        }
                        for field in structure["throw_fields"]:
                            if field in throw:
                                throw_row[field] = throw[field]
                            else:
                                throw_row[field] = None
                        throw_rows.append(throw_row)
    
    return {
        "characters": character_rows,
        "moves": move_rows,
        "hitboxes": hitbox_rows,
        "throws": throw_rows
    }

def export_to_csv(csv_data, output_dir):
    """
    Export the prepared data to CSV files.
    """
    print("\nExporting data to CSV files...")
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Export each dataset to a CSV file
    for dataset_name, dataset in csv_data.items():
        if dataset:  # Only export non-empty datasets
            df = pd.DataFrame(dataset)
            csv_file = output_path / f"{dataset_name}.csv"
            df.to_csv(csv_file, index=False)
            print(f"Exported {len(dataset)} rows to {csv_file}")

if __name__ == "__main__":
    # Load character data
    print("Loading character data from Ultimate Hitboxes repository...")
    character_data, character_attributes = load_character_data()
    print(f"Successfully loaded data for {len(character_data)} characters.")
    
    # Analyze data structure
    structure = analyze_data_structure(character_data, character_attributes)
    
    # Prepare data for CSV export
    csv_data = prepare_data_for_csv(character_data, character_attributes, structure)
    
    # Display some statistics
    print("\nData statistics:")
    print(f"Number of characters: {len(csv_data['characters'])}")
    print(f"Number of moves: {len(csv_data['moves'])}")
    print(f"Number of hitboxes: {len(csv_data['hitboxes'])}")
    print(f"Number of throws: {len(csv_data['throws'])}")
    
    # Preview first row of each dataset
    if csv_data['characters']:
        print("\nSample character data:")
        first_char = csv_data['characters'][0]
        keys = list(first_char.keys())
        print(f"Number of fields: {len(keys)}")
        print(f"First 5 fields: {keys[:5]}")
        
        # Show some attribute fields if they exist
        attr_fields = [k for k in keys if k.startswith('attr_')]
        if attr_fields:
            print(f"Sample attribute fields: {attr_fields[:5]}")
    
    if csv_data['moves']:
        print("\nSample move data:")
        print(list(csv_data['moves'][0].keys())[:5], "...")  # First 5 fields
    
    if csv_data['hitboxes']:
        print("\nSample hitbox data:")
        print(list(csv_data['hitboxes'][0].keys())[:5], "...")  # First 5 fields
    
    if csv_data['throws']:
        print("\nSample throw data:")
        print(list(csv_data['throws'][0].keys())[:5], "...")  # First 5 fields
    
    # Export data to CSV files
    output_dir = Path(os.path.expanduser("~")) / "Documents" / "GitHub" / "SakurAI" / "data"
    export_to_csv(csv_data, output_dir)
    
    print("\nData extraction and export complete!")