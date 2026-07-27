import { useState, useEffect, useRef, useCallback } from 'react'
import { api } from '../api/client'

const severityOrder = { Critical: 4, High: 3, Medium: 2, Low: 1 }

function formatTime(value) {
  if (!value) return '--:--'
  try {
    return new Intl.DateTimeFormat('en', { hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date(value))
  } catch {
    return '--:--'
  }
}

export function useDashboardData() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [lastFetchTime, setLastFetchTime] = useState(Date.now())
  const [secondsAgo, setSecondsAgo] = useState(0)

  const [notifications, setNotifications] = useState([])
  const [toasts, setToasts] = useState([])
  const knownSessionIds = useRef(new Set())

  const load = useCallback(async (isAutoRefresh = false) => {
    if (!isAutoRefresh) setError(false)
    try {
      const res = await api.getDashboard()
      setData(res)
      setLastFetchTime(Date.now())

      if (res.sessions) {
        const newItems = []
        res.sessions.forEach((s) => {
          if (!knownSessionIds.current.has(s.id)) {
            knownSessionIds.current.add(s.id)
            newItems.push(s)
          }
        })

        if (newItems.length > 0) {
          const newNotifs = newItems.map((s) => ({
            id: s.id + '_' + Date.now(),
            ip: s.ip,
            country: s.country,
            flag: s.flag,
            severity: s.severity,
            archetype: s.archetype,
            time: formatTime(s.startedAt),
            read: false,
          }))

          setNotifications((prev) => [...newNotifs, ...prev].slice(0, 20))

          const toastItems = newItems.filter((s) => severityOrder[s.severity] >= 3)
          if (toastItems.length > 0) {
            const newToasts = toastItems.map((s) => ({
              id: 'toast_' + s.id + '_' + Date.now(),
              ip: s.ip,
              country: s.country,
              flag: s.flag,
              severity: s.severity,
              archetype: s.archetype,
              time: formatTime(s.startedAt),
            }))
            setToasts((prev) => [...newToasts, ...prev].slice(0, 4))
          }
        }
      }
    } catch {
      if (!data) setError(true)
    }
  }, [data])

  useEffect(() => {
    load()
  }, [])

  useEffect(() => {
    const autoInterval = setInterval(() => {
      load(true)
    }, 10000)
    return () => clearInterval(autoInterval)
  }, [load])

  useEffect(() => {
    const tickInterval = setInterval(() => {
      setSecondsAgo(Math.floor((Date.now() - lastFetchTime) / 1000))
    }, 1000)
    return () => clearInterval(tickInterval)
  }, [lastFetchTime])

  const refresh = useCallback(async () => {
    setRefreshing(true)
    await load(false)
    setRefreshing(false)
  }, [load])

  const dismissNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }, [])

  const markAllNotificationsRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
  }, [])

  const dismissToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  return {
    data,
    error,
    refreshing,
    lastFetchTime,
    secondsAgo,
    notifications,
    toasts,
    refresh,
    load,
    dismissNotification,
    markAllNotificationsRead,
    dismissToast,
  }
}
