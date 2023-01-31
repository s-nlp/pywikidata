import re
from .utils import request_to_wikidata


class _WikiDataBase:
    @staticmethod
    def _entity_uri_to_id(uri):
        return uri.split("/")[-1]

    @staticmethod
    def _validate_entity_id(entity_id):
        return re.fullmatch(r"[P|Q][0-9]+", entity_id) is not None


class _WikiDataSPARQLBase(_WikiDataBase):
    @staticmethod
    def _request_one_hop_neighbours(entity_id):
        query = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX schema: <http://schema.org/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        SELECT DISTINCT ?property ?object WHERE {
            {?object ?property wd:<ENTITY>} UNION {wd:<ENTITY> ?property ?object} .
        }
        """.replace(
            "<ENTITY>", entity_id
        )

        responce = request_to_wikidata(query)
        return responce

    @staticmethod
    def _request_one_hop_neighbours_with_instance_of(entity_id):
        query = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>

        SELECT DISTINCT ?property ?object ?instance_of WHERE {
        {
            ?object ?property wd:<ENTITY> .
            ?object wdt:P31 ?instance_of
        } UNION {
            wd:<ENTITY> ?property ?object .
            ?object wdt:P31 ?instance_of
        }
        }
        """.replace(
            "<ENTITY>", entity_id
        )

        responce = request_to_wikidata(query)
        return responce

    @staticmethod
    def _request_forward_one_hop_neighbours_with_instance_of(entity_id):
        query = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>

        SELECT DISTINCT ?property ?object ?instance_of WHERE {
            wd:<ENTITY> ?property ?object .
            ?object wdt:P31 ?instance_of
        }
        """.replace(
            "<ENTITY>", entity_id
        )

        responce = request_to_wikidata(query)
        return responce

    @staticmethod
    def _request_backward_one_hop_neighbours_with_instance_of(entity_id):
        query = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>

        SELECT DISTINCT ?property ?object ?instance_of WHERE {
            ?object ?property wd:<ENTITY> .
            ?object wdt:P31 ?instance_of
        }
        """.replace(
            "<ENTITY>", entity_id
        )

        responce = request_to_wikidata(query)
        return responce

    @staticmethod
    def _request_instance_of(entity_id):
        query = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        SELECT DISTINCT ?instance_of WHERE {
            wd:<ENTITY> wdt:P31 ?instance_of
        }
        """.replace(
            "<ENTITY>", entity_id
        )

        return request_to_wikidata(query)

    @staticmethod
    def _request_label(entity_id):
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX wd: <http://www.wikidata.org/entity/> 
        SELECT DISTINCT ?label
        WHERE {
            wd:<ENTITY> rdfs:label ?label .
            FILTER (langMatches( lang(?label), "EN" ) )
        } 
        """.replace(
            "<ENTITY>", entity_id
        )

        responce = request_to_wikidata(query)
        return responce

    @staticmethod
    def _request_description(entity_id):
        query = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX schema: <http://schema.org/>

        SELECT ?description
        WHERE 
        {
            wd:Q3 schema:description ?description.
            FILTER ( lang(?description) = "en" )
        }
        """.replace(
            "<ENTITY>", entity_id
        )
        responce = request_to_wikidata(query)
        return responce

    @staticmethod
    def _request_image(entity_id):
        query = """
        PREFIX wd: <http://www.wikidata.org/entity/>

        SELECT ?image WHERE {
            wd:<ENTITY> wdt:P18 ?image
        }
        """.replace(
            "<ENTITY>", entity_id
        )
        responce = request_to_wikidata(query)
        return responce

    @staticmethod
    def _request_entity_by_label(label):
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        SELECT * WHERE{
            ?item rdfs:label "<LABEL>"@en .
        }
        """.replace(
            "<LABEL>", label
        )

        responce = request_to_wikidata(query)
        return responce


