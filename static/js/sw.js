/* PNG Compliance Hub 2026 — PWA Service Worker
   Offline-first caching strategy for low-bandwidth PNG networks */

const CACHE_NAME   = 'pngch-v1';
const STATIC_CACHE = 'pngch-static-v1';

// Assets to pre-cache for offline use
const PRECACHE_URLS = [
  '/',
  '/dashboard/',
  '/gst/',
  '/swt/',
  '/sbt/',
  '/static/css/theme.css',
  '/accounts/login/',
];

// ── Install: Pre-cache static assets ─────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('[SW] Pre-caching offline assets');
      return cache.addAll(PRECACHE_URLS);
    }).then(() => self.skipWaiting())
  );
});

// ── Activate: Clean old caches ────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keyList) =>
      Promise.all(
        keyList
          .filter((key) => key !== CACHE_NAME && key !== STATIC_CACHE)
          .map((key) => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch: Network-first, cache fallback ──────────────────────
self.addEventListener('fetch', (event) => {
  // Skip non-GET and browser-extension requests
  if (event.request.method !== 'GET') return;
  if (!event.request.url.startsWith('http')) return;

  // HTMX partials — always network, no cache
  if (event.request.headers.get('HX-Request')) return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Clone and cache successful responses
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() =>
        caches.match(event.request).then((cached) => {
          if (cached) return cached;
          // Offline fallback page
          if (event.request.destination === 'document') {
            return new Response(
              `<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width"><style>
              body{font-family:Inter,sans-serif;background:#060D1A;color:#E8F0FE;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;flex-direction:column;text-align:center}
              h1{color:#00E5A0;font-size:2rem}p{color:#7B9BB5}</style></head>
              <body><div style="margin-bottom:20px;color:#00E5A0"><svg width="64" height="64" fill="currentColor" viewBox="0 0 16 16"><path d="M10.706 3.294A1.25 1.25 0 1 1 12.47 5.06 1.25 1.25 0 0 1 10.706 3.294zM7 3.5a.5.5 0 0 0 .5.5H9a.5.5 0 0 0 0-1H7.5a.5.5 0 0 0-.5.5zm-4 4.5a.5.5 0 0 0 .5.5H5a.5.5 0 0 0 0-1H3.5a.5.5 0 0 0-.5.5zm4.5 4.5a.5.5 0 0 0 .5.5H9a.5.5 0 0 0 0-1H7.5a.5.5 0 0 0-.5.5zM11.5 12a.5.5 0 0 0 .5.5H13a.5.5 0 0 0 0-1h-1.5a.5.5 0 0 0-.5.5zM3.003 3.003a.5.5 0 0 0-.707 0l-1 1a.5.5 0 1 0 .707.707l1-1a.5.5 0 0 0 0-.707zM13 3.003a.5.5 0 0 1 .707 0l1 1a.5.5 0 1 1-.707.707l-1-1a.5.5 0 0 1 0-.707zM3.003 13a.5.5 0 0 1 0 .707l-1 1a.5.5 0 1 1-.707-.707l1-1a.5.5 0 0 1 .707 0zm10 0a.5.5 0 0 0 0 .707l1 1a.5.5 0 1 0 .707-.707l-1-1a.5.5 0 0 0-.707 0zM8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm0 13A6 6 0 1 1 8 2a6 6 0 0 1 0 12z"/></svg></div><h1>You're Offline</h1>
              <p>PNG Compliance Hub works offline for cached pages.<br>Connect to the internet to sync your latest data.</p></body></html>`,
              { headers: { 'Content-Type': 'text/html' } }
            );
          }
        })
      )
  );
});

// ── Background Sync: Queue ledger entries when offline ────────
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-ledger') {
    event.waitUntil(syncLedgerEntries());
  }
});

async function syncLedgerEntries() {
  // Use a temporary approach to get DB access within SW
  // In a real app, you'd use a shared library or broadcast channel
  console.log('[SW] Background sync: Processing queued ledger entries');
  
  // This is a stub for the actual fetch loop
  // Typically involves iterating through IndexedDB 'offline_ledger'
  // and POSTing to /gst/add-entry/ (or a dedicated sync endpoint)
}
