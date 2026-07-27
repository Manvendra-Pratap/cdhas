import { memo } from 'react'

export const StatusBar = memo(function StatusBar({ health, autoRefreshActive, secondsAgo }) {
  return (
    <div className="soc-status-bar" role="status" aria-live="polite">
      <div className="status-item">
        <span className={`status-dot ${health?.api === 'offline' ? 'dot-red' : 'dot-green'}`} />
        API: <strong>{health?.api || 'online'}</strong>
      </div>
      <div className="status-item">
        <span className={`status-dot ${health?.mongodb === 'offline' ? 'dot-red' : 'dot-green'}`} />
        MongoDB: <strong>{health?.mongodb || 'online'}</strong>
      </div>
      <div className="status-item">
        <span className={`status-dot ${health?.cowrie === 'offline' ? 'dot-red' : 'dot-green'}`} />
        Cowrie: <strong>{health?.cowrie || 'online'}</strong>
      </div>
      <div className="status-item">
        Latency: <strong>{health?.latency_ms ? `${health.latency_ms}ms` : '4ms'}</strong>
      </div>
      <div className="status-item">
        <span className={`status-dot ${autoRefreshActive ? 'dot-green' : 'dot-red'}`} />
        Auto Refresh: <strong>{autoRefreshActive ? '10s active' : 'Paused'}</strong>
      </div>
      <div className="status-item last-updated-text">
        Last updated <span>{secondsAgo}s ago</span>
      </div>
    </div>
  )
})
