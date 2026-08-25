// src/components/GapDetailCard.jsx

const RULE_EXPLANATIONS = {
  HEALTH_ACCESS_POPULATION: (ev) =>
    `This barangay has an estimated ${ev.population_total.toLocaleString()} residents. Measured from the barangay's geographic center, the nearest health facility is approximately ${ev.nearest_facility_km ?? 'unknown'} km away — beyond the ${ev.distance_threshold_km}km access standard used for this analysis.`,
  EDU_ACCESS_POPULATION: (ev) =>
    `This barangay has an estimated ${ev.population_total.toLocaleString()} residents. Measured from the barangay's geographic center, the nearest school is approximately ${ev.nearest_facility_km ?? 'unknown'} km away — beyond the ${ev.distance_threshold_km}km access standard used for this analysis.`,
}

function GapDetailCard({ gap, onClose }) {
  if (!gap) return null

  const explanation = RULE_EXPLANATIONS[gap.rule_id]
    ? RULE_EXPLANATIONS[gap.rule_id](gap.evidence_data)
    : 'No explanation available for this rule.'

  return (
    <div style={{
      position: 'absolute', bottom: '20px', left: '50%', transform: 'translateX(-50%)',
      zIndex: 1200, background: 'white', padding: '16px 20px', borderRadius: '10px',
      boxShadow: '0 4px 16px rgba(0,0,0,0.25)', maxWidth: '380px', fontFamily: 'sans-serif',
    }}>
      <button onClick={onClose} style={{ float: 'right', border: 'none', background: 'none', fontSize: '18px', cursor: 'pointer' }}>×</button>
      <div style={{ fontWeight: 'bold', fontSize: '16px', marginBottom: '4px' }}>{gap.sector} Gap — {gap.barangay_name}</div>
      <div style={{ fontSize: '13px', color: '#555', marginBottom: '10px' }}>{explanation}</div>
      <div style={{ fontSize: '13px', marginBottom: '10px' }}>
        <strong>Severity Score:</strong> {gap.severity_score} / 100
      </div>
      <button style={{ padding: '8px 14px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
        View Funding Matches
      </button>
      <div style={{ marginTop: '10px', fontSize: '11px', color: '#999', borderTop: '1px solid #eee', paddingTop: '8px' }}>
        Distance is estimated using each barangay's geographic centroid, not
        population-weighted location. Large or irregularly-shaped barangays
        may have residents closer to (or farther from) facilities than this
        estimate suggests.
      </div>
    </div>
  )
}

export default GapDetailCard
