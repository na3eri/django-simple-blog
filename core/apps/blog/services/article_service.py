from apps.blog.forms import CommentForm
from apps.blog.models import Article, Comment
from django.db.models import Prefetch
from django.http import Http404


class ArticleService:
    def __init__(self):
        self.article_model = Article
        self.comment_model = Comment

    def get_published_article(self, slug: str):
        try:
            return self.article_model.objects.published().by_slug(slug)
        except self.article_model.DoesNotExist:
            raise Http404

    def build_form(self):
        return CommentForm()

    def handle_comment(
        self,
        post_data,
        article,
        user_data: dict | None = None,
    ):
        if user_data:
            post_data = post_data.copy()
            post_data["name"] = user_data["full_name"]
            post_data["email"] = user_data["email"]

        form = CommentForm(post_data)

        if not form.is_valid():
            return {
                "status": False,
                "article": article,
                "form": form,
            }

        comment = form.save(commit=False)
        comment.article = article

        if user_data:
            comment.user_profile = user_data["user_profile"]

        parent_id = form.cleaned_data.get("parent_id")

        if parent_id:
            try:
                parent_comment = self.comment_model.objects.get(
                    id=parent_id,
                    article=article,
                )
            except self.comment_model.DoesNotExist:
                form.add_error(
                    "parent_id",
                    "The selected parent comment does not exist.",
                )

                return {
                    "status": False,
                    "article": article,
                    "form": form,
                }

            if parent_comment.parent and parent_comment.parent.parent:
                form.add_error(
                    "parent_id",
                    "Replies cannot be nested further.",
                )

                return {
                    "status": False,
                    "article": article,
                    "form": form,
                }

            comment.parent = parent_comment

        comment.save()

        return {
            "status": True,
            "article": article,
            "form": form,
        }

    def get_comments(self, article):
        approved_comments = Comment.objects.approved()

        return (
            Comment.objects.approved()
            .for_article(article)
            .root()
            .prefetch_related(
                Prefetch(
                    "sub_comments",
                    queryset=approved_comments.prefetch_related(
                        Prefetch(
                            "sub_comments",
                            queryset=approved_comments,
                        )
                    ),
                )
            )
        )
