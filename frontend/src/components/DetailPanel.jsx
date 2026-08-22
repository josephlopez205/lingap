// src/components/DetailPanel.jsx
import { useEffect, useState } from 'react'

const API_BASE = 'http://localhost:8000'

function formatNumber(num) {
  if (num === null || num === undefined) return 'N/A'
  return num.toLocaleString('en-US')
}

function DetailPanel({ selectedBarangay, onClose }) {
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!selectedBarangay) return

    setLoading(true)
    setError(null)
    setDetail(null)

    fetch(`${API_BASE}/api/barangay/${selectedBarangay}/detail`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server responded with ${res.status}`)
        return res.json()
      })
      .then((data) => {
        setDetail(data)
        setLoading(false)
      })
      .catch((err) => {
        console.error('Failed to fetch barangay detail:', err)
        setError(err.message)
        setLoading(false)
      })
  }, [selectedBarangay])

  const isOpen = selectedBarangay !== null

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        right: 0,
        height: '100%',
        width: '320px',
        background: 'white',
        boxShadow: '-2px 0 8px rgba(0,0,0,0.2)',
        zIndex: 1100,        // above LayerPanel (1000) and Legend (1000)
        transform: isOpen ? 'translateX(0)' : 'translateX(100%)',
        transition: 'transform 300ms ease-in-out',
        padding: '20px',
        fontFamily: 'sans-serif',
        boxSizing: 'border-box',
        overflowY: 'auto',
      }}
    >
      <button
        onClick={onClose}
        style={{
          position: 'absolute',
          top: '12px',
          right: '12px',
          background: 'none',
          border: 'none',
          fontSize: '20px',
          cursor: 'pointer',
          lineHeight: 1,
        }}
        aria-label="Close panel"
      >
        ×
      </button>

      {loading && <div style={{ marginTop: '40px' }}>Loading…</div>}

      {error && (
        <div style={{ marginTop: '40px', color: 'red' }}>
          Failed to load barangay data: {error}
        </div>
      )}

      {detail && !loading && !error && (
        <div style={{ marginTop: '30px' }}>
          <h2 style={{ marginBottom: '16px', fontSize: '20px' }}>{detail.name}</h2>

          <DetailRow label="Total Population" value={formatNumber(detail.population_total)} />
          <DetailRow label="Health Facilities" value={formatNumber(detail.health_facility_count)} />
          <DetailRow label="Schools" value={formatNumber(detail.school_count)} />
          <DetailRow label="Active Flagged Gaps" value={formatNumber(detail.active_gap_count)} />

          <div style={{ marginTop: '20px', fontSize: '12px', color: '#888', borderTop: '1px solid #eee', paddingTop: '12px' }}>
            Age-bracket and poverty incidence data pending PSA barangay-level release.
          </div>
        </div>
      )}
    </div>
  )
}

function DetailRow({ label, value }) {
  return (
    <div style={{ marginBottom: '12px' }}>
      <div style={{ fontSize: '12px', color: '#666', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
        {label}
      </div>
      <div style={{ fontSize: '18px', fontWeight: 600 }}>{value}</div>
    </div>
  )
}

export default DetailPanel
