// src/components/GapDetailCard.jsx

const RULE_EXPLANATIONS = {
  HEALTH_ACCESS_POPULATION: (ev) =>
    `This barangay has ${ev.population_total.toLocaleString()} residents, but the nearest health facility is ${ev.nearest_facility_km ?? 'unknown'} km away — exceeding the ${ev.distance_threshold_km}km threshold.`,
  EDU_ACCESS_POPULATION: (ev) =>
    `This barangay has ${ev.population_total.toLocaleString()} residents, but the nearest school is ${ev.nearest_facility_km ?? 'unknown'} km away — exceeding the ${ev.distance_threshold_km}km threshold.`,
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
    </div>
  )
}

export default GapDetailCard
