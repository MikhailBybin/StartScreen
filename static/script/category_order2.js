function updateCategoryName(categoryId) {
    var newName = $('#name-input-' + categoryId).val();
    $.ajax({
        url: '/category/update_name',
        type: 'POST',
        data: JSON.stringify({ id: categoryId, name: newName }),
        contentType: 'application/json;charset=UTF-8',
        success: function(response) {
            console.log(response.message);
            // Опционально: обновите имя категории в DOM без перезагрузки страницы
        },
        error: function(response) {
            alert('Ошибка обновления имени');
        }
    });
}
