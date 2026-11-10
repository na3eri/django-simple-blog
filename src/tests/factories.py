import factory
from apps.blog.models import Article, Category, Comment, Message
from apps.cms.models import (
    AboutPageData,
    AboutPageImage,
    ContactPageData,
    HomePageCategory,
    HomePageSlider,
    Page,
)
from apps.users.models import Profile, User
from django.db.models.signals import post_save
from django.utils import timezone
from taggit.models import Tag

from tests.cms.cms_test_app.models import TestServiceModel


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"test{n}@example.com")
    password = "test"
    is_superuser = True
    is_staff = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        raw_password = extracted or "test"

        self.set_password(raw_password)

        if create:
            self.save(update_fields=["password"])


@factory.django.mute_signals(post_save)
class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
        skip_postgeneration_save = True

    user = factory.SubFactory(UserFactory)

    full_name = "test"
    email = factory.Sequence(lambda n: f"profile{n}@example.com")
    role = Profile.ProfileRole.CONTENT_EDITOR
    job_title = "test"
    short_bio = "test"
    x_url = "https://x.com/test"
    facebook_url = "https://facebook.com/test"
    instagram_url = "https://instagram.com/test"
    linkedin_url = "https://linkedin.com/in/test"


@factory.django.mute_signals(post_save)
class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        skip_postgeneration_save = True

    user_profile = factory.SubFactory(ProfileFactory)

    name = "test"


@factory.django.mute_signals(post_save)
class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article
        skip_postgeneration_save = True

    user_profile = factory.SubFactory(ProfileFactory)
    category = factory.SubFactory(CategoryFactory)

    title = "test"
    image = factory.django.ImageField(filename="test.jpg")
    excerpt = "test"
    content = "test"
    status = Article.StatusChoices.PUBLISHED
    published_at = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.tags.add(*extracted)


@factory.django.mute_signals(post_save)
class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment
        skip_postgeneration_save = True

    user_profile = factory.SubFactory(ProfileFactory)
    article = factory.SubFactory(ArticleFactory)

    name = "test"
    email = "test@example.com"
    body = "test"
    is_approved = True
    approved_at = factory.LazyFunction(timezone.now)


@factory.django.mute_signals(post_save)
class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message
        skip_postgeneration_save = True

    user_profile = factory.SubFactory(ProfileFactory)

    name = "test"
    email = factory.Sequence(lambda n: f"test{n}.example.com")
    subject = "test"
    body = "test"
    is_read = True


class PageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Page
        skip_postgeneration_save = True

    name = "test"


@factory.django.mute_signals(post_save)
class AboutPageDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AboutPageData
        skip_postgeneration_save = True

    page = factory.SubFactory(PageFactory)

    title = "test"
    subtitle = "test"
    first_description = "test"
    second_description = "test"
    third_description = "test"


@factory.django.mute_signals(post_save)
class AboutPageImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AboutPageImage
        skip_postgeneration_save = True

    page = factory.SubFactory(PageFactory)

    alt_message = "test"

    image = factory.django.ImageField(
        filename="test.jpg",
    )


@factory.django.mute_signals(post_save)
class ContactPageDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactPageData
        skip_postgeneration_save = True

    page = factory.SubFactory(PageFactory)

    address = "test"
    email = "test@example.com"
    phone_number = "+999999999"
    linkedin_url = "https://linkedin.com/in/test"
    instagram_url = "https://instagram.com/test"
    x_url = "https://x.com/test"
    facebook_url = "https://facebook.com/test"
    map_url = "https://map.google.com/test"


@factory.django.mute_signals(post_save)
class HomePageSliderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HomePageSlider
        skip_postgeneration_save = True

    page = factory.SubFactory(PageFactory)

    title = "test"
    subtitle = "test"
    alt_message = "test"
    url = "https://example.com/test"
    order = 1
    image = factory.django.ImageField(filename="slider.jpg")


@factory.django.mute_signals(post_save)
class HomePageCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HomePageCategory
        skip_postgeneration_save = True

    page = factory.SubFactory(PageFactory)
    category = factory.SubFactory(CategoryFactory)

    component_type = "component_a"
    order = 1


@factory.django.mute_signals(post_save)
class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        skip_postgeneration_save = True

    article = factory.SubFactory(ArticleFactory)

    name = factory.Sequence(lambda n: f"test {n}")


@factory.django.mute_signals(post_save)
class TestServiceModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TestServiceModel

    page = factory.SubFactory(PageFactory)
    title = factory.Sequence(
        lambda n: f"test {n}",
    )
