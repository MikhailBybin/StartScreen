document.addEventListener("DOMContentLoaded", function() {
  const imageSelect = document.getElementById('image_id');
  const imagePreview = document.getElementById('image_preview');

  imageSelect.addEventListener('change', function() {
    const selectedOption = this.options[this.selectedIndex];
    const imagePath = selectedOption.getAttribute('data-img-path');
    imagePreview.src = imagePath;
  });
});