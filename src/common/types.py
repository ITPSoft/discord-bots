import abc
from enum import EnumMeta, Enum
from typing import Generic, cast, Type, TypeVar, Self, TYPE_CHECKING

if TYPE_CHECKING:
    # I want to have types -> constants in general, but I want to reference channel here
    # this is less ugly than yet another abstract class
    from common.constants import Channel


class ABCEnumMeta(EnumMeta, abc.ABCMeta):
    """Metaclass combining Enum and ABC functionality"""

    pass


class BaseRoleEnum(Enum):
    """
    This python enum subclass is a black magic, do not touch it, I sacrificed 3 goats during full moon to make it work.
    """

    _role_name: str
    _role_id: int
    _button_label: str

    def __new__(cls, role_name, role_id, button_label=None):
        obj = object.__new__(cls)
        obj._role_name = role_name
        obj._role_id = role_id
        obj._button_label = button_label if button_label is not None else role_name
        return obj

    @property
    def role_name(self) -> str:
        return self._role_name

    @property
    def role_id(self) -> int:
        return self._role_id

    @property
    def button_label(self) -> str:
        return self._button_label

    @property
    def role_tag(self) -> str:
        return f"<@&{self._role_id}>"

    @classmethod
    def get_role_id_by_name(cls, name: str) -> int | None:
        for member in cls:
            if member._role_name == name:
                return member._role_id
        return None

    @classmethod
    def get_by_role_id(cls, role_id: int) -> Self | None:
        for member in cls:
            if member._role_id == role_id:
                return member
        return None

    @classmethod
    def get_by_button_label(cls, button_label: str) -> Self | None:
        for member in cls:
            if member._button_label == button_label:
                return member
        return None


T = TypeVar("T", bound=BaseRoleEnum)


class ChamberRoles(abc.ABC, Generic[T]):
    """Private-ish roles requiring access appeal poll"""

    @abc.abstractmethod
    def get_channel(self) -> Channel:
        pass

    @classmethod
    def get_channels(cls) -> list[tuple[str, int]]:
        enum_cls = cast(Type[BaseRoleEnum], cls)
        return [(i.button_label, i.get_channel()) for i in enum_cls]  # type: ignore # mypy doesn't understand

    @classmethod
    def get_channel_names(cls) -> list[str]:
        return [i[0] for i in cls.get_channels()]
