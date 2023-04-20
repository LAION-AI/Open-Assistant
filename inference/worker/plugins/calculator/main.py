import json
import math
import re

import numexpr
from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# expression query parameter description for model
PROMPT = """Solves a math equation but you need to provide an expression\
that can be executed using Python's numexpr library."""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# From Langchain math chain
def _evaluate_expression(expression: str) -> str:
    try:
        local_dict = {"pi": math.pi, "e": math.e}
        output = str(
            numexpr.evaluate(
                expression.strip(),
                global_dict={},
                local_dict=local_dict,
            )
        )
    except Exception as e:
        return f"{e}. Please try again with a valid numerical expression"

    return re.sub(r"^\[|\]$", "", output)


# NOTE: operation_id is used to identify the endpoint in the LLM, and
# camelCase works better than snake_case for that
# .e.g. "webSearch" > "web_search"
# another important thing is parameter descriptions
@app.get("/calculate/", operation_id="calculate", tags=["Calculator"])
async def calculate(expression: str = Query(..., description=PROMPT)):
    return {"result": _evaluate_expression(expression)}


@app.get("/icon.png", include_in_schema=False)
async def api_icon():
    with open("icon.png", "rb") as f:
        icon = f.read()
    return Response(content=icon, media_type="image/png")


@app.get("/ai-plugin.json", include_in_schema=False)
async def api_ai_plugin():
    with open("ai-plugin.json", "r") as f:
        ai_plugin_json = json.load(f)
    return Response(content=json.dumps(ai_plugin_json), media_type="application/json")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Calculator",
        version="0.1",
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {
            "url": "http://192.168.0.35:8085",
        },
    ]
    openapi_schema["tags"] = [
        {
            "name": "Ai-Calculator",
            "description": """Ai-Calculator API""",
        },
    ]
    openapi_schema.pop("components", None)
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
