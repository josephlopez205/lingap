// src/components/GapsLayer.jsx
import { useEffect, useState } from 'react'
import { Marker } from 'react-leaflet'
import { gapIcon } from './gapIcon'

const API_BASE = 'http://localhost:8000'
const LGU_ID = 1

function GapsLayer({ onGapClick }) {
  const [gaps, setGaps] = useState([])

  useEffect(() => {
    fetch(`${API_BASE}/api/lgu/${LGU_ID}/gaps`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server responded with ${res.status}`)
        return res.json()
      })
      .then((data) => setGaps(data))
      .catch((err) => console.error('Failed to fetch gaps:', err))
  }, [])

  return (
    <>
      {gaps.map((gap) => (
        <Marker
          key={gap.gap_id}
          position={[gap.centroid_lat, gap.centroid_lng]}
          icon={gapIcon}
          eventHandlers={{
            click: () => onGapClick(gap),
          }}
        />
      ))}
    </>
  )
}

export default GapsLayer
