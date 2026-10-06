from apps.blog.forms import CommentForm, MessageForm
from apps.blog.models import Article, Comment, Message
from apps.blog.services.aboutpage_service import AboutPageService
from apps.blog.services.article_service import ArticleService
from apps.blog.services.articles_list_service import ArticleListPageService
from apps.blog.services.contact_service import ContactPageService
from apps.blog.services.message_service import MessageService
from apps.blog.services.homepage_service import (
    Component,
    ComponentA,
    ComponentB,
    ComponentC,
    HomePageService,
)
from apps.cms.models import (
    AboutPageData,
    AboutPageImage,
    ContactPageData,
    HomePageSlider,
)
from django.core.paginator import Page as DjangoPage
from django.http.response import Http404


from random import randint

import factory
import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture
def about_page(page_factory):
    return page_factory(name="about")


@pytest.fixture
def contact_page(page_factory):
    return page_factory(name="contact")


@pytest.fixture
def home_page(page_factory):
    return page_factory(name="home")


class TestAboutPageService:
    def test_init_object_variables(self):
        service = AboutPageService()

        assert service.about_data == AboutPageData
        assert service.about_image == AboutPageImage

    def test_build_data_method(self, about_page, about_page_data_factory):
        fac = about_page_data_factory(page=about_page)
        service = AboutPageService()
        about_page_data = service.build_data()

        assert about_page_data.page == about_page
        assert about_page_data.title == "test"
        assert about_page_data.first_description == "test"
        assert about_page_data.second_description == "test"
        assert about_page_data.third_description == "test"

    def test_image_method(self, about_page, about_page_image_factory):
        first_image = about_page_image_factory(
            page=about_page,
            image=factory.django.ImageField(filename="test-image-1.jpg"),
        )
        second_image = about_page_image_factory(
            page=about_page,
            image=factory.django.ImageField(filename="test-image-2.jpg"),
        )
        third_image = about_page_image_factory(
            page=about_page,
            image=factory.django.ImageField(filename="test-image-3.jpg"),
        )
        service = AboutPageService()

        images = service.build_images()

        assert images["first_image"] == first_image
        assert images["second_image"] == second_image
        assert images["third_image"] == third_image

    def test_team_method(self, profile_factory):
        profile = profile_factory()
        service = AboutPageService()
        team_members = service.build_team()

        assert team_members == [profile]


class TestArticleService:
    def test_init_object_variables(self):
        service = ArticleService()

        assert service.article_model == Article
        assert service.comment_model == Comment

    def test_get_published_article_method(self, article_factory):
        article = article_factory(title="test published method")
        service = ArticleService()

        assert service.get_published_article("test-published-method") == article

        try:
            service.get_published_article("test-not-existed-slug")
        except Http404:
            assert True

    def test_build_form(self):
        service = ArticleService()

        assert isinstance(service.build_form(), CommentForm)

    def test_handle_comment(self, article_factory, profile_factory, comment_factory):
        article = article_factory()
        service = ArticleService()

        # test a simple comment
        post_data = dict(name="test", email="test@gmail.com", body="test")
        assert service.handle_comment(post_data, article)["status"]

        # test signed user comment
        post_data = dict(body="test")
        user_data = dict(
            full_name="test name",
            email="testmail@example.com",
            user_profile=profile_factory(),
        )
        assert service.handle_comment(post_data, article, user_data)["status"]

        # test invalid form
        post_data = dict(body="test")
        assert not service.handle_comment(post_data, article)["status"]

        # test parent comment does not exist
        post_data = dict(
            name="test name",
            email="test@example.com",
            body="test body",
            parent_id=999,
        )
        assert not service.handle_comment(post_data, article)["status"]

        # test 3rd sub comment constraint
        parent_comment = comment_factory(
            name="parent",
            email="parent@example.com",
            body="parent body",
            article=article,
        )
        sub_parent_comment = comment_factory(
            parent=parent_comment,
            name="sub parent",
            email="subparent@example.com",
            body="sub parent body",
            article=article,
        )
        sub_comment = comment_factory(
            parent=sub_parent_comment,
            name="sub comment",
            email="subcomment@example.com",
            body="sub comment body",
            article=article,
        )
        post_data = dict(
            name="test",
            email="test@example.com",
            body="test",
            parent_id=sub_comment.id,
        )
        assert not service.handle_comment(post_data, article)["status"]

        # test parent comment
        post_data = dict(
            name="test",
            email="test@example.com",
            body="test",
            parent_id=parent_comment.id,
        )
        assert service.handle_comment(post_data, article)["status"]

    def test_get_comments_method(self, article_factory, comment_factory):
        article = article_factory()
        service = ArticleService()

        parent_comment = comment_factory(
            name="parent",
            email="parent@example.com",
            body="parent body",
            article=article,
        )
        sub_parent_comment = comment_factory(
            parent=parent_comment,
            name="sub parent",
            email="subparent@example.com",
            body="sub parent body",
            article=article,
        )
        just_comment = comment_factory(
            name="sub comment",
            email="subcomment@example.com",
            body="sub comment body",
            article=article,
            is_approved=False,
        )

        comments = service.get_comments(article)
        assert comments.count() == 1
        assert set(comments) == {parent_comment}


