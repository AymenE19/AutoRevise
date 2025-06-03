import json
import re

from fastapi import FastAPI


def clean_code_block(app: FastAPI, raw_str: str) -> dict | str | None:
    # Remove code block delimiters like ```json, ```markdown and ```
    pattern = r'^```(json|markdown)\n(.*?)\n```$'

    app.state.logger.info(f"Scanning for json or markdown pattern in {raw_str}")
    match = re.search(pattern, raw_str.strip(), re.DOTALL | re.IGNORECASE)

    if not match:
        return None

    block_type, content = match.groups()

    # Replace escaped newlines and escaped quotes
    cleaned = content.replace("\\n", "\n").replace("\n", "").replace('\\"', '"').replace("\\'", "'")

    if block_type == "json":
        return json.loads(cleaned)
    else:
        return content
