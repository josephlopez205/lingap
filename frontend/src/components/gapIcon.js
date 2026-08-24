// src/components/gapIcon.js
import L from 'leaflet'

const gapIconSvg = `
<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 30 30">
  <polygon points="15,3 27,25 3,25" fill="#f97316" stroke="white" stroke-width="2"/>
  <text x="15" y="21" font-size="12" font-weight="bold" fill="white" text-anchor="middle">!</text>
</svg>
`

function svgToDataUri(svg) {
  return `data:image/svg+xml;base64,${btoa(svg)}`
}

export const gapIcon = new L.Icon({
  iconUrl: svgToDataUri(gapIconSvg),
  iconSize: [30, 30],
  iconAnchor: [15, 25],
  popupAnchor: [0, -25],
})
