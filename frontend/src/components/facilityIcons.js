// src/components/facilityIcons.js
import L from 'leaflet'

// Red cross icon for health facilities
const healthIconSvg = `
<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 28 28">
  <circle cx="14" cy="14" r="13" fill="#e53e3e" stroke="white" stroke-width="2"/>
  <rect x="12" y="6" width="4" height="16" fill="white"/>
  <rect x="6" y="12" width="16" height="4" fill="white"/>
</svg>
`

// Blue book icon for schools
const schoolIconSvg = `
<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 28 28">
  <circle cx="14" cy="14" r="13" fill="#3182ce" stroke="white" stroke-width="2"/>
  <path d="M8 9 L14 7 L20 9 L20 19 L14 21 L8 19 Z" fill="white"/>
  <line x1="14" y1="7" x2="14" y2="21" stroke="#3182ce" stroke-width="1"/>
</svg>
`

function svgToDataUri(svg) {
  return `data:image/svg+xml;base64,${btoa(svg)}`
}

export const healthIcon = new L.Icon({
  iconUrl: svgToDataUri(healthIconSvg),
  iconSize: [28, 28],
  iconAnchor: [14, 14],   // center the icon on the exact coordinate
  popupAnchor: [0, -14],
})

export const schoolIcon = new L.Icon({
  iconUrl: svgToDataUri(schoolIconSvg),
  iconSize: [28, 28],
  iconAnchor: [14, 14],
  popupAnchor: [0, -14],
})

export function getIconForFacilityType(facilityType) {
  if (facilityType === 'health') return healthIcon
  if (facilityType === 'school') return schoolIcon
  return healthIcon // fallback, shouldn't happen given your DB's CHECK constraint
}
