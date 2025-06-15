// Exemple d'utilisation du CDN GeoJSON dans un plugin web

class BarrierDataCDN {
    constructor() {
        this.baseUrl = 'https://raw.githubusercontent.com/Gilles-Segura/carto-data-cdn/main';
        this.metadata = null;
        this.loadedData = new Map(); // Cache
    }
    
    /**
     * Initialise le CDN en chargeant les métadonnées
     */
    async initialize() {
        try {
            const response = await fetch(`${this.baseUrl}/metadata/catalog.json`);
            this.metadata = await response.json();
            console.log(`CDN initialized. Last updated: ${this.metadata.last_updated}`);
            return true;
        } catch (error) {
            console.error('Failed to initialize CDN:', error);
            return false;
        }
    }
    
    /**
     * Liste tous les fichiers disponibles d'une catégorie
     */
    listAvailableFiles(category) {
        if (!this.metadata) {
            throw new Error('CDN not initialized. Call initialize() first.');
        }
        
        if (!this.metadata.data_categories[category]) {
            throw new Error(`Invalid category: ${category}`);
        }
        
        return this.metadata.data_categories[category].files;
    }
    
    /**
     * Charge un fichier GeoJSON du CDN
     */
    async loadGeoJSON(filePath, useCompressed = true) {
        // Vérifier si déjà en cache
        if (this.loadedData.has(filePath)) {
            return this.loadedData.get(filePath);
        }
        
        // Construire le chemin complet
        let fullPath = `${this.baseUrl}/data/${filePath}`;
        if (useCompressed) {
            fullPath += '.gz';
        }
        
        try {
            const response = await fetch(fullPath);
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            let data;
            
            if (useCompressed) {
                // Pour les fichiers compressés, nous avons besoin de pako pour décompresser
                // <script src="https://cdn.jsdelivr.net/npm/pako@2.0.4/dist/pako.min.js"></script>
                const arrayBuffer = await response.arrayBuffer();
                const decompressed = pako.inflate(new Uint8Array(arrayBuffer), { to: 'string' });
                data = JSON.parse(decompressed);
            } else {
                data = await response.json();
            }
            
            // Mettre en cache
            this.loadedData.set(filePath, data);
            
            return data;
        } catch (error) {
            console.error(`Error loading ${filePath}:`, error);
            
            // Si on a essayé de charger un fichier compressé et ça a échoué,
            // essayer de charger la version non compressée
            if (useCompressed) {
                console.log('Falling back to uncompressed version...');
                return this.loadGeoJSON(filePath, false);
            }
            
            throw error;
        }
    }
    
    /**
     * Charge les données d'un pays
     */
    async loadCountry(countryCode) {
        const filePath = `countries/${countryCode.toLowerCase()}.geojson`;
        return this.loadGeoJSON(filePath);
    }
    
    /**
     * Charge les données d'un type de barrière
     */
    async loadBarrierType(typeName) {
        const filePath = `types/${typeName.toLowerCase()}.geojson`;
        return this.loadGeoJSON(filePath);
    }
    
    /**
     * Charge les données d'une région
     */
    async loadRegion(regionName) {
        const filePath = `regions/${regionName.toLowerCase()}.geojson`;
        return this.loadGeoJSON(filePath);
    }
    
    /**
     * Vide le cache
     */
    clearCache() {
        this.loadedData.clear();
        console.log('Cache cleared');
    }
}

// Exemple d'utilisation
async function initMap() {
    // Initialiser la carte Leaflet
    const map = L.map('map').setView([48.8566, 2.3522], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    
    // Initialiser le client CDN
    const cdn = new BarrierDataCDN();
    await cdn.initialize();
    
    // Afficher les données disponibles
    console.log('Available countries:', cdn.listAvailableFiles('countries'));
    console.log('Available barrier types:', cdn.listAvailableFiles('types'));
    
    // Charger et afficher les données pour la France
    try {
        const franceData = await cdn.loadCountry('france');
        console.log(`Loaded ${franceData.features.length} barriers for France`);
        
        // Ajouter à la carte
        L.geoJSON(franceData, {
            pointToLayer: (feature, latlng) => {
                return L.circleMarker(latlng, {
                    radius: 5,
                    fillColor: '#3388ff',
                    color: '#000',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
            },
            onEachFeature: (feature, layer) => {
                // Popup avec les propriétés
                const props = feature.properties;
                let popupContent = '';
                
                for (const key in props) {
                    popupContent += `<b>${key}:</b> ${props[key]}<br>`;
                }
                
                layer.bindPopup(popupContent);
            }
        }).addTo(map);
        
    } catch (error) {
        console.error('Failed to load France data:', error);
    }
}