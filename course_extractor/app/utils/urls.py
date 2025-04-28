from urllib.parse import urlencode, urljoin


def parameterized_url_generator(base_url: str, **kwargs):
    """Takes a base URL and any number of kwargs, then returns a URL with parameters"""

    # Converts the dictionary of kwargs into a URL compatible string
    query_string = urlencode(kwargs)

    # Returns the kwargs (if given ) as parameters concatenated to the base URL
    return urljoin(base_url, f"?{query_string}") if query_string else base_url
