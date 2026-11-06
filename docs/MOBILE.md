# StaySync mobile apps (Android & iOS)

StaySync ships as **one codebase on three surfaces**: the website, an installable PWA, and native
Android / iOS apps for the Google Play Store and Apple App Store. The native apps are the same React
frontend wrapped with [Capacitor](https://capacitorjs.com), talking to the same FastAPI backend.

```
frontend/ (React + Vite)  ──vite build──▶  dist/  ──cap sync──▶  android/   (Android Studio → Play Store)
                                                           └────▶  ios/       (Xcode        → App Store)
```

> The Android project in this repo has been compiled successfully (`assembleDebug`). It has **not** been
> run on a physical device or submitted to a store: that needs your developer accounts and signing keys.

## Contents

1. [Prerequisites](#1-prerequisites)
2. [One-time setup](#2-one-time-setup)
3. [Run on a device or emulator](#3-run-on-a-device-or-emulator)
4. [Release to Google Play](#4-release-to-google-play)
5. [Release to the App Store](#5-release-to-the-app-store)
6. [Store listing checklist](#6-store-listing-checklist)
7. [Shipping updates](#7-shipping-updates)
8. [How the native layer works](#8-how-the-native-layer-works)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites

| For | You need |
|-----|----------|
| Both | Node 20+, a deployed backend reachable over **HTTPS** (see the main README) |
| Android | JDK 21, [Android Studio](https://developer.android.com/studio) (includes the SDK), a [Google Play Console](https://play.google.com/console) account (one-time fee) |
| iOS | A Mac with Xcode 16+, [CocoaPods](https://cocoapods.org), an [Apple Developer Program](https://developer.apple.com/programs/) membership (annual fee) |

You can build the Android app on Windows, macOS or Linux. iOS builds require macOS.

## 2. One-time setup

### 2.1 Point the app at your backend

The app's UI is bundled inside the app, so it needs the backend's absolute URL baked in:

```bash
cd frontend
echo "VITE_API_URL=https://<your-backend>.up.railway.app" > .env.production
```

`npm run mobile:*` refuses to build without it (`scripts/require-api-url.mjs`).

On the backend, make sure:

- `PUBLIC_BASE_URL` is set, and uploads use `STORAGE_BACKEND=supabase`, so photo URLs are absolute and load in the app.
- You don't need to change `CORS_ORIGINS`: the origins used by the app shells
  (`https://localhost`, `capacitor://localhost`, `http://localhost`) are always allowed by the backend.

### 2.2 Choose your final app id and name (do this before the first upload)

The default application id / bundle id is **`com.staysync.app`**. It is permanent once published, so
change it now if you want your own domain (for example `app.staysync.in`):

| File | Field |
|------|-------|
| `frontend/capacitor.config.json` | `appId`, `appName` |
| `frontend/android/app/build.gradle` | `namespace`, `applicationId` (and move `android/app/src/main/java/com/staysync/app/` to match) |
| Xcode → *App* target → *General* | Bundle Identifier, Display Name |

Then run `npm run mobile:sync` from `frontend/`.

### 2.3 Icons and splash screen

All icons (PWA, Android adaptive icons, iOS App Store icon, splash screens) are generated from one design:

```bash
pip install pillow
cd frontend && npm run icons     # edit scripts/generate_icons.py to rebrand
```

## 3. Run on a device or emulator

```bash
cd frontend
npm install
npm run mobile:android     # builds the web app, syncs, opens Android Studio → press ▶
npm run mobile:ios         # macOS only: builds, syncs (runs pod install), opens Xcode → press ▶
```

For quick UI work you don't need a device: `npm run dev` and open the site at phone width
(browser dev tools → device toolbar). The app shell behaves the same way.

## 4. Release to Google Play

1. **Create an upload key** (keep it and its passwords safe, and back them up; losing it blocks updates):
   ```bash
   keytool -genkey -v -keystore staysync-upload.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
   ```
2. In Android Studio: **Build → Generate Signed Bundle / APK → Android App Bundle**, choose the keystore.
   Never commit the `.jks` file or passwords (`*.jks` and `local.properties` are already git-ignored).
3. Before each release, bump `versionCode` (must increase every upload) and `versionName` in
   `frontend/android/app/build.gradle`.
4. In Play Console: **Create app** → upload the `.aab` to **Internal testing** first, install it on a real
   phone, then promote to **Closed → Production**. New personal developer accounts may have to run a closed
   test with a minimum number of testers before production access is granted. Check Play Console for the
   current requirement.
5. Complete the **App content** section (see the [checklist](#6-store-listing-checklist)).

## 5. Release to the App Store

1. On the Mac: `cd frontend && npm run mobile:ios` (this also runs `pod install`).
2. In Xcode select the **App** target → **Signing & Capabilities** → choose your Team and let Xcode manage signing.
3. Set **Version** and **Build** (Build must increase with every upload).
4. Select *Any iOS Device (arm64)* → **Product → Archive** → **Distribute App → App Store Connect → Upload**.
5. In [App Store Connect](https://appstoreconnect.apple.com): create the app, pick the uploaded build, test
   it through **TestFlight**, fill in the listing, and **Submit for Review**.

`Info.plist` already contains the camera and photo-library purpose strings (needed for profile and listing
photos) and `ITSAppUsesNonExemptEncryption = false` (the app only uses standard HTTPS). Review the wording
of the purpose strings before submitting.

## 6. Store listing checklist

Both stores reject apps that skip these. Items marked ✅ are already built into StaySync.

| Requirement | Status |
|-------------|--------|
| **In-app account deletion** (Apple 5.1.1(v), Google Play policy) | ✅ Profile → *Delete account* (`DELETE /api/auth/me`) |
| **Report and block users, moderation** for user-generated content (Apple 1.2) | ✅ Report/block and an admin moderation queue |
| **Public privacy policy URL** | ⬜ You must publish one (e.g. `https://<your-site>/privacy`) |
| **Web link for account deletion** (Play *Data safety* form asks for one) | ⬜ A page explaining: *Profile → Delete account*, or how to email support |
| **Data safety / App Privacy answers** | ⬜ Declare: name, email/phone, age, city/area (typed in by the user, not GPS), photos, messages, questionnaire answers. Data is linked to the user, used for app functionality and matching, and can be deleted. Nothing is sold. |
| **Support contact / website** | ⬜ Provide an email address and your site URL |
| **Content rating questionnaire** | ⬜ Social app with user-generated content and chat |
| **Screenshots** | ⬜ Phone screenshots (portrait). The README screenshots are a good start. Apple also needs the large-iPhone size; Play needs 2–8 screenshots plus a 512×512 icon and a 1024×500 feature graphic |
| **Demo account for reviewers** | ⬜ Create a test user in production and put its login in *App Review notes* / *App access* |

> **Review tip:** Apple rejects apps that are only a thin wrapper around a website (Guideline 4.2).
> StaySync has app-style navigation, real-time chat and account features, but review goes better when the app
> clearly offers native value. **Push notifications for new chat messages and connection requests** is the most
> natural next addition (`@capacitor/push-notifications`).

## 7. Shipping updates

- **Web-only changes** (React code): `npm run mobile:sync`, bump the version, rebuild and upload a new
  build. The website and PWA update immediately on deploy; the store apps update when users install the new build.
- **Backend changes** deploy to Railway independently. Keep API changes backward compatible, because older app
  versions stay in use for weeks.
- A new Capacitor plugin or native change always needs a new store build.

## 8. How the native layer works

| Concern | Where |
|---------|-------|
| Capacitor config (app id, splash, status bar) | `frontend/capacitor.config.json` |
| Startup: status bar, splash screen, Android back button, service-worker cleanup | `frontend/src/lib/native.js` |
| Hides the PWA install banner inside the app | `frontend/src/components/InstallApp.jsx` |
| App-style UI: bottom tab bar, full-screen chat, safe areas | `BottomNav.jsx`, `styles.css` |
| Native origins allowed by CORS | `backend/app/config.py` (`native_app_origins`) |
| Icon and splash generator | `frontend/scripts/generate_icons.py` |
| Build guard for `VITE_API_URL` | `frontend/scripts/require-api-url.mjs` |

`android/` and `ios/` are normal native projects committed to the repo. Edit them in Android Studio / Xcode
when you need native changes. `npm run mobile:sync` only refreshes the bundled web assets and plugins.

## 9. Troubleshooting

| Symptom | Fix |
|---------|-----|
| App opens but every request fails | `VITE_API_URL` was missing or wrong at build time. Fix `.env.production` and run `npm run mobile:sync` again. The backend must be HTTPS. |
| Photos don't show | Set `PUBLIC_BASE_URL` and use Supabase storage (relative `/uploads/...` URLs only work on the website). |
| White flash / wrong status bar colour | Check `capacitor.config.json` colours match `#0f172a`. |
| `pod install` fails | Update CocoaPods (`sudo gem install cocoapods`) and re-run `npm run mobile:ios`. |
| Gradle can't find the SDK | Open `frontend/android` in Android Studio once, or create `frontend/android/local.properties` with `sdk.dir=/path/to/Android/sdk`. |
| Chat doesn't connect in the app | Confirm your backend allows WebSockets over `wss://` (Railway does) and that `VITE_API_URL` is `https://`. |
