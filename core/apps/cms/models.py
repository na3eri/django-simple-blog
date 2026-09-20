from apps.blog.models import Category
from django.db import models


class Page(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ContactPageData(models.Model):
    page = models.OneToOneField(
        Page,
        on_delete=models.CASCADE,
        related_name="contact_page_data",
    )

    address = models.CharField(max_length=500)
    email = models.EmailField(max_length=150)
    phone_number = models.CharField(max_length=14)
    linkedin_url = models.URLField(max_length=100)
    instagram_url = models.URLField(max_length=100)
    x_url = models.URLField(max_length=250)
    facebook_url = models.URLField(max_length=250)
    map_url = models.URLField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Page: {self.page.name} - Contact Data"


class AboutPageData(models.Model):
    page = models.OneToOneField(
        Page,
        on_delete=models.CASCADE,
        related_name="about_page_data",
    )

    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300)
    first_description = models.CharField(max_length=300)
    second_description = models.CharField(max_length=300)
    third_description = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Page: {self.page.name} - About Data"


class AboutPageImage(models.Model):
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="about_page_images",
    )

    alt_message = models.CharField(max_length=100)

    image = models.ImageField(
        upload_to="about_page",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - Page: {self.page.name} - About Image"


class HomePageSlider(models.Model):
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="home_page_sliders",
    )

    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300)
    alt_message = models.CharField(max_length=300)
    url = models.URLField(max_length=500)
    order = models.PositiveIntegerField()

    image = models.ImageField(
        upload_to="home_page",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["page", "order"],
                name="unique_slider_order_per_page",
            ),
        ]

    def __str__(self):
        return f"{self.id} - Title: {self.title} - Page: {self.page.name} - Home Slider"


class HomePageCategory(models.Model):
    class Components(models.TextChoices):
        COMPONENT_A = "component_a", "Component A"
        COMPONENT_B = "component_b", "Component B"
        COMPONENT_C = "component_c", "Component C"

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="home_page_categories",
    )
    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        related_name="page_categories",
    )

    component_type = models.CharField(
        max_length=20,
        choices=Components.choices,
        default=Components.COMPONENT_A,
    )
    order = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["page", "order"],
                name="unique_category_order_per_page",
            ),
        ]

    def __str__(self):
        return f"{self.id} - Page: {self.page.name} - Category: {self.category.name} - Home Category"
