import { memo } from 'react'
import { AttackChart } from '../components/AttackChart'
import { Badge } from '../components/Badge'

export default memo(function TimelineView({ data }) {
  const totals = (data.timeline || []).reduce((acc, value) => ({ sessions: acc.sessions + value.sessions, anomalies: acc.anomalies + value.anomalies }), { sessions: 0, anomalies: 0 })

  return (
    <div className="page-view-fade">
      <div className="page-heading">
        <div>
          <p className="eyebrow">OBSERVABILITY</p>
          <h1>Attack timeline</h1>
          <p className="subheading">Session activity and anomalous behavior from the last 24 hours.</p>
        </div>
        <div className="period-picker"><span>◷</span> Last 24 hours <b>⌄</b></div>
      </div>
      <section className="timeline-stat-row">
        <article><span>Sessions captured</span><strong>{totals.sessions}</strong></article>
        <article><span>Anomaly signals</span><strong>{totals.anomalies}</strong></article>
        <article><span>Peak hour</span><strong>14:00</strong></article>
      </section>
      <AttackChart timeline={data.timeline} />
      <section className="card event-summary">
        <div className="card-heading">
          <div>
            <p className="eyebrow">NOTABLE WINDOW</p>
            <h2>14:00–15:00 UTC</h2>
          </div>
          <Badge severity="High" />
        </div>
        <p>The busiest interval recorded 89 sessions and 8 anomaly signals. Activity concentrated around scripted credential attempts followed by downloader commands.</p>
      </section>
    </div>
  )
})
