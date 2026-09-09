// AUL Alpine.js Global Utilities
function initAulAlpineStores() {
    if (!window.Alpine) return;

    // Вспомогательное состояние для уведомлений и тоастов
    if (!Alpine.store('toast')) {
        Alpine.store('toast', {
            message: '',
            visible: false,
            show(msg) {
                this.message = msg;
                this.visible = true;
                setTimeout(() => { this.visible = false; }, 3000);
            }
        });
    }

    // Универсальный просмотрщик фотографий (Image Viewer / Lightbox)
    if (!Alpine.store('imageViewer')) {
        Alpine.store('imageViewer', {
            open: false,
            images: [],
            currentIndex: 0,
            show(images, index = 0) {
                if (!images) return;
                if (Array.isArray(images)) {
                    this.images = images;
                } else if (typeof images === 'string') {
                    this.images = [images];
                } else {
                    return;
                }
                if (this.images.length === 0) return;

                this.currentIndex = Math.max(0, Math.min(index, this.images.length - 1));
                this.open = true;
                document.body.classList.add('overflow-hidden');
            },
            close() {
                this.open = false;
                document.body.classList.remove('overflow-hidden');
            },
            next() {
                if (this.images.length > 1) {
                    this.currentIndex = (this.currentIndex + 1) % this.images.length;
                }
            },
            prev() {
                if (this.images.length > 1) {
                    this.currentIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
                }
            }
        });
    }
}

document.addEventListener('alpine:init', initAulAlpineStores);
if (window.Alpine) {
    initAulAlpineStores();
}



/* AUL Web Push — Service Worker registration */
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('[AUL Push] Service Worker registered:', registration.scope);
                subscribeToPush(registration);
            })
            .catch(error => {
                console.error('[AUL Push] Service Worker registration failed:', error);
            });
    });
}
/* AUL Web Push — browser subscription */
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);

    const base64 = (base64String + padding)
        .replace(/-/g, '+')
        .replace(/_/g, '/');

    const rawData = atob(base64);

    return Uint8Array.from(
        [...rawData].map(char => char.charCodeAt(0))
    );
}
async function subscribeToPush(registration) {
    try {
        if (!('PushManager' in window)) {
            console.warn('[AUL Push] Push API is not supported');
            return;
        }

        const vapidResponse = await fetch(
            '/notifications/push/vapid-public-key/'
        );

        if (!vapidResponse.ok) {
            throw new Error('Не удалось получить VAPID public key');
        }

        const { publicKey } = await vapidResponse.json();

        if (!publicKey) {
            throw new Error('VAPID public key отсутствует');
        }

        const permission = await Notification.requestPermission();

        if (permission !== 'granted') {
            console.log('[AUL Push] Notification permission:', permission);
            return;
        }

        let subscription = await registration.pushManager.getSubscription();

        if (!subscription) {
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(publicKey)
            });
        }

        const response = await fetch(
            '/notifications/push/subscribe/',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    subscription: subscription.toJSON()
                })
            }
        );

        if (!response.ok) {
            throw new Error('Не удалось сохранить Push-подписку');
        }

        const result = await response.json();

        console.log('[AUL Push] Subscription saved:', result);

    } catch (error) {
        console.error('[AUL Push] Subscription failed:', error);
    }
}


/* Django CSRF cookie */
function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(';') : [];

    for (const cookie of cookies) {
        const [key, ...value] = cookie.trim().split('=');

        if (key === name) {
            return decodeURIComponent(value.join('='));
        }
    }

    return null;
}