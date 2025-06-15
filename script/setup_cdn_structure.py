import os
import json
from datetime import datetime

def create_directory_structure():
    """Crée la structure de répertoires de base pour le CDN"""
    
    # Définir les répertoires à créer
    directories = [
        "data/types",
        "data/countries",
        "data/regions",
        "metadata",
        "scripts"
    ]
    
    # Créer chaque répertoire
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Répertoire créé : {directory}")
    
    # Créer un fichier catalog.json initial
    catalog = {
        "name": "Barrier Data CDN",
        "description": "Content Delivery Network for river barrier data",
        "last_updated": datetime.now().isoformat(),
        "data_categories": {
            "types": {
                "description": "Barrier data organized by type",
                "files": []
            },
            "countries": {
                "description": "Barrier data organized by country",
                "files": []
            },
            "regions": {
                "description": "Barrier data organized by geographical region",
                "files": []
            }
        }
    }
    
    # Sauvegarder le catalogue
    with open("metadata/catalog.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)
    
    # Créer un README.md initial
    readme_content = """# Barriers Data CDN

A Content Delivery Network for river barrier data in GeoJSON format.

## Structure

- `data/` - Contains all GeoJSON files
  - `types/` - Barriers organized by type
  - `countries/` - Barriers organized by country
  - `regions/` - Barriers organized by geographical region
- `metadata/` - Contains information about available data

## Usage

To use this CDN in your web application:

```javascript
// Example: Load data for a specific country
async function loadCountryData(countryCode) {
  const response = await fetch(`https://raw.githubusercontent.com/Gilles-Segura/carto-data-cdn/main/data/countries/${countryCode.toLowerCase()}.geojson`);
  return await response.json();
}
```

## Available Files

Check the `metadata/catalog.json` file for a complete list of available files.
"""
    
    # Sauvegarder le README
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("Structure de base du CDN créée avec succès!")

if __name__ == "__main__":
    create_directory_structure()