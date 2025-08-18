// Nome do cache (troque a versão quando fizer alterações importantes)
const CACHE_NAME = "sinuelo-cache-v12";

// Lista de arquivos para pré-cache
const ASSETS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/maskable-512.png",
  "./icons/favicon.ico"
];

// Instalação do service worker → faz cache inicial
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
  self.skipWaiting();
});

// Ativação → limpa caches antigos
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((k) => k !== CACHE_NAME && caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Estratégia de busca: cache-first para assets, network-first para resto
self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Cache-first para arquivos estáticos locais
  if (req.method === "GET" && url.origin === location.origin) {
    event.respondWith(
      caches.match(req).then((cached) => cached || fetch(req))
    );
    return;
  }

  // Network-first para o restante (ex.: chamadas externas futuramente)
  event.respondWith(
    fetch(req).catch(() => caches.match("./index.html"))
  );
});
