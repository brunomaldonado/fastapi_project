from sqlmodel import select
from config.db_connection import SessionDep
from utils.models import Customer, PaginatedTransactions, Transaction, TransactionCreate
from fastapi import APIRouter, HTTPException, Query, status

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

# challange 1: List transactions
# This endpoint will list all transactions, but we can add filtering and pagination later.
# obtner la cantidad total de paginas, cuantos elementos esta mos mostrando en esa pagina, etc.

@router.get("/transactions", response_model=PaginatedTransactions, tags=["Transactions"])
async def list_transactions(session: SessionDep, customer_id: int = Query(..., description="Customer ID"), skip: int = Query(0, description="Skip register"), limit: int = Query(4, description="Limit register")):
  customer = session.get(Customer, customer_id)
  if not customer:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")

  total_transactions = session.exec(select(Transaction).where(Transaction.customer_id == customer_id)).all()  # Get all transactions for the customer
  total_count = len(total_transactions)  # Get the total number of transactions for the customer
  query = select(Transaction).where(Transaction.customer_id == customer_id).offset(skip).limit(limit)

  transactions = session.exec(query).all()

  if not transactions:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No transactions found!")

  total_pages = (total_count + limit - 1) // limit  # Calculate total pages
  current_page = (skip // limit) + 1

  response = PaginatedTransactions(
  per_page=limit,
  total_pages=total_pages,
  current_page=current_page,
  customer_id=customer_id,
  transactions=transactions,
  )

  return response

