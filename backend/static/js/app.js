// AUL Alpine.js Global Utilities
document.addEventListener('alpine:init', () => {
    // Вспомогательное состояние для уведомлений и тоастов
    Alpine.store('toast', {
        message: '',
        visible: false,
        show(msg) {
            this.message = msg;
            this.visible = true;
            setTimeout(() => { this.visible = false; }, 3000);
        }
    });
});
