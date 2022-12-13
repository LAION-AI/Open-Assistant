# -*- coding: utf-8 -*-
# flake8: noqa
import argparse
import dataclasses
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import app.api.deps
from app.config import settings
from sqlmodel import Session, SQLModel, create_engine


def main():
    print(settings.dict())
    quit()

    args = parse_args()
    cfg = load_configuration_file(args.config)

    engine = create_engine(cfg.database_url)
    app.api.deps.engine = engine

    """
    with Session(engine) as session:
        # create a test serivice
        #sc1 = ServiceClient(name='blub', api_key='1234')
        #session.add(sc1)

        session.commit()
    """


if __name__ == "__main__":
    main()
