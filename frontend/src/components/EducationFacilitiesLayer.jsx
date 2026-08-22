// src/components/EducationFacilitiesLayer.jsx
import { useEffect, useState } from 'react'
import { Marker, Popup } from 'react-leaflet'
import MarkerClusterGroup from 'react-leaflet-cluster'
import { schoolIcon } from './facilityIcons'

const API_BASE = 'http://localhost:8000'
const LGU_ID = 1

function EducationFacilitiesLayer() {
  const [facilities, setFacilities] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE}/api/lgu/${LGU_ID}/facilities`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server responded with ${res.status}`)
        return res.json()
      })
      .then((data) => {
        const schoolsOnly = data.features.filter(
          (f) => f.properties.facility_type === 'school'
        )
        setFacilities(schoolsOnly)
      })
      .catch((err) => {
        console.error('Failed to fetch education facilities:', err)
        setError(err.message)
      })
  }, [])

  if (error || !facilities) return null

  return (
    <MarkerClusterGroup chunkedLoading maxClusterRadius={50}>
      {facilities.map((feature) => {
        const [lng, lat] = feature.geometry.coordinates
        const { facility_name, capacity } = feature.properties
        return (
          <Marker key={feature.properties.facility_id} position={[lat, lng]} icon={schoolIcon}>
            <Popup>
              <strong>{facility_name}</strong>
              <br />
              Type: School
              <br />
              Capacity: {capacity !== null ? capacity : 'Not specified'}
            </Popup>
          </Marker>
        )
      })}
    </MarkerClusterGroup>
  )
}

export default EducationFacilitiesLayer
