import { memo, useMemo } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  PieChart,
  Pie,
  Cell,
} from 'recharts'

export const AdditionalChartsSection = memo(function AdditionalChartsSection({ sessions, intelligence }) {
  const topCommands = useMemo(() => {
    const counts = {}
    sessions.forEach((s) => {
      if (s.commands) {
        s.commands.forEach((c) => {
          counts[c] = (counts[c] || 0) + 1
        })
      }
    })
    return Object.entries(counts)
      .map(([command, count]) => ({ command, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 6)
  }, [sessions])

  const protocolData = useMemo(() => {
    const counts = {}
    sessions.forEach((s) => {
      const p = s.protocol || 'SSH'
      counts[p] = (counts[p] || 0) + 1
    })
    return Object.entries(counts).map(([name, value]) => ({ name, value }))
  }, [sessions])

  const severityData = useMemo(() => {
    const counts = { Critical: 0, High: 0, Medium: 0, Low: 0 }
    sessions.forEach((s) => {
      counts[s.severity] = (counts[s.severity] || 0) + 1
    })
    return [
      { name: 'Critical', value: counts.Critical, color: '#ef7f88' },
      { name: 'High', value: counts.High, color: '#f4bf75' },
      { name: 'Medium', value: counts.Medium, color: '#4aadff' },
      { name: 'Low', value: counts.Low, color: '#54d5a5' },
    ]
  }, [sessions])

  const attackSources = useMemo(() => {
    const counts = {}
    sessions.forEach((s) => {
      const country = s.country || 'Unknown'
      counts[country] = (counts[country] || 0) + 1
    })
    return Object.entries(counts)
      .map(([country, count]) => ({ country, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5)
  }, [sessions])

  const archetypeChartData = useMemo(() => {
    return (intelligence || []).map((item) => ({
      name: item.label,
      value: item.sessions,
      color: item.color || '#4aadff',
    }))
  }, [intelligence])

  const customTooltipStyle = {
    backgroundColor: '#0c2033',
    borderColor: '#214059',
    color: '#dbe8f1',
    fontSize: '11px',
    borderRadius: '6px',
  }

  return (
    <div className="charts-section-grid">
      <section className="card chart-card">
        <div className="card-heading">
          <div>
            <p className="eyebrow">COMMAND TELEMETRY</p>
            <h2>Top Executed Commands</h2>
          </div>
        </div>
        <div style={{ width: '100%', height: 210, padding: '10px 15px' }}>
          <ResponsiveContainer>
            <BarChart data={topCommands}>
              <XAxis dataKey="command" tick={{ fill: '#7890a8', fontSize: 10 }} interval={0} />
              <YAxis tick={{ fill: '#7890a8', fontSize: 10 }} />
              <RechartsTooltip contentStyle={customTooltipStyle} />
              <Bar dataKey="count" fill="#4aadff" radius={[4, 4, 0, 0]} isAnimationActive={true} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="card chart-card">
        <div className="card-heading">
          <div>
            <p className="eyebrow">RISK LEVEL</p>
            <h2>Severity Distribution</h2>
          </div>
        </div>
        <div style={{ width: '100%', height: 210, padding: '10px 15px' }}>
          <ResponsiveContainer>
            <PieChart>
              <Pie data={severityData} innerRadius={45} outerRadius={70} dataKey="value" isAnimationActive={true}>
                {severityData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <RechartsTooltip contentStyle={customTooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="card chart-card">
        <div className="card-heading">
          <div>
            <p className="eyebrow">PROTOCOL ANALYSIS</p>
            <h2>Protocol Distribution</h2>
          </div>
        </div>
        <div style={{ width: '100%', height: 210, padding: '10px 15px' }}>
          <ResponsiveContainer>
            <PieChart>
              <Pie data={protocolData} dataKey="value" outerRadius={70} fill="#8d7cff" isAnimationActive={true}>
                {protocolData.map((_, index) => (
                  <Cell key={index} fill={['#8d7cff', '#4aadff', '#61dcb0'][index % 3]} />
                ))}
              </Pie>
              <RechartsTooltip contentStyle={customTooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="card chart-card">
        <div className="card-heading">
          <div>
            <p className="eyebrow">SOURCE BREAKDOWN</p>
            <h2>Attack Sources</h2>
          </div>
        </div>
        <div style={{ width: '100%', height: 210, padding: '10px 15px' }}>
          <ResponsiveContainer>
            <BarChart layout="vertical" data={attackSources}>
              <XAxis type="number" tick={{ fill: '#7890a8', fontSize: 10 }} />
              <YAxis type="category" dataKey="country" tick={{ fill: '#7890a8', fontSize: 10 }} width={80} />
              <RechartsTooltip contentStyle={customTooltipStyle} />
              <Bar dataKey="count" fill="#54d5a5" radius={[0, 4, 4, 0]} isAnimationActive={true} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="card chart-card full-width-chart">
        <div className="card-heading">
          <div>
            <p className="eyebrow">BEHAVIORAL SPECTRUM</p>
            <h2>Attack Archetypes</h2>
          </div>
        </div>
        <div style={{ width: '100%', height: 210, padding: '10px 15px' }}>
          <ResponsiveContainer>
            <PieChart>
              <Pie data={archetypeChartData} dataKey="value" innerRadius={40} outerRadius={75} isAnimationActive={true}>
                {archetypeChartData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <RechartsTooltip contentStyle={customTooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  )
})
