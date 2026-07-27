import { memo } from 'react'

export const CountryFlag = memo(function CountryFlag({ code, country }) {
  const displayCode = (code || (country ? country.slice(0, 2) : 'UN')).toUpperCase()
  return (
    <span className={`flag flag-${displayCode}`} title={country || displayCode} aria-label={`Country flag for ${country || displayCode}`}>
      {displayCode}
    </span>
  )
})
