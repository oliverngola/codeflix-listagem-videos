from abc import ABC

from src.domain.cast_member import CastMember
from src.domain.repository import Repository


class CastMemberRepository(Repository[CastMember], ABC):
    pass