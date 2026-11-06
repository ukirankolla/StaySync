import React from 'react'

export default class ErrorBoundary extends React.Component {
  state = { failed: false }

  static getDerivedStateFromError() {
    return { failed: true }
  }

  componentDidCatch(error) {
    console.error('UI error:', error)
  }

  render() {
    if (!this.state.failed) return this.props.children
    return (
      <div role="alert" style={{ padding: 32, textAlign: 'center' }}>
        <h2>Something went wrong</h2>
        <p>Please reload the page. If it keeps happening, try again in a few minutes.</p>
        <button className="btn" onClick={() => window.location.reload()}>Reload</button>
      </div>
    )
  }
}
