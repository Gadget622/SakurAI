import os
import json
import sys
from pathlib import Path

def load_character_mapping():
    """
    Create a mapping between character display names and internal names
    """
    # From the JS codebase
    display_names = ["Mario", "Luigi", "Peach", "Bowser", "Yoshi", "Rosalina & Luma", "Bowser Jr.", "Wario", 
                    "Donkey Kong", "Diddy Kong", "Mr. Game & Watch", "Little Mac", "Link", "Zelda", "Sheik", 
                    "Ganondorf", "Toon Link", "Samus", "Zero Suit Samus", "Pit", "Palutena", "Marth", "Ike", 
                    "Robin", "Duck Hunt", "Kirby", "King Dedede", "Meta Knight", "Fox", "Falco", "Pikachu", 
                    "Charizard", "Lucario", "Jigglypuff", "Greninja", "R.O.B", "Ness", "Captain Falcon", 
                    "Villager", "Olimar", "Wii Fit Trainer", "Shulk", "Dr. Mario", "Dark Pit", "Lucina", 
                    "PAC-MAN", "Mega Man", "Sonic", "Mewtwo", "Lucas", "Roy", "Ryu", "Cloud", "Corrin", 
                    "Bayonetta", "Mii Swordfighter", "Mii Brawler", "Mii Gunner", "Ice Climbers", "Pichu", 
                    "Young Link", "Snake", "Squirtle", "Ivysaur", "Wolf", "Inkling", "Daisy", "Ridley", 
                    "Chrom", "Dark Samus", "Simon", "Richter", "King K. Rool", "Isabelle", "Ken", 
                    "Incineroar", "Piranha Plant", "Joker", "Hero", "Banjo & Kazooie", "Terry", "Byleth", 
                    "Min Min", "Steve", "Sephiroth", "Pyra", "Mythra", "Kazuya", "Sora"]
    
    game_names = ["mario", "luigi", "peach", "koopa", "yoshi", "rosetta", "koopajr", "wario", "donkey", 
                 "diddy", "gamewatch", "littlemac", "link", "zelda", "sheik", "ganon", "toonlink", "samus", 
                 "szerosuit", "pit", "palutena", "marth", "ike", "reflet", "duckhunt", "kirby", "dedede", 
                 "metaknight", "fox", "falco", "pikachu", "plizardon", "lucario", "purin", "gekkouga", "robot", 
                 "ness", "captain", "murabito", "pikmin", "wiifit", "shulk", "mariod", "pitb", "lucina", 
                 "pacman", "rockman", "sonic", "mewtwo", "lucas", "roy", "ryu", "cloud", "kamui", "bayonetta", 
                 "miiswordsman", "miifighter", "miigunner", "popo", "pichu", "younglink", "snake", "pzenigame", 
                 "pfushigisou", "wolf", "inkling", "daisy", "ridley", "chrom", "samusd", "simon", "richter", 
                 "krool", "shizue", "ken", "gaogaen", "packun", "jack", "brave", "buddy", "dolly", "master", 
                 "tantan", "pickel", "edge", "eflame", "elight", "demon", "trail"]
    
    # Create the mapping
    char_mapping = {}
    for i in range(len(display_names)):
        if i < len(game_names):
            char_mapping[display_names[i]] = game_names[i]
    
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
                for display_name in display_names:
                    if display_name.lower() == name.lower() or display_name.lower().replace(' & ', '-') == value.lower():
                        char_mapping[display_name] = {
                            "internal_name": next((game_names[i] for i, dn in enumerate(display_names) if dn == display_name), None),
                            "value": value,
                            "number": number,
                            "id": char["id"],
                            "series": char.get("series", ""),
                            "completed": char.get("completed", False),
                            "version": char.get("version", "")
                        }
                        break
    
    return char_mapping

def extract_character_data(char_mapping):
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
            if isinstance(value, dict) and value["internal_name"] == internal_name:
                display_name = name
                break
            elif value == internal_name:
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

def save_output(char_mapping, character_data):
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
    
    # Save character data
    data_file = output_path / "character_attributes.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(character_data, f, indent=2)
    print(f"Saved character attributes to {data_file}")

if __name__ == "__main__":
    print("Loading character mapping...")
    char_mapping = load_character_mapping()
    print(f"Mapped {len(char_mapping)} characters")
    
    print("\nExtracting character data from SSBU-Calculator...")
    character_data = extract_character_data(char_mapping)
    print(f"Extracted data for {len(character_data)} characters")
    
    print("\nSaving output files...")
    save_output(char_mapping, character_data)
    
    print("\nData extraction complete!")