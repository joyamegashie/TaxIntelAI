import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom marker icons
const createCustomIcon = (color = '#3b82f6', size = 'medium') => {
  const sizes = {
    small: [20, 20],
    medium: [25, 25],
    large: [30, 30]
  };
  
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      background-color: ${color};
      width: ${sizes[size][0]}px;
      height: ${sizes[size][1]}px;
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    "></div>`,
    iconSize: sizes[size],
    iconAnchor: [sizes[size][0] / 2, sizes[size][1] / 2],
  });
};

// Map event handler component
const MapEventHandler = ({ onMapClick, onMapMove }) => {
  const map = useMap();

  useEffect(() => {
    if (onMapClick) {
      map.on('click', onMapClick);
    }
    if (onMapMove) {
      map.on('moveend', onMapMove);
    }

    return () => {
      if (onMapClick) {
        map.off('click', onMapClick);
      }
      if (onMapMove) {
        map.off('moveend', onMapMove);
      }
    };
  }, [map, onMapClick, onMapMove]);

  return null;
};

const MapComponent = ({
  center = [-1.2921, 36.8219], // Nairobi, Kenya default
  zoom = 10,
  markers = [],
  onMapClick,
  onMapMove,
  onMarkerClick,
  height = '400px',
  className = '',
  showControls = true,
  ...props
}) => {
  const mapRef = useRef();

  const getMarkerColor = (marker) => {
    if (marker.type === 'business') {
      const revenue = marker.estimated_revenue || 0;
      if (revenue > 100000) return '#ef4444'; // High revenue - red
      if (revenue > 50000) return '#f59e0b'; // Medium revenue - orange
      return '#10b981'; // Low revenue - green
    }
    if (marker.type === 'tax_opportunity') {
      const potential = marker.potential_tax || 0;
      if (potential > 50000) return '#8b5cf6'; // High potential - purple
      if (potential > 20000) return '#3b82f6'; // Medium potential - blue
      return '#06b6d4'; // Low potential - cyan
    }
    return marker.color || '#3b82f6';
  };

  const getMarkerSize = (marker) => {
    if (marker.type === 'business') {
      const revenue = marker.estimated_revenue || 0;
      if (revenue > 100000) return 'large';
      if (revenue > 50000) return 'medium';
      return 'small';
    }
    return marker.size || 'medium';
  };

  const handleMarkerClick = (marker, event) => {
    if (onMarkerClick) {
      onMarkerClick(marker, event);
    }
  };

  return (
    <div className={`taxintel-map ${className}`} style={{ height }}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        ref={mapRef}
        {...props}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapEventHandler onMapClick={onMapClick} onMapMove={onMapMove} />
        
        {markers.map((marker, index) => (
          <Marker
            key={marker.id || index}
            position={[marker.latitude, marker.longitude]}
            icon={createCustomIcon(getMarkerColor(marker), getMarkerSize(marker))}
            eventHandlers={{
              click: (e) => handleMarkerClick(marker, e),
            }}
          >
            <Popup>
              <div className="p-2 min-w-[200px]">
                <h3 className="font-semibold text-sm mb-2">
                  {marker.name || marker.title || 'Location'}
                </h3>
                
                {marker.type === 'business' && (
                  <div className="space-y-1 text-xs">
                    <p><strong>Type:</strong> {marker.business_type}</p>
                    <p><strong>Region:</strong> {marker.region}</p>
                    {marker.estimated_revenue && (
                      <p><strong>Est. Revenue:</strong> ${marker.estimated_revenue.toLocaleString()}</p>
                    )}
                    {marker.tax_potential && (
                      <p><strong>Tax Potential:</strong> ${marker.tax_potential.toLocaleString()}</p>
                    )}
                    {marker.confidence_score && (
                      <p><strong>Confidence:</strong> {(marker.confidence_score * 100).toFixed(1)}%</p>
                    )}
                  </div>
                )}
                
                {marker.type === 'tax_opportunity' && (
                  <div className="space-y-1 text-xs">
                    <p><strong>Sector:</strong> {marker.sector}</p>
                    <p><strong>Region:</strong> {marker.region}</p>
                    <p><strong>Potential Tax:</strong> ${marker.potential_tax?.toLocaleString()}</p>
                    <p><strong>Business Count:</strong> {marker.business_count}</p>
                    {marker.confidence_level && (
                      <p><strong>Confidence:</strong> {(marker.confidence_level * 100).toFixed(1)}%</p>
                    )}
                  </div>
                )}
                
                {marker.type === 'geofiscal' && (
                  <div className="space-y-1 text-xs">
                    <p><strong>Region:</strong> {marker.region}</p>
                    <p><strong>Activity Score:</strong> {(marker.economic_activity_score * 100).toFixed(1)}%</p>
                    <p><strong>Business Density:</strong> {marker.business_density}</p>
                    <p><strong>Tax Collection Rate:</strong> {(marker.tax_collection_rate * 100).toFixed(1)}%</p>
                    <p><strong>Informal Economy:</strong> {(marker.informal_economy_percentage * 100).toFixed(1)}%</p>
                  </div>
                )}
                
                {marker.description && (
                  <p className="text-xs mt-2 text-gray-600">{marker.description}</p>
                )}
                
                <div className="text-xs text-gray-500 mt-2">
                  Lat: {marker.latitude.toFixed(4)}, Lng: {marker.longitude.toFixed(4)}
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default MapComponent;

