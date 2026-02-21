from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter()


class OrderItem(BaseModel):
    name: str
    quantity: int
    price: float
    notes: Optional[str] = None


class ReceiptRequest(BaseModel):
    order_id: str
    order_number: int
    order_type: str  # dine_in, takeaway, delivery
    table_number: Optional[str] = None
    items: List[OrderItem]
    subtotal: float
    tax_amount: float
    discount_amount: float = 0
    service_charge: float = 0
    total: float
    payment_method: str
    staff_name: str
    restaurant_name: str
    restaurant_address: Optional[str] = None
    restaurant_phone: Optional[str] = None
    vat_number: Optional[str] = None


class ReceiptResponse(BaseModel):
    id: str
    order_id: str
    receipt_number: str
    content: str  # ESC/POS formatted content or plain text
    created_at: datetime


@router.post("/generate", response_model=ReceiptResponse)
async def generate_receipt(request: ReceiptRequest):
    """Generate a receipt for an order"""
    receipt_id = str(uuid.uuid4())
    receipt_number = f"R-{request.order_number:06d}"

    # Generate receipt content
    content = generate_receipt_content(request, receipt_number)

    return ReceiptResponse(
        id=receipt_id,
        order_id=request.order_id,
        receipt_number=receipt_number,
        content=content,
        created_at=datetime.utcnow()
    )


def generate_receipt_content(request: ReceiptRequest, receipt_number: str) -> str:
    """Generate plain text receipt content"""
    lines = []
    width = 42  # Standard thermal printer width

    # Header
    lines.append("=" * width)
    lines.append(request.restaurant_name.center(width))
    if request.restaurant_address:
        lines.append(request.restaurant_address.center(width))
    if request.restaurant_phone:
        lines.append(f"Tel: {request.restaurant_phone}".center(width))
    if request.vat_number:
        lines.append(f"VAT: {request.vat_number}".center(width))
    lines.append("=" * width)

    # Order info
    lines.append(f"Receipt: {receipt_number}")
    lines.append(f"Order:   #{request.order_number}")
    lines.append(f"Type:    {request.order_type.replace('_', ' ').title()}")
    if request.table_number:
        lines.append(f"Table:   {request.table_number}")
    lines.append(f"Staff:   {request.staff_name}")
    lines.append(f"Date:    {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    lines.append("-" * width)

    # Items
    for item in request.items:
        item_total = item.price * item.quantity
        name_line = f"{item.quantity}x {item.name}"
        price_str = f"£{item_total:.2f}"
        padding = width - len(name_line) - len(price_str)
        lines.append(f"{name_line}{' ' * padding}{price_str}")
        if item.notes:
            lines.append(f"   └ {item.notes}")

    lines.append("-" * width)

    # Totals
    def add_total_line(label, amount):
        price_str = f"£{amount:.2f}"
        padding = width - len(label) - len(price_str)
        lines.append(f"{label}{' ' * padding}{price_str}")

    add_total_line("Subtotal", request.subtotal)
    add_total_line("VAT (20%)", request.tax_amount)
    if request.discount_amount > 0:
        add_total_line("Discount", -request.discount_amount)
    if request.service_charge > 0:
        add_total_line("Service Charge", request.service_charge)

    lines.append("=" * width)
    total_label = "TOTAL"
    total_str = f"£{request.total:.2f}"
    padding = width - len(total_label) - len(total_str)
    lines.append(f"{total_label}{' ' * padding}{total_str}")
    lines.append("=" * width)

    # Payment
    lines.append(f"Paid by: {request.payment_method.upper()}")
    lines.append("")

    # Footer
    lines.append("Thank you for dining with us!".center(width))
    lines.append("Please come again".center(width))
    lines.append("")

    return "\n".join(lines)


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(receipt_id: str):
    """Get receipt by ID"""
    raise HTTPException(status_code=404, detail="Receipt not found")


@router.get("/order/{order_id}")
async def get_receipts_by_order(order_id: str):
    """Get all receipts for an order"""
    return []


@router.post("/{receipt_id}/print")
async def print_receipt(receipt_id: str, printer_name: Optional[str] = None):
    """Send receipt to printer"""
    # TODO: Implement actual printing via ESC/POS
    return {"status": "printed", "receipt_id": receipt_id, "printer": printer_name or "default"}
