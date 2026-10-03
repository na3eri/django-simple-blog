from apps.cms.services.cms_aboutpage_service import CMSAboutPageService
from apps.cms.services.cms_contactpage_service import (
    CMSContactPageService,
)
from apps.cms.services.cms_homepage_service import (
    CMSHomePageService,
)
from django.contrib import messages
from django.shortcuts import redirect, render


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

    if request.method != "POST":
        return redirect("cms_homepage")

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

    if request.method != "POST":
        return redirect("cms_homepage")

    service.delete_slider(pk=pk)

    messages.success(
        request,
        "Slider deleted successfully.",
    )

    return redirect("cms_homepage")


def cms_home_page_handle_category_view(request, pk=None):
    service = CMSHomePageService()

    if request.method != "POST":
        return redirect("cms_homepage")

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

    if request.method != "POST":
        return redirect("cms_homepage")

    service.delete_category(pk=pk)

    messages.success(
        request,
        "Category deleted successfully.",
    )

    return redirect("cms_homepage")


def cms_contact_page_view(request):
    service = CMSContactPageService()

    if request.method == "POST":
        result = service.handle_form(
            post_data=request.POST,
            files_data=request.FILES,
        )

        if result["status"]:
            messages.success(
                request,
                result["detail"],
            )

            form = service.build_form(
                instance=service.contact_data_instance,
            )

        else:
            messages.error(
                request,
                result["detail"],
            )

            form = result["form"]

    else:
        form = service.build_form(
            instance=service.contact_data_instance,
        )

    context = {
        "form": form,
    }

    return render(
        request,
        "cms/cms-contact-page.html",
        context,
    )


def cms_about_page_view(request):
    service = CMSAboutPageService()

    if request.method == "POST":
        result = service.handle_form(
            form_type="about_data",
            post_data=request.POST,
        )
        if result["status"]:
            messages.success(request, result["detail"])
            data_form = service.build_form(
                form_type="about_data",
                instance=service.about_data_instance,
            )
        else:
            messages.error(request, result["detail"])
            data_form = result["form"]
    else:
        data_form = service.build_form(
            form_type="about_data",
            instance=service.about_data_instance,
        )

    context = {
        "data_form": data_form,
        "image_form": service.build_form(form_type="about_image"),
        "images": service.build_images(),
    }
    return render(
        request,
        "cms/cms-about-page.html",
        context,
    )


def cms_about_page_handle_image_view(request, pk=None):
    service = CMSAboutPageService()

    if request.method != "POST":
        return redirect("cms_aboutpage")

    result = service.handle_form(
        form_type="about_image",
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

    return redirect("cms_aboutpage")
