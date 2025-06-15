import pyodbc
import geojson
import gzip
import json
import decimal
from decimal import Decimal
import os

# 1. Connexion SQL Server
conn_str = (
    r'DRIVER={SQL Server};'  
    r'SERVER=.;'   
    r'DATABASE=AMBER_202412_website;'   
    r'Trusted_Connection=yes;'
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Définir l'encodeur personnalisé pour les objets Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# 2. Obtenir la liste de toutes les tables de la base de données
cursor.execute("""
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG = 'AMBER_202412_website'
""")

tables = [row[0] for row in cursor.fetchall()]
print(f"Nombre de tables trouvées: {len(tables)}")

# Créer le dossier "data" pour stocker les fichiers GeoJSON si nécessaire
output_dir = "data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Dossier '{output_dir}' créé.")

# 3. Boucler sur chaque table
for table_name in tables:
    print(f"Traitement de la table: {table_name}")
    
    # Vérifier si la table a des colonnes lat/lon
    cursor.execute(f"""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
    """)
    
    columns = [row[0] for row in cursor.fetchall()]
    
    # Identifier les colonnes potentielles de latitude et longitude
    lat_columns = [col for col in columns if col.lower() in ('latitude', 'lat', 'y')]
    lon_columns = [col for col in columns if col.lower() in ('longitude', 'long', 'lon', 'lng', 'x')]
    
    # Vérifier si la table a des colonnes lat/lon
    if not (lat_columns and lon_columns):
        print(f"  La table {table_name} ne semble pas contenir de coordonnées géographiques. Ignorée.")
        continue
    
    # Utiliser les premières colonnes identifiées
    lat_col = lat_columns[0]
    lon_col = lon_columns[0]
    
    # Identifier une colonne ID potentielle
    id_columns = [col for col in columns if col.lower() in ('id', f'{table_name.lower()}_id', 'object_id', 'objectid')]
    id_col = id_columns[0] if id_columns else columns[0]  # Utiliser la première colonne si aucun ID n'est trouvé
    
    # Construire la liste des autres colonnes pour les propriétés
    property_columns = [col for col in columns if col not in (lat_col, lon_col)]
    
    # Construire la requête dynamiquement
    cols_str = ", ".join([f"[{col}]" for col in columns])
    
    try:
        cursor.execute(f"""
            SELECT {cols_str}
            FROM [{table_name}]
            WHERE [{lat_col}] IS NOT NULL 
            AND [{lon_col}] IS NOT NULL
            AND [{lat_col}] BETWEEN -90 AND 90
            AND [{lon_col}] BETWEEN -180 AND 180
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print(f"  Aucune donnée géographique valide trouvée dans la table {table_name}. Ignorée.")
            continue
            
        print(f"  {len(rows)} enregistrements trouvés avec coordonnées valides.")
        
        features = []
        
        # Construire les features GeoJSON
        for row in rows:
            # Créer un dictionnaire des valeurs de colonnes
            row_dict = {columns[i]: row[i] for i in range(len(columns))}
            
            # Extraire les coordonnées
            try:
                lat = float(row_dict[lat_col])
                lon = float(row_dict[lon_col])
                
                # Vérifier que les coordonnées sont valides
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    continue
                
                # Créer le point GeoJSON
                point = geojson.Point((lon, lat))  # longitude, latitude
                
                # Préparer les propriétés (toutes les colonnes sauf lat/lon)
                properties = {}
                for col in property_columns:
                    value = row_dict[col]
                    # Conversion des types non sérialisables
                    if isinstance(value, Decimal):
                        properties[col] = float(value)
                    elif value is None:
                        properties[col] = None
                    else:
                        properties[col] = str(value)
                
                # Créer la feature
                feature = geojson.Feature(geometry=point, properties=properties)
                features.append(feature)
                
            except (ValueError, TypeError):
                # Ignorer les lignes avec des coordonnées non convertibles
                continue
        
        # Créer la FeatureCollection si des features ont été créées
        if features:
            feature_collection = {
                "type": "FeatureCollection",
                "features": features
            }
            
            # Créer les fichiers de sortie dans le dossier "data"
            output_file = os.path.join(output_dir, f"{table_name}.geojson")
            compressed_file = os.path.join(output_dir, f"{table_name}.geojson.gz")
            
            # Écrire dans un fichier GeoJSON non compressé
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(feature_collection, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)
            
            # Écrire le même fichier compressé en gzip
            with gzip.open(compressed_file, "wt", encoding="utf-8") as f:
                json.dump(feature_collection, f, ensure_ascii=False, cls=DecimalEncoder)
                
            print(f"  Fichiers créés dans le dossier 'data': {table_name}.geojson et {table_name}.geojson.gz")
        else:
            print(f"  Aucune feature valide n'a pu être créée pour {table_name}.")
            
    except Exception as e:
        print(f"  Erreur lors du traitement de la table {table_name}: {str(e)}")
        continue

print("Export GeoJSON et compression terminés pour toutes les tables dans le dossier 'data'.")
