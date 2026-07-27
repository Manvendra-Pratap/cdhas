import { memo } from 'react'
import { CountryFlag } from './CountryFlag'
import { Badge } from './Badge'

function formatTime(value) {
  if (!value) return '--:--'
  try {
    return new Intl.DateTimeFormat('en', { hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date(value))
  } catch {
    return '--:--'
  }
}

export const SessionTable = memo(function SessionTable({ sessions, onSelect, limit, selectedId }) {
  const rows = limit ? sessions.slice(0, limit) : sessions

  return (
    <section className="card sessions-card">
      <div className="card-heading">
        <div>
          <p className="eyebrow">LIVE FEED</p>
          <h2>{limit ? 'Recent sessions' : 'All sessions'}</h2>
        </div>
        {limit && (
          <button className="text-button" onClick={() => onSelect('all')} aria-label="View all sessions">
            View all <span>→</span>
          </button>
        )}
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Source</th>
              <th>Started</th>
              <th>Duration</th>
              <th>Commands</th>
              <th>Archetype</th>
              <th>Risk</th>
              <th aria-label="Open session" />
            </tr>
          </thead>
          <tbody>
            {rows.map((session) => (
              <tr
                key={session.id}
                className={selectedId === session.id ? 'selected-row' : ''}
                onClick={() => onSelect(session)}
                tabIndex={0}
                onKeyDown={(event) => event.key === 'Enter' && onSelect(session)}
                aria-label={`Session from ${session.ip}, ${session.country}`}
              >
                <td>
                  <div className="source-cell">
                    <CountryFlag code={session.flag} country={session.country} />
                    <div>
                      <strong>{session.ip}</strong>
                      <small>{session.city}, {session.country}</small>
                    </div>
                  </div>
                </td>
                <td>{formatTime(session.startedAt)}</td>
                <td>{session.duration}</td>
                <td>{session.commands ? session.commands.length : 0}</td>
                <td><span className="archetype-label">{session.archetype}</span></td>
                <td><Badge severity={session.severity} /></td>
                <td className="open-cell">→</td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td className="empty-cell" colSpan="7">No sessions match the selected filters.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
})
