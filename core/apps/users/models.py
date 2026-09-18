from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set.")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class Profile(models.Model):
    class ProfileRole(models.TextChoices):
        CONTENT_EDITOR = "content_editor", "Content Editor"
        ADMIN = "admin", "Admin"

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", editable=False
    )

    image = models.ImageField(
        upload_to="article",
        default="placeholder.png",
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=200, unique=True, editable=False)
    role = models.CharField(
        max_length=30, choices=ProfileRole.choices, default=ProfileRole.CONTENT_EDITOR
    )
    job_title = models.CharField(max_length=40)
    short_bio = models.CharField(max_length=500)
    x_url = models.URLField(max_length=300)
    facebook_url = models.URLField(max_length=300)
    instagram_url = models.URLField(max_length=300)
    linkedin_url = models.URLField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("email", "-updated_at", "-created_at")

    def __str__(self):
        return f"{self.id} | {self.email} | {self.role} | {self.job_title} | {self.updated_at}"
