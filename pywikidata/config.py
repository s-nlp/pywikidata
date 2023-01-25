from pathlib import Path
import os

SPARQL_ENDPOINT = os.environ.get("SPARQL_ENDPOINT", "https://query.wikidata.org/sparql")
DEFAULT_CACHE_PATH = str(Path(__file__).parent / ".." / ".cache")

LOG_FILENAME = "log.json"
