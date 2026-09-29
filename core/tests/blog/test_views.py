import factory
import pytest
from apps.blog.models import Article
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture
def home_page(page_factory):
    return page_factory(name="home")


class TestHomeView:
    def test_home_view_url(
        self,
        client,
        home_page,
        home_page_category_factory,
        article_factory,
        category_factory,
    ):
        cat_one = category_factory(name="catOne")
        home_page_cat_one = home_page_category_factory(
            page=home_page, category=cat_one, component_type="component_a", order=1
        )

        cat_two = category_factory(name="catTwo")
        home_page_cat_two = home_page_category_factory(
            page=home_page, category=cat_two, component_type="component_b", order=2
        )

        cat_three = category_factory(name="catThree")
        home_page_cat_three = home_page_category_factory(
            page=home_page, category=cat_three, component_type="component_c", order=3
        )

        article_factory.create_batch(
            10,
            category=cat_one,
            title=factory.Faker("sentence", nb_words=6),
            excerpt=factory.Faker("paragraph", nb_sentences=2),
            content=factory.Faker("text", max_nb_chars=500),
            status=Article.StatusChoices.PUBLISHED,
        )

        article_factory.create_batch(
            10,
            category=cat_two,
            title=factory.Faker("sentence", nb_words=6),
            excerpt=factory.Faker("paragraph", nb_sentences=2),
            content=factory.Faker("text", max_nb_chars=500),
            status=Article.StatusChoices.PUBLISHED,
        )

        article_factory.create_batch(
            15,
            category=cat_three,
            title=factory.Faker("sentence", nb_words=6),
            excerpt=factory.Faker("paragraph", nb_sentences=2),
            content=factory.Faker("text", max_nb_chars=500),
            status=Article.StatusChoices.PUBLISHED,
        )

        url = reverse("home")
        response = client.get(url)
        assert response.status_code == 200


class TestAboutView:
    def test_about_view_url(self, client, about_page_data_factory):
        data = about_page_data_factory()
        url = reverse("about")
        response = client.get(url)

        assert response.status_code == 200


class TestSingleView:
    def test_single_view_url(self, client, article_factory, category_factory):
        category = category_factory(name="testSingle")
        article = article_factory(title="test single view")
        url = reverse("single", kwargs={"slug": article.slug})
        response = client.get(url)
        assert response.status_code == 200

    def test_single_view_post_method(
        self, profile_factory, user_factory, client, article_factory, category_factory
    ):
        category = category_factory(name="testSingle")
        article = article_factory(title="test single view post method")
        url = reverse("single", kwargs={"slug": article.slug})
        post_data = dict(
            name="test",
            email="test@example.com",
            body="test",
        )
        response = client.post(url, data=post_data)
        assert response.status_code == 302

        user = user_factory(
            email="something@example.com", password="someverysecret:password"
        )
        # user_profile = profile_factory(user=user, email="something@example.com")
        client.force_login(user)
        response = client.post(url, data=post_data)
        assert response.status_code == 200


class TestContactView:
    def test_contact_view_url(self, client, contact_page_data_factory):
        contact_data = contact_page_data_factory()
        url = reverse("contact")
        response = client.get(url)

        assert response.status_code == 200


class TestArticleListView:
    def test_article_list_view_for_blog(
        self, client, article_factory, category_factory
    ):
        category = category_factory(name="blog")
        article_factory.create_batch(
            10,
            category=category,
            title=factory.Faker("sentence", nb_words=6),
            excerpt=factory.Faker("paragraph", nb_sentences=2),
            content=factory.Faker("text", max_nb_chars=500),
            status=Article.StatusChoices.PUBLISHED,
        )

        url = reverse("blog")
        response = client.get(url)

        assert response.status_code == 200

    def test_article_list_view_for_search(
        self, client, article_factory, category_factory
    ):
        category = category_factory(name="search")
        article_factory.create_batch(
            10,
            category=category,
            title=factory.Faker("sentence", nb_words=6),
            excerpt=factory.Faker("paragraph", nb_sentences=2),
            content=factory.Faker("text", max_nb_chars=500),
            status=Article.StatusChoices.PUBLISHED,
        )

        url = reverse("search_results")
        response = client.get(url, data={"q": "python"})

        assert response.status_code == 200

    def test_article_list_view_for_category(
        self, client, article_factory, category_factory
    ):
        category = category_factory(name="someCategory")
        article_factory.create_batch(
            10,
            category=category,
            title=factory.Faker("sentence", nb_words=6),
            excerpt=factory.Faker("paragraph", nb_sentences=2),
            content=factory.Faker("text", max_nb_chars=500),
            status=Article.StatusChoices.PUBLISHED,
        )

        url = reverse("category", kwargs={"category_slug": category.slug})
        response = client.get(url)

        assert response.status_code == 200

    def test_article_list_view_for_tag(
        self, client, article_factory, category_factory, tag_factory
    ):
        tag = tag_factory(name="someTag")
        category = category_factory(name="tag")
        article_factory.create_batch(
            10,
            category=category,
            title=factory.Faker("sentence", nb_words=6),
            excerpt=factory.Faker("paragraph", nb_sentences=2),
            content=factory.Faker("text", max_nb_chars=500),
            status=Article.StatusChoices.PUBLISHED,
        )

        url = reverse("tag", kwargs={"tag_slug": tag.slug})
        response = client.get(url)

        assert response.status_code == 200
