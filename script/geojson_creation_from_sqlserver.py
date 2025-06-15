import pyodbc
import geojson
import gzip
import json
import decimal
from decimal import Decimal

# 1. Connexion SQL Server (modifie selon ton serveur)
conn_str = (
    r'DRIVER={SQL Server};'  
    r'SERVER=.;'   
    r'DATABASE=AMBER_202412_website;'   
    r'Trusted_Connection=yes;'  # Pour l'authentification Windows
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# 2. Requête pour récupérer les points
cursor.execute("""
    SELECT id, latitude, longitude, LabelAtlas, country
    FROM atlas
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL
""")

features = []

# 3. Construire les features GeoJSON
for row in cursor.fetchall():
    id_, lat, lon, typ, country = row
    point = geojson.Point((lon, lat))  # longitude, latitude
    properties = {
        "id": id_,
        "type": typ,
        "country": country
    }
    feature = geojson.Feature(geometry=point, properties=properties)
    features.append(feature)

# 4. Créer la FeatureCollection
feature_collection = {
    "type": "FeatureCollection",
    "features": features
}

# 5. Écrire dans un fichier GeoJSON non compressé
output_file = "atlas.geojson"
with open(output_file, 'w', encoding='utf-8') as f:
    # Option 1: Utiliser default
    json.dump(feature_collection, f, ensure_ascii=False, indent=2, 
              default=lambda o: float(o) if isinstance(o, Decimal) else str(o))
    
    # OU Option 2: Utiliser un encodeur personnalisé
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return super(DecimalEncoder, self).default(obj)
    json.dump(feature_collection, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)

# 6. Écrire le même fichier compressé en gzip
with gzip.open("atlas.geojson.gz", "wt", encoding="utf-8") as f:
    geojson.dump(feature_collection, f, ensure_ascii=False, cls=DecimalEncoder)

print("Export GeoJSON et compression terminés.")
