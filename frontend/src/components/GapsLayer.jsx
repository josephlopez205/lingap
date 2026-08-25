// src/components/GapsLayer.jsx
import { useEffect, useState } from 'react'
import { Marker } from 'react-leaflet'
import { gapIcon } from './gapIcon'

const API_BASE = 'http://localhost:8000'
const LGU_ID = 1

// Small offset in degrees (~roughly 15-20 meters at this latitude) to visually
// separate multiple gaps that share the same barangay centroid.
const OFFSET_DEGREES = 0.00015

function applyOffsets(gaps) {
  // Group gaps by barangay_id
  const grouped = {}
  gaps.forEach((gap) => {
    if (!grouped[gap.barangay_id]) grouped[gap.barangay_id] = []
    grouped[gap.barangay_id].push(gap)
  })

  const offsetGaps = []
  Object.values(grouped).forEach((groupGaps) => {
    if (groupGaps.length === 1) {
      // Only one gap here — no offset needed
      offsetGaps.push({
        ...groupGaps[0],
        display_lat: groupGaps[0].centroid_lat,
        display_lng: groupGaps[0].centroid_lng,
      })
      return
    }

    // Multiple gaps at the same centroid — spread them in a small circle
    groupGaps.forEach((gap, i) => {
      const angle = (2 * Math.PI * i) / groupGaps.length
      offsetGaps.push({
        ...gap,
        display_lat: gap.centroid_lat + OFFSET_DEGREES * Math.sin(angle),
        display_lng: gap.centroid_lng + OFFSET_DEGREES * Math.cos(angle),
      })
    })
  })

  return offsetGaps
}

function GapsLayer({ onGapClick }) {
  const [gaps, setGaps] = useState([])

  useEffect(() => {
    fetch(`${API_BASE}/api/lgu/${LGU_ID}/gaps`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server responded with ${res.status}`)
        return res.json()
      })
      .then((data) => setGaps(applyOffsets(data)))
      .catch((err) => console.error('Failed to fetch gaps:', err))
  }, [])

  return (
    <>
      {gaps.map((gap) => (
        <Marker
          key={gap.gap_id}
          position={[gap.display_lat, gap.display_lng]}
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
