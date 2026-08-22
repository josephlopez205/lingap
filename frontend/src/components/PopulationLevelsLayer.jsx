// src/components/PopulationLevelsLayer.jsx
import { jenks } from 'simple-statistics'

// 5-step blue color ramp, light to dark
const COLOR_RAMP = ['#deebf7', '#9ecae1', '#4292c6', '#2171b5', '#08519c']

function PopulationLevelsLayer({ boundaries }) {
  if (!boundaries || !boundaries.features || boundaries.features.length === 0) {
    return null
  }

  // Step A: extract population values, filtering out null/undefined
  const populationValues = boundaries.features
    .map((f) => f.properties.population_total)
    .filter((v) => v !== null && v !== undefined)

  if (populationValues.length === 0) {
    console.warn('PopulationLevelsLayer: no population data available')
    return null
  }

  // Step B: compute Jenks breaks
  // jenks() needs at least as many data points as classes requested,
  // so guard against a pilot LGU with very few barangays
  const numClasses = Math.min(5, populationValues.length)
  const breaks = jenks(populationValues, numClasses)

  console.log('Jenks breaks computed:', breaks)

  // more steps below...
  return null // placeholder — styling logic comes in Step 4
}

export default PopulationLevelsLayer
