// src/components/PovertyIncidenceLayer.jsx
import { GeoJSON } from 'react-leaflet'
import { jenks } from 'simple-statistics'
import Legend from './Legend'

// Orange/red ramp — visually distinct from the blue population scale
const COLOR_RAMP = ['#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15']

function getColorForValue(value, breaks, colorRamp) {
  if (value === null || value === undefined) {
    return '#cccccc'
  }
  for (let i = 0; i < breaks.length; i++) {
    if (value <= breaks[i]) {
      return colorRamp[i]
    }
  }
  return colorRamp[colorRamp.length - 1]
}

function PovertyIncidenceLayer({ boundaries }) {
  if (!boundaries || !boundaries.features || boundaries.features.length === 0) {
    return null
  }

  const povertyValues = boundaries.features
    .map((f) => f.properties.poverty_incidence_pct)
    .filter((v) => v !== null && v !== undefined)

  if (povertyValues.length === 0) {
    console.warn('PovertyIncidenceLayer: no poverty data available yet')
    return null
  }

  const numClasses = Math.min(5, povertyValues.length)
  const breaks = jenks(povertyValues, numClasses)

  const styleByPoverty = (feature) => {
    const value = feature.properties.poverty_incidence_pct
    const fillColor = getColorForValue(value, breaks, COLOR_RAMP)
    return {
      fillColor,
      fillOpacity: 0.7,
      color: '#555555',
      weight: 1,
      opacity: 0.8,
    }
  }

  return (
    <>
      <GeoJSON data={boundaries} style={styleByPoverty} onEachFeature={onEachFeature}/>
      <Legend title="Poverty Incidence (%)" breaks={breaks} colorRamp={COLOR_RAMP} position="bottom-right" />
    </>
  )
}

export default PovertyIncidenceLayer
