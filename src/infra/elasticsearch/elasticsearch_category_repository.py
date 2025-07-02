import logging
import os

from elasticsearch import Elasticsearch
from pydantic import ValidationError

from src.application.list_category import CategorySortableFields
from src.application.listing import DEFAULT_PAGINATION_SIZE, SortDirection
from src.domain.category import Category
from src.domain.category_repository import (
    CategoryRepository,
)

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
ELASTICSEARCH_HOST_TEST = os.getenv("ELASTICSEARCH_TEST_HOST", "http://localhost:9201")


class ElasticsearchCategoryRepository(CategoryRepository):
    INDEX = "catalog-db.codeflix.categories"

    def __init__(
        self,
        client: Elasticsearch | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._client = client or Elasticsearch(hosts=[ELASTICSEARCH_HOST])
        self._logger = logger or logging.getLogger(__name__)

    def search(
        self,
        page: int = 1,
        per_page: int = DEFAULT_PAGINATION_SIZE,
        search: str | None = None,
        sort: CategorySortableFields | None = None,
        direction: SortDirection = SortDirection.ASC,
    ) -> list[Category]:
        query = {
            "from": (page - 1) * per_page,
            "size": per_page,
            "sort": [{f"{sort}.keyword": {"order": direction}}] if sort else [],
            "query": {
                "bool": {
                    "must": (
                        [{"multi_match": {"query": search, "fields": ["name", "description"]}}]
                        if search
                        else [{"match_all": {}}]
                    )
                }
            },
        }

        hits = self._client.search(
            index=self.INDEX,
            body=query,
        )["hits"]["hits"]

        parsed_entities = []
        for hit in hits:
            try:
                parsed_entity = Category(**hit["_source"])
            except ValidationError:
                self._logger.error(f"Malformed category: {hit}")
            else:
                parsed_entities.append(parsed_entity)

        return parsed_entities