import { memo, useState, useEffect } from 'react'
import { CountryFlag } from './CountryFlag'
import { Badge } from './Badge'
import { RiskGauge } from './RiskGauge'

function formatTime(value) {
  if (!value) return '--:--'
  try {
    return new Intl.DateTimeFormat('en', { hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date(value))
  } catch {
    return '--:--'
  }
}

export const SessionDrawer = memo(function SessionDrawer({ session, onClose }) {
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (!session) return null

  const commands = session.commands || []
  const copyCommands = () => {
    if (commands.length > 0) {
      navigator.clipboard.writeText(commands.join('\n'))
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const downloadedUrls = commands.flatMap((c) => {
    const matches = c.match(/(https?:\/\/[^\s"']+)/g)
    return matches || []
  })

  const executedFiles = commands.flatMap((c) => {
    const files = []
    if (c.includes('./')) files.push(c.split('./')[1]?.split(' ')[0])
    if (c.includes('chmod +x')) files.push(c.split('chmod +x')[1]?.trim()?.split(' ')[0])
    return files.filter(Boolean)
  })

  const privilegeEscalation = commands.some((c) =>
    c.includes('sudo') || c.includes('su') || c.includes('shadow') || c.includes('passwd') || c.includes('pty.spawn')
  )

  const mitreMapping = []
  if (commands.some((c) => c.includes('uname') || c.includes('whoami') || c.includes('id') || c.includes('cpuinfo'))) {
    mitreMapping.push({ id: 'T1082', name: 'System Information Discovery' })
  }
  if (commands.some((c) => c.includes('curl') || c.includes('wget') || c.includes('busybox'))) {
    mitreMapping.push({ id: 'T1105', name: 'Ingress Tool Transfer' })
  }
  if (commands.some((c) => c.includes('shadow') || c.includes('passwd'))) {
    mitreMapping.push({ id: 'T1003', name: 'OS Credential Dumping' })
  }
  if (privilegeEscalation) {
    mitreMapping.push({ id: 'T1548', name: 'Abuse Elevation Control' })
  }
  if (mitreMapping.length === 0) {
    mitreMapping.push({ id: 'T1059.004', name: 'Unix Shell Execution' })
  }

  const categories = []
  if (commands.some((c) => c.includes('curl') || c.includes('wget'))) categories.push('File Fetch')
  if (privilegeEscalation) categories.push('Privilege Escalation')
  if (commands.some((c) => c.includes('ls') || c.includes('pwd') || c.includes('whoami'))) categories.push('Reconnaissance')

  return (
    <div className="drawer-layer" role="presentation" onMouseDown={onClose}>
      <aside
        className="session-drawer"
        role="dialog"
        aria-modal="true"
        aria-label="Session details drawer"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <button className="close-button" onClick={onClose} aria-label="Close session details drawer">×</button>
        <p className="eyebrow">SESSION DRILLDOWN</p>
        
        <div className="drawer-header-row">
          <div className="drawer-title">
            <CountryFlag code={session.flag} country={session.country} />
            <div>
              <h2>{session.ip}</h2>
              <p>{session.city}, {session.country}</p>
            </div>
          </div>
          <RiskGauge score={session.score} />
        </div>

        <div className="drawer-badges">
          <Badge severity={session.severity} />
          <span className="status-pill">{session.status}</span>
          {privilegeEscalation && <span className="priv-badge">⚠️ Priv Escalation</span>}
        </div>

        <dl className="details-grid">
          <div><dt>Session ID</dt><dd>{session.id}</dd></div>
          <div><dt>Protocol</dt><dd>{session.protocol}</dd></div>
          <div><dt>Started</dt><dd>{new Date(session.startedAt).toLocaleString()}</dd></div>
          <div><dt>Duration</dt><dd>{session.duration}</dd></div>
          <div><dt>Username</dt><dd>{session.username}</dd></div>
          <div><dt>Unique Cmds</dt><dd>{new Set(commands).size} / {commands.length}</dd></div>
        </dl>

        <section className="drawer-section">
          <p className="eyebrow">MITRE ATT&CK MAPPING</p>
          <div className="mitre-tags">
            {mitreMapping.map((m) => (
              <span key={m.id} className="mitre-tag" title={m.name}>
                <strong>{m.id}</strong> {m.name}
              </span>
            ))}
          </div>
        </section>

        {(downloadedUrls.length > 0 || executedFiles.length > 0) && (
          <section className="drawer-section">
            <p className="eyebrow">ARTIFACT & IOCS</p>
            {downloadedUrls.length > 0 && (
              <div className="artifact-group">
                <small>Downloaded URLs:</small>
                {downloadedUrls.map((url, i) => (
                  <code key={i} className="url-code">{url}</code>
                ))}
              </div>
            )}
            {executedFiles.length > 0 && (
              <div className="artifact-group">
                <small>Executed Binaries/Scripts:</small>
                {executedFiles.map((file, i) => (
                  <span key={i} className="file-chip">⚙️ {file}</span>
                ))}
              </div>
            )}
          </section>
        )}

        <section className="drawer-section">
          <p className="eyebrow">ATTACK TIMELINE STEPS</p>
          <ol className="step-timeline">
            <li><span className="step-num">01</span> Session Connected ({formatTime(session.startedAt)})</li>
            <li><span className="step-num">02</span> Auth Attempt (User: <code>{session.username}</code>)</li>
            <li><span className="step-num">03</span> Command Execution ({commands.length} inputs)</li>
            <li><span className="step-num">04</span> Session Closed ({session.duration})</li>
          </ol>
        </section>

        <section className="command-panel">
          <div className="command-header">
            <div>
              <p className="eyebrow">COMMAND SEQUENCE</p>
              <h3>{commands.length} commands observed</h3>
            </div>
            <button className="copy-button" onClick={copyCommands}>
              {copied ? 'Copied ✓' : 'Copy sequence'}
            </button>
          </div>
          {categories.length > 0 && (
            <div className="cat-chips">
              {categories.map((c) => <span key={c} className="cat-chip">{c}</span>)}
            </div>
          )}
          <ol>
            {commands.map((command, index) => (
              <li key={index}>
                <span>{String(index + 1).padStart(2, '0')}</span>
                <code>{command}</code>
              </li>
            ))}
          </ol>
        </section>

        <section className="classification">
          <p className="eyebrow">BEHAVIORAL CLASSIFICATION</p>
          <h3>{session.archetype}</h3>
          <p>Classification is derived from session duration, command sequence, authentication behavior, and anomaly score.</p>
        </section>
      </aside>
    </div>
  )
})
