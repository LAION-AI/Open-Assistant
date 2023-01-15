from fastapi_pagination import Params, paginate
from oasst_backend.database import engine
from oasst_backend.models import Message, MessageEmbedding
from sqlmodel import Session

"""from oasst_backend.batch.broker.celery import app


@app.task
def batch_toxicity():
    return 1"""


def get_batch_toxic_messages(pagination: int = 100):
    class PersonalizedParams(Params):
        size: int = pagination

    params = PersonalizedParams()

    with Session(engine) as db:
        res = (
            db.query(Message.id, Message.payload)
            .outerjoin(MessageEmbedding)
            .filter(MessageEmbedding.message_id is None)
            .order_by(Message.id)
            .all()
        )

        return paginate(res, params)


if __name__ == "__main__":
    get_batch_toxic_messages()
