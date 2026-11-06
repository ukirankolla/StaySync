// Store builds load the UI from the device, so the app needs the backend's absolute URL baked in.
// Usage: runs automatically before `npm run mobile:*`. Set VITE_API_URL in frontend/.env.production.
import { loadEnv } from 'vite'

const url = (process.env.VITE_API_URL || loadEnv('production', process.cwd(), 'VITE_').VITE_API_URL || '').trim()
if (!/^https:\/\/.+/.test(url)) {
  console.error('\n✖ VITE_API_URL is missing or not an https:// URL.\n' +
    '  The mobile app cannot reach your backend without it. Create frontend/.env.production with:\n' +
    '    VITE_API_URL=https://<your-backend>.up.railway.app\n')
  process.exit(1)
}
console.log(`✔ Mobile build will talk to ${url}`)
