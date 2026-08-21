// src/components/LayerPanel.jsx

const LAYER_CONFIG = [
  { key: 'populationLevels', label: 'Population Levels' },
  { key: 'povertyIncidence', label: 'Poverty Incidence' },
  { key: 'healthFacilities', label: 'Health Facilities' },
  { key: 'educationFacilities', label: 'Education Facilities' },
]

const INITIAL_STATE = {
  populationLevels: false,
  povertyIncidence: false,
  healthFacilities: false,
  educationFacilities: false,
}

function LayerPanel({ activeLayers, setActiveLayers }) {
  const handleToggle = (key) => {
    setActiveLayers((prev) => ({
      ...prev,          // keeps every other key's current value untouched
      [key]: !prev[key], // flips only the one that was clicked
    }))
  }

  return (
    <div
      style={{
        position: 'absolute',
        top: '10px',
        right: '10px',
        zIndex: 1000,
        background: 'white',
        padding: '12px 16px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
        fontFamily: 'sans-serif',
        fontSize: '14px',
      }}
    >
      <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Layers</div>
      {LAYER_CONFIG.map(({ key, label }) => (
        <div key={key} style={{ marginBottom: '4px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={activeLayers[key]}
              onChange={() => handleToggle(key)}
            />
            {label}
          </label>
        </div>
      ))}
    </div>
  )
}

export { INITIAL_STATE as initialLayerState }
export default LayerPanel
