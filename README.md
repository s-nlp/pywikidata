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

entity = Entity('Q90')
entity.label # >> Paris

Entity.from_label('Paris') # >> [<Entity: Q116373885>, <Entity: Q116373939>, <Entity: Q90>, ...]

entity.instance_of # >> [<Entity: Q174844>, <Entity: Q200250>, <Entity: Q208511>, ...]

entity.forward_one_hop_neighbours # >> [(<Entity(Property): P6>, <Entity: Q2851133>), (<Entity(Property): P8138>, <Entity: Q108921672>), ...]
entity.backward_one_hop_neighbours

Entity("P81").is_property # >> True
Entity("Q90").is_property # >> False
```