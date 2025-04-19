import json
import sqlite3
import os
import requests
from pathlib import Path

# Create a SQLite database
conn = sqlite3.connect('incineroar_frame_data.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS characters (
    character_id INTEGER PRIMARY KEY,
    internal_name TEXT,
    display_name TEXT,
    walk_speed REAL,
    run_speed REAL,
    dash_speed REAL,
    air_speed REAL,
    gravity REAL,
    fall_speed REAL,
    fast_fall_speed REAL,
    weight REAL,
    jump_squat INTEGER,
    air_jumps INTEGER,
    shield_size REAL,
    nair_landing_lag INTEGER,
    fair_landing_lag INTEGER,
    bair_landing_lag INTEGER,
    uair_landing_lag INTEGER,
    dair_landing_lag INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS moves (
    move_id INTEGER PRIMARY KEY,
    character_id INTEGER,
    name TEXT,
    move_type TEXT,
    faf INTEGER,
    landing_lag INTEGER,
    auto_cancel_before INTEGER,
    auto_cancel_after INTEGER,
    is_smash BOOLEAN,
    is_aerial BOOLEAN,
    is_special BOOLEAN,
    FOREIGN KEY (character_id) REFERENCES characters (character_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS hitboxes (
    hitbox_id INTEGER PRIMARY KEY,
    move_id INTEGER,
    hitbox_number INTEGER,
    damage REAL,
    angle INTEGER,
    bkb INTEGER,
    kbg INTEGER,
    wbkb INTEGER,
    start_frame INTEGER,
    end_frame INTEGER,
    size REAL,
    x_pos REAL,
    y_pos REAL,
    z_pos REAL,
    hitlag_mult REAL,
    sdi_mult REAL,
    shield_damage REAL,
    FOREIGN KEY (move_id) REFERENCES moves (move_id)
)
''')

# Add dodge data table for completeness
cursor.execute('''
CREATE TABLE IF NOT EXISTS dodge_data (
    character_id INTEGER PRIMARY KEY,
    spotdodge_intangibility_start INTEGER,
    spotdodge_intangibility_duration INTEGER,
    spotdodge_faf INTEGER,
    forward_roll_intangibility_start INTEGER,
    forward_roll_intangibility_duration INTEGER,
    forward_roll_faf INTEGER,
    back_roll_intangibility_start INTEGER,
    back_roll_intangibility_duration INTEGER,
    back_roll_faf INTEGER,
    airdodge_intangibility_start INTEGER,
    airdodge_intangibility_duration INTEGER,
    airdodge_faf INTEGER,
    dir_airdodge_intangibility_start INTEGER,
    dir_airdodge_intangibility_duration INTEGER,
    dir_airdodge_faf_sideways INTEGER,
    FOREIGN KEY (character_id) REFERENCES characters (character_id)
)
''')

# Function to insert character parameters
def insert_character_params(data):
    cursor.execute('''
    INSERT INTO characters (
        internal_name, display_name, walk_speed, run_speed, dash_speed, 
        air_speed, gravity, fall_speed, fast_fall_speed, weight, 
        jump_squat, air_jumps, shield_size, nair_landing_lag, fair_landing_lag,
        bair_landing_lag, uair_landing_lag, dair_landing_lag
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['InternalName'],
        "Incineroar",
        data['Params']['WalkSpeed'],
        data['Params']['RunSpeed'],
        data['Params']['DashInitialSpeed'],
        data['Params']['AirSpeed'],
        data['Params']['Gravity'],
        data['Params']['FallSpeed'],
        data['Params']['FastFallSpeed'],
        data['Params']['Weight'],
        data['Params']['Jumpsquat'],
        data['Params']['JumpCount'],
        data['Params']['ShieldSize'],
        data['Params']['NairLandingLag'],
        data['Params']['FairLandingLag'],
        data['Params']['BairLandingLag'],
        data['Params']['UairLandingLag'],
        data['Params']['DairLandingLag']
    ))
    
    return cursor.lastrowid

# Function to insert dodge data
def insert_dodge_data(character_id, dodge_data):
    cursor.execute('''
    INSERT INTO dodge_data (
        character_id, spotdodge_intangibility_start, spotdodge_intangibility_duration,
        spotdodge_faf, forward_roll_intangibility_start, forward_roll_intangibility_duration,
        forward_roll_faf, back_roll_intangibility_start, back_roll_intangibility_duration,
        back_roll_faf, airdodge_intangibility_start, airdodge_intangibility_duration,
        airdodge_faf, dir_airdodge_intangibility_start, dir_airdodge_intangibility_duration,
        dir_airdodge_faf_sideways
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        character_id,
        dodge_data['SpotdodgeIntangibilityStart'],
        dodge_data['SpotdodgeIntangibilityDuration'],
        dodge_data['SpotdodgeFAF'],
        dodge_data['ForwardRollIntangibilityStart'],
        dodge_data['ForwardRollIntangibilityDuration'],
        dodge_data['ForwardRollFAF'],
        dodge_data['BackRollIntangibilityStart'],
        dodge_data['BackRollIntangibilityDuration'],
        dodge_data['BackRollFAF'],
        dodge_data['AirdodgeIntangibilityStart'],
        dodge_data['AirdodgeIntangibilityDuration'],
        dodge_data['AirdodgeFAF'],
        dodge_data['DirectionalAirdodgeIntangibilityStart'],
        dodge_data['DirectionalAirdodgeIntangibilityDuration'],
        dodge_data['DirectionalAirdodgeSidewaysFAF']
    ))

# Function to fetch and insert move data
def fetch_and_insert_move_data(character_id):
    # Based on the codebase, move data might be in a file like:
    # ./Data/ulthitboxes/69_incineroar.json
    # Let's try to fetch this file
    
    # Try local first
    move_data = None
    local_paths = [
        "../SSBU-Calculator/Data/ulthitboxes/69_incineroar.json",
        "../SSBU-Calculator/Data/69_incineroar.json",
        "../SSBU-Calculator/js/Data/ulthitboxes/69_incineroar.json"
    ]
    
    for path in local_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                move_data = json.load(f)
                print(f"Found move data at {path}")
                break
    
    # If not found locally, try fetching from a potential remote URL
    if move_data is None:
        try:
            # This URL is a guess based on the code patterns
            url = "https://raw.githubusercontent.com/RSN-Bran/ultimate-hitboxes/master/server/data/69_incineroar.json"
            response = requests.get(url)
            if response.status_code == 200:
                move_data = response.json()
                print(f"Fetched move data from {url}")
        except Exception as e:
            print(f"Failed to fetch remote move data: {e}")
    
    if move_data is None:
        print("Could not find move data. Creating placeholder entry for future import.")
        # Create a placeholder move entry for manual addition later
        cursor.execute('''
        INSERT INTO moves (character_id, name, move_type, is_smash, is_aerial, is_special)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (character_id, "PLACEHOLDER - ADD MOVES MANUALLY", "unknown", 0, 0, 0))
        return
    
    # If we have move data, process and insert it
    move_count = 0
    hitbox_count = 0
    
    # The structure depends on the actual format of the move data
    # This assumes a structure similar to what's seen in the code
    for move in move_data.get('moves', []):
        cursor.execute('''
        INSERT INTO moves (
            character_id, name, move_type, faf, landing_lag, 
            is_smash, is_aerial, is_special
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            character_id,
            move.get('name', 'Unknown Move'),
            determine_move_type(move.get('name', '')),
            move.get('faf', 0),
            move.get('landing_lag', 0),
            1 if 'smash' in move.get('name', '').lower() else 0,
            1 if any(aerial in move.get('name', '').lower() for aerial in ['nair', 'fair', 'bair', 'uair', 'dair']) else 0,
            1 if determine_move_type(move.get('name', '')) == 'special' else 0
        ))
        
        move_id = cursor.lastrowid
        move_count += 1
        
        # Process hitboxes if available
        for i, hitbox in enumerate(move.get('hitboxes', [])):
            if 'damage' in hitbox:
                cursor.execute('''
                INSERT INTO hitboxes (
                    move_id, hitbox_number, damage, angle, bkb, kbg,
                    start_frame, end_frame
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    move_id,
                    i + 1,
                    hitbox.get('damage', 0),
                    hitbox.get('angle', 0),
                    hitbox.get('bkb', 0),
                    hitbox.get('kbg', 0),
                    hitbox.get('frames', [0])[0] if len(hitbox.get('frames', [])) > 0 else 0,
                    hitbox.get('frames', [0])[-1] if len(hitbox.get('frames', [])) > 0 else 0
                ))
                hitbox_count += 1
    
    print(f"Inserted {move_count} moves and {hitbox_count} hitboxes")

# Helper function to determine move type
def determine_move_type(move_name):
    move_name = move_name.lower()
    if any(smash in move_name for smash in ['fsmash', 'usmash', 'dsmash']):
        return 'smash'
    elif any(tilt in move_name for tilt in ['ftilt', 'utilt', 'dtilt']):
        return 'tilt'
    elif any(aerial in move_name for aerial in ['nair', 'fair', 'bair', 'uair', 'dair']):
        return 'aerial'
    elif 'jab' in move_name:
        return 'jab'
    elif any(throw in move_name for throw in ['fthrow', 'bthrow', 'uthrow', 'dthrow']):
        return 'throw'
    elif 'dash attack' in move_name:
        return 'dash'
    elif any(grab in move_name for grab in ['grab']):
        return 'grab'
    elif 'special' in move_name or any(spec in move_name for spec in ['neutral b', 'side b', 'up b', 'down b']):
        return 'special'
    return 'unknown'

# Main function to run the database creation and data import
def main():
    try:
        # Check if data.json exists
        data_file = '../SSBU-Calculator/Data/gaogaen/data.json'
        if not os.path.exists(data_file):
            print(f"Error: {data_file} not found")
            return
        
        # Load character parameters
        with open(data_file, 'r') as f:
            incineroar_data = json.load(f)
        
        # Insert character data
        character_id = insert_character_params(incineroar_data)
        print(f"Inserted Incineroar's parameters with ID: {character_id}")
        
        # Insert dodge data if available
        if 'DodgeData' in incineroar_data:
            insert_dodge_data(character_id, incineroar_data['DodgeData'])
            print("Inserted dodge data")
        
        # Try to fetch and insert move data
        fetch_and_insert_move_data(character_id)
        
        # Commit changes
        conn.commit()
        print("Database successfully created and populated with available data")
        
        # Print instructions for manually adding move data if needed
        print("\nIf move data could not be found automatically, you can add it manually:")
        print("1. Find move data from UltimateFrameData or similar sources")
        print("2. Use the database's move and hitbox tables to add the data")
        print("3. Or use the database's import functionality with CSV/JSON data")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()