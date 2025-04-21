import os
import json
import sys
from pathlib import Path
import pandas as pd

def normalize_character_name(name):
    """
    Normalize character names by removing or replacing special characters
    for consistent matching across different data sources
    """
    if not name:
        return ""
    # Convert to lowercase
    normalized = name.lower()
    # Replace common special characters
    normalized = normalized.replace(' & ', '-')
    normalized = normalized.replace('&', '-')
    normalized = normalized.replace('.', '')
    normalized = normalized.replace(' ', '-')
    # Remove any remaining special characters
    normalized = ''.join(c for c in normalized if c.isalnum() or c == '-')
    return normalized

def update_characters_csv():
    """
    Update the characters.csv file with additional attributes from the SSBU-Calculator data
    """
    # Define paths
    sakurai_path = Path.home() / "Documents" / "GitHub" / "SakurAI"
    extracted_data_path = sakurai_path / "extracted_data"
    csv_path = sakurai_path / "data" / "characters.csv"
    
    # Check if paths exist
    if not extracted_data_path.exists():
        print(f"Error: Extracted data path '{extracted_data_path}' not found.")
        print("Please run character_attributes_extractor.py first.")
        sys.exit(1)
    
    if not csv_path.exists():
        print(f"Error: Characters CSV file '{csv_path}' not found.")
        print("Please run data_extractor_csv.py first to create the characters.csv file.")
        sys.exit(1)
    
    # Load the extracted character attributes
    attrs_file = extracted_data_path / "character_attributes.json"
    mapping_file = extracted_data_path / "character_mapping.json"
    normalized_file = extracted_data_path / "normalized_character_names.json"
    display_game_file = extracted_data_path / "display_to_game_names.json"
    
    required_files = [attrs_file, mapping_file]
    for file in required_files:
        if not file.exists():
            print(f"Error: Required JSON file '{file}' not found.")
            print("Please run character_attributes_extractor.py first.")
            sys.exit(1)
    
    with open(attrs_file, 'r', encoding='utf-8') as f:
        character_attrs = json.load(f)
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        char_mapping = json.load(f)
    
    # Load normalized mappings if available
    normalized_mappings = {}
    if normalized_file.exists():
        with open(normalized_file, 'r', encoding='utf-8') as f:
            normalized_mappings = json.load(f)
    
    # Load display to game name mapping if available
    display_to_game = {}
    if display_game_file.exists():
        with open(display_game_file, 'r', encoding='utf-8') as f:
            display_to_game = json.load(f)
    
    # Load the existing characters.csv
    try:
        characters_df = pd.read_csv(csv_path)
        print(f"Loaded existing characters.csv with {len(characters_df)} rows")
    except Exception as e:
        print(f"Error loading characters.csv: {e}")
        sys.exit(1)
    
    # Add game_name column if it doesn't exist
    if 'game_name' not in characters_df.columns:
        characters_df['game_name'] = None
    
    # Add normalized_name column if it doesn't exist
    if 'normalized_name' not in characters_df.columns:
        characters_df['normalized_name'] = characters_df['character_id'].apply(normalize_character_name)
    
    # Process the character attributes and create new columns for the CSV
    print("Processing character attributes...")
    
    # Keep track of new columns we'll add
    new_columns = set()
    
    # Create a dictionary of normalized character_ids for easier lookup
    normalized_char_ids = {normalize_character_name(row['character_id']): row['character_id'] 
                        for _, row in characters_df.iterrows()}
    
    # First pass: Add game_names from the display_to_game mapping
    for _, row in characters_df.iterrows():
        char_id = row['character_id']
        
        # Extract character name from char_id (remove number prefix)
        char_name = char_id.split('_', 1)[1] if '_' in char_id else char_id
        
        # Try to find game_name from our mapping
        if display_to_game:
            for display_name, game_name in display_to_game.items():
                normalized_display = normalize_character_name(display_name)
                normalized_char = normalize_character_name(char_name)
                
                if normalized_display == normalized_char:
                    characters_df.loc[characters_df['character_id'] == char_id, 'game_name'] = game_name
                    break
    
    # Second pass: Process character attributes
    for display_name, attr_data in character_attrs.items():
        # Get the normalized version of this display name
        normalized_display = normalize_character_name(display_name)
        
        # Try to find the corresponding character_id in our CSV
        matched_char_id = None
        
        # Try multiple matching strategies
        for _, row in characters_df.iterrows():
            char_id = row['character_id']
            char_name = char_id.split('_', 1)[1] if '_' in char_id else char_id
            normalized_char = normalize_character_name(char_name)
            
            # Direct match
            if normalized_char == normalized_display:
                matched_char_id = char_id
                break
            
            # Match on internal_name
            if attr_data.get('internal_name') == row.get('game_name'):
                matched_char_id = char_id
                break
            
            # Match using normalized variants
            if normalized_char in normalized_display or normalized_display in normalized_char:
                matched_char_id = char_id
                break
        
        if matched_char_id:
            # We found a match, add attributes
            if 'data' in attr_data and 'Params' in attr_data['data']:
                params = attr_data['data']['Params']
                
                # Add all parameters as new columns
                for param, value in params.items():
                    col_name = f"param_{param}"
                    new_columns.add(col_name)
                    characters_df.loc[characters_df['character_id'] == matched_char_id, col_name] = value
            
            # Add internal name and game name
            characters_df.loc[characters_df['character_id'] == matched_char_id, 'game_name'] = attr_data.get('game_name')
            
            # Add other attributes from attr_data
            for key, value in attr_data.items():
                if key not in ['data', 'internal_name', 'game_name']:
                    col_name = f"attr_{key}"
                    new_columns.add(col_name)
                    characters_df.loc[characters_df['character_id'] == matched_char_id, col_name] = value
    
    # Add mapping data if available
    for char_id, row in characters_df.iterrows():
        char_name = row['character_id'].split('_', 1)[1] if '_' in row['character_id'] else row['character_id']
        normalized_char = normalize_character_name(char_name)
        
        # Look for this character in our mapping data
        for map_name, map_data in char_mapping.items():
            if isinstance(map_data, dict):
                normalized_map = normalize_character_name(map_name)
                if normalized_map == normalized_char or map_data.get('normalized_name') == normalized_char:
                    for key, value in map_data.items():
                        if key not in ['internal_name', 'game_name']:  # We already have these
                            col_name = f"map_{key}"
                            new_columns.add(col_name)
                            characters_df.loc[characters_df['character_id'] == row['character_id'], col_name] = value
    
    # Save the updated CSV
    print(f"Added {len(new_columns)} new columns to characters.csv")
    characters_df.to_csv(csv_path, index=False)
    print(f"Updated characters.csv saved to {csv_path}")
    
    # Also save a backup of the original
    backup_path = csv_path.with_suffix('.csv.bak')
    characters_df.to_csv(backup_path, index=False)
    print(f"Backup of characters.csv saved to {backup_path}")
    
    # Print sample of updated data
    print("\nSample of updated data:")
    sample_cols = ['character_id', 'game_name', 'normalized_name']
    sample_cols.extend(list(new_columns)[:3])  # Add up to 3 new columns
    print(characters_df[sample_cols].head().to_string())
    
    return len(new_columns)

if __name__ == "__main__":
    print("Updating characters.csv with SSBU-Calculator attributes...")
    num_columns = update_characters_csv()
    print(f"\nSuccessfully added {num_columns} attribute columns to characters.csv")