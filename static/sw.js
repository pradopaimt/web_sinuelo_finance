// Nome do cache (troque a versão quando fizer alterações importantes)
const CACHE_NAME = "sinuelo-cache-v15"; // bump a versão para forçar update

const ASSETS = [
  "/static/",
  "/static/index.html",
  "/static/manifest.webmanifest",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png",
  "/static/icons/maskable-512.png",
  "/static/icons/favicon.ico",
  "/static/demonstrativo_tree.js",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((k) => k !== CACHE_NAME && caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Nunca interceptar a API (sempre rede, sem cache)
  if (url.origin === location.origin && url.pathname.startsWith("/api/")) {
    event.respondWith(fetch(req));
    return;
  }

  // Apenas GET do mesmo origin pode usar cache
  if (req.method === "GET" && url.origin === location.origin) {
    // Cache-first para assets estáticos
    event.respondWith(
      caches.match(req).then((cached) => cached || fetch(req))
    );
    return;
  }

  // Para o resto, tenta rede e, se offline, cai para index.html (SPA fallback)
  event.respondWith(
    fetch(req).catch(() => caches.match("./index.html"))
  );
});