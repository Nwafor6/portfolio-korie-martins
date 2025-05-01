from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Project
import base64
from io import BytesIO
from PIL import Image


class ProjectAdminForm(forms.ModelForm):
    # Add a FileField for image uploads in the admin
    cover_image_file = forms.FileField(required=False, label="Cover Image")

    class Meta:
        model = Project
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        cover_image_file = cleaned_data.get("cover_image_file")

        if cover_image_file:
            try:
                # Open the uploaded image
                img = Image.open(cover_image_file)
                # Validate image format (optional: restrict to PNG/JPEG)
                if img.format not in ["PNG", "JPEG"]:
                    raise forms.ValidationError(
                        "Only PNG and JPEG images are supported."
                    )
                # Validate file size (optional: e.g., max 5MB)
                if cover_image_file.size > 5 * 1024 * 1024:
                    raise forms.ValidationError(
                        "Image file size must be less than 5MB."
                    )
                # Convert to a BytesIO buffer
                buffered = BytesIO()
                img.save(buffered, format=img.format)
                # Encode to Base64
                img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                # Prefix with data URI scheme
                mime_type = f"image/{img.format.lower()}"
                cleaned_data["cover_image"] = f"data:{mime_type};base64,{img_base64}"
            except Exception as e:
                raise forms.ValidationError(f"Invalid image file: {str(e)}")
        elif not cover_image_file and not self.instance.cover_image:
            # If no file is uploaded and no existing image, clear cover_image
            cleaned_data["cover_image"] = None

        return cleaned_data


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ["title", "is_published", "display_cover_image"]
    prepopulated_fields = {"slug": ("title",)}
    fields = [
        "title",
        "slug",
        "content",
        "cover_image_file",
        "meta_description",
        "meta_keywords",
        "is_published",
    ]

    def display_cover_image(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height: 100px;" />', obj.cover_image
            )
        return "No Image"

    display_cover_image.short_description = "Cover Image"

    def save_model(self, request, obj, form, change):
        # Update cover_image with the Base64 string from cleaned_data
        obj.cover_image = form.cleaned_data.get("cover_image")
        super().save_model(request, obj, form, change)

    class Media:
        js = ("js/admin_image_preview.js",)  # Reference to custom JavaScript file


# Register other models (unchanged)
from django.apps import apps

app_models = apps.get_app_config("core").get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
