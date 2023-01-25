import time
from functools import lru_cache
from joblib import Memory

import requests

from .config import SPARQL_ENDPOINT, DEFAULT_CACHE_PATH
from .logger import get_logger


logger = get_logger()

memory = Memory(DEFAULT_CACHE_PATH, verbose=0)


@memory.cache
def request_to_wikidata(query, sparql_endpoint=SPARQL_ENDPOINT):
    params = {"format": "json", "query": query}
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    }
    logger.info(
        {
            "msg": "Send request to Wikidata",
            "params": params,
            "endpoint": sparql_endpoint,
        }
    )
    response = requests.get(
        sparql_endpoint,
        params=params,
        headers=headers,
    )
    to_sleep = 0.2
    while response.status_code == 429:
        logger.warning(
            {
                "msg": f"Request to wikidata endpoint failed. Retry.",
                "params": params,
                "endpoint": sparql_endpoint,
                "response": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                },
                "retry_after": to_sleep,
            }
        )
        if "retry-after" in response.headers:
            to_sleep += int(response.headers["retry-after"])
        to_sleep += 0.5
        time.sleep(to_sleep)
        response = requests.get(
            sparql_endpoint,
            params=params,
            headers=headers,
        )

    try:
        return response.json()["results"]["bindings"]
    except Exception as e:
        logger.error(
            {
                "msg": str(e),
                "params": params,
                "endpoint": sparql_endpoint,
                "response": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                },
            }
        )
        raise e
