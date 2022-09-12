from fastapi import FastAPI, HTTPException, Request
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from fastapi.responses import JSONResponse, UJSONResponse
from fastapi.encoders import jsonable_encoder

from DBConnection import DataBaseConnection
from models import SystemItemImport, SystemItemImportRequest, Error as MyError

connection = DataBaseConnection()
database = connection.database


class MyException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


app = FastAPI()


@app.exception_handler(MyException)
async def unicorn_exception_handler(request: Request, exc: MyException):
    return UJSONResponse(
        headers={"description": getattr(exc, "detail", "Невалидная схема документа или входные данные не верны.")},
        status_code=exc.code,
        content=jsonable_encoder(MyError(exc.code, exc.message)),
    )


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/imports")
async def create_item(item: SystemItemImportRequest):
    parent_type = await database.fetch_all(check_parent(item.items[0].parent_id))
    if parent_type[0][0] == 'FOLDER':
        return {"id": parent_type}
        # last_id = await database.execute(insert_items(item.items[0], item.updateDate))
        # await database.execute(insert_connections(item.items[0].id, item.items[0].parent_id))
    else:
        raise MyException(code=400, message="Validation Failed")


def insert_items(item: SystemItemImport, update_date: str):
    stmt = insert(connection.items_table).values(
        id=item.id,
        url=item.url,
        parentId=item.parent_id,
        date=datetime.now().isoformat().__str__(),
        type=item.type,
        size=item.size
    )
    do_update_stmt = stmt.on_conflict_do_update(
        index_elements=['id'],
        set_=dict(date=update_date, url=item.url,
                  parentId=item.parent_id, size=item.size)
    )
    print(do_update_stmt)
    return do_update_stmt


def insert_connections(last_id, parent_id):
    stmt = insert(connection.connections_table).values(
        itemId=last_id,
        parentId=parent_id
    )
    do_update_stmt = stmt.on_conflict_do_update(
        index_elements=['itemId'],
        set_=dict(parentId=parent_id)
    )
    print(do_update_stmt)
    return do_update_stmt


def check_parent(parent_id):
    query = select(connection.items_table.c.type) \
        .where(connection.items_table.c.id == parent_id)
    print(query)
    return query
