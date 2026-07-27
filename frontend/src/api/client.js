import { mockIntelligence, mockOverview, mockSessions, mockTimeline } from '../data/mockData'

const useMockApi = import.meta.env.VITE_USE_MOCK_API !== 'false'
const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')
const pause = (ms = 520) => new Promise((resolve) => setTimeout(resolve, ms))

async function request(path) {
  const response = await fetch(`${apiBaseUrl}${path}`)
  if (!response.ok) throw new Error(`API request failed (${response.status})`)
  return response.json()
}

function buildQuery(filters) {
  const query = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') query.set(key, value)
  })
  const value = query.toString()
  return value ? `?${value}` : ''
}

function sessionMatches(session, filters) {
  const term = (filters.ip ?? '').toLowerCase()
  const start = filters.start_time ? new Date(filters.start_time) : null
  const end = filters.end_time ? new Date(filters.end_time) : null
  const timestamp = new Date(session.startedAt)
  return (!term || session.ip.toLowerCase().includes(term))
    && (!filters.archetype || session.archetype === filters.archetype)
    && (!start || timestamp >= start)
    && (!end || timestamp <= end)
}

export const api = {
  async getDashboard() {
    if (useMockApi) {
      await pause()
      return { overview: mockOverview, timeline: mockTimeline, sessions: mockSessions, intelligence: mockIntelligence }
    }
    return request('/api/dashboard')
  },
  async getSession(id) {
    if (useMockApi) {
      await pause(220)
      return mockSessions.find((session) => session.id === id)
    }
    return request(`/api/sessions/${id}`)
  },
  async getSessions({ page = 1, page_size = 20, ...filters } = {}) {
    if (useMockApi) {
      await pause(260)
      const matchingSessions = mockSessions.filter((session) => sessionMatches(session, filters))
      const start = (page - 1) * page_size
      return { items: matchingSessions.slice(start, start + page_size), total: matchingSessions.length, page, page_size }
    }
    const response = await request(`/api/sessions${buildQuery({ page, page_size, ...filters })}`)
    return {
      items: response.items ?? response.sessions ?? [],
      total: response.total ?? response.count ?? 0,
      page: response.page ?? page,
      page_size: response.page_size ?? page_size,
    }
  },
}
