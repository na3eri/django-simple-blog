from apps.users.models import Profile
from django.db import models
from django.urls import reverse
from slugify import slugify
from taggit.managers import TaggableManager


# ==========  Custom Managers  ==========
class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            status=Article.StatusChoices.PUBLISHED,
            is_deleted=False,
        )

    def popular(self):
        return self.order_by("-views")

    def by_category(self, category_name: str):
        return self.filter(
            category__name=category_name,
        )

    def by_slug(self, slug: str):
        return self.get(slug=slug)

    def by_tag(self, tag_slug: str):
        return self.filter(tags__slug=tag_slug)


class CommentQuerySet(models.QuerySet):
    def approved(self):
        return self.filter(is_approved=True)

    def root(self):
        return self.filter(parent__isnull=True)

    def for_article(self, article):
        return self.filter(article=article)

    def by_id(self, id: int):
        return self.get(id=id)


# Create your models here.
class Category(models.Model):
    user_profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="profile_categories",
    )
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    user_profile = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name="profile_articles",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="category_articles",
    )

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    excerpt = models.CharField(max_length=500)
    content = models.TextField()
    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.DRAFT
    )
    views = models.PositiveIntegerField(default=0)
    is_comment_enabled = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    deleted_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    image = models.ImageField(
        upload_to="articles",
        default="article_placeholder.jpg",
    )
    tags = TaggableManager(blank=True)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ("-published_at",)

    def save(self, *args, **kwargs):
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 2

        while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "single",
            kwargs={"slug": self.slug},
        )

    def __str__(self):
        return self.title


class Comment(models.Model):
    user_profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="profile_comments",
        null=True,
        blank=True,
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="article_comments",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="sub_comments",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=180)
    body = models.CharField(max_length=1000)
    is_approved = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = CommentQuerySet.as_manager()

    def __str__(self):
        return self.name


class Message(models.Model):
    class TopicChoices(models.TextChoices):
        QUESTION_ABOUT_A_ARTICLE = (
            "question_about_a_article",
            "Question about a article",
        )
        STORY_TIP = "story_tip", "Story tip"
        FEEDBACK = "feedback", "Feedback"
        COLLABORATION_PROPOSAL = "collaboration_proposal", "Collaboration proposal"
        SOMETHING_ELSE = "something_else", "Something else"

    user_profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="profile_messages",
        null=True,
        blank=True,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="sub_messages",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=180)
    subject = models.CharField(max_length=250)
    topic = models.CharField(max_length=30, choices=TopicChoices.choices)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
