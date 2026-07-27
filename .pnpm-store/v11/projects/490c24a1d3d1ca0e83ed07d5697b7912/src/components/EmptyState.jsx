import { memo } from 'react'

export const EmptyState = memo(function EmptyState({ onRefresh }) {
  return (
    <section className="card empty-state-card" role="status" aria-live="polite">
      <svg className="empty-shield-icon" viewBox="0 0 24 24" fill="none" stroke="#4aadff" strokeWidth="1.5">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        <path d="M9 12l2 2 4-4" stroke="#54d5a5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <h2>No attacks detected</h2>
      <p>Your deception network has not captured any active attack sessions in this time window.</p>
      <button className="primary-button" onClick={onRefresh} aria-label="Refresh telemetry feed">
        Refresh telemetry feed
      </button>
    </section>
  )
})

export const ErrorPanel = memo(function ErrorPanel({ onRetry }) {
  return (
    <main className="error-screen" role="alert">
      <div className="error-mark">!</div>
      <h1>Security Operations Backend Offline</h1>
      <p>Could not connect to the CDHAS FastAPI backend on port 8000. Ensure the API server is active.</p>
      <div className="error-checklist">
        <div><span>•</span> FastAPI server on <code>http://localhost:8000</code></div>
        <div><span>•</span> CORS policy & Vite proxy forwarding</div>
        <div><span>•</span> MongoDB daemon / local database instance</div>
      </div>
      <button className="primary-button" onClick={onRetry} aria-label="Retry connection to backend API">
        Retry connection
      </button>
    </main>
  )
})
