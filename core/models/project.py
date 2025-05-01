from django.db import models
from django.utils.text import slugify
from support.models.mixims import TouchDatesMixim
from django_ckeditor_5.fields import CKEditor5Field


class Project(TouchDatesMixim):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = CKEditor5Field("Content", config_name="extends")
    cover_image = models.TextField(blank=True, null=True)  # Store Base64 string
    meta_description = models.CharField(max_length=160)
    meta_keywords = models.CharField(max_length=200)
    is_published = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
