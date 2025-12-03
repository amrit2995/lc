/*eslint-disable */
importScripts('https://storage.googleapis.com/workbox-cdn/releases/5.1.2/workbox-sw.js');

// You can add additional path here.
self.__precacheManifest = [].concat(self.__precacheManifest || self.__WB_MANIFEST);

// Configure Debug Builds. content we can see in console.
workbox.setConfig({ debug: false });
// workbox.setConfig({modulePathPrefix: "workbox-v3.0.0"});
workbox.core.setCacheNameDetails({
    prefix: 'helix-app',
    suffix: 'v1',
    precache: 'install-time', // precache on install time, check in application tab
    runtime: 'run-time' // precache on run time, check in application tab
});

// Some developers want to be able to publish a new service worker
// and have it update and control a web page as soon as possible,
// skipping the default service worker lifecycle.
workbox.core.skipWaiting();
// once its been skipped it enter the activated mode and will wait
// for caching but it wont cache the clients interaction. To do so apply the following line
workbox.core.clientsClaim();

// An Example
// workbox.routing.registerRoute(
//     new RegExp('http://localhost:3000'),
//     new workbox.strategies.CacheFirst()
// );

// Example: How to cache
workbox.routing.registerRoute(
    // Cache CSS files.
    // /\.css$/,
    new RegExp('.+\\.css$'),
    // Use cache but update in the background.
    new workbox.strategies.StaleWhileRevalidate({
    // Use a custom cache name.
        cacheName: 'css-cache'
    })
);


// It will precache all js, css, images files. If you want to cache
// only few specific file then remove this line and with the help of
// workbox routing logic achieve the goal.
workbox.precaching.precacheAndRoute(self.__precacheManifest);
workbox.precaching.precacheAndRoute(self.__WB_MANIFEST || [])

self.addEventListener('activate', event => {
  console.debug('SW activate');
});

self.addEventListener('install', event => {
  console.debug('SW install');
});
