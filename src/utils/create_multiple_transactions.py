from sqlmodel import Session
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))  # Adjust the path as needed
from config.db_connection import engine
from utils.models import Customer, Transaction

session = Session(engine)
customer = Customer(name="John Doe", email="doe@icloud.com", age=30, description="Test customer")
session.add(customer)
session.commit()

for x in range(100):
  session.add(Transaction(customer_id=customer.id, description=f"Transaction {x}", ammount=x * 10))
session.commit()


# chargerit wireless desk charger (CHARGit)
# DELL ULTRASHARP CURVED MONITOR (U3821DW)
# FLEXISPOT E7Q ELECTRIC STANDING DESK FRAME (E7Q)
