// src/components/MapView.jsx
import { useEffect, useState, useRef } from 'react'
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet'
import L from 'leaflet'
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'
import 'leaflet/dist/leaflet.css'
import LayerPanel, { initialLayerState } from './LayerPanel'

// Fix Leaflet's default marker icon path under Vite bundling
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl: icon,
  shadowUrl: iconShadow,
})

const API_BASE = 'http://localhost:8000'
const LGU_ID = 1

// Style for barangay boundary polygons: transparent fill, dark outline
const boundaryStyle = {
  fillColor: '#000000',
  fillOpacity: 0,       // transparent fill
  color: '#333333',     // dark outline
  weight: 1.5,
  opacity: 0.8,
}

/**
 * Sub-component that has access to the Leaflet map instance via useMap().
 * Must live INSIDE <MapContainer> — this is a react-leaflet requirement,
 * you cannot call fitBounds from the parent because the map instance
 * doesn't exist until MapContainer has mounted its children.
 */
function FitBoundsOnLoad({ bbox }) {
  const map = useMap()
  useEffect(() => {
    if (!bbox) return
    const leafletBounds = [
      [bbox.min_lat, bbox.min_lng],   // southwest corner
      [bbox.max_lat, bbox.max_lng],   // northeast corner
    ]
    map.fitBounds(leafletBounds)
  }, [bbox, map])
  return null   // this component renders nothing visually, it just triggers a side effect
}

function MapView() {
  const [boundaries, setBoundaries] = useState(null)
  const [bbox, setBbox] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // NEW: layer toggle state, lifted here so it can control what renders on the map
  const [activeLayers, setActiveLayers] = useState(initialLayerState)

  useEffect(() => {
    fetch(`${API_BASE}/api/lgu/${LGU_ID}/boundaries`)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Server responded with ${res.status}`)
        }
        return res.json()
      })
      .then((data) => {
        setBoundaries(data)
        setBbox(data.bbox)
        setLoading(false)
      })
      .catch((err) => {
        console.error('Failed to fetch boundaries:', err)
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div style={{ padding: '2rem' }}>Loading map…</div>
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', color: 'red' }}>
        Failed to load map data: {error}
      </div>
    )
  }

  return (
    <div style={{ height: '100vh', width: '100vw' }}>
      <MapContainer
        center={[14.65, 121.10]}   // fallback center, overridden by fitBounds once data loads
        zoom={12}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        {boundaries && (
          <GeoJSON data={boundaries} style={boundaryStyle} />
        )}
        {bbox && <FitBoundsOnLoad bbox={bbox} />}

        {/* Choropleth/facility layers will be added here in the next step,
            each conditionally rendered based on activeLayers.<key> */}
      </MapContainer>

      {/* LayerPanel sits OUTSIDE MapContainer as a plain HTML overlay,
          positioned absolutely via its own internal styles */}
      <LayerPanel activeLayers={activeLayers} setActiveLayers={setActiveLayers} />
    </div>
  )
}

export default MapView