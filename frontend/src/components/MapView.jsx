// src/components/MapView.jsx
import { useEffect, useState, useRef, useCallback } from 'react'
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet'
import L from 'leaflet'
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'
import 'leaflet/dist/leaflet.css'
import 'react-leaflet-cluster/dist/assets/MarkerCluster.css'
import 'react-leaflet-cluster/dist/assets/MarkerCluster.Default.css'
import LayerPanel, { initialLayerState } from './LayerPanel'
import PopulationLevelsLayer from './PopulationLevelsLayer'
import HealthFacilitiesLayer from './HealthFacilitiesLayer'
import EducationFacilitiesLayer from './EducationFacilitiesLayer'
import DetailPanel from './DetailPanel'
import GapsLayer from './GapsLayer'
import GapDetailCard from './GapDetailCard'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl: icon,
  shadowUrl: iconShadow,
})

const API_BASE = 'http://localhost:8000'
const LGU_ID = 1

const boundaryStyle = {
  fillColor: '#000000',
  fillOpacity: 0,
  color: '#333333',
  weight: 1.5,
  opacity: 0.8,
}

const highlightStyle = {
  weight: 4,
  color: 'yellow',
  opacity: 1,
  fillOpacity: 0.3,
}

function FitBoundsOnLoad({ bbox }) {
  const map = useMap()
  useEffect(() => {
    if (!bbox) return
    const leafletBounds = [
      [bbox.min_lat, bbox.min_lng],
      [bbox.max_lat, bbox.max_lng],
    ]
    map.fitBounds(leafletBounds)
  }, [bbox, map])
  return null
}

function MapView() {
  const [boundaries, setBoundaries] = useState(null)
  const [bbox, setBbox] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeLayers, setActiveLayers] = useState(initialLayerState)
  const [selectedBarangay, setSelectedBarangay] = useState(null)
  const highlightedLayerRef = useRef(null)
  const [selectedGap, setSelectedGap] = useState(null)

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

  const onEachBarangay = (feature, layer) => {
    layer.on({
      click: () => {
        if (highlightedLayerRef.current && highlightedLayerRef.current._lingapOriginalStyle) {
          highlightedLayerRef.current.setStyle(highlightedLayerRef.current._lingapOriginalStyle)
        }
	
	layer._lingapOriginalStyle = { ...layer.options }
	layer.setStyle({
	  ...layer.options,
	  weight: 4,
	  color: '#ffff00',
	  opacity: 1,
	})
	layer.bringToFront()
        highlightedLayerRef.current = layer

        setSelectedBarangay(feature.properties.barangay_id)
      },
    })
  }

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
        center={[14.65, 121.10]}
        zoom={12}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        {boundaries && (
          <GeoJSON
            data={boundaries}
            style={boundaryStyle}
            onEachFeature={onEachBarangay}
          />
        )}
        {bbox && <FitBoundsOnLoad bbox={bbox} />}

        {activeLayers.populationLevels && (
          <PopulationLevelsLayer boundaries={boundaries} onEachFeature={onEachBarangay} />
        )}
        {activeLayers.healthFacilities && <HealthFacilitiesLayer />}
        {activeLayers.educationFacilities && <EducationFacilitiesLayer />}

	<GapsLayer onGapClick={setSelectedGap} />
      </MapContainer>

      <LayerPanel activeLayers={activeLayers} setActiveLayers={setActiveLayers} />

      <DetailPanel
        selectedBarangay={selectedBarangay}
        onClose={() => setSelectedBarangay(null)}
      />

      <GapDetailCard
        gap={selectedGap}
        onClose={() =>setSelectedGap(null)}
      />
    </div>
  )
}

export default MapView
