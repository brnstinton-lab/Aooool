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


