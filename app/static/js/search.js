let selectedSolution = '';
let selectedSource = '';
let allResults = [];

$(document).ready(function () {
    console.log("Search page initialized");

    // Обработка поискового запроса при клике на кнопку
    $('#search-button').click(function () {
        const query = $('#search-input').val().trim();
        if (query) {
            console.log("Search button clicked with query:", query);
            searchSolutions(query);
        } else {
            // Предупреждение, если запрос пустой
            alert('Пожалуйста, введите поисковый запрос');
        }
    });

    // Поиск при нажатии Enter в поле ввода
    $('#search-input').keypress(function (e) {
        if (e.which === 13) {
            const query = $(this).val().trim();
            if (query) {
                console.log("Enter pressed with query:", query);
                searchSolutions(query);
            } else {
                // Предупреждение, если запрос пустой
                alert('Пожалуйста, введите поисковый запрос');
            }
        }
    });

    // Обработка фильтра "Все источники"
    $('#filter-all').change(function () {
        const isChecked = $(this).prop('checked');
        $('.source-filter').prop('checked', isChecked);
        applyFilters();
    });

    // Обработка изменения отдельных фильтров
    $('.source-filter').change(function () {
        const allFiltersChecked = $('#filter-opensearch').prop('checked') &&
            $('#filter-mediawiki').prop('checked') &&
            $('#filter-mock').prop('checked');

        $('#filter-all').prop('checked', allFiltersChecked);
        applyFilters();
    });

    // Открыть форму с выбранным решением
    $(document).on('click', '.create-ticket-btn', function () {
        selectedSolution = $(this).data('solution');
        selectedSource = $(this).data('source');

        $('#solution-content').text(selectedSolution);
        $('#solution-source').text(`Источник: ${getSourceLabel(selectedSource)}`);
        $('#selected-solution').removeClass('d-none');
        $('#ticket-form').removeClass('d-none');

        // Предзаполнить поля
        $('#ticket-subject').val('Запрос на помощь');
        $('#ticket-description').val('Мне нужна помощь с проблемой.');

        // Прокрутка к форме
        $('html, body').animate({
            scrollTop: $('#ticket-form').offset().top - 50
        }, 500);
    });

    // Отмена создания заявки
    $('#cancel-ticket').click(function () {
        $('#ticket-form').addClass('d-none');
        selectedSolution = '';
        selectedSource = '';
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
                // Прикрепить решение к заявке
                $.ajax({
                    url: `/api/tickets/${response.id}/solution`,
                    method: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        solution: selectedSolution,
                        source: selectedSource
                    }),
                    success: function () {
                        alert(`Заявка #${response.id} успешно создана!`);
                        $('#ticket-form').addClass('d-none');
                        selectedSolution = '';
                        selectedSource = '';
                    },
                    error: function (xhr, status, error) {
                        console.error("Error attaching solution:", error);
                        alert('Ошибка при прикреплении решения к заявке');
                    }
                });
            },
            error: function (xhr, status, error) {
                console.error("Error creating ticket:", error);
                alert('Ошибка при создании заявки');
            }
        });
    });

    // Добавим отображение информации об ошибке
    $(document).ajaxError(function (event, xhr, settings) {
        console.error('Ajax error:', xhr.status, xhr.statusText);
        if (xhr.responseJSON && xhr.responseJSON.error) {
            console.error('Error details:', xhr.responseJSON.error);
        }
    });
});

// Функция поиска решений
function searchSolutions(query) {
    $('#search-results').html('<div class="text-center"><div class="spinner-border text-success" role="status"></div><p class="mt-2">Поиск решений...</p></div>');

    // Получаем выбранные источники для фильтрации
    const sources = [];
    if ($('#filter-opensearch').prop('checked')) sources.push('opensearch');
    if ($('#filter-mediawiki').prop('checked')) sources.push('mediawiki');
    if ($('#filter-mock').prop('checked')) sources.push('mock');

    // Добавляем дополнительные параметры для отладки
    const searchData = {
        query: query,
        sources: sources,
        debug: true
    };

    console.log("Sending search request:", searchData);

    $.ajax({
        url: '/api/search',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(searchData),
        success: function (data) {
            console.log("Search results:", data);

            if (data.results && data.results.length > 0) {
                // Сохраняем все результаты
                allResults = data.results;
                // Применяем фильтры и отображаем результаты
                applyFilters();
            } else {
                $('#search-results').html('<div class="alert alert-warning">Решений не найдено. Попробуйте изменить запрос.</div>');
            }
        },
        error: function (xhr, status, error) {
            console.error("Search error:", error);
            let errorMessage = 'Произошла ошибка при поиске. Пожалуйста, попробуйте еще раз.';

            // Если есть подробности ошибки, добавляем их
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage += '<br><small class="text-muted">Детали: ' + xhr.responseJSON.error + '</small>';
            }

            $('#search-results').html(`<div class="alert alert-danger">${errorMessage}</div>`);
        }
    });
}

