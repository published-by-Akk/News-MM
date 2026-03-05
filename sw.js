// This script allows your site to be installed as an app
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installed');
});

self.addEventListener('fetch', (event) => {
  // This helps with loading performance later
  event.respondWith(fetch(event.request));
});