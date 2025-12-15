import strawberry
from uuid import UUID
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig

from src.application.list_cast_member import (
    CastMemberSortableFields, 
    ListCastMember, 
    ListCastMemberInput
)
from src.application.list_category import (
    CategorySortableFields,
    ListCategory,
    ListCategoryInput,
)
from src.application.list_genre import (
    GenreSortableFields,
    ListGenre,
    ListGenreInput,
)
from src.application.list_video import (
    VideoSortableFields,
    ListVideo,
    ListVideoInput,
)
from src.application.listing import DEFAULT_PAGINATION_SIZE, SortDirection, ListOutputMeta
from src.domain.cast_member import CastMember
from src.domain.category import Category
from src.domain.genre import Genre
from src.domain.video import Video
from src.infra.api.http.dependencies import (
    get_category_repository, 
    get_cast_member_repository, 
    get_genre_repository,
    get_video_repository
)


@strawberry.experimental.pydantic.type(model=Category)
class CategoryGraphQL:
    id: strawberry.auto
    name: strawberry.auto
    description: strawberry.auto


@strawberry.experimental.pydantic.type(model=CastMember)
class CastMemberGraphQL:
    id: strawberry.auto
    name: strawberry.auto
    type: strawberry.auto


@strawberry.experimental.pydantic.type(model=Genre)
class GenreGraphQL:
    id: strawberry.auto
    name: strawberry.auto
    categories: list[UUID] = strawberry.auto


@strawberry.experimental.pydantic.type(model=Video)
class VideoGraphQL:
    id: strawberry.auto
    title: strawberry.auto
    launch_year: strawberry.auto
    rating: strawberry.auto
    categories: list[UUID] = strawberry.auto
    genres: list[UUID] = strawberry.auto
    cast_members: list[UUID] = strawberry.auto
    banner_url: strawberry.auto


@strawberry.experimental.pydantic.type(model=ListOutputMeta, all_fields=True)
class Meta:
    pass


@strawberry.type
class Result[T]:
    data: list[T]
    meta: Meta


def get_categories(
    sort: CategorySortableFields = CategorySortableFields.NAME,
    search: str | None = None,
    page: int = 1,
    per_page: int = DEFAULT_PAGINATION_SIZE,
    direction: SortDirection = SortDirection.ASC,
) -> Result[CategoryGraphQL]:
    _repository = get_category_repository()
    use_case = ListCategory(repository=_repository)
    output = use_case.execute(
        ListCategoryInput(
            search=search,
            page=page,
            per_page=per_page,
            sort=sort,
            direction=direction,
        )
    )

    return Result(data=[
        CategoryGraphQL.from_pydantic(category) for category in output.data],
        meta=Meta.from_pydantic(output.meta),
    )


def get_cast_members(
    sort: CastMemberSortableFields = CastMemberSortableFields.NAME,
    search: str | None = None,
    page: int = 1,
    per_page: int = DEFAULT_PAGINATION_SIZE,
    direction: SortDirection = SortDirection.ASC,
) -> Result[CastMemberGraphQL]:
    repository = get_cast_member_repository()
    use_case = ListCastMember(repository=repository)
    output = use_case.execute(
        ListCastMemberInput(
            search=search,
            page=page,
            per_page=per_page,
            sort=sort,
            direction=direction,
        )
    )

    return Result(
        data=[CastMemberGraphQL.from_pydantic(cast_member) for cast_member in output.data],
        meta=Meta.from_pydantic(output.meta),
    )


def get_genres(
    sort: GenreSortableFields = GenreSortableFields.NAME,
    search: str | None = None,
    page: int = 1,
    per_page: int = DEFAULT_PAGINATION_SIZE,
    direction: SortDirection = SortDirection.ASC,
) -> Result[GenreGraphQL]:
    repository = get_genre_repository()
    use_case = ListGenre(repository=repository)
    output = use_case.execute(
        ListGenreInput(
            search=search,
            page=page,
            per_page=per_page,
            sort=sort,
            direction=direction,
        )
    )

    return Result(
        data=[GenreGraphQL.from_pydantic(genre) for genre in output.data],
        meta=Meta.from_pydantic(output.meta),
    )


def get_videos(
    sort: VideoSortableFields = VideoSortableFields.TITLE,
    search: str | None = None,
    page: int = 1,
    per_page: int = DEFAULT_PAGINATION_SIZE,
    direction: SortDirection = SortDirection.ASC,
) -> Result[VideoGraphQL]:
    repository = get_video_repository()
    use_case = ListVideo(repository=repository)
    output = use_case.execute(
        ListVideoInput(
            search=search,
            page=page,
            per_page=per_page,
            sort=sort,
            direction=direction,
        )
    )

    return Result(
        data=[VideoGraphQL.from_pydantic(video) for video in output.data],
        meta=Meta.from_pydantic(output.meta),
    )


@strawberry.type
class Query:
    categories: Result[CategoryGraphQL] = strawberry.field(resolver=get_categories)
    cast_members: Result[CastMemberGraphQL] = strawberry.field(resolver=get_cast_members)
    genres: Result[GenreGraphQL] = strawberry.field(resolver=get_genres)
    videos: Result[VideoGraphQL] = strawberry.field(resolver=get_videos)


schema = strawberry.Schema(query=Query, config=StrawberryConfig(auto_camel_case=False))
graphql_app = GraphQLRouter(schema)

# strawberry server src.infra.api.graphql.schema_pydantic --port 8001