import { useState, lazy, Suspense, useCallback } from 'react'
import { Sidebar } from './components/Sidebar'
import { StatusBar } from './components/StatusBar'
import { NotificationCenter, ToastContainer } from './components/NotificationCenter'
import { SessionDrawer } from './components/SessionDrawer'
import { LoadingPanel } from './components/SkeletonLoaders'
import { ErrorPanel } from './components/ErrorPanel'
import { useDashboardData } from './hooks/useDashboardData'

// Lazy loading views for code splitting
const OverviewView = lazy(() => import('./views/OverviewView'))
const TimelineView = lazy(() => import('./views/TimelineView'))
const SessionsView = lazy(() => import('./views/SessionsView'))
const IntelligenceView = lazy(() => import('./views/IntelligenceView'))

const navLabels = {
  overview: 'Overview',
  timeline: 'Attack timeline',
  sessions: 'Sessions',
  intelligence: 'Intelligence',
}

export default function App() {
  const [active, setActive] = useState('overview')
  const [selectedSession, setSelectedSession] = useState(null)
  const [countryFilter, setCountryFilter] = useState('')

  const {
    data,
    error,
    refreshing,
    secondsAgo,
    notifications,
    toasts,
    refresh,
    load,
    dismissNotification,
    markAllNotificationsRead,
    dismissToast,
  } = useDashboardData()

  const handleSelectCountry = useCallback((country) => {
    setCountryFilter(country)
    setActive('sessions')
  }, [])

  const handleCloseDrawer = useCallback(() => {
    setSelectedSession(null)
  }, [])

  if (!data && !error) return <LoadingPanel />
  if (error) return <ErrorPanel onRetry={() => load(false)} />

  return (
    <div className="app-shell">
      <Sidebar active={active} setActive={setActive} />
      
      <div className="content-shell">
        <header className="topbar" role="banner">
          <div className="crumb">
            CDHAS <span>/</span> <strong>{navLabels[active]}</strong>
          </div>
          <div className="top-actions">
            <span className="api-badge" title="FastAPI REST Backend Connected">
              <i className="status-dot" /> API Live
            </span>

            <button
              className={`refresh-button ${refreshing ? 'spinning' : ''}`}
              onClick={refresh}
              aria-label="Refresh telemetry feed"
              title={`Last updated ${secondsAgo}s ago`}
            >
              ↻
            </button>

            <NotificationCenter
              notifications={notifications}
              onDismiss={dismissNotification}
              onMarkAllRead={markAllNotificationsRead}
            />

            <div className="avatar" aria-label="User profile avatar">AA</div>
          </div>
        </header>

        <StatusBar
          health={data.health}
          autoRefreshActive={true}
          secondsAgo={secondsAgo}
        />

        <main className="page-content" role="main">
          <Suspense fallback={<LoadingPanel />}>
            {active === 'overview' && (
              <OverviewView
                data={data}
                onSession={setSelectedSession}
                onViewSessions={() => setActive('sessions')}
                onSelectCountry={handleSelectCountry}
                onRefresh={refresh}
              />
            )}
            {active === 'timeline' && <TimelineView data={data} />}
            {active === 'sessions' && (
              <SessionsView
                sessions={data.sessions}
                onSession={setSelectedSession}
                selectedSession={selectedSession}
                initialCountryFilter={countryFilter}
              />
            )}
            {active === 'intelligence' && (
              <IntelligenceView
                intelligence={data.intelligence}
                sessions={data.sessions}
                timeline={data.timeline}
              />
            )}
          </Suspense>
        </main>
      </div>

      <ToastContainer toasts={toasts} onDismiss={dismissToast} />

      <SessionDrawer session={selectedSession} onClose={handleCloseDrawer} />
    </div>
  )
}
