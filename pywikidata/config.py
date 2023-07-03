from pathlib import Path
import os

SPARQL_ENDPOINT = os.environ.get("SPARQL_ENDPOINT", "https://query.wikidata.org/sparql")
WIKIDATA_URI = os.environ.get("WIKIDATA_URI", "https://www.wikidata.org/")
DEFAULT_CACHE_PATH = str(Path(__file__).parent / ".." / ".cache")

LOG_FILENAME = "log.json"
