# -*- coding: utf-8 -*-
from app.crud.base import CRUDBase
from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate


class CRUDPrompt(CRUDBase[Prompt, PromptCreate, None]):
    pass


prompt = CRUDPrompt(Prompt)
