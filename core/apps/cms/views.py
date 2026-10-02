from apps.cms.services.cms_homepage_service import CMSHomePageService
from django.contrib import messages
from django.shortcuts import redirect, render

# Create your views here.


def cms_dashboard_view(request):
    return render(
        request,
        "cms/cms-dashboard.html",
    )


def cms_home_page_view(request):
    service = CMSHomePageService()

    context = {
        "sliders": service.build_sliders(),
        "categories": service.build_categories(),
        "slider_form": service.build_slider_form(),
        "category_form": service.build_category_form(),
    }

    return render(
        request,
        "cms/cms-home-page.html",
        context,
    )


def cms_home_page_handle_slider_view(request, pk=None):
    service = CMSHomePageService()

    if request.method == "POST":
        result = service.handle_form(
            form_type="slider_form",
            post_data=request.POST,
            files_data=request.FILES,
            pk=pk,
        )

        if result["status"]:
            messages.success(
                request,
                result["detail"],
            )
        else:
            messages.error(
                request,
                result["detail"],
            )

    return redirect("cms_homepage")


def cms_home_page_delete_slider_view(request, pk):
    service = CMSHomePageService()

    if request.method == "POST":
        service.delete_slider(pk=pk)

        messages.success(
            request,
            "Slider deleted successfully.",
        )

    return redirect("cms_homepage")


def cms_home_page_handle_category_view(request, pk=None):
    service = CMSHomePageService()

    if request.method == "POST":
        result = service.handle_form(
            form_type="category_form",
            post_data=request.POST,
            files_data=request.FILES,
            pk=pk,
        )

        if result["status"]:
            messages.success(
                request,
                result["detail"],
            )
        else:
            messages.error(
                request,
                result["detail"],
            )

    return redirect("cms_homepage")


def cms_home_page_delete_category(request, pk):
    service = CMSHomePageService()

    if request.method == "POST":
        service.delete_category(pk=pk)

        messages.success(
            request,
            "Category deleted successfully.",
        )

    return redirect("cms_homepage")


def cms_contact_page_view(request):
    return render(
        request,
        "cms/cms-contact-page.html",
    )


def cms_about_page_view(request):
    return render(
        request,
        "cms/cms-about-page.html",
    )
