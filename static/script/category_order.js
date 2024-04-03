$(function() {
    $('#categories-list').sortable({
        update: function(event, ui) {
            var orderData = $(this).sortable('toArray', { attribute: 'data-id' });
            $.ajax({
                url: '/category/update_order',
                type: 'POST',
                data: JSON.stringify(orderData.map(function(id, index) {
                    return { id: id, order: index };
                })),
                contentType: 'application/json;charset=UTF-8',
                success: function(response) {
                    console.log(response.message);
                },
                error: function(response) {
                    alert('Ошибка обновления порядка');
                }
            });
        }
    });
});