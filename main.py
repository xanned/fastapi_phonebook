import re

import redis
from fastapi import FastAPI
from fastapi import status
from pydantic import BaseModel
from starlette.responses import Response

redis = redis.from_url("redis://redis", decode_responses=True)

app = FastAPI()


class Data(BaseModel):
    phone: str
    address: str


@app.get("/check_data", status_code=200)
async def check_data(phone: str, response: Response):
    check_phone = re.match(r'^[78]\d{10}$', phone)
    if check_phone is None:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"error": "Phone number is incorrect"}
    address = redis.get(phone)
    if address is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Address not found'}

    return {"address": address}


@app.post("/write_data", status_code=201)
async def write_data(data: Data, response: Response):
    phone = data.phone
    address = data.address
    check_phone = re.match(r'^[78]\d{10}$', phone)
    if not check_phone or not address:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"error": "Data is incorrect"}
    redis.set(phone, address)
    return {"phone": phone, "address": address}
