import codecs
import io
import json
import re
from pathlib import Path

import aiohttp
import PyPDF2
import yaml
from bs4 import BeautifulSoup
from fastapi import FastAPI, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.responses import FileResponse

# In total, the text + image links + prompts should be <= 2048
CHAR_LIMIT = 1585  # TODO: increase these values after long-context support has been added
IMAGES_CHAR_LIMIT = 300
MAX_DOWNLOAD_SIZE = 4 * 1024 * 1024
MAX_CHUNK_SIZE = 1024 * 1024

IMAGES_SUFIX = """, and I will also include images formatted like this:
![](image url)
"""

folder_path = Path(__file__).parent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_image_links(text: str):
    image_pattern = r"https?://\S+\.(?:jpg|jpeg|png|gif|bmp|webp|svg)"
    images = re.findall(image_pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return images


def detect_content_type(content: bytes) -> str:
    if content.startswith(b"%PDF-"):
        return "application/pdf"
    elif (content).lstrip().upper().startswith(b"<!DOCTYPE HTML") or content.startswith(b"<html"):
        return "text/html"
    elif content.startswith(b"{") or content.startswith(b"["):
        try:
            json.loads(content)
            return "application/json"
        except json.JSONDecodeError:
            pass
    elif content.startswith(b"---") or content.startswith(b"%YAML"):
        try:
            yaml.safe_load(content)
            return "application/x-yaml"
        except yaml.YAMLError:
            pass

    return "text/plain"


def limit_image_count(images, max_chars=300):
    limited_images = []
    current_length = 0

    for url in images:
        # Add the length of "http:" if the URL starts with "//"
        url_length = len("http:") + len(url) if url.startswith("//") else len(url)

        if current_length + url_length > max_chars:
            break

        if url.startswith("//"):
            limited_images.append(f"http:{url}")
        else:
            limited_images.append(url)

        current_length += url_length

    return limited_images


def truncate_paragraphs(paragraphs, max_length):
    truncated_paragraphs = []
    current_length = 0

    for paragraph in paragraphs:
        if len(paragraph) == 0:
            continue
        paragraph = paragraph.strip()
        if current_length + len(paragraph) <= max_length:
            truncated_paragraphs.append(paragraph)
            current_length += len(paragraph)
        else:
            remaining_length = max_length - current_length
            truncated_paragraph = paragraph[:remaining_length]
            truncated_paragraphs.append(truncated_paragraph)
            break

    return truncated_paragraphs


@app.get("/get-url-content/", operation_id="getUrlContent", summary="It will return a web page's or pdf's content")
async def get_url_content(url: str = Query(..., description="url to fetch content from")) -> Response:
    try:
        buffer = io.BytesIO()
        encoding: str | None
        content_type: str | None

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                try:
                    encoding = response.get_encoding()
                except RuntimeError:
                    encoding = None
                content_type = response.content_type

                if response.content_length is not None and response.content_length > MAX_DOWNLOAD_SIZE:
                    error_message = (
                        f"Sorry, the file at {url} is too large.\nYou should report this message to the user!"
                    )
                    return JSONResponse(content={"error": error_message}, status_code=500)

                async for chunk in response.content.iter_chunked(MAX_CHUNK_SIZE):
                    buffer.write(chunk)
                    if buffer.tell() > MAX_DOWNLOAD_SIZE:
                        error_message = (
                            f"Sorry, the file at {url} is too large.\nYou should report this message to the user!"
                        )
                        return JSONResponse(content={"error": error_message}, status_code=500)

        content_bytes: bytes = buffer.getvalue()
        if content_type is None or content_type == "application/octet-stream":
            content_type = detect_content_type(content_bytes)
        buffer.seek(0)

        def decode_text() -> str:
            decoder = codecs.getincrementaldecoder(encoding or "utf-8")(errors="replace")
            return decoder.decode(content_bytes, True)

        text = ""
        images = []

        if content_type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(buffer)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

        elif content_type == "text/html":
            soup = BeautifulSoup(decode_text(), "html.parser")

            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
            # if there are no paragraphs, try to get text from divs
            if not paragraphs:
                paragraphs = [p.get_text(strip=True) for p in soup.find_all("div")]
            # if there are no paragraphs or divs, try to get text from spans
            if not paragraphs:
                paragraphs = [p.get_text(strip=True) for p in soup.find_all("span")]

            paragraphs = truncate_paragraphs(paragraphs, CHAR_LIMIT)
            text = "\n".join(paragraphs)

            for p in soup.find_all("p"):
                parent = p.parent
                images.extend([img["src"] for img in parent.find_all("img") if img.get("src")])

        elif content_type == "application/json":
            json_data = json.loads(decode_text())
            text = yaml.dump(json_data, sort_keys=False, default_flow_style=False)

            for _, value in json_data.items():
                if isinstance(value, str):
                    images.extend(extract_image_links(value))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            images.extend(extract_image_links(item))

        elif content_type == "text/plain":
            text = decode_text()
            images.extend(extract_image_links(text))

        else:
            error_message = f"Sorry, unsupported content type '{content_type}' at {url}.\nYou should report this message to the user!"
            return JSONResponse(content={"error": error_message}, status_code=500)

        images = [f"http:{url}" if url.startswith("//") else url for url in images]
        images = limit_image_count(images, max_chars=IMAGES_CHAR_LIMIT)

        if len(text) > CHAR_LIMIT:
            text = text[:CHAR_LIMIT]

        MULTILINE_SYM = "|" if content_type != "applicaion/json" else ""
        text_yaml = f"text_content: {MULTILINE_SYM}\n"
        for line in text.split("\n"):
            text_yaml += f"  {line}\n"

        images_yaml = "images:\n" if len(images) > 0 else ""
        for image in images:
            images_yaml += f"- {image}\n"

        yaml_text = f"{text_yaml}\n{images_yaml}"
        text = f"""{yaml_text}
Thought: I now know the answer{IMAGES_SUFIX if len(images) > 0 else "."}
"""
        return Response(content=text, media_type="text/plain")

    except Exception as e:
        logger.opt(exception=True).debug("web_retriever GET failed:")
        error_message = f"Sorry, the url is not available. {e}\nYou should report this message to the user!"
        return JSONResponse(content={"error": error_message}, status_code=500)


@app.get("/icon.png", include_in_schema=False)
async def api_icon():
    return FileResponse(folder_path / "icon.png")


@app.get("/ai-plugin.json", include_in_schema=False)
async def api_ai_plugin(request: Request):
    json_path = folder_path / "ai-plugin.json"
    with json_path.open("r") as f:
        ai_plugin_json = json.load(f)

    base_url, _, _ = request.url._url.rpartition("/")
    ai_plugin_json["logo_url"] = base_url + "/icon.png"
    ai_plugin_json["api"]["url"] = base_url + "/openapi.json"

    return Response(content=json.dumps(ai_plugin_json), media_type="application/json")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Web Retriever",
        version="0.1",
        routes=app.routes,
        servers=[{"url": "/plugins/web_retriever"}],
    )
    openapi_schema["tags"] = [
        {
            "name": "web-retriever",
            "description": "Use this plugin to retrieve web page and pdf content",
        },
    ]
    openapi_schema.pop("components", None)
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    # simple built-in test
    import asyncio

    url = "https://huggingface.co/OpenAssistant/oasst-sft-1-pythia-12b"
    x = asyncio.run(get_url_content(url))
    print(x.status_code, x.body)
