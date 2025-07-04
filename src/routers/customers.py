from fastapi.params import Query
from utils.models import Customer, CustomerCreate, CustomerPlan, CustomerUpdate, Plan, StatusEnum, Transaction
from config.db_connection import SessionDep, engine
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from fastapi import APIRouter

router = APIRouter()

db_customers: list[Customer] = [] #This is a list to store customers in memory, not persisten storage

@router.post("/customers", response_model=Customer, tags=["Customers"])
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
  customer = Customer.model_validate(customer_data.model_dump())
  session.add(customer)
  session.commit()
  session.refresh(customer)
  # database simulate increment id when to create doscs...
  # customer.id = len(db_customers)
  # db_customers.append(customer)
  return customer

@router.get("/customers", response_model=list[Customer], tags=["Customers"])
async def list_customer(session: SessionDep):
  return session.exec(select(Customer)).all()

# new endpoint by id get customer
@router.get("/customers/{customer_id}", response_model=Customer, tags=["Customers"])
async def get_customer(customer_id: int, session: SessionDep):
  try:
    response = session.exec(select(Customer).where(Customer.id == customer_id)).one() # .one() will raise an error if no record is found
    if response is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

  return response


# delete endpoint by id get customer
@router.delete("/customers/{customer_id}", tags=["Customers"])
async def delete_customer(customer_id: int, session: SessionDep):
  try:
    customer = session.exec(select(Customer).where(Customer.id == customer_id)).one() # .one() will raise an error if no record is found
    transactions = session.exec(select(CustomerPlan).where(Transaction.customer_id == customer_id)).all()
    if transactions:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete customer with existing transactions!")
    if customer is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist!!")
    session.delete(customer)
    session.commit()
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

  return {"detail": "Customer deleted successfully!"}

# @router.put("/customers/{id}", response_model=Customer) # put is used to update a resource completely
# async def update_customer(customer_id: int, customer_data: CustomerUpdate, session: SessionDep):
#   try:
#     customer = session.exec(select(Customer).where(Customer.id == customer_id)).one() # .one() will raise an error if no record is found
#     if customer is None:
#       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")

#     for key, value in customer_data.model_dump().items():
#       setattr(customer, key, value)

#     session.add(customer)
#     session.commit()
#     session.refresh(customer)
#   except Exception as e:
#     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

#   return customer

@router.patch("/customers/{customer_id}", response_model=Customer, status_code=status.HTTP_201_CREATED, tags=["Customers"]) # patch is used to update a resource partially
async def partial_update_customer(customer_id: int, customer_data: CustomerUpdate, session: SessionDep):
  customer_db = session.get(Customer, customer_id)
  if not customer_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")

  customer_data_dict = customer_data.model_dump(exclude_unset=True)
  customer_db.sqlmodel_update(customer_data_dict)
  session.add(customer_db)
  session.commit()
  session.refresh(customer_db)

  return customer_db

# subscribe a customer to a plan
@router.post("/customers/{customer_id}/plans/{plan_id}", tags=["Customers"])
async def subscribe_customer_plan(customer_id: int, plan_id: int, session: SessionDep, plan_status: StatusEnum = Query()):
  customer_db = session.get(Customer, customer_id)
  plan_db = session.get(Plan, plan_id)

  if not customer_db or not plan_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer or Plan not found!")

  # Remove existing plans
  existing_plans = session.exec(select(CustomerPlan).where(CustomerPlan.customer_id == customer_id)).all()
  for plan in existing_plans:
    session.delete(plan)
  session.commit()

  customer_plan_db = CustomerPlan(customer_id=customer_db.id, plan_id=plan_db.id, status=plan_status)
  session.add(customer_plan_db)
  session.commit()
  session.refresh(customer_plan_db)

  return customer_plan_db

# list plans of a customer
@router.get("/customers/{customer_id}/plans", tags=["Customers"])
async def list_customer_plans(customer_id: int, session: SessionDep):
  customer_db = session.get(Customer, customer_id)
  if not customer_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")

  return customer_db.plans

# customer change plan
@router.put("/customers/{customer_id}/plans/{plan_id}", tags=["Customers"])
async def change_customer_plan(customer_id: int, plan_id: int, session: SessionDep, plan_status: StatusEnum = Query()):
  customer_db = session.get(Customer, customer_id)
  plan_db = session.get(Plan, plan_id)

  if not customer_db or not plan_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer or Plan not found!")

  # Remove existing plans
  existing_plans = session.exec(select(CustomerPlan).where(CustomerPlan.customer_id == customer_id)).all()
  for plan in existing_plans:
    session.delete(plan)
  session.commit()

  # Add new plan
  customer_plan_db = CustomerPlan(plan_id=plan_db.id, customer_id=customer_db.id, status=plan_status)
  session.add(customer_plan_db)
  session.commit()
  session.refresh(customer_plan_db)

  return customer_plan_db

# status customer plan //modificar el endpoint para que pueda filtrar todos los planes que estan activos
# @router.get("/customers/plans/status", tags=["Customers"])
# async def status_customer_plan(customer_id: int, session: SessionDep):
#   customer_db = session.get(Customer, customer_id)

#   if not customer_db:
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found!")

#   active_plans = [plan for plan in customer_db.plans if getattr(plan, 'is_active', True)]
#   return active_plans

@router.get("/customers/plans/active", response_model=list[CustomerPlan], tags=["Customers"])
async def list_active_plans(session: SessionDep, plan_status: StatusEnum=Query()):
  query = select(CustomerPlan).where(CustomerPlan.status == plan_status)
  active_plans = session.exec(query).all()
  if not active_plans:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active plans found!")
  return active_plans
