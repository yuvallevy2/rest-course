# PEP 585
from collections.abc import Iterable
from uuid import uuid4

from anyio import Event
from fastapi import FastAPI, HTTPException, Request, Response, status

from . import bdb_manager, errors
from .params import BDBParams, BDBResponse, EventResponse
from .types import UID
from .util import url_for
import logging

app = FastAPI(title="REST Course", description="REST API Course")


@app.post("/bdbs", tags=["bdb"], operation_id="create_bdb", response_model=BDBResponse)
def create_bdb(params: BDBParams, request: Request, response: Response):
    bdb = bdb_manager.create_bdb(params)

    # TODO: Add fields: created_at
    url = url_for(request, "get_bdb", uid=str(bdb.uid))
    response.headers["location"] = url
    return BDBResponse(bdb=bdb, url=url)


@app.get(
    "/bdbs/{uid}", tags=["bdb"], operation_id="get_bdb", response_model=BDBResponse
)
def get_bdb(uid: UID, request: Request):
    try:
        bdb = bdb_manager.get_bdb(uid)
        url = url_for(request, "get_bdb", uid=str(bdb.uid))
        return BDBResponse(bdb=bdb, url=url)
    except LookupError:
        raise HTTPException(status_code=404)


@app.put(
    "/bdbs/{uid}",
    tags=["bdb"],
    operation_id="update_bdb",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def update_bdb(uid: UID, params: BDBResponse):
    try:
        bdb_manager.update_bdb(uid, params.bdb)
    except errors.InvalidOperationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@app.get(
    "/bdbs",
    tags=["bdb"],
    operation_id="get_all_bdbs",
    response_model=Iterable[BDBResponse],
)
def get_all_bdbs(request: Request):
    for bdb in bdb_manager.get_all_bdbs():
        url = url_for(request, "get_bdb", uid=str(bdb.uid))
        yield BDBResponse(bdb=bdb, url=url)



@app.put(
    "/bdbs/{uid}/upgrade",
    tags=["bdb"],
    operation_id="upgrade_bdb",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def upgrade_bdb(uid: UID, request: Request):
    new_version = request.query_params['version']
    logging.critical(f"upgrade_bdb called uid: {uid} version: {new_version}")
    try:
        await bdb_manager.update_version(uid=uid, version=new_version)
    except errors.InvalidOperationError as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=str(e))






#############################################
#
# Testing endpoints

events: dict[str, Event] = {}


@app.post("/test/events", response_model=EventResponse)
async def create_event(request: Request):
    uuid = str(uuid4())
    events[uuid] = Event()
    return EventResponse(uuid=uuid, url=url_for(request, "wait_for_event", uuid=uuid))


@app.put("/test/events/{uuid}")
async def trigger_event(uuid: str):
    event = events[uuid]
    await event.set()


@app.get("/test/events/{uuid}")
async def wait_for_event(uuid: str):
    event = events[uuid]
    await event.wait()
