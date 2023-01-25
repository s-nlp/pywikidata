# pyWikiData

Python wrapper for Wikidata Knowledge Graph

Supported SPARQL backend

## Install

```bash
pip install pywikidata
```

#### Install from source by poetry
```bash
poetry build
```

## Usage
```python
from pywikidata import Entity
e = Entity('Q90')
e.label # >> Paris
```