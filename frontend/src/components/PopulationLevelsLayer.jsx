// src/components/PopulationLevelsLayer.jsx
import { useMemo, useCallback } from 'react'
import { GeoJSON } from 'react-leaflet'
import { jenks } from 'simple-statistics'
import Legend from './Legend'

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

function PopulationLevelsLayer({ boundaries, onEachFeature }) {
  const populationValues = useMemo(() => {
    if (!boundaries || !boundaries.features) return []
    return boundaries.features
      .map((f) => f.properties.population_total)
      .filter((v) => v !== null && v !== undefined)
  }, [boundaries])

  const breaks = useMemo(() => {
    if (populationValues.length === 0) return []
    const numClasses = Math.min(5, populationValues.length)
    return jenks(populationValues, numClasses)
  }, [populationValues])

  // useCallback keeps this function's REFERENCE stable across re-renders,
  // as long as `breaks` hasn't actually changed — this is what stops
  // react-leaflet from re-applying styles and wiping out the click highlight
  const styleByPopulation = useCallback(
    (feature) => {
      const value = feature.properties.population_total
      const fillColor = getColorForValue(value, breaks, COLOR_RAMP)
      return {
        fillColor,
        fillOpacity: 0.7,
        color: '#555555',
        weight: 1,
        opacity: 0.8,
      }
    },
    [breaks]
  )

  if (!boundaries || !boundaries.features || boundaries.features.length === 0) {
    return null
  }

  if (populationValues.length === 0) {
    console.warn('PopulationLevelsLayer: no population data available')
    return null
  }

  return (
    <>
      <GeoJSON
        data={boundaries}
        style={styleByPopulation}
        onEachFeature={onEachFeature}
      />
      <Legend title="Population" breaks={breaks} colorRamp={COLOR_RAMP} position="bottom-right" />
    </>
  )
}

export default PopulationLevelsLayer
