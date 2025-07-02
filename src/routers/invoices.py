from utils.models import Invoice
from fastapi import APIRouter

router = APIRouter()

@router.post("/invoices", tags=["Invoices"])
async def create_invoice(invoice_data: Invoice):
  return invoice_data
