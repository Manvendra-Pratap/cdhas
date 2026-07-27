import { memo } from 'react'

export const SkeletonBox = memo(function SkeletonBox({ width = '100%', height = '20px', borderRadius = '6px', className = '' }) {
  return <div className={`skeleton-box ${className}`} style={{ width, height, borderRadius }} aria-hidden="true" />
})

export const LoadingPanel = memo(function LoadingPanel() {
  return (
    <main className="page-content" aria-label="Loading dashboard metrics">
      <div className="skeleton-grid">
        <SkeletonBox height="110px" borderRadius="10px" />
        <div className="metric-grid">
          <SkeletonBox height="145px" borderRadius="10px" />
          <SkeletonBox height="145px" borderRadius="10px" />
          <SkeletonBox height="145px" borderRadius="10px" />
          <SkeletonBox height="145px" borderRadius="10px" />
        </div>
        <SkeletonBox height="340px" borderRadius="10px" />
        <div className="split-grid">
          <SkeletonBox height="240px" borderRadius="10px" />
          <SkeletonBox height="240px" borderRadius="10px" />
        </div>
      </div>
    </main>
  )
})
