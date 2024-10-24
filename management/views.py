from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
import json
from django.views.generic import TemplateView

from export.export import export_all_data, export_user_data
from vadipartiSweets.utils import convert_number_to_weight
from .forms import ConfigForm
from booking.models import Order, OrderItem
from .models import BillBook, UserDeposits, DailyReadyItem
from custom_auth.models import User

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

            return redirect("/management/configuration")

    context = {
        "allow_new_order": ALLOW_NEW_ORDER,
        "allow_edit_order": ALLOW_UPDATE_ORDER,
        "allow_delete_order": ALLOW_DELETE_ORDER,
    }
    return render(request, "management/config.html", context)


@login_required
def download_excel(request):
    try:
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
    except Exception as e:
        print(e)
        return JsonResponse({"detail": "error occurred"})


class AdminDashboardAPIView(APIView):
    def get(self, request):
        user_deposit_queryset = UserDeposits.objects.prefetch_related("user").all()
        users = User.objects.filter(is_superuser=False)
        order_item_queryset = OrderItem.objects.prefetch_related(
            "item", "item__base_item", "booking", "booking__book", "booking__book__user"
        ).all()
        bill_book_queryset = BillBook.objects.prefetch_related("user").all()
        ready_item_queryset = DailyReadyItem.objects.prefetch_related(
            "item", "item__base_item"
        ).all()

        orders: set[Order] = set()
        items_quantity = {}
        for order_item in order_item_queryset:
            orders.add(order_item.booking)
            if order_item.item.base_item.name not in items_quantity:
                items_quantity[order_item.item.base_item.name] = {
                    "quantity": 0,
                    "amount": 0,
                    "ready_quantity": 0,
                    "box_quantity": {},
                }
            items_quantity[order_item.item.base_item.name][
                "quantity"
            ] += order_item.order_quantity * int(order_item.item.box_size)
            items_quantity[order_item.item.base_item.name]["amount"] += (
                order_item.order_quantity * order_item.item.price
            )

            if (
                str(order_item.item.box_size)
                not in items_quantity[order_item.item.base_item.name]["box_quantity"]
            ):
                items_quantity[order_item.item.base_item.name]["box_quantity"][
                    str(order_item.item.box_size)
                ] = {
                    "order_quantity": 0,
                    "delivered_quantity": 0,
                    "ready_quantity": 0,
                }
            items_quantity[order_item.item.base_item.name]["box_quantity"][
                str(order_item.item.box_size)
            ]["order_quantity"] += order_item.order_quantity
            items_quantity[order_item.item.base_item.name]["box_quantity"][
                str(order_item.item.box_size)
            ]["delivered_quantity"] += order_item.delivered_quantity

        for ready_item in ready_item_queryset:
            item_name = ready_item.item.base_item.name
            if item_name not in items_quantity:
                items_quantity[item_name] = {
                    "quantity": 0,
                    "amount": 0,
                    "ready_quantity": 0,
                    "box_quantity": {},
                }
            items_quantity[item_name]["ready_quantity"] += ready_item.quantity * int(
                ready_item.item.box_size
            )
            item_box = str(ready_item.item.box_size)
            if item_box not in items_quantity[item_name]["box_quantity"]:
                items_quantity[item_name]["box_quantity"][
                    str(ready_item.item.box_size)
                ] = {
                    "order_quantity": 0,
                    "delivered_quantity": 0,
                    "ready_quantity": 0,
                }
            items_quantity[item_name]["box_quantity"][item_box][
                "ready_quantity"
            ] += ready_item.quantity

        dealer_wise_data = {}
        for user in users:
            dealer_name = user.username
            dealer_wise_data[dealer_name] = {
                "full_name": user.get_full_name(),
                "total_order": 0,
                "total_order_amount": 0,
                "total_deposit": 0,
                "books": [],
            }
        for bill_book in bill_book_queryset:
            dealer_name = bill_book.user.username
            # if dealer_name not in dealer_wise_data:
            #     dealer_wise_data[dealer_name] = {
            #         "total_order": 0,
            #         "total_order_amount": 0,
            #         "total_deposit": 0,
            #         "books": [],
            #     }
            dealer_wise_data[dealer_name]["books"].append(bill_book.book_number)

        total_orders = 0
        total_order_amount = 0
        for order in orders:
            total_orders += 1
            total_order_amount += order.total_order_price
            dealer_name = order.book.user.username
            # if dealer_name not in dealer_wise_data:
            #     dealer_wise_data[dealer_name] = {
            #         "total_order": 0,
            #         "total_order_amount": 0,
            #         "total_deposit": 0,
            #     }
            dealer_wise_data[dealer_name]["total_order"] += 1
            dealer_wise_data[dealer_name][
                "total_order_amount"
            ] += order.total_order_price

        total_deposit_amount = 0
        for user_deposit in user_deposit_queryset:
            dealer_name = user_deposit.user.username
            dealer_wise_data[dealer_name]["total_deposit"] += user_deposit.amount
            total_deposit_amount += user_deposit.amount

        dealer_wise_data = [
            {"dealer": dealer_name, **data}
            for dealer_name, data in dealer_wise_data.items()
        ]

        dealer_wise_data = sorted(
            dealer_wise_data, key=lambda x: x["total_order_amount"], reverse=True
        )

        item_box_wise_table_data = []
        item_wise_table_data = []
        for item in items_quantity:
            item_data = items_quantity[item]
            for item_box in item_data["box_quantity"]:
                item_box_data = items_quantity[item]["box_quantity"][item_box]
                item_box_wise_table_data.append(
                    {
                        "item": f"{item} - {convert_number_to_weight(item_box)}",
                        "order_quantity": item_box_data["order_quantity"],
                        "delivered_quantity": item_box_data["delivered_quantity"],
                        "ready_quantity": item_box_data["ready_quantity"],
                    }
                )
            item_wise_table_data.append(
                {
                    "item": item,
                    "quantity": item_data["quantity"],
                    "amount": item_data["amount"],
                    "ready_quantity": item_data["ready_quantity"],
                }
            )

        return Response(
            {
                "total_orders": total_orders,
                "total_order_amount": total_order_amount,
                "total_deposit_amount": total_deposit_amount,
                "total_dealers": len(dealer_wise_data),
                "dealer_wise_data": dealer_wise_data,
                "item_wise_table_data": item_wise_table_data,
                "item_box_wise_table_data": item_box_wise_table_data,
            }
        )


class DepositPaymentFormTemplateView(TemplateView):
    template_name = "management/deposit_payment.html"
