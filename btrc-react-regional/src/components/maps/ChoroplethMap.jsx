/**
 * Choropleth Map Component using Leaflet
 * Displays geographic data with color-coded regions
 */

import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { getColorForValue } from '../../utils/dataTransform';

// Fix for default marker icons in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

/**
 * Component to fit map bounds
 */
const FitBounds = ({ geojson }) => {
  const map = useMap();

  useEffect(() => {
    if (geojson && geojson.features) {
      const geoJsonLayer = L.geoJSON(geojson);
      const bounds = geoJsonLayer.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [20, 20] });
      }
    }
  }, [geojson, map]);

  return null;
};

/**
 * Choropleth Map Component
 * @param {object} geojson - GeoJSON feature collection with properties.value
 * @param {string} title - Map title
 * @param {function} onRegionClick - Callback when region is clicked (feature) => {}
 * @param {object} colorScale - Color scale configuration
 */
const ChoroplethMap = ({
  geojson,
  title = 'Regional Analysis',
  onRegionClick,
  colorScale = { min: 0, max: 100, thresholds: { low: 30, medium: 60 } },
  height = '500px',
}) => {
  const [mapKey, setMapKey] = useState(0);

  // Reload map when geojson changes
  useEffect(() => {
    setMapKey((prev) => prev + 1);
  }, [geojson]);

  // Style function for GeoJSON features
  const style = (feature) => {
    const value = feature.properties.value || 0;
    const fillColor = getColorForValue(value, colorScale.thresholds);

    return {
      fillColor: fillColor,
      weight: 2,
      opacity: 1,
      color: 'white',
      dashArray: '3',
      fillOpacity: 0.7,
    };
  };

  // Highlight feature on hover
  const highlightFeature = (e) => {
    const layer = e.target;
    layer.setStyle({
      weight: 5,
      color: '#666',
      dashArray: '',
      fillOpacity: 0.9,
    });
    layer.bringToFront();
  };

  // Reset highlight
  const resetHighlight = (e) => {
    const layer = e.target;
    layer.setStyle(style(layer.feature));
  };

  // Handle click on feature
  const onFeatureClick = (feature, layer) => {
    if (onRegionClick) {
      onRegionClick(feature);
    }
  };

  // Attach event listeners to each feature
  const onEachFeature = (feature, layer) => {
    const name = feature.properties.shapeName || feature.properties.name || 'Unknown';
    const value = feature.properties.value || 0;

    // Tooltip - show violations as integer
    layer.bindTooltip(
      `<div style="padding: 8px;">
        <strong>${name}</strong><br/>
        Violations: ${Math.round(value)}
      </div>`,
      {
        permanent: false,
        direction: 'auto',
      }
    );

    // Event listeners
    layer.on({
      mouseover: highlightFeature,
      mouseout: resetHighlight,
      click: () => onFeatureClick(feature, layer),
    });
  };

  if (!geojson || !geojson.features || geojson.features.length === 0) {
    return (
      <div
        style={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          border: '1px solid #d9d9d9',
          borderRadius: '4px',
          background: '#f5f5f5',
        }}
      >
        <div style={{ textAlign: 'center', color: '#999' }}>
          <p>No geographic data available</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: 'relative', height }}>
      {title && (
        <div
          style={{
            position: 'absolute',
            top: 10,
            left: 50,
            zIndex: 1000,
            background: 'white',
            padding: '8px 16px',
            borderRadius: '4px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            fontWeight: 'bold',
          }}
        >
          {title}
        </div>
      )}

      <MapContainer
        key={mapKey}
        center={[23.8103, 90.4125]} // Center of Bangladesh
        zoom={7}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {geojson && (
          <>
            <GeoJSON data={geojson} style={style} onEachFeature={onEachFeature} />
            <FitBounds geojson={geojson} />
          </>
        )}
      </MapContainer>

      {/* Legend */}
      <div
        style={{
          position: 'absolute',
          bottom: 20,
          right: 20,
          zIndex: 1000,
          background: 'white',
          padding: '12px',
          borderRadius: '4px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
        }}
      >
        <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '12px' }}>
          Performance
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div
              style={{
                width: 20,
                height: 15,
                background: '#ef4444',
                border: '1px solid #999',
              }}
            />
            <span>Low</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div
              style={{
                width: 20,
                height: 15,
                background: '#f59e0b',
                border: '1px solid #999',
              }}
            />
            <span>Medium</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div
              style={{
                width: 20,
                height: 15,
                background: '#10b981',
                border: '1px solid #999',
              }}
            />
            <span>High</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChoroplethMap;
