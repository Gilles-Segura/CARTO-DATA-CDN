import os
import json
import gzip
import glob
import argparse

def compress_geojson_file(file_path, delete_original=False):
    """
    Compresse un fichier GeoJSON en gzip
    
    Args:
        file_path: Chemin vers le fichier GeoJSON
        delete_original: Supprimer le fichier original après compression
    
    Returns:
        Chemin vers le fichier compressé
    """
    # Vérifier que le fichier existe
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
    
    # Construire le chemin de destination
    compressed_path = f"{file_path}.gz"
    
    # Lire le fichier JSON
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Compresser et sauvegarder
    with gzip.open(compressed_path, 'wt', encoding='utf-8') as f:
        json.dump(data, f)
    
    # Obtenir les tailles des fichiers
    original_size = os.path.getsize(file_path)
    compressed_size = os.path.getsize(compressed_path)
    reduction = (1 - compressed_size / original_size) * 100
    
    print(f"Fichier compressé : {compressed_path}")
    print(f"  Taille originale : {original_size / 1024:.1f} KB")
    print(f"  Taille compressée : {compressed_size / 1024:.1f} KB")
    print(f"  Réduction : {reduction:.1f}%")
    
    # Supprimer l'original si demandé
    if delete_original:
        os.remove(file_path)
        print(f"Fichier original supprimé : {file_path}")
    
    return compressed_path

def compress_all_geojson(directory=None, delete_originals=False):
    """Compresse tous les fichiers GeoJSON dans un répertoire"""
    # Si aucun répertoire n'est spécifié, utiliser le répertoire data
    if directory is None:
        directory = "data"
    
    # Trouver tous les fichiers GeoJSON
    geojson_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.geojson') and not file.endswith('.geojson.gz'):
                geojson_files.append(os.path.join(root, file))
    
    print(f"Trouvé {len(geojson_files)} fichiers GeoJSON à compresser")
    
    # Compresser chaque fichier
    compressed_files = []
    for file_path in geojson_files:
        try:
            compressed_path = compress_geojson_file(file_path, delete_originals)
            compressed_files.append(compressed_path)
        except Exception as e:
            print(f"Erreur lors de la compression de {file_path}: {e}")
    
    print(f"Compression terminée. {len(compressed_files)} fichiers compressés.")
    
    return compressed_files

def main():
    parser = argparse.ArgumentParser(description='Compresser des fichiers GeoJSON')
    parser.add_argument('--file', '-f', help='Chemin vers un fichier GeoJSON spécifique')
    parser.add_argument('--directory', '-d', help='Répertoire contenant les fichiers GeoJSON')
    parser.add_argument('--delete', '-x', action='store_true', 
                        help='Supprimer les fichiers originaux après compression')
    
    args = parser.parse_args()
    
    try:
        if args.file:
            compress_geojson_file(args.file, args.delete)
        else:
            compress_all_geojson(args.directory, args.delete)
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    main()