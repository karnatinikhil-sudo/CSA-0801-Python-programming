// Service Worker for Digital To-Do & Wellness Manager (PWA & Mobile App)

const CACHE_NAME = 'todo-wellness-pwa-v3';
const OFFLINE_URL = '/offline/';

const STATIC_ASSETS = [
    '/',
    '/offline/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/js/charts.js',
    '/static/manifest.json',
    '/static/icons/icon-192.svg',
    '/static/icons/icon-512.svg',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS).catch(err => {
                console.log('PWA cache prefill notice (some dynamic assets deferred):', err);
            });
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
            );
        }).then(() => clients.claim())
    );
});

// Network-first strategy with cache fallback & offline template support
self.addEventListener('fetch', (event) => {
    // Skip POST, PUT, DELETE, and admin routes
    if (event.request.method !== 'GET' || event.request.url.includes('/admin/')) {
        return;
    }

    // Handle HTML Navigation requests
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request)
                .then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        const responseClone = networkResponse.clone();
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(event.request, responseClone);
                        });
                    }
                    return networkResponse;
                })
                .catch(async () => {
                    const cachedResponse = await caches.match(event.request);
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    const fallbackResponse = await caches.match(OFFLINE_URL);
                    return fallbackResponse || caches.match('/');
                })
        );
        return;
    }

    // Static Assets: Stale-while-revalidate or Cache-first
    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            const fetchPromise = fetch(event.request).then((networkResponse) => {
                if (networkResponse && networkResponse.status === 200) {
                    const responseClone = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                }
                return networkResponse;
            }).catch(() => cachedResponse);

            return cachedResponse || fetchPromise;
        })
    );
});

// Mobile Push Notifications & Alarm Vibrate
self.addEventListener('push', (event) => {
    let data = {};
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data = { title: 'Task & Wellness Reminder', body: event.data.text() };
        }
    }

    const title = data.title || 'Task & Wellness Reminder';
    const isUrgent = data.stage === 'URGENT' || data.is_alarm_urgent;
    
    const options = {
        body: data.body || 'You have an active deadline or medication reminder.',
        icon: '/static/icons/icon-192.svg',
        badge: '/static/icons/icon-192.svg',
        vibrate: isUrgent ? [300, 150, 300, 150, 500] : [200, 100, 200],
        requireInteraction: isUrgent,
        data: {
            url: data.url || '/'
        },
        actions: [
            { action: 'open', title: 'Open App' },
            { action: 'snooze', title: 'Snooze 15m' }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    if (event.action === 'snooze') {
        // Can postMessage to client if open
    } else {
        event.waitUntil(
            clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
                for (let i = 0; i < clientList.length; i++) {
                    const client = clientList[i];
                    if (client.url && 'focus' in client) {
                        return client.focus();
                    }
                }
                if (clients.openWindow) {
                    return clients.openWindow(event.notification.data ? event.notification.data.url : '/');
                }
            })
        );
    }
});
