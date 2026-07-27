import { memo } from 'react'

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