class TestArticleListService:
    def test_build_category_method(self, category_factory):
        first_category = category_factory(name="first test")
        second_category = category_factory(name="second test")
        service = ArticleListPageService()
        categories = service.build_categories()

        assert isinstance(categories, list)
        assert set(categories) == {first_category, second_category}

    def test_recent_posts(self, article_factory, category_factory):
        category = category_factory(name="recent posts")
        articles = set()
        for i in range(1, 5):
            article = article_factory(
                title=f"random title {i}",
                category=category,
            )
            articles.add(article)
        service = ArticleListPageService()

        assert set(service.build_recent_posts()) == articles

    def test_build_tags_method(self, tag_factory, article_factory, category_factory):
        category = category_factory(name="forTagMethod")
        article = article_factory(title="for tags method", category=category)
        tags = set()
        for i in range(1, 5):
            tag = tag_factory(
                article=article,
                name=f"random name {i}",
            )
            tags.add(tag)
        service = ArticleListPageService()

        assert set(service.build_tags()) == tags

    def test_build_articles(self, rf, article_factory, category_factory):
        service = ArticleListPageService()
        category = category_factory(name="forBuildArticles")
        articles = set()
        titles = ["python", "programming", "learning"]
        for t in titles:
            article = article_factory(
                category=category, title=f"title about {t}", tags=["mytag"]
            )
            articles.add(article)

        request = rf.get("/blog/")
        custom_range, pages = service.build_articles(request)

        assert isinstance(custom_range, range)
        assert isinstance(pages, DjangoPage)
        assert set(pages.object_list) == articles

        request = rf.get("/search/?q=python")
        custom_range, pages = service.build_articles(request, search="python")

        assert isinstance(custom_range, range)
        assert isinstance(pages, DjangoPage)
        assert set(pages.object_list) == set(
            article for article in articles if "python" in article.title
        )

        request = rf.get("/search/forBuildArticles/")
        custom_range, pages = service.build_articles(
            request, category="forBuildArticles"
        )

        assert isinstance(custom_range, range)
        assert isinstance(pages, DjangoPage)
        assert set(pages.object_list) == articles

        request = rf.get("/search/mytag/")
        custom_range, pages = service.build_articles(
            request,
            tag="mytag",
        )

        assert isinstance(custom_range, range)
        assert isinstance(pages, DjangoPage)
        assert set(pages.object_list) == articles


class TestContactPageService:
    def test_init_object_variables(self):
        service = ContactPageService()

        assert service.contact_data == ContactPageData

    def test_build_data_method(self, contact_page, contact_page_data_factory):
        contact_data = contact_page_data_factory(page=contact_page)
        service = ContactPageService()

        assert service.build_data() == contact_data


