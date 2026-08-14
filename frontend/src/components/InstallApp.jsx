import React, { useEffect, useState } from 'react'

const isStandalone = () =>
  window.matchMedia('(display-mode: standalone)').matches ||
  window.navigator.standalone === true

const isIOS = () =>
  /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream

export default function InstallApp() {
  const [deferredPrompt, setDeferredPrompt] = useState(null)
  const [show, setShow] = useState(false)
  const [dismissed, setDismissed] = useState(false)

  useEffect(() => {
    if (isStandalone()) return
    const timer = setTimeout(() => setShow(true), 4000)
    const handler = (e) => {
      e.preventDefault()
      setDeferredPrompt(e)
      setShow(true)
    }
    const installed = () => setShow(false)
    window.addEventListener('beforeinstallprompt', handler)
    window.addEventListener('appinstalled', installed)
    return () => {
      clearTimeout(timer)
      window.removeEventListener('beforeinstallprompt', handler)
      window.removeEventListener('appinstalled', installed)
    }
  }, [])

  const install = async () => {
    if (!deferredPrompt) return
    deferredPrompt.prompt()
    await deferredPrompt.userChoice
    setDeferredPrompt(null)
    setShow(false)
  }

  if (!show || dismissed || isStandalone()) return null

  return (
    <div className="install-bar">
      {deferredPrompt ? (
        <>
          <div className="install-text">Get the StaySync app</div>
          <button className="btn btn-primary btn-sm" onClick={install}>Install</button>
        </>
      ) : isIOS() ? (
        <>
          <div className="install-text">Install StaySync: tap Share ➜ Add to Home Screen</div>
          <button className="btn btn-ghost btn-sm" onClick={() => setDismissed(true)}>OK</button>
        </>
      ) : (
        <></>
      )}
    </div>
  )
}
