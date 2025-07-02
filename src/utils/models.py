from enum import Enum # Enum para definir estados: python library
from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import SQLModel, Field, Relationship, Session, select

from config.db_connection import engine

class StatusEnum(str, Enum):
  ACTIVE = "active"
  INACTIVE = "inactive"

class CustomerPlan(SQLModel, table=True):
  id: int | None = Field(default=None, primary_key=True)
  plan_id: int = Field(foreign_key="plan.id")
  customer_id: int = Field(foreign_key="customer.id")
  status: StatusEnum = Field(default=StatusEnum.ACTIVE)

class Plan(SQLModel, table=True):
  id: int | None = Field(default=None, primary_key=True)
  name: str = Field(default=None)
  description: str | None = Field(default=None)
  price: int = Field(default=None)
  customers: list["Customer"] = Relationship(back_populates="plans", link_model=CustomerPlan)

# printdiwpasdasdasd
class CustomerBase(SQLModel):
  name: str = Field(default=None)
  email: EmailStr = Field(default=None)
  age: int = Field(default=None)
  description: str | None = Field(default=None)

  @field_validator("email")
  @classmethod
  def validate_email(cls, value):
    session = Session(engine)
    query = select(Customer).where(Customer.email == value)
    existing_customer = session.exec(query).first() # first() devuelve el primer resultado de la consulta
    session.close()
    if existing_customer:
      raise ValueError(f"Email {value} is already registered.")
    return value

class CustomerCreate(CustomerBase): # herenciass
  pass

class CustomerUpdate(CustomerBase): # herencia
  pass

class Customer(CustomerBase, table=True):
  id: int | None = Field(default=None, primary_key=True)
  transactions: list["Transaction"] = Relationship(back_populates="customer")
  plans: list[Plan] = Relationship(back_populates="customers", link_model=CustomerPlan)


class TransactionBase(SQLModel):
  ammount: int = Field(default=None)
  description: str = Field(default=None)

class TransactionCreate(TransactionBase): # herencia
  customer_id: int = Field(foreign_key="customer.id")

class Transaction(TransactionBase, table=True):
  id: int | None = Field(default=None, primary_key=True)
  customer_id: int = Field(foreign_key="customer.id")
  customer: Customer = Relationship(back_populates="transactions")

# cuenta de cobro o factura
class Invoice(BaseModel):
  id: int
  customer: Customer
  transactions: list[Transaction]
  total: int

  @property
  def amount_total(self):
    return sum(transaction.ammount for transaction in self.transactions)