class TestHomePageService:
    def test_abstract_component(self):
        class TestComponent(Component):
            def build(self):
                pass

        component = TestComponent("test name")
        assert component.category_name == "test name"

        test_list = [i for i in range(10)]
        assert component.get_item(test_list) == None
        assert component.get_item(test_list, 1) == test_list[1]
        assert component.get_item(test_list, start=3, end=6) == test_list[3:6]
        assert component.get_item(test_list, start=-1, end=-2) == None
        assert component.get_item(test_list, start=5) == test_list[5:]
        assert component.get_item(test_list, start=-5) == None
        assert component.get_item(test_list, end=8) == test_list[:8]
        assert component.get_item(test_list, end=-8) == None

    def test_component_a(self, category_factory, article_factory):
        component_a_category = category_factory(name="compA")
        component_a = ComponentA("compA")

        article_titles = [
            "python",
            "rust",
            "javascript",
            "jackal",
            "c++",
            "c",
            "go",
            "r",
            "perl",
            "visual basic",
        ]
        articles = set()
        for t in article_titles:
            article = article_factory(
                category=component_a_category, title=f"Title with {t}"
            )
            articles.add(article)
        data = list(Article.objects.published().by_category("compA")[:10])

        assert component_a._query("compA") == data

        assert component_a._parse_data(
            "compA",
            component_a._query("compA"),
        ) == {
            "category_name": "compA",
            "head_article": component_a.get_item(data, 0),
            "second_article": component_a.get_item(data, 1),
            "third_article": component_a.get_item(data, 2),
            "fourth_article": component_a.get_item(data, 3),
            "column_articles": component_a.get_item(data, start=4),
        }

        assert component_a.build() == {
            "category_name": "compA",
            "head_article": component_a.get_item(data, 0),
            "second_article": component_a.get_item(data, 1),
            "third_article": component_a.get_item(data, 2),
            "fourth_article": component_a.get_item(data, 3),
            "column_articles": component_a.get_item(data, start=4),
        }

    def test_component_b(self, category_factory, article_factory):
        component_category = category_factory(name="compB")
        component = ComponentB("compB")

        article_titles = [
            "python",
            "rust",
            "javascript",
            "jackal",
            "c++",
            "c",
            "go",
            "r",
            "perl",
            "visual basic",
        ]
        articles = set()
        for t in article_titles:
            article = article_factory(
                category=component_category, title=f"Title with {t}"
            )
            articles.add(article)
        data = list(Article.objects.published().by_category("compB")[:10])

        assert component._query("compB") == data

        assert component._parse_data(
            "compB",
            component._query("compB"),
        ) == {
            "category_name": "compB",
            "head_article": component.get_item(data, 0),
            "second_article": component.get_item(data, 1),
            "third_article": component.get_item(data, 2),
            "fourth_article": component.get_item(data, 3),
            "column_articles": component.get_item(data, start=4),
        }

        assert component.build() == {
            "category_name": "compB",
            "head_article": component.get_item(data, 0),
            "second_article": component.get_item(data, 1),
            "third_article": component.get_item(data, 2),
            "fourth_article": component.get_item(data, 3),
            "column_articles": component.get_item(data, start=4),
        }

    def test_component_c(self, category_factory, article_factory):
        component_category = category_factory(name="compC")
        component = ComponentC("compC")

        article_titles = [
            "python",
            "rust",
            "javascript",
            "jackal",
            "c++",
            "c",
            "go",
            "r",
            "perl",
            "visual basic",
            "lion",
            "wolf",
            "cat",
            "duck",
            "monkey",
        ]
        articles = set()
        for t in article_titles:
            article = article_factory(
                category=component_category, title=f"Title with {t}"
            )
            articles.add(article)
        data = list(Article.objects.published().by_category("compC")[:15])

        assert component._query("compC") == data

        assert component._parse_data(
            "compC",
            component._query("compC"),
        ) == {
            "category_name": "compC",
            "head_article": component.get_item(data, 0),
            "second_article": component.get_item(data, 1),
            "third_article": component.get_item(data, 2),
            "first_column": component.get_item(data, start=3, end=6),
            "second_column": component.get_item(data, start=6, end=9),
            "third_column": component.get_item(data, start=9),
        }

        assert component.build() == {
            "category_name": "compC",
            "head_article": component.get_item(data, 0),
            "second_article": component.get_item(data, 1),
            "third_article": component.get_item(data, 2),
            "first_column": component.get_item(data, start=3, end=6),
            "second_column": component.get_item(data, start=6, end=9),
            "third_column": component.get_item(data, start=9),
        }

    def test_init_object_variables(self):
        service = HomePageService()

        assert service.components["component_a"] == ComponentA
        assert service.components["component_b"] == ComponentB
        assert service.components["component_c"] == ComponentC

    def test_build_slider_method(self, home_page, home_page_slider_factory):
        slider = home_page_slider_factory(page=home_page)
        service = HomePageService()

        assert service.build_slider() == list(HomePageSlider.objects.all())

    def test_build_popular_method(self, article_factory, category_factory):
        service = HomePageService()
        component_category = category_factory(name="popularMethod")
        article_titles = [
            "python",
            "rust",
            "javascript",
            "jackal",
            "c++",
            "c",
            "go",
            "r",
            "perl",
            "visual basic",
            "lion",
            "wolf",
            "cat",
            "duck",
            "monkey",
        ]
        articles = set()
        for t in article_titles:
            article = article_factory(
                category=component_category,
                title=f"Title with {t}",
                views=randint(100, 1000),
            )
            articles.add(article)
        articles_data = list(Article.objects.published()[:7])
        most_viewed_articles_data = list(Article.objects.popular()[:6])

        assert service.build_popular() == {
            "head_article": articles_data[0],
            "first_column": articles_data[1:4],
            "second_column": articles_data[4:7],
            "most_viewed": most_viewed_articles_data,
        }

    def test_build_component_method(self, category_factory, article_factory):
        service = HomePageService()
        component_category = category_factory(name="buildComponent")
        article_titles = [
            "python",
            "rust",
            "javascript",
            "jackal",
            "c++",
            "c",
            "go",
            "r",
            "perl",
            "visual basic",
        ]
        articles = set()
        for t in article_titles:
            article = article_factory(
                category=component_category, title=f"Title with {t}"
            )
            articles.add(article)

        component = service.build_component("component_a", component_category.name)
        data = list(
            Article.objects.published().by_category(component_category.name)[:10]
        )

        assert isinstance(component, dict)
        assert component == {
            "category_name": component_category.name,
            "head_article": ComponentA.get_item(data, 0),
            "second_article": ComponentA.get_item(data, 1),
            "third_article": ComponentA.get_item(data, 2),
            "fourth_article": ComponentA.get_item(data, 3),
            "column_articles": ComponentA.get_item(data, start=4),
        }

    def test_build_all_components_method(
        self,
        article_factory,
        home_page,
        home_page_category_factory,
        category_factory,
    ):
        service = HomePageService()

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

        assert service.build_all_components() == {
            home_page_cat_one.component_type: ComponentA(cat_one.name).build(),
            home_page_cat_two.component_type: ComponentB(cat_two.name).build(),
            home_page_cat_three.component_type: ComponentC(cat_three.name).build(),
        }


