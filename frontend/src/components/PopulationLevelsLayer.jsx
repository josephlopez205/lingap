// src/components/PopulationLevelsLayer.jsx
import { GeoJSON } from 'react-leaflet'
import { jenks } from 'simple-statistics'
import Legend from './Legend'
import MarkerClusterGroup from 'react-leaflet-cluster'

const COLOR_RAMP = ['#deebf7', '#9ecae1', '#4292c6', '#2171b5', '#08519c']

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

function PopulationLevelsLayer({ boundaries }) {
  if (!boundaries || !boundaries.features || boundaries.features.length === 0) {
    return null
  }

  const populationValues = boundaries.features
    .map((f) => f.properties.population_total)
    .filter((v) => v !== null && v !== undefined)

  if (populationValues.length === 0) {
    console.warn('PopulationLevelsLayer: no population data available')
    return null
  }

  const numClasses = Math.min(5, populationValues.length)
  const breaks = jenks(populationValues, numClasses)

  const styleByPopulation = (feature) => {
    const value = feature.properties.population_total
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
      <GeoJSON data={boundaries} style={styleByPopulation} />
      <Legend title="Population" breaks={breaks} colorRamp={COLOR_RAMP} position="bottom-right" />
    </>
  )
}

export default PopulationLevelsLayer
