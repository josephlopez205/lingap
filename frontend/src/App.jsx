import L from 'leaflet'
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'
import { MapContainer, TileLayer } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import MapView from './components/MapView'

// Fix Leaflet's default marker icon path issue under Vite bundling
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl: icon,
  shadowUrl: iconShadow,
})

function App() {
  return <MapView />
}

export default App