class TestMessageService:
    def test_init_object_variables(self):
        service = MessageService()

        assert service.model == Message
        assert service.form == MessageForm

    def test_build_form_method(self):
        service = MessageService()

        assert isinstance(service.build_form(), MessageForm)

    def test_build_form_authenticated_user(
        self,
        profile_factory,
    ):
        profile = profile_factory()
        user = profile.user

        post_data = {
            "name": "fake name",
            "email": "fake@example.com",
            "subject": "test subject",
            "topic": Message.TopicChoices.FEEDBACK,
            "body": "test body",
        }

        service = MessageService()
        form = service.build_form(
            post_data=post_data,
            user=user,
        )

        assert form.data["name"] == user.profile.full_name
        assert form.data["email"] == user.email

    def test_send_message_invalid_form(self):
        service = MessageService()

        post_data = {
            "name": "",
            "email": "",
            "subject": "",
            "topic": "",
            "body": "",
        }

        result = service.send_message(post_data=post_data)

        assert result["status"] is False
        assert isinstance(result["form"], MessageForm)
        assert result["detail"] == "Form is invalid"

    def test_send_message_method(self):
        service = MessageService()

        post_data = {
            "name": "test name",
            "email": "test@example.com",
            "subject": "test subject",
            "topic": Message.TopicChoices.FEEDBACK,
            "body": "test body",
        }

        result = service.send_message(post_data=post_data)

        assert result["status"] is True
        assert result["detail"] == "Message was sent"

        message = Message.objects.first()

        assert message.name == "test name"
        assert message.email == "test@example.com"
        assert message.subject == "test subject"
        assert message.topic == Message.TopicChoices.FEEDBACK
        assert message.body == "test body"

    def test_send_message_with_profile(
        self,
        profile_factory,
    ):
        profile = profile_factory()

        post_data = {
            "name": "test name",
            "email": "test@example.com",
            "subject": "test subject",
            "topic": Message.TopicChoices.FEEDBACK,
            "body": "test body",
            "profile_id": profile.id,
        }

        service = MessageService()
        result = service.send_message(post_data=post_data)

        assert result["status"] is True

        message = Message.objects.first()

        assert message.user_profile == profile

    def test_send_message_with_parent(
        self,
        message_factory,
    ):
        parent_message = message_factory()

        post_data = {
            "name": "test name",
            "email": "test@example.com",
            "subject": "test subject",
            "topic": Message.TopicChoices.FEEDBACK,
            "body": "test body",
            "parent_id": parent_message.id,
        }

        service = MessageService()
        result = service.send_message(post_data=post_data)

        assert result["status"] is True

        message = Message.objects.exclude(id=parent_message.id).first()

        assert message.parent == parent_message

    def test_send_message_with_profile_and_parent(
        self,
        profile_factory,
        message_factory,
    ):
        profile = profile_factory()
        parent_message = message_factory()

        post_data = {
            "name": "test name",
            "email": "test@example.com",
            "subject": "test subject",
            "topic": Message.TopicChoices.FEEDBACK,
            "body": "test body",
            "profile_id": profile.id,
            "parent_id": parent_message.id,
        }

        service = MessageService()
        result = service.send_message(post_data=post_data)

        assert result["status"] is True

        message = Message.objects.exclude(id=parent_message.id).first()

        assert message.user_profile == profile
        assert message.parent == parent_message

    def test_send_message_with_nonexistent_profile(
        self,
    ):
        service = MessageService()

        post_data = {
            "name": "test name",
            "email": "test@example.com",
            "subject": "test subject",
            "topic": Message.TopicChoices.FEEDBACK,
            "body": "test body",
            "profile_id": 999,
        }

        result = service.send_message(post_data=post_data)

        assert result["status"] is True

        message = Message.objects.first()

        assert message.user_profile is None

    def test_send_message_with_nonexistent_parent(
        self,
    ):
        service = MessageService()

        post_data = {
            "name": "test name",
            "email": "test@example.com",
            "subject": "test subject",
            "topic": Message.TopicChoices.FEEDBACK,
            "body": "test body",
            "parent_id": 999,
        }

        result = service.send_message(post_data=post_data)

        assert result["status"] is True

        message = Message.objects.first()

        assert message.parent is None

    def test_send_message_authenticated_user(
        self,
        profile_factory,
    ):
        profile = profile_factory()
        user = profile.user

        post_data = {
            "name": "fake name",
            "email": "fake@example.com",
            "subject": "test subject",
            "topic": Message.TopicChoices.FEEDBACK,
            "body": "test body",
        }

        service = MessageService()
        result = service.send_message(
            post_data=post_data,
            user=user,
        )

        assert result["status"] is True

        message = Message.objects.first()

        assert message.name == user.profile.full_name
        assert message.email == user.email
