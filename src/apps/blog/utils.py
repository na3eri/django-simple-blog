from django.core.paginator import Paginator


def paginate_handler(request, queryset, results=6):
    paginator = Paginator(queryset, results)

    page_number = request.GET.get("page", 1)

    page_obj = paginator.get_page(page_number)

    current_page = page_obj.number
    total_pages = paginator.num_pages

    left_index = max(current_page - 4, 1)
    right_index = min(current_page + 4, total_pages)

    custom_range = range(
        left_index,
        right_index + 1,
    )

    return custom_range, page_obj
