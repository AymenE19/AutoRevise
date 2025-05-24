from urllib.parse import urlencode, urljoin


def build_url(base_url: str, **params) -> str:
    """Builds a parameterized URL by appending query parameters (if given) to a base URL."""

    query_string = urlencode(params)
    return urljoin(base_url, f"?{query_string}") if query_string else base_url
