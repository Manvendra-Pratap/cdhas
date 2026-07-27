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
  LineChart,
  Line,
} from 'recharts'
import { CountryFlag } from '../components/CountryFlag'
import { Badge } from '../components/Badge'

const severityOrder = { Critical: 4, High: 3, Medium: 2, Low: 1 }

export default memo(function IntelligenceView({ intelligence, sessions, timeline }) {
  const highPrioritySessions = useMemo(() => sessions.filter((session) => severityOrder[session.severity] >= 3), [sessions])

  const kpis = useMemo(() => {
    const total = sessions.length || 1
    const highestThreat = sessions.slice().sort((a, b) => (b.score || 0) - (a.score || 0))[0] || { archetype: 'Post-exploitation', score: 0.96 }
    
    const countryCounts = {}
    sessions.forEach((s) => { countryCounts[s.country] = (countryCounts[s.country] || 0) + 1 })
    const mostActiveCountry = Object.entries(countryCounts).sort((a, b) => b[1] - a[1])[0] || ['India', 248]

    const avgRisk = Math.round((sessions.reduce((acc, s) => acc + (s.score || 0.5), 0) / total) * 100)
    
    const archetypeCounts = {}
    sessions.forEach((s) => { archetypeCounts[s.archetype] = (archetypeCounts[s.archetype] || 0) + 1 })
    const mostCommonArch = Object.entries(archetypeCounts).sort((a, b) => b[1] - a[1])[0] || ['Reconnaissance bot', 502]
    const mostCommonShare = Math.round((mostCommonArch[1] / total) * 100)

    const latestCritical = sessions.find((s) => s.severity === 'Critical') || sessions[0]

    const ipCounts = {}
    sessions.forEach((s) => { ipCounts[s.ip] = (ipCounts[s.ip] || 0) + 1 })
    const topAttackerIp = Object.entries(ipCounts).sort((a, b) => b[1] - a[1])[0] || ['185.220.101.42', 14]

    return {
      highestThreat: highestThreat.archetype,
      highestScore: `${Math.round(highestThreat.score * 100)}%`,
      mostActiveCountry: mostActiveCountry[0],
      mostActiveCount: mostActiveCountry[1],
      avgRisk: `${avgRisk}%`,
      mostCommonAttack: mostCommonArch[0],
      mostCommonShare: `${mostCommonShare}%`,
      latestCriticalIp: latestCritical.ip,
      latestCriticalCountry: latestCritical.country,
      topAttackerIp: topAttackerIp[0],
      topAttackerCount: `${topAttackerIp[1]} sessions`,
    }
  }, [sessions])

  const threatTrend = useMemo(() => {
    return (timeline || []).map((t) => ({
      time: t.time,
      threatScore: Math.min(100, Math.round(t.sessions * 0.9 + t.anomalies * 5)),
      anomalies: t.anomalies,
    }))
  }, [timeline])

  const riskDist = useMemo(() => {
    const counts = { Critical: 0, High: 0, Medium: 0, Low: 0 }
    sessions.forEach((s) => { counts[s.severity] = (counts[s.severity] || 0) + 1 })
    return [
      { name: 'Critical', value: counts.Critical, color: '#ef7f88' },
      { name: 'High', value: counts.High, color: '#f4bf75' },
      { name: 'Medium', value: counts.Medium, color: '#4aadff' },
      { name: 'Low', value: counts.Low, color: '#54d5a5' },
    ]
  }, [sessions])

  const topMalware = [
    { family: 'Mirai Botnet', count: 184, share: 38 },
    { family: 'Bashlite / Gafgyt', count: 126, share: 26 },
    { family: 'CoinMiner Script', count: 89, share: 18 },
    { family: 'SSH-Brute Hydra', count: 54, share: 11 },
    { family: 'Tsunami Downloader', count: 32, share: 7 },
  ]

  const dangerousIPs = useMemo(() => {
    const ipMap = {}
    sessions.forEach((s) => {
      if (!ipMap[s.ip]) {
        ipMap[s.ip] = { ip: s.ip, country: s.country, flag: s.flag, score: s.score, severity: s.severity, count: 0 }
      }
      ipMap[s.ip].count += 1
      if (s.score > ipMap[s.ip].score) ipMap[s.ip].score = s.score
    })
    return Object.values(ipMap).sort((a, b) => b.score - a.score).slice(0, 5)
  }, [sessions])

  const commandCatData = [
    { category: 'System Discovery', count: 342, pct: 42 },
    { category: 'File Fetching (curl/wget)', count: 218, pct: 27 },
    { category: 'Privilege Escalation', count: 145, pct: 18 },
    { category: 'Credential Access', count: 104, pct: 13 },
  ]

  const protocolData = [
    { name: 'SSH', value: 78, color: '#4aadff' },
    { name: 'Telnet', value: 16, color: '#8d7cff' },
    { name: 'HTTP', value: 6, color: '#54d5a5' },
  ]

  const heatmapGrid = [
    { slot: '00:00 - 04:00', intensity: 3, label: 'Moderate' },
    { slot: '04:00 - 08:00', intensity: 5, label: 'High' },
    { slot: '08:00 - 12:00', intensity: 8, label: 'Critical' },
    { slot: '12:00 - 16:00', intensity: 10, label: 'Peak Peak' },
    { slot: '16:00 - 20:00', intensity: 6, label: 'High' },
    { slot: '20:00 - 24:00', intensity: 4, label: 'Moderate' },
  ]

  const customTooltipStyle = {
    backgroundColor: '#0c2033',
    borderColor: '#214059',
    color: '#dbe8f1',
    fontSize: '11px',
    borderRadius: '6px',
  }

  return (
    <div className="page-view-fade">
      <div className="page-heading">
        <div>
          <p className="eyebrow">BEHAVIOR ANALYSIS & THREAT INTELLIGENCE</p>
          <h1>Attacker intelligence dashboard</h1>
          <p className="subheading">AI classification, threat trends, dangerous vectors, and risk telemetry.</p>
        </div>
        <div className="model-chip"><span className="status-dot" />AI Analytics Engine v2.4</div>
      </div>

      <section className="metric-grid">
        <article className="metric-card metric-coral">
          <div className="metric-icon">▲</div>
          <p>Highest Threat</p>
          <strong>{kpis.highestThreat}</strong>
          <small>{kpis.highestScore} Anomaly Score</small>
        </article>

        <article className="metric-card metric-violet">
          <div className="metric-icon">◎</div>
          <p>Most Active Country</p>
          <strong>{kpis.mostActiveCountry}</strong>
          <small>{kpis.mostActiveCount} Sessions</small>
        </article>

        <article className="metric-card metric-blue">
          <div className="metric-icon">◫</div>
          <p>Average Risk Score</p>
          <strong>{kpis.avgRisk}</strong>
          <small>Network Baseline 64%</small>
        </article>

        <article className="metric-card metric-green">
          <div className="metric-icon">◉</div>
          <p>Most Common Attack</p>
          <strong>{kpis.mostCommonAttack}</strong>
          <small>{kpis.mostCommonShare} of Total</small>
        </article>

        <article className="metric-card metric-coral">
          <div className="metric-icon">⚡</div>
          <p>Latest Critical Session</p>
          <strong>{kpis.latestCriticalIp}</strong>
          <small>{kpis.latestCriticalCountry}</small>
        </article>

        <article className="metric-card metric-blue">
          <div className="metric-icon">🛡️</div>
          <p>Top Attacker IP</p>
          <strong>{kpis.topAttackerIp}</strong>
          <small>{kpis.topAttackerCount}</small>
        </article>
      </section>

      <section className="card threat-score-card">
        <div className="threat-score-inner">
          <div className="threat-score-box">
            <span className="eyebrow">GLOBAL THREAT SCORE</span>
            <div className="threat-score-val">78<span>/100</span></div>
            <p>Elevated threat activity detected across Honeypot Sensors</p>
          </div>
          <div className="threat-confidence-box">
            <span className="eyebrow">AI CLASSIFICATION CONFIDENCE</span>
            <div className="confidence-bar-wrap">
              <strong>94.2%</strong>
              <div className="bar-track"><i style={{ width: '94.2%', background: '#54d5a5' }} /></div>
            </div>
            <p>High precision pattern recognition enabled</p>
          </div>
        </div>
      </section>

      <div className="charts-section-grid" style={{ marginBottom: 22 }}>
        <section className="card chart-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">TEMPORAL ANALYSIS</p>
              <h2>Threat Index Trend (24 Hours)</h2>
            </div>
          </div>
          <div style={{ width: '100%', height: 220, padding: '10px 15px' }}>
            <ResponsiveContainer>
              <LineChart data={threatTrend}>
                <XAxis dataKey="time" tick={{ fill: '#7890a8', fontSize: 10 }} />
                <YAxis tick={{ fill: '#7890a8', fontSize: 10 }} />
                <RechartsTooltip contentStyle={customTooltipStyle} />
                <Line type="monotone" dataKey="threatScore" stroke="#ef7f88" strokeWidth={2.5} dot={{ r: 3, fill: '#ef7f88' }} isAnimationActive={true} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="card chart-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">SEVERITY ALLOCATION</p>
              <h2>Risk Level Distribution</h2>
            </div>
          </div>
          <div style={{ width: '100%', height: 220, padding: '10px 15px' }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={riskDist} innerRadius={45} outerRadius={75} dataKey="value" isAnimationActive={true}>
                  {riskDist.map((entry) => (
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
              <p className="eyebrow">PAYLOAD CLASSIFICATION</p>
              <h2>Top Malware Families</h2>
            </div>
          </div>
          <div style={{ padding: '15px 23px' }}>
            {topMalware.map((mal) => (
              <div key={mal.family} className="malware-row">
                <div className="malware-top">
                  <strong>{mal.family}</strong>
                  <span>{mal.count} sessions ({mal.share}%)</span>
                </div>
                <div className="bar-track"><i style={{ width: `${mal.share}%`, background: '#f4bf75' }} /></div>
              </div>
            ))}
          </div>
        </section>

        <section className="card chart-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">VECTOR ANALYSIS</p>
              <h2>Protocol Usage breakdown</h2>
            </div>
          </div>
          <div style={{ width: '100%', height: 220, padding: '10px 15px' }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={protocolData} dataKey="value" outerRadius={75} isAnimationActive={true}>
                  {protocolData.map((entry) => (
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
              <p className="eyebrow">HIGH RISK THREAT ACTORS</p>
              <h2>Most Dangerous IPs</h2>
            </div>
          </div>
          <div style={{ padding: '10px 23px 20px' }}>
            <div className="dangerous-ip-list">
              {dangerousIPs.map((ipItem) => (
                <div key={ipItem.ip} className="dangerous-ip-row">
                  <CountryFlag code={ipItem.flag} country={ipItem.country} />
                  <div>
                    <strong>{ipItem.ip}</strong>
                    <small>{ipItem.country} · {ipItem.count} sessions</small>
                  </div>
                  <Badge severity={ipItem.severity} />
                  <div className="ip-risk-score">{Math.round(ipItem.score * 100)}%</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="card chart-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">ATTACK DENSITY</p>
              <h2>Hourly Attack Heat Map</h2>
            </div>
          </div>
          <div style={{ padding: '15px 23px' }}>
            <div className="heatmap-grid">
              {heatmapGrid.map((h) => (
                <div
                  key={h.slot}
                  className={`heatmap-cell heat-lvl-${h.intensity}`}
                  title={`${h.slot}: ${h.label} attack intensity`}
                >
                  <small>{h.slot}</small>
                  <strong>{h.label}</strong>
                </div>
              ))}
            </div>
            <div className="cmd-cat-section" style={{ marginTop: 20 }}>
              <p className="eyebrow" style={{ marginBottom: 10 }}>TOP COMMAND CATEGORIES</p>
              {commandCatData.map((cat) => (
                <div key={cat.category} className="cat-progress-row">
                  <span>{cat.category}</span>
                  <div className="bar-track"><i style={{ width: `${cat.pct}%`, background: '#4aadff' }} /></div>
                  <small>{cat.pct}%</small>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>

      <div className="intelligence-layout">
        <section className="card archetype-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">CLUSTER DISTRIBUTION</p>
              <h2>Observed archetypes</h2>
            </div>
          </div>
          {intelligence.map((item) => (
            <div className="archetype-row" key={item.label}>
              <div className="archetype-top">
                <span><i style={{ background: item.color }} />{item.label}</span>
                <strong>{item.share}%</strong>
              </div>
              <div className="bar-track">
                <i style={{ width: `${item.share}%`, background: item.color }} />
              </div>
              <small>{item.sessions} sessions · {item.description}</small>
            </div>
          ))}
        </section>

        <section className="card risk-card">
          <p className="eyebrow">RISK QUEUE</p>
          <h2>Sessions needing review</h2>
          <div className="risk-number">{highPrioritySessions.length}<span> high priority</span></div>
          <p>These sessions show activity inconsistent with baseline reconnaissance behavior.</p>
          <div className="risk-list">
            {highPrioritySessions.map((session) => (
              <div key={session.id}>
                <Badge severity={session.severity} />
                <span>{session.ip}</span>
                <small>{session.archetype}</small>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
})
