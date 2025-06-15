import os
import json
import shutil
import argparse
from datetime import datetime

def add_geojson_to_cdn(source_file, category, name):
    """
    Ajoute un fichier GeoJSON au CDN
    
    Args:
        source_file: Chemin vers le fichier GeoJSON source
        category: Catégorie (types, countries, regions)
        name: Nom à donner au fichier (sans extension)
    """
    # Vérifier que la catégorie est valide
    valid_categories = ['types', 'countries', 'regions']
    if category not in valid_categories:
        raise ValueError(f"Catégorie invalide. Doit être l'une de : {valid_categories}")
    
    # Vérifier que le fichier source existe
    if not os.path.isfile(source_file):
        raise FileNotFoundError(f"Le fichier source {source_file} n'existe pas")
    
    # Construire le chemin de destination
    dest_dir = f"data/{category}"
    os.makedirs(dest_dir, exist_ok=True)
    
    dest_file = f"{dest_dir}/{name.lower()}.geojson"
    
    # Copier le fichier
    shutil.copy2(source_file, dest_file)
    print(f"Fichier copié : {dest_file}")
    
    # Mettre à jour le catalogue
    update_catalog(dest_file)
    
    return dest_file

def update_catalog(file_path):
    """Met à jour le catalogue avec le nouveau fichier"""
    catalog_path = "metadata/catalog.json"
    
    # Lire le catalogue existant
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    # Déterminer la catégorie
    if '/types/' in file_path:
        category = 'types'
    elif '/countries/' in file_path:
        category = 'countries'
    elif '/regions/' in file_path:
        category = 'regions'
    else:
        category = None
    
    # Ajouter le fichier au catalogue
    if category:
        # Retirer le préfixe "data/" pour le stockage dans le catalogue
        relative_path = file_path
        if relative_path.startswith('data/'):
            relative_path = relative_path[5:]
        
        # Vérifier si le fichier existe déjà
        if relative_path not in catalog['data_categories'][category]['files']:
            catalog['data_categories'][category]['files'].append(relative_path)
    
    # Mettre à jour la date
    catalog['last_updated'] = datetime.now().isoformat()
    
    # Sauvegarder le catalogue
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)
    
    print(f"Catalogue mis à jour avec {file_path}")

def main():
    parser = argparse.ArgumentParser(description='Ajouter un fichier GeoJSON au CDN')
    parser.add_argument('source', help='Chemin vers le fichier GeoJSON source')
    parser.add_argument('--category', '-c', required=True, 
                        choices=['types', 'countries', 'regions'],
                        help='Catégorie du fichier')
    parser.add_argument('--name', '-n', required=True,
                        help='Nom à donner au fichier (sans extension)')
    
    args = parser.parse_args()
    
    try:
        dest_file = add_geojson_to_cdn(args.source, args.category, args.name)
        print(f"Fichier ajouté avec succès : {dest_file}")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    main()