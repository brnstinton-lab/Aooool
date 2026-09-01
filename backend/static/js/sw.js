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

    const data = event.data.json();

    const title = data.title || "AUL";
    const options = {
        body: data.body || "",
        icon: data.icon || "/static/images/icon-192.png",
        badge: data.badge || "/static/images/icon-192.png",
        data: {
            url: data.url || "/"
        }
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener("notificationclick", event => {
    event.notification.close();

    const url = event.notification.data?.url || "/";

    event.waitUntil(
        clients.matchAll({
            type: "window",
            includeUncontrolled: true
        }).then(clientList => {
            for (const client of clientList) {
                if ("focus" in client) {
                    client.navigate(url);
                    return client.focus();
                }
            }

            if (clients.openWindow) {
                return clients.openWindow(url);
            }
        })
    );
});
