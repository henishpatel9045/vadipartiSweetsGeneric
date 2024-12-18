from django.contrib.auth import get_user_model
from io import BytesIO
import xlsxwriter
import xlsxwriter.worksheet

from booking.models import OrderItem
from management.models import Item, UserDeposits
from vadipartiSweets.utils import convert_number_to_weight


User = get_user_model()

COMMON_COLOR = "#82CD47"
WHITE = "#fff"
BOX_LABLES = [
    "500 GM",
    "1 KG",
]
COLORS = [
    "#FFD933",
    "#33FFD9",
    "#FF33FF",
    "#33D9FF",
    "#FF6633",
    "#33FF66",
    "#FF9933",
    "#3399FF",
    "#FF3399",
    "#99FF33",
    "#33CCFF",
    "#FFCC33",
    "#33FFCC",
    "#FF5733",
    "#33FF57",
    "#3366FF",
    "#FF33B8",
    "#33FFFF",
    "#FF3366",
    "#66FF33",
]


def extract_data(pack):
    data = {}
    return data


def write_orders_data(
    worksheet: xlsxwriter.worksheet.Worksheet,
    excel_file,
    data,
    start_row=0,
    start_col=0,
):
    items = (
        Item.objects.prefetch_related("base_item")
        .all()
        .values("base_item__name", "box_size")
    )
    title_items = {}
    for item in items:
        if item["base_item__name"] not in title_items:
            title_items[item["base_item__name"]] = [int(item["box_size"])]
        else:
            title_items[item["base_item__name"]].append(int(item["box_size"]))
    title_items = {k: sorted(v) for k, v in title_items.items()}
    title_items = [
        (k, [convert_number_to_weight(i) for i in v]) for k, v in title_items.items()
    ]

    DATA_CELL_FORMAT = excel_file.add_format(
        {
            "align": "center",
            "valign": "vcenter",
            "border": 1,
        }
    )

    curr_row, curr_col = start_row, start_col

    def add_title(
        row, col, end_row, end_col, title: str, is_single_cell: bool = False, style={}
    ):
        is_single_cell = is_single_cell or (row == end_row and col == end_col)
        if is_single_cell:
            worksheet.write(
                row,
                col,
                title,
                excel_file.add_format(
                    {
                        "bg_color": COMMON_COLOR,
                        "color": "white",
                        "bold": True,
                        "align": "center",
                        "valign": "vcenter",
                        "size": 18,
                        **style,
                    }
                ),
            )
        else:
            worksheet.merge_range(
                row,
                col,
                end_row,
                end_col,
                title,
                excel_file.add_format(
                    {
                        "bg_color": COMMON_COLOR,
                        "font_color": "white",
                        "bold": True,
                        "align": "center",
                        "valign": "vcenter",
                        "size": 18,
                        **style,
                    }
                ),
            )

    add_title(
        curr_row,
        curr_col,
        curr_row + 1,
        curr_col,
        "Order Number",
        style={"border_color": "black", "border": 1},
    )
    curr_col += 1
    add_title(
        curr_row,
        curr_col,
        curr_row + 1,
        curr_col,
        "Customer Name",
        style={"border_color": "black", "border": 1},
    )
    curr_col += 1
    for item in title_items:
        item_name, sizes = item
        add_title(
            curr_row,
            curr_col,
            curr_row,
            curr_col + len(sizes) - 1,
            item_name,
            style={"border_color": "black", "top": 1, "left": 1, "right": 1},
        )
        for size in sizes:
            add_title(
                curr_row + 1,
                curr_col,
                curr_row + 1,
                curr_col,
                size,
                is_single_cell=True,
                style={"border_color": "black", "bottom": 1, "left": 1, "right": 1},
            )
            curr_col += 1
    add_title(
        curr_row,
        curr_col,
        curr_row + 1,
        curr_col,
        "Total Amount",
        style={"border_color": "black", "border": 1},
    )
    curr_col += 1
    add_title(
        curr_row,
        curr_col,
        curr_row + 1,
        curr_col,
        "Amount Received",
        style={"border_color": "black", "border": 1},
    )
    curr_col += 1
    add_title(
        curr_row,
        curr_col,
        curr_row + 1,
        curr_col,
        "Comment",
        style={"border_color": "black", "border": 1},
    )
    curr_col += 1
    add_title(
        curr_row,
        curr_col,
        curr_row + 1,
        curr_col,
        "Is Special Price",
        style={"border_color": "black", "border": 1},
    )
    curr_row += 2
    curr_col = start_col

    for order_pk in data:
        pk, order = order_pk
        worksheet.write(curr_row, curr_col, str(order["bill_number"]), DATA_CELL_FORMAT)
        curr_col += 1
        worksheet.write(curr_row, curr_col, order["customer_name"], DATA_CELL_FORMAT)
        curr_col += 1
        for item in title_items:
            item_name, sizes = item
            for size in sizes:
                worksheet.write_number(
                    curr_row,
                    curr_col,
                    order["items"].get(f"{item_name} {size}", 0),
                    DATA_CELL_FORMAT,
                )
                curr_col += 1
        worksheet.write_number(
            curr_row, curr_col, order["total_amount"], DATA_CELL_FORMAT
        )
        curr_col += 1
        worksheet.write_number(
            curr_row, curr_col, order["amount_received"], DATA_CELL_FORMAT
        )
        curr_col += 1
        worksheet.write(curr_row, curr_col, order["comment"], DATA_CELL_FORMAT)
        curr_col += 1
        worksheet.write(curr_row, curr_col, order["is_special_price"], DATA_CELL_FORMAT)
        curr_row += 1
        curr_col = start_col


