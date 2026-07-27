import { memo } from 'react'

const navItems = [
  { id: 'overview', label: 'Overview', icon: '▦' },
  { id: 'timeline', label: 'Attack timeline', icon: '⌁' },
  { id: 'sessions', label: 'Sessions', icon: '◫' },
  { id: 'intelligence', label: 'Intelligence', icon: '◇' },
]

export const Sidebar = memo(function Sidebar({ active, setActive }) {
  return (
    <aside className="sidebar" aria-label="Main Navigation">
      <div className="brand">
        <div className="brand-mark"><i /><i /><i /></div>
        <span>CDHAS</span>
      </div>
      <p className="workspace-label">SECURITY OPERATIONS</p>
      <nav aria-label="Dashboard sections">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${active === item.id ? 'active' : ''}`}
            onClick={() => setActive(item.id)}
            aria-current={active === item.id ? 'page' : undefined}
          >
            <span>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="sensor-state">
          <span className="status-dot" />
          Cowrie sensor <strong>online</strong>
        </div>
        <button
          className="help-link"
          onClick={() => alert('CDHAS Monitoring System: Live honeypot session capture and threat intelligence.')}
          aria-label="Open Dashboard Guide"
        >
          ? &nbsp;Dashboard guide
        </button>
      </div>
    </aside>
  )
})
