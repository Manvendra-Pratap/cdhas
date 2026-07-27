import { memo, useState } from 'react'
import { CountryFlag } from './CountryFlag'
import { Badge } from './Badge'

export const NotificationCenter = memo(function NotificationCenter({ notifications, onDismiss, onMarkAllRead }) {
  const [open, setOpen] = useState(false)
  const unread = notifications.filter((n) => !n.read).length

  return (
    <div className="notif-wrapper">
      <button
        className="notification-button"
        onClick={() => setOpen(!open)}
        aria-label={`Notifications, ${unread} unread`}
        aria-expanded={open}
      >
        ♢
        {unread > 0 && <span className="notif-badge">{unread}</span>}
      </button>

      {open && (
        <div className="notif-panel" role="dialog" aria-label="Notifications panel">
          <div className="notif-panel-header">
            <h3>Notifications</h3>
            {unread > 0 && (
              <button className="text-button" onClick={onMarkAllRead}>
                Mark all read
              </button>
            )}
          </div>
          <div className="notif-list">
            {notifications.length === 0 ? (
              <div className="notif-empty">No notifications</div>
            ) : (
              notifications.map((n) => (
                <div key={n.id} className={`notif-item ${n.severity === 'Critical' ? 'notif-critical' : ''}`}>
                  <div className="notif-item-top">
                    <CountryFlag code={n.flag} country={n.country} />
                    <strong>{n.ip}</strong>
                    <Badge severity={n.severity} />
                    <button className="dismiss-notif" onClick={() => onDismiss(n.id)} aria-label="Dismiss notification">×</button>
                  </div>
                  <div className="notif-item-body">
                    <span>{n.archetype}</span> · <small>{n.time}</small>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
})

export const ToastContainer = memo(function ToastContainer({ toasts, onDismiss }) {
  return (
    <div className="toast-container" role="region" aria-label="Live attack alerts">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`toast-card ${toast.severity === 'Critical' ? 'toast-critical' : ''}`}
          role="alert"
        >
          <button className="toast-close" onClick={() => onDismiss(toast.id)} aria-label="Dismiss alert">×</button>
          <div className="toast-header">
            <span className="toast-alert-mark">!</span>
            <strong>{toast.severity === 'Critical' ? 'CRITICAL ATTACK ALERT' : 'New Attack Session'}</strong>
          </div>
          <div className="toast-content">
            <div className="toast-row">
              <CountryFlag code={toast.flag} country={toast.country} />
              <strong>{toast.ip}</strong> ({toast.country})
            </div>
            <div className="toast-row">
              <Badge severity={toast.severity} />
              <span className="toast-archetype">{toast.archetype}</span>
              <span className="toast-time">{toast.time}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
})
