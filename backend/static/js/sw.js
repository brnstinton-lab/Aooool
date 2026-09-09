self.addEventListener("install", event => {
    console.log("[AUL SW] Installed");
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    console.log("[AUL SW] Activated");
    event.waitUntil(self.clients.claim());
});

self.addEventListener("push", event => {
    if (!event.data) return;

    let data = {};
    try {
        data = event.data.json();
    } catch (err) {
        data = {
            title: "AUL Оповещение",
            body: typeof event.data.text === "function" ? event.data.text() : ""
        };
    }

    const title = data.title || "AUL Оповещение";
    const options = {
        body: data.body || "",
        icon: data.icon || "/static/images/icon-192.png",
        badge: data.badge || "/static/images/icon-192.png",
        vibrate: [200, 100, 200],
        tag: data.tag || `aul-notification-${data.announcement_id || Date.now()}`,
        renotify: true,
        data: {
            url: data.url || "/notifications/",
            type: data.type,
            category: data.category,
            announcement_id: data.announcement_id
        }
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener("notificationclick", event => {
    event.notification.close();

    const targetPath = event.notification.data?.url || "/notifications/";
    const targetUrl = new URL(targetPath, self.location.origin).href;

    event.waitUntil(
        clients.matchAll({
            type: "window",
            includeUncontrolled: true
        }).then(clientList => {
            for (const client of clientList) {
                if ("focus" in client) {
                    if ("navigate" in client) {
                        client.navigate(targetUrl);
                    }
                    return client.focus();
                }
            }

            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});
