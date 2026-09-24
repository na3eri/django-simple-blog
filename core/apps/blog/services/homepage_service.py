from abc import ABC, abstractmethod

from apps.blog.models import Article
from apps.cms.models import HomePageCategory, HomePageSlider


class Component(ABC):
    def __init__(self, category_name: str):
        self.category_name = category_name

    @abstractmethod
    def build(self) -> dict:
        pass

    @staticmethod
    def get_item(
        data: list,
        index: int | None = None,
        start: int | None = None,
        end: int | None = None,
    ):
        if index is not None:
            return data[index] if 0 <= index < len(data) else None

        if start is not None and end is not None:
            if start < 0 or end < 0:
                return None

            return data[start:end]

        if start is not None:
            if start < 0:
                return None

            return data[start:]

        if end is not None:
            if end < 0:
                return None

            return data[:end]

        return None


class ComponentA(Component):
    def _query(self, category_name: str) -> list:
        return list(Article.objects.published().by_category(category_name)[:10])

    def _parse_data(self, category_name: str, data: list) -> dict:
        return {
            "category_name": category_name,
            "head_article": self.get_item(data, 0),
            "second_article": self.get_item(data, 1),
            "third_article": self.get_item(data, 2),
            "fourth_article": self.get_item(data, 3),
            "column_articles": self.get_item(data, start=4),
        }

    def build(self) -> dict:
        data = self._query(self.category_name)
        return self._parse_data(self.category_name, data)


class ComponentB(Component):
    def _query(self, category_name: str) -> list:
        return list(Article.objects.published().by_category(category_name)[:10])

    def _parse_data(self, category_name: str, data: list) -> dict:
        return {
            "category_name": category_name,
            "head_article": self.get_item(data, 0),
            "second_article": self.get_item(data, 1),
            "third_article": self.get_item(data, 2),
            "fourth_article": self.get_item(data, 3),
            "column_articles": self.get_item(data, start=4),
        }

    def build(self) -> dict:
        data = self._query(self.category_name)
        return self._parse_data(self.category_name, data)


class ComponentC(Component):
    def _query(self, category_name: str) -> list:
        return list(Article.objects.published().by_category(category_name))

    def _parse_data(self, category_name: str, data: list) -> dict:
        return {
            "category_name": category_name,
            "head_article": data[0],
            "second_article": data[1],
            "third_article": data[2],
            "fourth_article": data[3],
            "column_articles": data[4:],
        }

    def build(self) -> dict:
        data = self._query(self.category_name)
        return self._parse_data(self.category_name, data)


class HomePageService:
    def __init__(self):
        self.components = {
            "component_a": ComponentA,
            "component_b": ComponentB,
            "component_c": ComponentC,
        }

    def build_slider(self) -> list:
        return list(HomePageSlider.objects.all())

    def build_popular(self) -> dict:
        articles = list(Article.objects.published()[:7])
        most_viewed_articles = list(Article.objects.popular()[:6])

        return {
            "head_article": articles[0],
            "first_column": articles[1:4],
            "second_column": articles[4:7],
            "most_viewed": most_viewed_articles,
        }

    def build_component(
        self,
        component_type: str,
        category_name: str,
    ) -> dict:
        component_class = self.components[component_type]
        return component_class(category_name).build()

    def build_all_components(self):
        return {
            category_section.component_type: self.build_component(
                category_section.component_type,
                category_section.category.name,
            )
            for category_section in list(HomePageCategory.objects.all())
        }
