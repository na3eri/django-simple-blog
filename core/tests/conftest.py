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
