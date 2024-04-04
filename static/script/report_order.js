
$(function() {
    $('.reports-list').sortable({
        connectWith: '.reports-list',
        placeholder: "ui-state-highlight",
        update: function(event, ui) {
            $(this).data('changed', true);
        }
    }).disableSelection();

    $('#save-order').click(function() {
    var allReportsData = [];
    $('.reports-list').each(function() {
        var category_id = $(this).data('category-id');
        var reportOrder = $(this).sortable('toArray', { attribute: 'data-id' });
        var reportsData = reportOrder.map(function(reportId, index) {
            return { id: reportId, order: index, new_category_id: category_id };
        });
        allReportsData = allReportsData.concat(reportsData);
    });

    $.ajax({
        url: "/update-report-order-and-category",
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(allReportsData),
        success: function(response) {
            alert("Порядок отчетов успешно обновлён!");
        },
        error: function(xhr, status, error) {
            alert('Произошла ошибка: ' + xhr.responseText);
        }
    });
});


});

