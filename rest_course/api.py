# PEP 585
from collections.abc import Iterable

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import NonNegativeInt

from . import bdb_manager
from .params import BDBParams, BDBResponse
from .types import UID
from .util import link, url_for

app = FastAPI(title="REST Course", description="REST API Course")


@app.post("/bdbs", tags=["bdb"], operation_id="create_bdb", response_model=BDBResponse)
def create_bdb(req: BDBParams, request: Request, response: Response):
    bdb = bdb_manager.create_bdb(req)

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


@app.get(
    "/bdbs",
    tags=["bdb"],
    operation_id="get_all_bdbs",
    response_model=Iterable[BDBResponse],
)
def get_all_bdbs(
    request: Request,
    response: Response,
    offset: NonNegativeInt = 0,
    limit: NonNegativeInt = 1000,
):
    def url_with_offset(offset):
        return url_for(
            request, "get_all_bdbs", query_params=dict(offset=offset, limit=limit)
        )

    # Exercise: Look up and use the correct numbers
    prev_offset = min(offset - limit, 0)
    last_offset = (bdb_manager.get_bdb_count() // limit) * limit
    next_offset = min(offset + limit, last_offset)
    # prev_offset = 0
    # last_offset = 20
    # next_offset = 10

    rels = dict(
        first=url_with_offset(0),
        last=url_with_offset(last_offset),
    )
    if offset != 0:
        rels['prev'] = url_with_offset(prev_offset)

    if offset <= last_offset:
        rels['next'] = url_with_offset(next_offset)

    response.headers["link"] = link(rels)

    for bdb in bdb_manager.get_all_bdbs(offset=offset, limit=limit):
        url = url_for(request, "get_bdb", uid=str(bdb.uid))
        yield BDBResponse(bdb=bdb, url=url)
