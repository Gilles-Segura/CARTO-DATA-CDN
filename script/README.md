# Barriers Data CDN

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

=> under modification