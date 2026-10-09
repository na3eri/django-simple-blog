from django.db.models import Prefetch, Q
from django.utils import timezone

from apps.blog.models import Comment


class ProfileCommentsService:
    def __init__(self, user, status, search_query=None):
        self.user = user
        self.user_profile = user.profile
        self.status = self._set_status(status)
        self.search_query = self._set_search_query(search_query)
        self.comment_model = Comment

    @staticmethod
    def _set_status(status: str) -> str | None:
        if not (status and isinstance(status, str)):
            return None

        status = status.lower()

        if status not in ("all", "approved", "pending"):
            return None

        return status

    @staticmethod
    def _set_search_query(search_query: str | None) -> str | None:
        if not (search_query and isinstance(search_query, str)):
            return None

        search_query = search_query.strip()

        return search_query or None

    def _get_active_replies_prefetch(self):
        nested_replies = Prefetch(
            "sub_comments",
            queryset=self.comment_model.objects.filter(
                is_deleted=False,
            ).order_by("created_at"),
            to_attr="active_sub_comments",
        )

        return Prefetch(
            "sub_comments",
            queryset=(
                self.comment_model.objects.filter(is_deleted=False)
                .order_by("created_at")
                .prefetch_related(nested_replies)
            ),
            to_attr="active_sub_comments",
        )

    def _get_base_queryset(self):
        return (
            self.comment_model.objects.filter(
                article__user_profile=self.user_profile,
                is_deleted=False,
                parent__isnull=True,
            )
            .select_related(
                "user_profile",
                "article",
            )
            .prefetch_related(self._get_active_replies_prefetch())
        )

    def _get_total_comments(self):
        return self._get_base_queryset().count()

    def _get_total_approved_comments(self):
        return self._get_base_queryset().filter(is_approved=True).count()

    def _get_total_pending_comments(self):
        return self._get_base_queryset().filter(is_approved=False).count()

    def get_comments(self):
        queryset = self._get_base_queryset()

        if self.status == "approved":
            queryset = queryset.filter(
                is_approved=True,
            )

        elif self.status == "pending":
            queryset = queryset.filter(
                is_approved=False,
            )

        if self.search_query:
            queryset = queryset.filter(
                Q(name__icontains=self.search_query)
                | Q(email__icontains=self.search_query)
                | Q(body__icontains=self.search_query)
                | Q(article__title__icontains=self.search_query)
            )

        return queryset

    def get_context(self, view_context):
        return {
            "profile_instance": self.user_profile,
            "status": self.status,
            "search_query": self.search_query,
            "total_comments": self._get_total_comments(),
            "total_approved_comments": self._get_total_approved_comments(),
            "total_pending_comments": self._get_total_pending_comments(),
            "custom_range": view_context["paginator"].get_elided_page_range(
                number=view_context["page_obj"].number,
                on_each_side=2,
                on_ends=1,
            ),
        }

    def accept_comment(self, comment_id):
        try:
            comment = self.comment_model.objects.get(
                id=comment_id,
                article__user_profile=self.user_profile,
                is_deleted=False,
            )
        except self.comment_model.DoesNotExist:
            return False

        if comment.is_approved:
            return True

        comment.is_approved = True
        comment.approved_at = timezone.now()

        comment.save(
            update_fields=[
                "is_approved",
                "approved_at",
            ]
        )

        return True

    def reject_comment(self, comment_id):
        try:
            comment = self.comment_model.objects.get(
                id=comment_id,
                article__user_profile=self.user_profile,
                is_deleted=False,
            )
        except self.comment_model.DoesNotExist:
            return False

        if not comment.is_approved and comment.approved_at is None:
            return True

        comment.is_approved = False
        comment.approved_at = None

        comment.save(
            update_fields=[
                "is_approved",
                "approved_at",
            ]
        )

        return True

    def delete_comment(self, comment_id):
        try:
            comment = self.comment_model.objects.get(
                id=comment_id,
                article__user_profile=self.user_profile,
            )
        except self.comment_model.DoesNotExist:
            return False

        if comment.is_deleted:
            return True

        comment.is_deleted = True
        comment.deleted_at = timezone.now()

        comment.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
            ]
        )

        return True

    def reply_comment(self, parent_id, body):
        body = body.strip()

        if not body:
            return False

        try:
            parent_comment = self.comment_model.objects.get(
                id=parent_id,
                article__user_profile=self.user_profile,
                is_deleted=False,
            )
        except self.comment_model.DoesNotExist:
            return False

        if not parent_comment.is_approved:
            return False

        if (
            parent_comment.parent_id is not None
            and parent_comment.parent.parent_id is not None
        ):
            return False

        self.comment_model.objects.create(
            user_profile=self.user_profile,
            article=parent_comment.article,
            parent=parent_comment,
            name=self.user_profile.full_name,
            email=self.user_profile.email,
            body=body,
            is_approved=False,
            approved_at=None,
        )

        return True
