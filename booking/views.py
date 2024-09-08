from typing import Any
from datetime import datetime
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.views.generic import TemplateView
from django.utils import timezone
from django.db import transaction, IntegrityError
from django.contrib.auth.decorators import login_required as login_required_func
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from booking.decorators import login_required
from booking.models import Order, OrderItem
from booking.utils import create_booking, delete_order, update_booking
from management.models import Item


class NewOrderTemplateView(TemplateView):
    template_name = "booking/new_order.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        items = Item.objects.prefetch_related("base_item").all()
        item_data = {}
        for item in items:
            pk = str(item.base_item.pk)
            if item.box_size not in ["1000", "500"]:
                continue
            if not item_data.get(pk):
                item_data[pk] = {
                    "id": pk,
                    "title": item.base_item.name,
                    "1000": {},
                    "500": {},
                }
            item_data[pk][str(item.box_size)] = {
                "id": item.pk,
                "price": item.price,
            }

        return {"items_data": list(item_data.values()), "date": timezone.now().strftime("%Y-%m-%d")}


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        try:
            with transaction.atomic():
                data = request.data
                user = request.user
                items = {}
                for item in Item.objects.prefetch_related("base_item").all():
                    items[f"{item.pk}"] = item

                booking_data = data["booking"]
                order_items = []
                for item in booking_data.keys():
                    order_items.append(
                        {"item": items[f"{item}"], "quantity": booking_data[item]}
                    )

                create_booking(
                    int(data["order_id"]),
                    data["customer_name"],
                    order_items,
                    float(data["received_amount"]),
                    data["special_note"],
                    user=user,
                    order_date=data["order_date"],
                    phone=data.get("phone", None),
                )
                return Response("OK")
        except IntegrityError:
            return Response(f"Order with order number {data["order_id"]} already exists.", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
               str(e.args[0]), status=status.HTTP_400_BAD_REQUEST
            )


class EditOrderTemplateView(TemplateView):
    template_name = "booking/edit_order.html"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        pk = self.kwargs.get("pk")
        order = Order.objects.get(pk=pk)
        order_items = OrderItem.objects.prefetch_related("booking", "item", "item__base_item").filter(booking=order)
        tmp = {}
        for order_item in order_items:
            tmp[f"{order_item.item.base_item.pk}_{order_item.item.box_size}"] = {
                "id": order_item.pk,
                "quantity": order_item.order_quantity,
            }
        
        items = Item.objects.prefetch_related("base_item").all()
        item_data = {}
        for item in items:
            pk = str(item.base_item.pk)
            if item.box_size not in ["1000", "500"]:
                continue
            if not item_data.get(pk):
                item_data[pk] = {
                    "id": pk,
                    "title": item.base_item.name,
                    "1000": {},
                    "500": {},
                }
            item_data[pk][str(item.box_size)] = {
                "id": item.pk,
                "price": item.price,
                "order_id": tmp.get(f"{pk}_{item.box_size}", {}).get("id", -1),
                "quantity": tmp.get(f"{pk}_{item.box_size}", {}).get("quantity", 0),
            }

        return {"items_data": list(item_data.values()), "order": order, "order_number": order.bill_number, "order_date": order.date.strftime("%Y-%m-%d"), "customer_name": order.customer_name, "received_amount": order.received_amount, "special_note": order.comment,}

class EditOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, pk, *args, **kwargs) -> Response:
        try:
            with transaction.atomic():
                print(request.data)
                data = request.data
                items = {}
                for item in Item.objects.prefetch_related("base_item").all():
                    items[f"{item.pk}"] = item
                
                order = Order.objects.get(pk=pk)
                order_items = OrderItem.objects.prefetch_related("booking", "item", "item__base_item").filter(booking=order)
                tmp = {}
                for order_item in order_items:
                    tmp[f"{order_item.pk}"] = order_item

                booking_data = data["booking"]
                order_items = []
                for item in booking_data.keys():
                    order_items.append(
                        {"item": items[f"{item}"], "quantity": booking_data[item]["quantity"], "order_item": tmp.get(f"{booking_data[item]["id"]}", None)}
                    )            

                update_booking(
                    pk,
                    int(data["order_id"]),
                    data["customer_name"],
                    order_items,
                    float(data["received_amount"]),
                    data["special_note"],
                    order_date=data["order_date"],
                    phone=data.get("phone", None),
                )
                
                return Response("OK")
        except IntegrityError:
            return Response(f"Order with order number {data["order_id"]} already exists.", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
            str(e.args[0]), status=status.HTTP_400_BAD_REQUEST
            )


@login_required_func
def deleteOrderView(request: HttpRequest, pk: int) -> HttpResponse:
    try:
        print(request.method.lower() == "delete")
        if not request.method.lower() == "delete":
            return HttpResponse("Method not allowed.", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        delete_order(pk=pk, user=request.user)
        return HttpResponse("OK")
    except Order.DoesNotExist:
        return HttpResponse("Order does not exist.", status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return HttpResponse(str(e.args[0]), status=status.HTTP_400_BAD_REQUEST)


## User Template Views
class UserHomeTemplateView(TemplateView):
    template_name = "booking/user_home.html"

    @login_required
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)


class UserBookingsTemplateView(TemplateView):
    template_name = "booking/user_bookings.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = {}
        
        search = self.request.GET.get("search", None)

        total_summary = (
            (
                Order.objects.prefetch_related("book", "book__user")
                .filter(book__user=self.request.user)
                .aggregate(
                    user_total=Sum("total_order_price"),
                    total_orders=Count("pk"),
                )
            )
            if self.request.user.is_superuser == False
            else (
                Order.objects.prefetch_related("book", "book__user").aggregate(
                    user_total=Sum("total_order_price"),
                    total_orders=Count("pk"),
                )
            )
        )
        total_summary["user_total"] = total_summary["user_total"] or 0
        total_summary["total_orders"] = total_summary["total_orders"] or 0
        if search:
            search = search.strip()
            dealer_orders = (
                Order.objects.prefetch_related("book", "book__user")
                .filter(book__user=self.request.user)
                .filter(
                    Q(bill_number__icontains=search)
                    | Q(customer_name__icontains=search)
                    | Q(customer_phone__icontains=search)
                )
                if self.request.user.is_superuser == False
                else Order.objects.prefetch_related("book", "book__user").filter(
                    Q(bill_number__icontains=search
                      | Q(customer_name__icontains=search)
                    | Q(customer_phone__icontains=search))
                )
            )
        else:
            dealer_orders = (
                Order.objects.prefetch_related("book", "book__user").filter(book__user=self.request.user)
                if self.request.user.is_superuser == False
                else Order.objects.prefetch_related("book", "book__user").all()
            )
        paginator = Paginator(dealer_orders, 50)  # Create a Paginator object
        page_number = self.request.GET.get("page")
        page = paginator.get_page(page_number)
       
        context = {"page": page, "total_summary": total_summary}
        return context
    
    @login_required
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)
