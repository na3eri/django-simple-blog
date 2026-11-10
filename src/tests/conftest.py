import pytest
from pytest_factoryboy import register

from tests.factories import (
    AboutPageDataFactory,
    AboutPageImageFactory,
    ArticleFactory,
    CategoryFactory,
    CommentFactory,
    ContactPageDataFactory,
    HomePageCategoryFactory,
    HomePageSliderFactory,
    MessageFactory,
    PageFactory,
    ProfileFactory,
    TagFactory,
    TestServiceModelFactory,
    UserFactory,
)

register(UserFactory)
register(ProfileFactory)
register(CategoryFactory)
register(ArticleFactory)
register(CommentFactory)
register(MessageFactory)
register(PageFactory)
register(AboutPageDataFactory)
register(AboutPageImageFactory)
register(TagFactory)
register(ContactPageDataFactory)
register(HomePageSliderFactory)
register(HomePageCategoryFactory)
register(TestServiceModelFactory)


@pytest.fixture(autouse=True)
def use_temp_media_root(tmp_path, settings):
    """All files (images) that generated for tests
    will save in this temp directory and after tests
    finished it will be erase automatically"""

    settings.MEDIA_ROOT = tmp_path
