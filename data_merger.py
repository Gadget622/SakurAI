import os
import json
import sys
from pathlib import Path
import pandas as pd

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
        print("Please run character_attributes_extractor_csv.py first.")
        sys.exit(1)
    
    if not csv_path.exists():
        print(f"Error: Characters CSV file '{csv_path}' not found.")
        print("Please run data_extractor_csv.py first to create the characters.csv file.")
        sys.exit(1)
    
    # Load the extracted character attributes
    attrs_file = extracted_data_path / "character_attributes.json"
    mapping_file = extracted_data_path / "character_mapping.json"
    
    if not attrs_file.exists() or not mapping_file.exists():
        print(f"Error: Required JSON files not found in '{extracted_data_path}'.")
        print("Please run character_attributes_extractor_csv.py first.")
        sys.exit(1)
    
    with open(attrs_file, 'r', encoding='utf-8') as f:
        character_attrs = json.load(f)
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        char_mapping = json.load(f)
    
    # Load the existing characters.csv
    try:
        characters_df = pd.read_csv(csv_path)
        print(f"Loaded existing characters.csv with {len(characters_df)} rows")
    except Exception as e:
        print(f"Error loading characters.csv: {e}")
        sys.exit(1)
    
    # Process the character attributes and create new columns for the CSV
    print("Processing character attributes...")
    
    # Keep track of new columns we'll add
    new_columns = set()
    
    # Prepare the data for updating the DataFrame
    for _, row in characters_df.iterrows():
        char_id = row['character_id']
        
        # Extract character name from char_id (remove number prefix)
        char_name = char_id.split('_', 1)[1] if '_' in char_id else char_id
        
        # Find the corresponding character in our extracted data
        for display_name, attr_data in character_attrs.items():
            # Try different matching strategies
            if (char_name == attr_data['internal_name'] or
                char_name == display_name.lower().replace(' ', '-') or
                char_name == display_name.lower().replace(' & ', '-') or
                char_name == display_name.lower().replace(' ', '')):
                
                # Found a match, add attributes
                if 'data' in attr_data and 'Params' in attr_data['data']:
                    params = attr_data['data']['Params']
                    
                    # Add all parameters as new columns
                    for param, value in params.items():
                        col_name = f"param_{param}"
                        new_columns.add(col_name)
                        characters_df.loc[characters_df['character_id'] == char_id, col_name] = value
                
                # Add mapping data if available
                found_in_mapping = False
                for map_name, map_data in char_mapping.items():
                    if isinstance(map_data, dict) and map_data.get('internal_name') == attr_data['internal_name']:
                        found_in_mapping = True
                        for key, value in map_data.items():
                            if key != 'internal_name':  # Already have this
                                col_name = f"map_{key}"
                                new_columns.add(col_name)
                                characters_df.loc[characters_df['character_id'] == char_id, col_name] = value
                
                break
    
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
    print(characters_df.head()[['character_id'] + list(new_columns)[:5]].to_string())
    
    return len(new_columns)

if __name__ == "__main__":
    print("Updating characters.csv with SSBU-Calculator attributes...")
    num_columns = update_characters_csv()
    print(f"\nSuccessfully added {num_columns} attribute columns to characters.csv")