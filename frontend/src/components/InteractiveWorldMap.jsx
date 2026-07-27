import { memo, useState, useMemo } from 'react'
import { ComposableMap, Geographies, Geography, Marker, ZoomableGroup } from 'react-simple-maps'

const geoUrl = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json'

const countryCentroids = {
  IN: [78.9629, 20.5937],
  US: [-95.7129, 37.0902],
  BR: [-51.9253, -14.2350],
  DE: [10.4515, 51.1657],
  NL: [5.2913, 52.1326],
  VN: [108.2772, 14.0583],
  CN: [104.1954, 35.8617],
  RU: [105.3188, 61.5240],
  FR: [2.2137, 46.2276],
  GB: [-3.4360, 55.3781],
  JP: [138.2529, 36.2048],
  CA: [-106.3468, 56.1304],
  AU: [133.7751, -25.2744],
}

const severityColorMap = {
  Low: '#54d5a5',
  Medium: '#4aadff',
  High: '#f4bf75',
  Critical: '#ef7f88',
}

const severityOrder = { Critical: 4, High: 3, Medium: 2, Low: 1 }

export const InteractiveWorldMap = memo(function InteractiveWorldMap({ sessions, onSelectCountry }) {
  const [tooltip, setTooltip] = useState(null)
  const [position, setPosition] = useState({ coordinates: [0, 20], zoom: 1 })

  const mapData = useMemo(() => {
    const grouped = {}
    sessions.forEach((s) => {
      const country = s.country || 'Unknown'
      const code = s.flag || (country ? country.slice(0, 2).toUpperCase() : 'UN')
      if (!grouped[country]) {
        grouped[country] = {
          country,
          code,
          count: 0,
          highRisk: 0,
          archetypes: {},
          maxSeverity: 'Low',
          coordinates: countryCentroids[code] || [0, 0],
        }
      }

      grouped[country].count += 1
      if (severityOrder[s.severity] >= 3) grouped[country].highRisk += 1
      grouped[country].archetypes[s.archetype] = (grouped[country].archetypes[s.archetype] || 0) + 1

      if (severityOrder[s.severity] > severityOrder[grouped[country].maxSeverity]) {
        grouped[country].maxSeverity = s.severity
      }
    })

    return Object.values(grouped).map((item) => {
      const topArch = Object.entries(item.archetypes).sort((a, b) => b[1] - a[1])[0]?.[0] || 'Reconnaissance bot'
      return {
        ...item,
        topArchetype: topArch,
      }
    })
  }, [sessions])

  const handleZoomIn = () => {
    if (position.zoom < 4) setPosition((prev) => ({ ...prev, zoom: prev.zoom * 1.5 }))
  }

  const handleZoomOut = () => {
    if (position.zoom > 1) setPosition((prev) => ({ ...prev, zoom: prev.zoom / 1.5 }))
  }

  const handleResetZoom = () => {
    setPosition({ coordinates: [0, 20], zoom: 1 })
  }

  return (
    <section className="card map-card">
      <div className="card-heading">
        <div>
          <p className="eyebrow">INTERACTIVE WORLD MAP</p>
          <h2>Attack Locations & Severity Clusters</h2>
        </div>
        <div className="map-controls">
          <button type="button" onClick={handleZoomIn} title="Zoom In" aria-label="Zoom in on map">+</button>
          <button type="button" onClick={handleZoomOut} title="Zoom Out" aria-label="Zoom out on map">-</button>
          <button type="button" onClick={handleResetZoom} title="Reset Zoom" aria-label="Reset map zoom">Reset</button>
        </div>
      </div>

      <div className="map-container">
        <ComposableMap projectionConfig={{ scale: 140 }} style={{ width: '100%', height: '320px' }}>
          <ZoomableGroup zoom={position.zoom} center={position.coordinates} onMoveEnd={(pos) => setPosition(pos)}>
            <Geographies geography={geoUrl}>
              {({ geographies }) =>
                geographies.map((geo) => (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill="#102538"
                    stroke="#1d3d5a"
                    strokeWidth={0.5}
                    style={{
                      default: { outline: 'none' },
                      hover: { fill: '#163550', outline: 'none' },
                      pressed: { outline: 'none' },
                    }}
                  />
                ))
              }
            </Geographies>

            {mapData.map((item) => {
              if (!item.coordinates || (item.coordinates[0] === 0 && item.coordinates[1] === 0)) return null
              const radius = Math.max(6, Math.min(22, Math.sqrt(item.count) * 4))
              const color = severityColorMap[item.maxSeverity] || '#4aadff'

              return (
                <Marker
                  key={item.country}
                  coordinates={item.coordinates}
                  onMouseEnter={() => setTooltip(item)}
                  onMouseLeave={() => setTooltip(null)}
                  onClick={() => onSelectCountry(item.country)}
                  style={{ cursor: 'pointer' }}
                >
                  <circle r={radius} fill={color} fillOpacity={0.6} stroke={color} strokeWidth={2} />
                  <circle r={radius * 0.4} fill="#ffffff" />
                </Marker>
              )
            })}
          </ZoomableGroup>
        </ComposableMap>

        {tooltip && (
          <div className="map-tooltip" role="tooltip">
            <strong>{tooltip.country}</strong>
            <div>Total Attacks: <span>{tooltip.count}</span></div>
            <div>High Risk: <span className="coral-text">{tooltip.highRisk}</span></div>
            <div>Top Threat: <span>{tooltip.topArchetype}</span></div>
            <small>Click marker to filter table</small>
          </div>
        )}
      </div>

      <div className="map-legend">
        <span><i style={{ background: '#54d5a5' }} /> Low</span>
        <span><i style={{ background: '#4aadff' }} /> Medium</span>
        <span><i style={{ background: '#f4bf75' }} /> High</span>
        <span><i style={{ background: '#ef7f88' }} /> Critical</span>
      </div>
    </section>
  )
})