class Entity(_WikiDataSPARQLBase):
    """Entity - python wrapper for Wikidata entities and properties
    Works like Fabric of Singletones,
    it's mean that two object with same entity_identifier absolutly equal and it's same object.
    For example, if you request label for one of them, for second it will available without addition http request.

    Args:
        entity_identifier: str - URI or ID of entity or property, for example: Q90
    """

    __instances = {}

    def __new__(cls, entity_identifier, *args, **kwargs):
        entity_identifier = Entity.entity_identifier_to_id(entity_identifier)
        if entity_identifier not in cls.__instances:
            obj = super(Entity, cls).__new__(cls)
            cls.__instances[entity_identifier] = obj
        return cls.__instances[entity_identifier]

    def __init__(self, entity_identifier: str):
        entity_identifier = Entity.entity_identifier_to_id(entity_identifier)
        if not hasattr(self, "idx"):
            if self._validate_entity_id(entity_identifier):
                self.idx = entity_identifier
            else:
                raise ValueError(
                    f"Wrong entity_identifier, can not be extracted Id for {entity_identifier}"
                )

            self._label = None
            self._description = None
            self._image = None
            self._forward_one_hop_neighbours = None
            self._backward_one_hop_neighbours = None
            self._instance_of = None
            self.is_property = self.idx[0] == "P"

    @classmethod
    def from_label(cls, label: str):
        """
        Returns list of entities with corresponding label
        """
        responce = cls._request_entity_by_label(label)
        if len(responce) > 0:
            return [Entity(r["item"]["value"]) for r in responce]
        else:
            label = label[:1].lower() + label[1:]
            responce = cls._request_entity_by_label(label)
            if len(responce) > 0:
                return [Entity(r["item"]["value"]) for r in responce]
            else:
                raise ValueError(
                    f"Wrong label, no one entity with label {label} was found. Attention: Supported only English labels"
                )

    @property
    def label(self):
        if self._label is None:
            responce = self._request_label(self.idx)
            if len(responce) > 0:
                self._label = responce[0]["label"]["value"]
        return self._label

    @property
    def description(self):
        if self._description is None:
            responce = self._request_description(self.idx)
            if len(responce) > 0:
                self._description = [r["description"]["value"] for r in responce]

        return self._description

    @property
    def image(self):
        if self._image is None:
            responce = self._request_image(self.idx)
            if len(responce) > 0:
                self._image = [r["image"]["value"] for r in responce]

        return self._image

    @property
    def forward_one_hop_neighbours(self):
        if self._forward_one_hop_neighbours is None:
            responce = self._request_forward_one_hop_neighbours_with_instance_of(
                self.idx
            )
            self._forward_one_hop_neighbours = (
                Entity._process_one_hop_neighbours_with_instance_of(responce)
            )
        return self._forward_one_hop_neighbours

    @property
    def backward_one_hop_neighbours(self):
        if self._backward_one_hop_neighbours is None:
            responce = self._request_backward_one_hop_neighbours_with_instance_of(
                self.idx
            )
            self._backward_one_hop_neighbours = (
                Entity._process_one_hop_neighbours_with_instance_of(responce)
            )
        return self._backward_one_hop_neighbours

    @property
    def one_hop_neighbours(self):
        return self.forward_one_hop_neighbours + self.backward_one_hop_neighbours

    @staticmethod
    def _process_one_hop_neighbours_with_instance_of(
        one_hop_neighbours_with_instance_of_responce,
    ):
        _one_hop_neighbours = []
        for r in one_hop_neighbours_with_instance_of_responce:
            try:
                property = Entity(r["property"]["value"])
                neighbor = Entity(r["object"]["value"])
            except ValueError:
                continue

            try:
                neighbor_instance_of = Entity(r["instance_of"]["value"])
                if neighbor._instance_of is None:
                    neighbor._instance_of = []
                if neighbor_instance_of not in neighbor._instance_of:
                    neighbor._instance_of.append(neighbor_instance_of)
            except ValueError:
                continue

            if (property, neighbor) not in _one_hop_neighbours:
                _one_hop_neighbours.append((property, neighbor))
        return _one_hop_neighbours

    @property
    def instance_of(self):
        if self._instance_of is None:
            self._instance_of = [
                Entity(r["instance_of"]["value"])
                for r in self._request_instance_of(self.idx)
            ]
        return self._instance_of

    def __repr__(self):
        if self.is_property:
            return f"<Entity(Property): {self.idx}>"
        else:
            return f"<Entity: {self.idx}>"

    @staticmethod
    def entity_identifier_to_id(entity_identifier: str) -> str:
        """entity_identifier_to_id - helper for formatting entity_identifier to index

        Args:
            entity_identifier: str - URI or Id of Wikidata Entity or Property

        Returns:
            str - Formatted entity_identifier
        """
        if "http" in entity_identifier:
            return Entity._entity_uri_to_id(entity_identifier)
        return entity_identifier.upper()

    def __json__(self):
        return {
            "idx": self.idx,
            "_label": self._label,
        }
