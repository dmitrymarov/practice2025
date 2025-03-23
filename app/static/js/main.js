// Общие утилиты и функции

// Форматирование даты
function formatDate(dateStr) {
    if (!dateStr) return '';

    const date = new Date(dateStr);
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
}

// Получение параметра из URL
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

// Общая функция для отправки уведомлений
function showNotification(message, type = 'success') {
    const alertBox = $('<div>')
        .addClass(`alert alert-${type} alert-dismissible fade show`)
        .attr('role', 'alert')
        .html(`
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `);

    // Добавление уведомления в контейнер
    if ($('#notifications-container').length === 0) {
        $('body').append($('<div id="notifications-container" class="position-fixed top-0 end-0 p-3" style="z-index: 1050;">'));
    }

    $('#notifications-container').append(alertBox);

    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        alertBox.alert('close');
    }, 5000);
}

// Инициализация всплывающих подсказок Bootstrap
$(function () {
    $('[data-bs-toggle="tooltip"]').tooltip();

    // Другая общая инициализация
});