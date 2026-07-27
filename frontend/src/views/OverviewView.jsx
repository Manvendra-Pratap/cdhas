import { memo } from 'react'
import { ExecutiveSummary } from '../components/ExecutiveSummary'
import { MetricCard } from '../components/MetricCard'
import { InteractiveWorldMap } from '../components/InteractiveWorldMap'
import { AttackChart } from '../components/AttackChart'
import { AdditionalChartsSection } from '../components/AdditionalChartsSection'
import { SessionTable } from '../components/SessionTable'
import { CountryFlag } from '../components/CountryFlag'
import { EmptyState } from '../components/EmptyState'

export default memo(function OverviewView({ data, onSession, onViewSessions, onSelectCountry, onRefresh }) {
  if (!data.sessions || data.sessions.length === 0) {
    return <EmptyState onRefresh={onRefresh} />
  }

  return (
    <div className="page-view-fade">
      <div className="page-heading">
        <div>
          <p className="eyebrow">HONEYPOT INTELLIGENCE</p>
          <h1>Good morning, <span>Akshat.</span></h1>
          <p className="subheading">Here’s what your deception network has observed today.</p>
        </div>
        <div className="period-picker"><span>◷</span> Last 24 hours <b>⌄</b></div>
      </div>

      <ExecutiveSummary data={data} />

      <section className="metric-grid">
        {data.overview.metrics.map((metric) => <MetricCard key={metric.label} metric={metric} />)}
      </section>

      <InteractiveWorldMap sessions={data.sessions} onSelectCountry={onSelectCountry} />

      <div className="split-grid">
        <AttackChart timeline={data.timeline} compact />
        <section className="card geography-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">GEOGRAPHY</p>
              <h2>Top source locations</h2>
            </div>
          </div>
          <div className="geo-list">
            {data.overview.geography.map((location, index) => (
              <div className="geo-row" key={location.code || location.country}>
                <div className="rank">0{index + 1}</div>
                <CountryFlag code={location.code} country={location.country} />
                <div className="geo-name">
                  <strong>{location.country}</strong>
                  <small>{location.sessions} sessions</small>
                </div>
                <div className="bar-track">
                  <i style={{ width: `${(location.sessions / data.overview.geography[0].sessions) * 100}%`, background: location.color }} />
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <AdditionalChartsSection sessions={data.sessions} intelligence={data.intelligence} />

      <SessionTable sessions={data.sessions} onSelect={(value) => value === 'all' ? onViewSessions() : onSession(value)} limit={5} />
    </div>
  )
})