def export_data(queryset, worksheet, excel_file, output):
    order_data = {}
    for order in queryset:
        if order.booking_id not in order_data:
            order_data[order.booking_id] = {
                "bill_number": order.booking.bill_number,
                "customer_name": order.booking.customer_name,
                "items": {},
                "total_amount": order.booking.total_order_price,
                "amount_received": order.booking.received_amount,
                "comment": order.booking.comment,
                "is_special_price": order.booking.is_special_price,
            }
        item_name = order.item.base_item.name
        size = convert_number_to_weight(order.item.box_size)
        order_data[order.booking_id]["items"][
            f"{item_name} {size}"
        ] = order.order_quantity

    order_data = [(k, v) for k, v in order_data.items()]
    order_data = sorted(order_data, key=lambda x: x[1]["bill_number"])

    write_orders_data(worksheet, excel_file, order_data, 0, 0)


def export_all_data():
    with BytesIO() as output:
        excel_file = xlsxwriter.Workbook(output)
        queryset = OrderItem.objects.prefetch_related(
            "booking", "booking__book", "booking__book__user", "item", "item__base_item"
        )
        for user in User.objects.all():
            SHEET_NAME = f"{user.username}"
            worksheet = excel_file.add_worksheet(SHEET_NAME)
            if user.is_superuser:
                export_data(queryset, worksheet, excel_file, output)
            else:
                export_data(
                    queryset.filter(booking__book__user=user),
                    worksheet,
                    excel_file,
                    output,
                )
        excel_file.close()
        output.seek(0)
        return output.read()


def export_user_data(user):
    with BytesIO() as output:
        SHEET_NAME = "Orders"
        excel_file = xlsxwriter.Workbook(output)
        worksheet = excel_file.add_worksheet(SHEET_NAME)
        queryset = OrderItem.objects.prefetch_related(
            "booking", "booking__book", "booking__book__user", "item", "item__base_item"
        ).filter(booking__book__user=user)
        export_data(queryset, worksheet, excel_file, output)
        excel_file.close()
        output.seek(0)
        return output.read()


def export_deposits_data(
    queryset: list[UserDeposits], worksheet, excel_file, curr_row, curr_col
):
    def add_title(
        row, col, end_row, end_col, title: str, is_single_cell: bool = False, style={}
    ):
        is_single_cell = is_single_cell or (row == end_row and col == end_col)
        if is_single_cell:
            worksheet.write(
                row,
                col,
                title,
                excel_file.add_format(
                    {
                        "bg_color": COMMON_COLOR,
                        "color": "white",
                        "bold": True,
                        "align": "center",
                        "valign": "vcenter",
                        "size": 18,
                        **style,
                    }
                ),
            )
        else:
            worksheet.merge_range(
                row,
                col,
                end_row,
                end_col,
                title,
                excel_file.add_format(
                    {
                        "bg_color": COMMON_COLOR,
                        "font_color": "white",
                        "bold": True,
                        "align": "center",
                        "valign": "vcenter",
                        "size": 18,
                        **style,
                    }
                ),
            )

    TITLES = [
        "Dealer Number",
        "Dealer Name",
        "Amount",
        "Payment Option",
        "Date",
        "Is Deposited By Dealer",
        "Bill Number",
        "Comment",
    ]
    curr_row = 0
    curr_col = 0
    for title in TITLES:
        add_title(
            curr_row,
            curr_col,
            curr_row,
            curr_col,
            title,
            style={"border_color": "black", "border": 1},
        )
        curr_col += 1
    curr_row += 1
    curr_col = 0

    DATA_CELL_FORMAT = excel_file.add_format(
        {
            "align": "center",
            "valign": "vcenter",
            "border": 1,
        }
    )

    for deposit in queryset:
        try:
            bill_number = deposit.order.bill_number
        except Exception as e:
            bill_number = ""
        worksheet.write(
            curr_row, curr_col, deposit.user.username, DATA_CELL_FORMAT
        )
        curr_col += 1
        worksheet.write(
            curr_row, curr_col, deposit.user.get_full_name(), DATA_CELL_FORMAT
        )
        curr_col += 1
        worksheet.write_number(curr_row, curr_col, deposit.amount, DATA_CELL_FORMAT)
        curr_col += 1
        worksheet.write(curr_row, curr_col, deposit.payment_option, DATA_CELL_FORMAT)
        curr_col += 1
        worksheet.write(
            curr_row, curr_col, deposit.date.strftime("%Y-%m-%d || %H:%M:%S %p"), DATA_CELL_FORMAT
        )
        curr_col += 1
        worksheet.write(
            curr_row, curr_col, deposit.is_deposited_by_dealer, DATA_CELL_FORMAT
        )
        curr_col += 1
        worksheet.write(
            curr_row, curr_col, bill_number, DATA_CELL_FORMAT
        )
        curr_col += 1
        worksheet.write(curr_row, curr_col, deposit.comment, DATA_CELL_FORMAT)
        curr_row += 1
        curr_col = 0


def export_for_deposit():
    with BytesIO() as output:
        SHEET_NAME = "Deposits"
        excel_file = xlsxwriter.Workbook(output)
        worksheet = excel_file.add_worksheet(SHEET_NAME)
        queryset = UserDeposits.objects.prefetch_related("user", "order").all()
        export_deposits_data(queryset, worksheet, excel_file, 0, 0)
        excel_file.close()
        output.seek(0)
        return output.read()
