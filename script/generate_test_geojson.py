import json
import random
import os

def generate_test_geojson(filename, feature_count=100, region=None):
    """
    Génère un fichier GeoJSON de test avec des points aléatoires
    
    Args:
        filename: Nom du fichier à créer
        feature_count: Nombre de features à générer
        region: Tuple (min_lon, min_lat, max_lon, max_lat) pour limiter les coordonnées
    """
    # Définir la région par défaut (Europe)
    if region is None:
        region = (-10, 35, 30, 70)  # min_lon, min_lat, max_lon, max_lat
    
    min_lon, min_lat, max_lon, max_lat = region
    
    # Générer des features aléatoires
    features = []
    for i in range(feature_count):
        # Coordonnées aléatoires dans la région
        lon = random.uniform(min_lon, max_lon)
        lat = random.uniform(min_lat, max_lat)
        
        # Propriétés de test
        properties = {
            "id": f"test-{i}",
            "name": f"Test Point {i}",
            "value": random.randint(1, 100)
        }
        
        # Créer la feature
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": properties
        }
        
        features.append(feature)
    
    # Créer la collection de features
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Créer le répertoire parent si nécessaire
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Sauvegarder le fichier
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(geojson, f)
    
    print(f"Fichier GeoJSON de test créé : {filename} avec {feature_count} features")
    
    return filename

def update_catalog(new_file):
    """Met à jour le catalogue avec le nouveau fichier"""
    catalog_path = "metadata/catalog.json"
    
    # Lire le catalogue existant
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    # Déterminer la catégorie
    if '/types/' in new_file:
        category = 'types'
    elif '/countries/' in new_file:
        category = 'countries'
    elif '/regions/' in new_file:
        category = 'regions'
    else:
        category = None
    
    # Ajouter le fichier au catalogue
    if category:
        # Retirer le préfixe "data/" pour le stockage dans le catalogue
        file_path = new_file
        if file_path.startswith('data/'):
            file_path = file_path[5:]
        
        # Vérifier si le fichier existe déjà
        if file_path not in catalog['data_categories'][category]['files']:
            catalog['data_categories'][category]['files'].append(file_path)
    
    # Mettre à jour la date
    catalog['last_updated'] = datetime.now().isoformat()
    
    # Sauvegarder le catalogue
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)
    
    print(f"Catalogue mis à jour avec {new_file}")

def generate_sample_files():
    """Génère quelques fichiers GeoJSON d'exemple"""
    from datetime import datetime
    
    # Générer un exemple par pays
    countries = [
        ('france', (-5, 42, 8, 51)),  # France
        ('spain', (-9, 36, 3, 44)),   # Espagne
        ('germany', (5, 47, 15, 55))  # Allemagne
    ]
    
    for country, region in countries:
        filename = f"data/countries/{country}.geojson"
        generate_test_geojson(filename, feature_count=200, region=region)
        update_catalog(filename)
    
    # Générer un exemple par type
    barrier_types = ['dam', 'weir', 'sluice', 'lock']
    
    for barrier_type in barrier_types:
        filename = f"data/types/{barrier_type}.geojson"
        generate_test_geojson(filename, feature_count=150)
        update_catalog(filename)
    
    # Générer un exemple par région
    regions = [
        ('europe', (-10, 35, 30, 70)),
        ('mediterranean', (-5, 30, 40, 45))
    ]
    
    for region_name, bounds in regions:
        filename = f"data/regions/{region_name}.geojson"
        generate_test_geojson(filename, feature_count=300, region=bounds)
        update_catalog(filename)
    
    print("Génération des fichiers d'exemple terminée!")

if __name__ == "__main__":
    generate_sample_files()