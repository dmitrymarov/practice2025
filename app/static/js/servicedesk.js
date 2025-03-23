// Глобальные переменные
let currentTicketId = null;
let tickets = [];

$(document).ready(function () {
    console.log("ServiceDesk page initialized");

    // Загрузка заявок с сервера
    loadTickets();

    // Показать форму создания заявки
    $('#new-ticket-btn').click(function () {
        $('#ticket-form').removeClass('d-none');
        $('#ticket-details').addClass('d-none');
    });

    // Отмена создания заявки
    $('#cancel-ticket').click(function () {
        $('#ticket-form').addClass('d-none');
        clearTicketForm();
    });

    // Создание заявки
    $('#submit-ticket').click(function () {
        const ticketData = {
            subject: $('#ticket-subject').val(),
            description: $('#ticket-description').val(),
            priority: $('#ticket-priority').val(),
            project_id: 1
        };

        $.ajax({
            url: '/api/tickets',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(ticketData),
            success: function (response) {
                // После успешного создания заявки загружаем все заявки заново
                loadTickets();
                $('#ticket-form').addClass('d-none');
                clearTicketForm();
                alert(`Заявка #${response.id} успешно создана!`);
            },
            error: function (xhr, status, error) {
                console.error("Error creating ticket:", error);
                alert('Ошибка при создании заявки: ' + (xhr.responseJSON?.error || error));
            }
        });
    });

    // Возврат к списку заявок
    $('#back-to-list').click(function () {
        $('#ticket-details').addClass('d-none');
        currentTicketId = null;
    });

    // Добавление комментария
    $('#add-comment').click(function () {
        const comment = $('#new-comment').val().trim();
        if (!comment) return;

        if (currentTicketId) {
            $.ajax({
                url: `/api/tickets/${currentTicketId}/comment`,
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ comment: comment }),
                success: function () {
                    // После успешного добавления комментария - загружаем заявки заново
                    loadTickets(function () {
                        // После загрузки показываем детали текущей заявки
                        const ticket = tickets.find(t => t.id === currentTicketId);
                        if (ticket) {
                            showTicketDetails(ticket);
                        }
                    });
                    $('#new-comment').val('');
                },
                error: function (xhr, status, error) {
                    console.error("Error adding comment:", error);
                    alert('Ошибка при добавлении комментария: ' + (xhr.responseJSON?.error || error));
                }
            });
        }
    });

    // Обработка клика по заявке
    $(document).on('click', '.ticket-item', function () {
        const ticketId = parseInt($(this).data('ticket-id'));
        currentTicketId = ticketId;

        // Найти заявку в массиве
        const ticket = tickets.find(t => t.id === ticketId);
        if (ticket) {
            showTicketDetails(ticket);
        }
    });
});

// Загрузка заявок с сервера
function loadTickets(callback) {
    $.ajax({
        url: '/api/tickets',
        method: 'GET',
        success: function (data) {
            tickets = data;
            console.log(`Загружено ${tickets.length} заявок с сервера`);
            updateTicketsList();
            if (callback) callback();
        },
        error: function (xhr, status, error) {
            console.error("Error loading tickets:", error);
            $('#tickets-container').html('<div class="alert alert-danger">Ошибка при загрузке заявок. Попробуйте обновить страницу.</div>');
        }
    });
}

// Очистка формы заявки
function clearTicketForm() {
    $('#ticket-subject').val('');
    $('#ticket-description').val('');
    $('#ticket-priority').val('normal');
}

// Обновление списка заявок
function updateTicketsList() {
    const container = $('#tickets-container');

    if (tickets.length === 0) {
        container.html('<div class="text-center text-muted py-4"><p>У вас пока нет заявок</p></div>');
        return;
    }

    container.empty();

    // Сортировка заявок по дате (новые сверху)
    tickets.sort((a, b) => {
        return new Date(b.created_on) - new Date(a.created_on);
    });

    tickets.forEach(ticket => {
        const priorityClass = getPriorityClass(ticket.priority);
        const statusClass = getStatusClass(ticket.status);

        container.append(`
            <div class="card mb-2 ticket-item" data-ticket-id="${ticket.id}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="card-title mb-0">#${ticket.id}: ${ticket.subject}</h5>
                        <span class="badge ${statusClass}">${ticket.status || 'new'}</span>
                    </div>
                    <div class="d-flex mt-2">
                        <span class="badge ${priorityClass} me-2">${ticket.priority}</span>
                        <small class="text-muted">${formatDate(ticket.created_on)}</small>
                    </div>
                </div>
            </div>
        `);
    });
}

// Показать детали заявки
function showTicketDetails(ticket) {
    $('#ticket-details-subject').text(`#${ticket.id}: ${ticket.subject}`);
    $('#ticket-details-status').text(ticket.status || 'new');
    $('#ticket-details-status').attr('class', `badge ${getStatusClass(ticket.status)}`);
    $('#ticket-details-priority').text(ticket.priority);
    $('#ticket-details-priority').attr('class', `badge ${getPriorityClass(ticket.priority)} ms-2`);
    $('#ticket-details-date').text(formatDate(ticket.created_on));
    $('#ticket-details-description').text(ticket.description);

    // Комментарии
    const commentsContainer = $('#ticket-comments');
    commentsContainer.empty();

    if (ticket.comments && ticket.comments.length > 0) {
        ticket.comments.forEach(comment => {
            commentsContainer.append(`
                <div class="card mb-2">
                    <div class="card-body">
                        <p class="card-text">${comment.text}</p>
                        <small class="text-muted">${formatDate(comment.created_on)}</small>
                    </div>
                </div>
            `);
        });
    } else {
        commentsContainer.html('<p class="text-muted">Нет комментариев</p>');
    }

    $('#ticket-details').removeClass('d-none');
    $('#ticket-form').addClass('d-none');

    // Прокрутка к деталям
    $('html, body').animate({
        scrollTop: $('#ticket-details').offset().top - 20
    }, 300);
}

// Получить класс для отображения приоритета
function getPriorityClass(priority) {
    switch (priority) {
        case 'low':
            return 'bg-secondary';
        case 'normal':
            return 'bg-primary';
        case 'high':
            return 'bg-warning';
        case 'urgent':
            return 'bg-danger';
        default:
            return 'bg-primary';
    }
}

// Получить класс для отображения статуса
function getStatusClass(status) {
    switch (status) {
        case 'new':
            return 'bg-info';
        case 'in_progress':
            return 'bg-primary';
        case 'resolved':
            return 'bg-success';
        case 'closed':
            return 'bg-secondary';
        default:
            return 'bg-info';
    }
}

// Форматирование даты
function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
        const date = new Date(dateStr);
        return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
    } catch (e) {
        return dateStr;
    }
}