from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
import json

from export.export import export_all_data, export_data, export_user_data

from .forms import ConfigForm

# Create your views here.


def home(request):
    if not request.user.is_superuser:
        return HttpResponse("You are not authorized to view this page.")
    ALLOW_NEW_ORDER = settings.ALLOW_NEW_ORDER
    ALLOW_UPDATE_ORDER = settings.ALLOW_EDIT_ORDER
    ALLOW_DELETE_ORDER = settings.ALLOW_DELETE_ORDER
    BASE_DIR = settings.BASE_DIR

    if request.method == "POST":
        form = ConfigForm(request.POST)
        if form.is_valid():
            config = {
                "allowNewOrder": form.cleaned_data.get("allow_new_order"),
                "allowUpdateOrder": form.cleaned_data.get("allow_update_order"),
                "allowDeleteOrder": form.cleaned_data.get("allow_delete_order"),
            }
            print(config)
            with open(BASE_DIR / "global.config.json", "w") as f:
                json.dump(config, f, indent=4)
            setattr(settings, "ALLOW_NEW_ORDER", config.get("allowNewOrder"))
            setattr(settings, "ALLOW_EDIT_ORDER", config.get("allowUpdateOrder"))
            setattr(settings, "ALLOW_DELETE_ORDER", config.get("allowDeleteOrder"))

            return redirect("/management")

    context = {
        "allow_new_order": ALLOW_NEW_ORDER,
        "allow_edit_order": ALLOW_UPDATE_ORDER,
        "allow_delete_order": ALLOW_DELETE_ORDER,
    }
    return render(request, "management/config.html", context)


@login_required
def download_excel(request):
    # if request.user.is_superuser == False:
    #     return JsonResponse({"detail": "You are not authorized to perform this action"})
    # try:
        # Generate your Excel data and save it to a BytesIO object
        download_type = request.GET.get("type", "all")
        
        if download_type == "all":
            FILE_NAME = f"Sales Report ({timezone.now().strftime('%d-%m-%Y')}).xlsx"
            excel_buffer = export_all_data()
        else:
            FILE_NAME = f"Sales Report - {request.user} - ({timezone.now().strftime('%d-%m-%Y')}).xlsx"
            excel_buffer = export_user_data(request.user)
        # Create an HTTP response with the Excel data
        response = HttpResponse(content_type="application/ms-excel")
        response["Content-Disposition"] = f'attachment; filename="{FILE_NAME}"'
        response.write(excel_buffer)
        return response
    # except Exception as e:
    #     print(e)
    #     return JsonResponse({"detail": "error occurred"})
