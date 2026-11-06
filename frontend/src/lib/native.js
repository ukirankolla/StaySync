import { Capacitor } from '@capacitor/core'

/** True when running inside the Android / iOS app shell (Capacitor), false in a normal browser or PWA. */
export const isNative = Capacitor.isNativePlatform()

const HOME_PATHS = ['/', '/discover', '/login']

/**
 * One-time setup for the store apps. A no-op in the browser, so the website is unaffected.
 * Plugins are imported lazily so they never load on the web.
 */
export async function initNative() {
  if (!isNative) return
  document.documentElement.classList.add('native-app', `native-${Capacitor.getPlatform()}`)

  // The app ships its own assets: a service worker would only serve stale files after an update.
  try {
    const regs = await navigator.serviceWorker?.getRegistrations?.()
    regs?.forEach((r) => r.unregister())
  } catch { /* ignore */ }

  const [{ StatusBar, Style }, { SplashScreen }, { App }, { Keyboard }] = await Promise.all([
    import('@capacitor/status-bar'),
    import('@capacitor/splash-screen'),
    import('@capacitor/app'),
    import('@capacitor/keyboard'),
  ])

  try {
    await StatusBar.setStyle({ style: Style.Dark }) // light icons on our dark UI
    if (Capacitor.getPlatform() === 'android') await StatusBar.setBackgroundColor({ color: '#0f172a' })
  } catch { /* status bar not available */ }

  try { Keyboard.setAccessoryBarVisible?.({ isVisible: false }) } catch { /* android */ }

  // Android hardware / gesture back: go back in the app, exit only from the top-level screens.
  App.addListener('backButton', () => {
    if (HOME_PATHS.includes(window.location.pathname) || window.history.length <= 1) App.exitApp()
    else window.history.back()
  })

  // Keep the splash up until React has painted its first frame.
  requestAnimationFrame(() => SplashScreen.hide({ fadeOutDuration: 250 }))
}
