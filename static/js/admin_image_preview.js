document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('#id_cover_image_file');
    const formField = document.querySelector('.field-cover_image_file');

    if (fileInput && formField) {
        // Create a preview container
        const previewContainer = document.createElement('div');
        previewContainer.id = 'cover-image-preview';
        previewContainer.style.marginTop = '10px';
        formField.appendChild(previewContainer);

        // Handle file selection
        fileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            previewContainer.innerHTML = ''; // Clear previous preview

            if (file) {
                // Validate file type
                if (!file.type.match('image/(png|jpeg)')) {
                    previewContainer.innerHTML = '<p style="color: red;">Only PNG and JPEG images are supported.</p>';
                    return;
                }

                // Create and display preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.style.maxWidth = '200px';
                    img.style.maxHeight = '200px';
                    previewContainer.appendChild(img);
                };
                reader.readAsDataURL(file);
            }
        });
    }
});