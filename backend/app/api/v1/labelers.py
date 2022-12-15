# -*- coding: utf-8 -*-
from typing import Any, List

from app import crud, schemas
from app.api import deps
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.api_key import APIKey
from sqlmodel import Session
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

router = APIRouter()


@router.get("/", response_model=List[schemas.Labeler])
def read_labelers(
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    begin_id: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve labelers.
    """
    deps.api_auth(api_key, db, read=True)
    if limit > 10000:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Bad request")
    labelers = crud.labeler.get_multi(db, begin_id=begin_id, limit=limit)
    return labelers


@router.post("/", response_model=schemas.Labeler)
def create_labeler(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    item_in: schemas.LabelerCreate,
) -> Any:
    """
    Create new labeler.
    """
    print("create_labelere")
    deps.api_auth(api_key, db, create=True)
    print(item_in)
    item = crud.labeler.create(db=db, obj_in=item_in)
    print(item)
    return item


@router.put("/{id}", response_model=schemas.Labeler)
def update_labeler(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    id: int,
    item_in: schemas.LabelerUpdate,
) -> Any:
    """
    Update a labeler.
    """
    deps.api_auth(api_key, db, update=True, read=True)
    item = crud.labeler.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found")
    item = crud.labeler.update(db=db, db_obj=item, obj_in=item_in)
    return item


@router.get("/by-username", response_model=schemas.Labeler)
def read_labeler_by_username(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    discord_username: str,
) -> Any:
    """
    Get labeler by ID.
    """
    deps.api_auth(api_key, db, read=True)
    item = crud.labeler.get_by_discord_username(db=db, discord_username=discord_username)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/{id}", response_model=schemas.Labeler)
def read_labeler(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    id: int,
) -> Any:
    """
    Get labeler by ID.
    """
    deps.api_auth(api_key, db, read=True)
    item = crud.labeler.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.delete("/{id}", response_model=schemas.Labeler)
def delete_labeler(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    id: int,
) -> Any:
    """
    Delete a labeler.
    """
    deps.api_auth(api_key, db, delete=True)
    labeler = crud.labeler.get(db=db, id=id)
    if not labeler:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found")
    labeler = crud.labeler.remove(db=db, id=id)
    return labeler
