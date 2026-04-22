// static/js/script.js
// Здесь будут ваши кастомные JavaScript функции

// Активация тултипов Bootstrap (если нужны)
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех тултипов
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});