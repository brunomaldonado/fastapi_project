# print("Welcome to the jungle!")
from fastapi import FastAPI
import uvicorn
from datetime import datetime
from zoneinfo import ZoneInfo

from config.db_connection import create_all_tables
from routers.customers import router as customers_router
from routers.transactions import router as transactions_router
from routers.invoices import router as invoices_router
from routers.plans import router as plans_router

routers = [customers_router, transactions_router, invoices_router, plans_router]

app = FastAPI(lifespan=create_all_tables)
for router in routers:
  app.include_router(router)

@app.get("/")
async def root():
  return {
    "message": f"hello world! The current date &--- time is: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}",
    # "date": current_date.strftime("%d/%m/%Y %H:%M:%S")
  }

country_timezones = {
  "US": "America/New_York",
  "UK": "Europe/London",
  "DE": "Europe/Berlin",
  "FR": "Europe/Paris",
  "JP": "Asia/Tokyo",
  "CO": "America/Bogota",
  "BR": "America/Sao_Paulo",
  "AR": "America/Argentina/Buenos_Aires",
  "MX": "America/Mexico_City",
}

def format_country(country: str):
  parts = country.split("/")
  if len(parts) == 2:
    return parts[1].replace("_", " ")
  elif len(parts) >= 3:
    return " ".join(part.replace("_", " ") for part in parts[-2:])
  else:
    return country.replace("_", " ")

time_format = {
  "24": "%H:%M:%S",
  "12": "%I:%M:%S %p"
}

@app.get("/time/{iso_code}")
async def date(iso_code: str):
  iso = iso_code.upper()
  timezone_str = country_timezones.get(iso)
  country = format_country(timezone_str)
  tz = ZoneInfo(timezone_str)
  return {
    "date": datetime.now(tz).strftime(f"%d/%m/%Y {country}, {iso}, to %H:%M:%S"),
    # "time": datetime.now(tz).strftime(f" %H:%M:%S")
  }

@app.get("/time/{iso_code}/{hour_format}")
async def time(iso_code: str, hour_format: str):
  iso = iso_code.upper()
  timezone_str = country_timezones.get(iso)
  tz = ZoneInfo(timezone_str)
  # country = timezone_str.split("/")[-1].replace("_", " ")
  # parts = timezone_str.split("/")
  # country = " ".join(part.replace("_", " ") for part in parts[-2:])
  # print(country)
  # print(format_country(timezone_str))
  country = format_country(timezone_str)
  timeformat_str = time_format.get(hour_format, "24")

  return {
    "date": datetime.now(tz).strftime(f"%d/%m/%Y {country}, {iso}, to {timeformat_str}")
  }


if __name__ == '__main__':
  uvicorn.run(app, host="0.0.0.0", port=8000)
