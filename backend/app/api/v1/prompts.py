from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.api_key import APIKey
from sqlmodel import Session
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from app import crud, schemas
from app.api import deps


router = APIRouter()


@router.get("/", response_model=List[schemas.Prompt])
def read_prompts(
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    begin_id: int = 0,
    limit: int = 1000,
) -> Any:
    """
    Retrieve prompts.
    """
    deps.api_auth(api_key, db, read=True)
    if limit > 10000:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Bad request")
    return crud.prompt.get_multi(db, begin_id=begin_id, limit=limit)


@router.post("/", response_model=schemas.Prompt)
def create_prompt(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    item_in: schemas.PromptCreate,
) -> Any:
    """
    Create new prompt.
    """
    deps.api_auth(api_key, db, create=True)
    if item_in.labeler_id is None:
        if item_in.discord_username is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Bad request")
        labeler = crud.labeler.get_by_discord_username(db=db, discord_username=item_in.discord_username)
    else:
        labeler = crud.labeler.get(db=db, id=item_in.labeler_id)

    if labeler is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Invalid labeler user name")
    if not labeler.is_enabled:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Labeler disabled")
    
    item_in.labeler_id = labeler.id
    item_in.discord_username = None
    item = crud.prompt.create(db=db, obj_in=item_in)
    return item


@router.get("/{id}", response_model=schemas.Prompt)
def read_prompt(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    id: int,
) -> Any:
    """
    Get prompt by ID.
    """
    deps.api_auth(api_key, db, read=True)
    item = crud.prompt.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.delete("/{id}", response_model=schemas.Prompt)
def delete_prompt(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    id: int,
) -> Any:
    """
    Delete a prompt.
    """
    deps.api_auth(api_key, db, delete=True)
    item = crud.prompt.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found")
    item = crud.prompt.remove(db=db, id=id)
    return item
