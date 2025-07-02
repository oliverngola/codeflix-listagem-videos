import logging
import os

from elasticsearch import Elasticsearch
from pydantic import ValidationError

from src.application.list_cast_member import CastMemberSortableFields
from src.application.listing import DEFAULT_PAGINATION_SIZE, SortDirection
from src.domain.cast_member import CastMember
from src.domain.cast_member_repository import (
    CastMemberRepository,
)

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
ELASTICSEARCH_HOST_TEST = os.getenv("ELASTICSEARCH_TEST_HOST", "http://localhost:9201")


class ElasticsearchCastMemberRepository(CastMemberRepository):
    INDEX = "catalog-db.codeflix.cast_members"

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
        sort: CastMemberSortableFields | None = None,
        direction: SortDirection = SortDirection.ASC,
    ) -> list[CastMember]:
        query = {
            "from": (page - 1) * per_page,
            "size": per_page,
            "sort": [{f"{sort}.keyword": {"order": direction}}] if sort else [],
            "query": {
                "bool": {
                    "must": (
                        [{"multi_match": {"query": search, "fields": ["name", "type"]}}]
                        if search
                        else [{"match_all": {}}]
                    )
                }
            },
        }

        response = self._client.search(
            index=self.INDEX,
            body=query,
        )
        cast_member_hits = response["hits"]["hits"]

        parsed_cast_members = []
        for cast_member in cast_member_hits:
            try:
                parsed_cast_member = CastMember(**cast_member["_source"])
            except ValidationError:
                self._logger.error(f"Malformed cast_member: {cast_member}")
            else:
                parsed_cast_members.append(parsed_cast_member)

        return parsed_cast_members