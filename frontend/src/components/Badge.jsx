import { memo } from 'react'

export const Badge = memo(function Badge({ severity }) {
  const sev = severity ? severity.toLowerCase() : 'low'
  return <span className={`badge badge-${sev}`}>{severity}</span>
})