// Применение фильтров к результатам поиска
function applyFilters() {
    if (!allResults || allResults.length === 0) {
        return;
    }

    // Получаем состояние фильтров
    const showOpensearch = $('#filter-opensearch').prop('checked');
    const showMediawiki = $('#filter-mediawiki').prop('checked');
    const showMock = $('#filter-mock').prop('checked');

    // Фильтруем результаты
    const filteredResults = allResults.filter(result => {
        const source = result.source || 'mock';

        if (source === 'opensearch' && !showOpensearch) return false;
        if (source === 'mediawiki' && !showMediawiki) return false;
        if (source === 'mock' && !showMock) return false;

        return true;
    });

    // Отображаем отфильтрованные результаты
    displayResults(filteredResults);
}

// Получение метки источника
function getSourceLabel(source) {
    switch (source) {
        case 'opensearch': return 'OpenSearch';
        case 'mediawiki': return 'MediaWiki';
        case 'mock': return 'База знаний (демо)';
        default: return 'Неизвестный источник';
    }
}

// Получение класса для бейджа источника
function getSourceBadgeClass(source) {
    switch (source) {
        case 'opensearch': return 'badge bg-primary source-badge-opensearch';
        case 'mediawiki': return 'badge bg-success source-badge-mediawiki';
        case 'mock': return 'badge bg-secondary source-badge-mock';
        default: return 'badge bg-secondary';
    }
}

// Отображение результатов поиска
function displayResults(results) {
    const resultsContainer = $('#search-results');
    resultsContainer.empty();

    if (results.length === 0) {
        resultsContainer.html('<div class="alert alert-warning">Нет результатов, соответствующих выбранным фильтрам.</div>');
        return;
    }

    resultsContainer.append(`<h4>Найдено решений: ${results.length}</h4>`);

    results.forEach(result => {
        const source = result.source || 'mock';
        const sourceLabel = getSourceLabel(source);
        const sourceBadgeClass = getSourceBadgeClass(source);

        // Формируем содержимое
        let content = result.content;

        // Если есть подсветка, добавляем её
        if (result.highlight) {
            const highlightHtml = result.highlight.replace(/\n/g, '<br>');
            content = `<p class="card-text">${highlightHtml}</p>`;
        } else {
            // Обрезаем длинный текст
            const maxLength = 300;
            if (content && content.length > maxLength) {
                content = content.substring(0, maxLength) + '...';
            }
            content = `<p class="card-text">${content}</p>`;
        }

        // Добавляем теги, если они есть
        let tagsHtml = '';
        if (result.tags && result.tags.length > 0) {
            tagsHtml = '<div class="mt-2"><strong>Теги:</strong> ';
            tagsHtml += result.tags.map(tag => `<span class="badge bg-light text-dark me-1">${tag}</span>`).join('');
            tagsHtml += '</div>';
        }

        // Создаем карточку результата
        const cardHtml = `
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">${result.title}</h5>
                    <div>
                        <span class="${sourceBadgeClass}">${sourceLabel}</span>
                        <span class="badge bg-info ms-1">Релевантность: ${Math.round(result.score * 10) / 10}</span>
                    </div>
                </div>
                <div class="card-body">
                    ${content}
                    ${tagsHtml}
                    <div class="mt-2">
                        ${result.url ? `<a href="${result.url}" target="_blank" class="btn btn-outline-primary btn-sm me-2">Перейти к источнику</a>` : ''}
                        <button class="btn btn-success btn-sm create-ticket-btn" 
                                data-solution="${result.content.replace(/"/g, '&quot;')}"
                                data-source="${source}">
                            Создать заявку с этим решением
                        </button>
                    </div>
                </div>
            </div>
        `;

        resultsContainer.append(cardHtml);
    });
}