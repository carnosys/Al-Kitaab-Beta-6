import json
import os

def generate_script_files():
    # Load the base Arabic Quran for structure
    with open('quran.json', 'r', encoding='utf-8') as f:
        quran = json.load(f)
    
    # Initialize Indopak and Tajweed structures
    indopak = {"quran": {}}
    tajweed = {"quran": {}}
    
    # Generate Indopak and Tajweed data
    verse_id = 1
    for surah in quran:
        for verse in surah["verses"]:
            # Create Indopak entry
            indopak["quran"][str(verse_id)] = {
                "surah": surah["id"],
                "ayah": verse["id"],
                "text": verse["text"]  # Using Arabic text as placeholder
            }
            
            # Create Tajweed entry
            tajweed["quran"][str(verse_id)] = {
                "surah": surah["id"],
                "ayah": verse["id"],
                "text": verse["text"]  # Using Arabic text as placeholder
            }
            
            verse_id += 1
    
    # Save Indopak file
    with open('indopak.json', 'w', encoding='utf-8') as f:
        json.dump(indopak, f, ensure_ascii=False, indent=2)
    
    # Save Tajweed file
    with open('tajweed.json', 'w', encoding='utf-8') as f:
        json.dump(tajweed, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generate_script_files() 