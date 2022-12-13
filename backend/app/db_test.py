import dataclasses
from datetime import datetime
import json
from typing import Optional
import argparse
from dataclasses import dataclass


from sqlmodel import Session, SQLModel, create_engine
from app.config import settings

import app.api.deps



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
    

if __name__ == '__main__':
    main()
