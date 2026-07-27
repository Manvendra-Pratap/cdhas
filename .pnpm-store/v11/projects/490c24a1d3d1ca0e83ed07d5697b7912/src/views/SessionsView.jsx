import { memo, useState, useEffect, useMemo, useCallback } from 'react'
import { api } from '../api/client'
import { SessionTable } from '../components/SessionTable'

export default memo(function SessionsView({ sessions, onSession, selectedSession, initialCountryFilter = '' }) {
  const [globalSearch, setGlobalSearch] = useState('')
  const [country, setCountry] = useState('')
  const [severity, setSeverity] = useState('All')
  const [protocol, setProtocol] = useState('')
  const [username, setUsername] = useState('')
  const [archetype, setArchetype] = useState('')
  const [cmdQuery, setCmdQuery] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [pageSize, setPageSize] = useState(20)

  const [page, setPage] = useState(1)
  const [result, setResult] = useState({ items: sessions, total: sessions.length, page: 1, page_size: 20 })
  const [loading, setLoading] = useState(false)
  const [requestError, setRequestError] = useState('')

  const countriesList = useMemo(() => [...new Set(sessions.map((s) => s.country))], [sessions])
  const archetypesList = useMemo(() => [...new Set(sessions.map((s) => s.archetype))], [sessions])
  const usernamesList = useMemo(() => [...new Set(sessions.map((s) => s.username).filter(Boolean))], [sessions])

  const loadPage = useCallback(async (targetPage = 1, currentFilters = {}) => {
    setLoading(true)
    setRequestError('')
    try {
      const activeGlobal = currentFilters.globalSearch !== undefined ? currentFilters.globalSearch : globalSearch
      const activeCountry = currentFilters.country !== undefined ? currentFilters.country : country
      const activeSeverity = currentFilters.severity !== undefined ? currentFilters.severity : severity
      const activeProtocol = currentFilters.protocol !== undefined ? currentFilters.protocol : protocol
      const activeUsername = currentFilters.username !== undefined ? currentFilters.username : username
      const activeArchetype = currentFilters.archetype !== undefined ? currentFilters.archetype : archetype
      const activeCmd = currentFilters.cmdQuery !== undefined ? currentFilters.cmdQuery : cmdQuery
      const activeStart = currentFilters.startTime !== undefined ? currentFilters.startTime : startTime
      const activeEnd = currentFilters.endTime !== undefined ? currentFilters.endTime : endTime
      const activePageSize = currentFilters.pageSize !== undefined ? currentFilters.pageSize : pageSize

      const queryParams = {
        page: targetPage,
        page_size: activePageSize,
        ip: activeGlobal,
        country: activeCountry,
        severity: activeSeverity,
        protocol: activeProtocol,
        username: activeUsername,
        archetype: activeArchetype,
        command: activeCmd,
        start_time: activeStart,
        end_time: activeEnd,
      }

      const nextResult = await api.getSessions(queryParams)
      setResult(nextResult)
      setPage(nextResult.page)
    } catch {
      setRequestError('Could not load sessions. Check the API connection and try again.')
    } finally {
      setLoading(false)
    }
  }, [globalSearch, country, severity, protocol, username, archetype, cmdQuery, startTime, endTime, pageSize])

  useEffect(() => {
    if (initialCountryFilter) {
      setCountry(initialCountryFilter)
      loadPage(1, { country: initialCountryFilter })
    }
  }, [initialCountryFilter, loadPage])

  const handleFilterChange = (setter, key) => (e) => {
    const val = e.target.value
    setter(val)
    loadPage(1, { [key]: val })
  }

  const resetFilters = useCallback(() => {
    setGlobalSearch('')
    setCountry('')
    setSeverity('All')
    setProtocol('')
    setUsername('')
    setArchetype('')
    setCmdQuery('')
    setStartTime('')
    setEndTime('')
    loadPage(1, {
      globalSearch: '',
      country: '',
      severity: 'All',
      protocol: '',
      username: '',
      archetype: '',
      cmdQuery: '',
      startTime: '',
      endTime: '',
    })
  }, [loadPage])

  const exportCSV = useCallback(() => {
    const headers = ['ID,IP,Country,City,Severity,Score,Archetype,Username,Protocol,StartedAt,Duration,CommandsCount']
    const rows = result.items.map((s) =>
      `"${s.id}","${s.ip}","${s.country}","${s.city}","${s.severity}",${s.score},"${s.archetype}","${s.username}","${s.protocol}","${s.startedAt}","${s.duration}",${s.commands ? s.commands.length : 0}`
    )
    const blob = new Blob([[headers, ...rows].join('\n')], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `cdhas_sessions_${Date.now()}.csv`
    a.click()
  }, [result.items])

  const exportJSON = useCallback(() => {
    const blob = new Blob([JSON.stringify(result.items, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `cdhas_sessions_${Date.now()}.json`
    a.click()
  }, [result.items])

  const exportPDF = useCallback(() => {
    window.print()
  }, [])

  const pageCount = Math.max(1, Math.ceil(result.total / result.page_size))
  const startItem = (page - 1) * result.page_size + 1
  const endItem = Math.min(result.total, page * result.page_size)

  return (
    <div className="page-view-fade">
      <div className="page-heading">
        <div>
          <p className="eyebrow">SESSION EXPLORER</p>
          <h1>Captured sessions</h1>
          <p className="subheading">Search, assess, and drill into attacker interactions.</p>
        </div>
        <div className="export-actions">
          <button className="export-btn" onClick={exportCSV} title="Export CSV" aria-label="Export sessions as CSV">📄 CSV</button>
          <button className="export-btn" onClick={exportJSON} title="Export JSON" aria-label="Export sessions as JSON">📦 JSON</button>
          <button className="export-btn" onClick={exportPDF} title="Print / Save PDF" aria-label="Print or save as PDF">🖨️ PDF</button>
        </div>
      </div>

      <form className="advanced-filter-row" onSubmit={(e) => e.preventDefault()}>
        <label className="search-field full-search">
          <span>⌕</span>
          <input
            value={globalSearch}
            onChange={handleFilterChange(setGlobalSearch, 'globalSearch')}
            placeholder="Global search (IP, Country, Username, Archetype...)"
            aria-label="Global session search"
          />
        </label>

        <label className="filter-select">
          <span>Country</span>
          <select value={country} onChange={handleFilterChange(setCountry, 'country')} aria-label="Filter by Country">
            <option value="">All Countries</option>
            {countriesList.map((c) => <option value={c} key={c}>{c}</option>)}
          </select>
        </label>

        <label className="filter-select">
          <span>Severity</span>
          <select value={severity} onChange={handleFilterChange(setSeverity, 'severity')} aria-label="Filter by Severity">
            <option value="All">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </label>

        <label className="filter-select">
          <span>Protocol</span>
          <select value={protocol} onChange={handleFilterChange(setProtocol, 'protocol')} aria-label="Filter by Protocol">
            <option value="">All Protocols</option>
            <option value="SSH">SSH</option>
            <option value="Telnet">Telnet</option>
            <option value="HTTP">HTTP</option>
          </select>
        </label>

        <label className="filter-select">
          <span>Username</span>
          <select value={username} onChange={handleFilterChange(setUsername, 'username')} aria-label="Filter by Username">
            <option value="">All Usernames</option>
            {usernamesList.map((u) => <option value={u} key={u}>{u}</option>)}
          </select>
        </label>

        <label className="filter-select">
          <span>Archetype</span>
          <select value={archetype} onChange={handleFilterChange(setArchetype, 'archetype')} aria-label="Filter by Archetype">
            <option value="">All Archetypes</option>
            {archetypesList.map((item) => <option value={item} key={item}>{item}</option>)}
          </select>
        </label>

        <label className="search-field">
          <span>&gt;_</span>
          <input
            value={cmdQuery}
            onChange={handleFilterChange(setCmdQuery, 'cmdQuery')}
            placeholder="Command Search..."
            aria-label="Filter by Command string"
          />
        </label>

        <label className="filter-select">
          <span>From</span>
          <input type="datetime-local" value={startTime} onChange={handleFilterChange(setStartTime, 'startTime')} aria-label="Filter start time" />
        </label>

        <label className="filter-select">
          <span>To</span>
          <input type="datetime-local" value={endTime} onChange={handleFilterChange(setEndTime, 'endTime')} aria-label="Filter end time" />
        </label>

        <button className="reset-button" type="button" onClick={resetFilters} aria-label="Reset all filters">
          Reset filters
        </button>
      </form>

      <section className="filter-row">
        <div className="filter-caption" role="status" aria-live="polite">
          Showing {result.total === 0 ? 0 : startItem}–{endItem} of {result.total.toLocaleString()} matching sessions
        </div>
        <div className="page-size-selector">
          <span>Rows per page:</span>
          <select
            value={pageSize}
            onChange={(e) => {
              const sz = Number(e.target.value)
              setPageSize(sz)
              loadPage(1, { pageSize: sz })
            }}
            aria-label="Select rows per page"
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>
      </section>

      {requestError && <p className="request-error" role="alert">{requestError}</p>}
      <SessionTable sessions={result.items} onSelect={onSession} selectedId={selectedSession?.id} />

      <div className="pagination">
        <span>Page {page} of {pageCount}</span>
        <div>
          <button type="button" disabled={page <= 1 || loading} onClick={() => loadPage(page - 1)} aria-label="Previous page">← Previous</button>
          <button type="button" disabled={page >= pageCount || loading} onClick={() => loadPage(page + 1)} aria-label="Next page">Next →</button>
        </div>
      </div>
    </div>
  )
})
