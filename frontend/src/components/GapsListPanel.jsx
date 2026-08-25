// src/components/GapsListPanel.jsx
import { useEffect, useState } from 'react'

const API_BASE = 'http://localhost:8000'
const LGU_ID = 1

function GapsListPanel({ onSelectGap }) {
  const [gaps, setGaps] = useState([])
  const [sortField, setSortField] = useState('severity_score')
  const [sortDir, setSortDir] = useState('desc')

  useEffect(() => {
    fetch(`${API_BASE}/api/lgu/${LGU_ID}/gaps`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server responded with ${res.status}`)
        return res.json()
      })
      .then(setGaps)
      .catch((err) => console.error('Failed to fetch gaps list:', err))
  }, [])

  const sorted = [...gaps].sort((a, b) => {
    const dir = sortDir === 'asc' ? 1 : -1
    if (a[sortField] < b[sortField]) return -1 * dir
    if (a[sortField] > b[sortField]) return 1 * dir
    return 0
  })

  const handleSort = (field) => {
    if (field === sortField) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDir('desc')
    }
  }

  return (
    <div style={{ position: 'absolute', top: '10px', left: '10px', zIndex: 1000, background: 'white', padding: '12px', borderRadius: '8px', maxHeight: '400px', overflowY: 'auto', fontFamily: 'sans-serif', fontSize: '13px', boxShadow: '0 2px 8px rgba(0,0,0,0.2)' }}>
      <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Gaps ({gaps.length})</div>
      <table style={{ borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th onClick={() => handleSort('barangay_name')} style={{ cursor: 'pointer', padding: '4px 8px', textAlign: 'left' }}>Barangay</th>
            <th onClick={() => handleSort('sector')} style={{ cursor: 'pointer', padding: '4px 8px', textAlign: 'left' }}>Sector</th>
            <th onClick={() => handleSort('severity_score')} style={{ cursor: 'pointer', padding: '4px 8px', textAlign: 'left' }}>Score</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((gap) => (
            <tr key={gap.gap_id} onClick={() => onSelectGap(gap)} style={{ cursor: 'pointer' }}>
              <td style={{ padding: '4px 8px' }}>{gap.barangay_name}</td>
              <td style={{ padding: '4px 8px' }}>{gap.sector}</td>
              <td style={{ padding: '4px 8px' }}>{gap.severity_score.toFixed(1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default GapsListPanel
