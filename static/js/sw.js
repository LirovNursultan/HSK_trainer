const CACHE_NAME = 'hsk-cards-v1';
const urlsToCache = [
  '/',
  '/static/manifest.json',
  // Добавь важные страницы и статику
  '/train/',
  '/train/flashcards/',
  '/train/quiz/',
  // CSS, JS, шрифты и т.д.
];

// Установка Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// Стратегия Cache First + Network Fallback
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Возвращаем из кэша если есть
        if (response) return response;

        // Иначе идём в сеть
        return fetch(event.request).then(
          response => {
            // Кэшируем успешные ответы
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => cache.put(event.request, responseToCache));

            return response;
          }
        );
      })
  );
});