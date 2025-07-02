from sqlmodel import select
from config.db_connection import SessionDep
from utils.models import Customer, Transaction, TransactionCreate
from fastapi import APIRouter, HTTPException, status

router = APIRouter()

@router.post("/transactions", status_code=status.HTTP_201_CREATED, tags=["Transactions"])
async def create_transaction(transaction_data: TransactionCreate, session: SessionDep):
  transaction_data_dict = transaction_data.model_dump()
  customer = session.get(Customer, transaction_data_dict.get("customer_id"))  # Ensure customer exists
  if not customer:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")

  transaction_db = Transaction.model_validate(transaction_data_dict)
  session.add(transaction_db)
  session.commit()
  session.refresh(transaction_db)

  return transaction_db

@router.get("/transactions", response_model=list[Transaction], tags=["Transactions"])
async def list_transactions(session: SessionDep):
  transaction = session.exec(select(Transaction)).all()
  return transaction  # Placeholder for listing transactions, to be implemented later
