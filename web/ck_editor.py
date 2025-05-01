import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
import base64
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

# @csrf_exempt  # Allows requests without CSRF token
# @staff_member_required  # Restricts to staff users (optional, adjust as needed)
# def custom_upload_file(request):
#     if request.method == "POST" and request.FILES.get("upload"):
#         uploaded_file = request.FILES["upload"]
#         # Define the upload path (customize as needed)
#         upload_path = os.path.join("ckeditor_uploads", uploaded_file.name)

#         # Save the file using Django's storage system
#         file_path = default_storage.save(upload_path, uploaded_file)
#         file_url = default_storage.url(file_path)

#         # Return the response CKEditor 5 expects
#         return JsonResponse({"url": file_url})

#     # If the request is invalid, return an error
#     return JsonResponse(
#         {"error": {"message": "Invalid request or no file uploaded."}}, status=400
#     )

from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
import base64
from io import BytesIO
from PIL import Image


@csrf_exempt  # Required for CKEditor uploads
@staff_member_required  # Restrict to staff users (optional)
def custom_upload_file(request):
    if request.method == "POST" and request.FILES.get("upload"):
        uploaded_file = request.FILES["upload"]

        try:
            # Open the image with PIL
            img = Image.open(uploaded_file)
            if img.format not in ["PNG", "JPEG"]:
                return JsonResponse(
                    {"error": {"message": "Only PNG and JPEG images are supported."}},
                    status=400,
                )
            if uploaded_file.size > 5 * 1024 * 1024:  # Max 5MB
                return JsonResponse(
                    {"error": {"message": "Image file size must be less than 5MB."}},
                    status=400,
                )

            # Convert to a BytesIO buffer
            buffered = BytesIO()
            img.save(buffered, format=img.format)
            # Encode to Base64
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            # Create data URI
            mime_type = f"image/{img.format.lower()}"
            data_uri = f"data:{mime_type};base64,{img_base64}"

            # Return the data URI in the format CKEditor expects
            return JsonResponse({"url": data_uri})
        except Exception as e:
            return JsonResponse(
                {"error": {"message": f"Failed to process image: {str(e)}"}}, status=400
            )

    # Handle invalid requests
    return JsonResponse(
        {"error": {"message": "Invalid request or no file uploaded."}}, status=400
    )
