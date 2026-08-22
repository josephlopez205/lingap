// src/components/Legend.jsx

function formatNumber(num) {
  return Math.round(num).toLocaleString('en-US')
}

function Legend({ title, breaks, colorRamp, position = 'bottom-right' }) {
  if (!breaks || breaks.length === 0) return null

  // Build labeled ranges, skipping any band that's degenerate (lower === upper)
  const ranges = []
  for (let i = 0; i < breaks.length; i++) {
    const lower = i === 0 ? 0 : breaks[i - 1]
    const upper = breaks[i]

    if (lower === upper) {
      // This band has zero width — skip it rather than showing e.g. "164,822–164,822"
      continue
    }

    ranges.push({
      color: colorRamp[i],
      label: `${formatNumber(lower)}–${formatNumber(upper)}`,
    })
  }

  const positionStyles = {
    'bottom-right': { bottom: '20px', right: '10px' },
    'bottom-left': { bottom: '20px', left: '10px' },
  }

  return (
    <div
      style={{
        position: 'absolute',
        zIndex: 1000,
        background: 'white',
        padding: '10px 14px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
        fontFamily: 'sans-serif',
        fontSize: '12px',
        ...positionStyles[position],
      }}
    >
      <div style={{ fontWeight: 'bold', marginBottom: '6px' }}>{title}</div>
      {ranges.map((r, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}>
          <div
            style={{
              width: '14px',
              height: '14px',
              backgroundColor: r.color,
              border: '1px solid #999',
              flexShrink: 0,
            }}
          />
          <span>{r.label}</span>
        </div>
      ))}
    </div>
  )
}

export default Legend
