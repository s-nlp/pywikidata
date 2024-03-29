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


@memory.cache
def get_wd_search_results(
    search_string: str,
    max_results: int = 500,
    language: str = "en",
    mediawiki_api_url: str = "https://www.wikidata.org/w/api.php",
    user_agent: str = None,
) -> list:
    params = {
        "action": "wbsearchentities",
        "language": language,
        "search": search_string,
        "format": "json",
        "limit": 50,
    }

    user_agent = "pywikidata" if user_agent is None else user_agent
    headers = {"User-Agent": user_agent}

    cont_count = 1
    results = []
    while cont_count > 0:
        params.update({"continue": 0 if cont_count == 1 else cont_count})

        reply = requests.get(mediawiki_api_url, params=params, headers=headers)
        reply.raise_for_status()
        search_results = reply.json()

        if search_results["success"] != 1:
            raise Exception("WD search failed")
        else:
            for i in search_results["search"]:
                results.append(i["id"])

        if "search-continue" not in search_results:
            cont_count = 0
        else:
            cont_count = search_results["search-continue"]

        if cont_count > max_results:
            break

    return results
