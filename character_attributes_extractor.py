import os
import json
import sys
from pathlib import Path

def load_character_mapping():
    """
    Create a mapping between character display names and internal names
    """
    # Create a combined dictionary of display names to game names
    display_to_game_names = {
        "Mario": "mario",
        "Luigi": "luigi", 
        "Peach": "peach", 
        "Bowser": "koopa", 
        "Yoshi": "yoshi", 
        "Rosalina & Luma": "rosetta", 
        "Bowser Jr.": "koopajr", 
        "Wario": "wario", 
        "Donkey Kong": "donkey", 
        "Diddy Kong": "diddy", 
        "Mr. Game & Watch": "gamewatch", 
        "Little Mac": "littlemac", 
        "Link": "link", 
        "Zelda": "zelda", 
        "Sheik": "sheik", 
        "Ganondorf": "ganon", 
        "Toon Link": "toonlink", 
        "Samus": "samus", 
        "Zero Suit Samus": "szerosuit", 
        "Pit": "pit", 
        "Palutena": "palutena", 
        "Marth": "marth", 
        "Ike": "ike", 
        "Robin": "reflet", 
        "Duck Hunt": "duckhunt", 
        "Kirby": "kirby", 
        "King Dedede": "dedede", 
        "Meta Knight": "metaknight", 
        "Fox": "fox", 
        "Falco": "falco", 
        "Pikachu": "pikachu", 
        "Charizard": "plizardon", 
        "Lucario": "lucario", 
        "Jigglypuff": "purin", 
        "Greninja": "gekkouga", 
        "R.O.B": "robot", 
        "Ness": "ness", 
        "Captain Falcon": "captain", 
        "Villager": "murabito", 
        "Olimar": "pikmin", 
        "Wii Fit Trainer": "wiifit", 
        "Shulk": "shulk", 
        "Dr. Mario": "mariod", 
        "Dark Pit": "pitb", 
        "Lucina": "lucina", 
        "PAC-MAN": "pacman", 
        "Mega Man": "rockman", 
        "Sonic": "sonic", 
        "Mewtwo": "mewtwo", 
        "Lucas": "lucas", 
        "Roy": "roy", 
        "Ryu": "ryu", 
        "Cloud": "cloud", 
        "Corrin": "kamui", 
        "Bayonetta": "bayonetta", 
        "Mii Swordfighter": "miiswordsman", 
        "Mii Brawler": "miifighter", 
        "Mii Gunner": "miigunner", 
        "Ice Climbers": "popo", 
        "Pichu": "pichu", 
        "Young Link": "younglink", 
        "Snake": "snake", 
        "Squirtle": "pzenigame", 
        "Ivysaur": "pfushigisou", 
        "Wolf": "wolf", 
        "Inkling": "inkling", 
        "Daisy": "daisy", 
        "Ridley": "ridley", 
        "Chrom": "chrom", 
        "Dark Samus": "samusd", 
        "Simon": "simon", 
        "Richter": "richter", 
        "King K. Rool": "krool", 
        "Isabelle": "shizue", 
        "Ken": "ken", 
        "Incineroar": "gaogaen", 
        "Piranha Plant": "packun", 
        "Joker": "jack", 
        "Hero": "brave", 
        "Banjo & Kazooie": "buddy", 
        "Terry": "dolly", 
        "Byleth": "master", 
        "Min Min": "tantan", 
        "Steve": "pickel", 
        "Sephiroth": "edge", 
        "Pyra": "eflame", 
        "Mythra": "elight", 
        "Kazuya": "demon", 
        "Sora": "trail"
    }
    
    # Create the mapping
    char_mapping = {}
    
    for display_name, game_name in display_to_game_names.items():
        char_mapping[display_name] = game_name
    
    # Add the character data from characterData.json
    char_data_path = Path.home() / "Documents" / "GitHub" / "ultimate-hitboxes" / "server" / "data" / "characterData.json"
    if char_data_path.exists():
        with open(char_data_path, 'r', encoding='utf-8') as f:
            char_data = json.load(f)
            for char in char_data:
                name = char["name"]
                value = char["value"]
                number = char["number"]
                # Add this information to our mapping
                for display_name in display_to_game_names.keys():
                    if display_name.lower() == name.lower() or display_name.lower().replace(' & ', '-') == value.lower():
                        game_name = display_to_game_names.get(display_name)
                        char_mapping[display_name] = {
                            "internal_name": game_name,
                            "game_name": game_name,  # Add game_name explicitly
                            "value": value,
                            "number": number,
                            "id": char["id"],
                            "series": char.get("series", ""),
                            "completed": char.get("completed", False),
                            "version": char.get("version", "")
                        }
                        break
    
    return char_mapping, display_to_game_names

