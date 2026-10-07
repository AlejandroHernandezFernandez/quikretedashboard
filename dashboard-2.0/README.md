# Dashboard 2.0

Installable, responsive Quikrete operations dashboard using the existing ThingSpeak channel. Static HTML/CSS/JavaScript; no build dependencies.

Serve `dist/` using any static HTTPS host. For local development: `python3 -m http.server 8000 --directory dist`. Run regression tests with `npm test`.

## Data behavior

Seven existing fields and original status thresholds are preserved. Refreshes every 60 seconds while visible and on return to the app. The latest 8,000 feed entries are inspected to recover sparse field updates. Blank, nonnumeric and infinite values never overwrite valid readings; zero remains valid. Each field retains its own timestamp. Readings older than 10 minutes are explicitly marked stale. This freshness threshold is a display convention, not a plant safety limit. Cached last-known values are retained on this device for offline use. The API is fetched directly; it is not cached by the service worker.

Coal Mill field6 was sending empty strings at inspection on 2026-10-07. The UI can preserve valid history but the upstream publisher must resume numeric values for current production readings. No replacement data is fabricated.

The existing read API key is retained in the browser client, as in the original public repository. Browser-delivered configuration is visible to visitors. No write API is used.

## PWA

Manifest, 192/512 PNG icons and service worker included. HTTPS required for installation outside localhost. On iOS: Safari → Share → Add to Home Screen. Increment the service-worker shell cache version when releasing shell changes. The app shell is available offline after one successful online load; values retain their original timestamps.
