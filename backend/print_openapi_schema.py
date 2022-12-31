import json
from main import app


def get_openapi_schema():
    return json.dumps(app.openapi())


if __name__ == "__main__":
    print(get_openapi_schema())