def extract_character_data(char_mapping, display_to_game_names):
    """
    Extract character data from SSBU-Calculator/Data directory
    """
    # Define the path to the SSBU-Calculator Data directory
    calc_path = Path.home() / "Documents" / "GitHub" / "SSBU-Calculator" / "Data"
    
    # Check if path exists
    if not calc_path.exists():
        print(f"Error: SSBU-Calculator path '{calc_path}' not found.")
        print("Please provide the correct path to the SSBU-Calculator repository:")
        user_path = input("Path to repository: ")
        calc_path = Path(user_path) / "Data"
        if not calc_path.exists():
            print("Path still not found. Exiting.")
            sys.exit(1)
    
    # Directory should contain folders for each character
    char_dirs = [d for d in calc_path.iterdir() if d.is_dir()]
    print(f"Found {len(char_dirs)} character directories in SSBU-Calculator/Data")
    
    # Extract data from each character directory
    character_data = {}
    for char_dir in char_dirs:
        internal_name = char_dir.name
        
        # Find the display name that matches this internal name
        display_name = None
        for name, value in char_mapping.items():
            if isinstance(value, dict) and value.get("internal_name") == internal_name:
                display_name = name
                break
            elif value == internal_name:
                display_name = name
                break
        
        if not display_name:
            # Try to find a match in the display_to_game_names mapping
            for name, game_name in display_to_game_names.items():
                if game_name == internal_name:
                    display_name = name
                    break
        
        if not display_name:
            print(f"Warning: Could not find display name for internal name '{internal_name}'")
            display_name = internal_name  # Use internal name as fallback
        
        # Find data.json in the character directory
        data_file = char_dir / "data.json"
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    character_data[display_name] = {
                        "internal_name": internal_name,
                        "game_name": internal_name,  # Add game_name explicitly
                        "data": data
                    }
                    print(f"Loaded data for {display_name} ({internal_name})")
            except json.JSONDecodeError:
                print(f"Error: Could not parse JSON in {data_file}")
            except Exception as e:
                print(f"Error loading {data_file}: {e}")
        else:
            print(f"Warning: No data.json found for {display_name} ({internal_name})")
    
    return character_data

def save_output(char_mapping, character_data, display_to_game_names):
    """
    Save the extracted data and mapping to JSON files
    """
    # Create output directory
    output_path = Path.home() / "Documents" / "GitHub" / "SakurAI" / "extracted_data"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save character mapping
    mapping_file = output_path / "character_mapping.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(char_mapping, f, indent=2)
    print(f"Saved character mapping to {mapping_file}")
    
    # Save display_name to game_name mapping
    name_game_mapping_file = output_path / "display_to_game_names.json"
    with open(name_game_mapping_file, 'w', encoding='utf-8') as f:
        json.dump(display_to_game_names, f, indent=2)
    print(f"Saved display_name to game_name mapping to {name_game_mapping_file}")
    
    # Save character data
    data_file = output_path / "character_attributes.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(character_data, f, indent=2)
    print(f"Saved character attributes to {data_file}")

if __name__ == "__main__":
    print("Loading character mapping...")
    char_mapping, display_to_game_names = load_character_mapping()
    print(f"Mapped {len(char_mapping)} characters")
    print(f"Created display_name to game_name mapping with {len(display_to_game_names)} entries")
    
    print("\nExtracting character data from SSBU-Calculator...")
    character_data = extract_character_data(char_mapping, display_to_game_names)
    print(f"Extracted data for {len(character_data)} characters")
    
    print("\nSaving output files...")
    save_output(char_mapping, character_data, display_to_game_names)
    
    print("\nData extraction complete!")