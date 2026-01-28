import logging
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Mapped, relationship

from .base import Base, TableNames

logger = logging.getLogger(__name__)

@dataclass
class ParentRelation:
    parent_attr: str
    child_attr: str
    kwargs: dict[str, Any]

RELATIONSHIPS: dict[TableNames, dict[TableNames, ParentRelation]] = {
    TableNames.CURRENCY: {
        TableNames.CURRENCY_RATE: ParentRelation(
            parent_attr="rates",
            child_attr="currency",
            kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
        )
    },
    TableNames.COMPANY: {
        TableNames.USER_PERMISSION: ParentRelation(
            parent_attr="permissions",
            child_attr="company",
            kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
        )
    },
    TableNames.USER: {
        TableNames.USER_PERMISSION: ParentRelation(
            parent_attr="permissions",
            child_attr="user",
            kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
        )
    },
}

def build_single_relationship(
    child_table_name: str | TableNames,
    relation_def: ParentRelation
) -> Mapped:
    if isinstance(child_table_name, TableNames):
        child_table_name = child_table_name.value
    child_cls = Base.get_class_by_table_name(child_table_name)
    logger.info(
        f"Building relationship for parent class to child ({child_cls}) {relation_def}"
    )
    return relationship(
        child_cls,
        back_populates=relation_def.child_attr,
        **relation_def.kwargs
    )

def get_parent_relationship_def(
    parent_table_name: TableNames, child_table_name: TableNames
) -> ParentRelation:
    rd = RELATIONSHIPS[parent_table_name][child_table_name]
    logger.info(
        f"Got relationship definition from {parent_table_name} to "
        f"{child_table_name}: {rd}"
    )
    return rd

def get_relationship(
    parent_table_name: TableNames, child_table_name: TableNames
) -> Mapped:
    logger.info(
        f"Getting relationship from {parent_table_name} to {child_table_name}"
    )
    rel = get_parent_relationship_def(parent_table_name, child_table_name)
    return build_single_relationship(child_table_name, rel)

# def build_parent_relationships(parent: type[Base]) -> None:
#     if rels_dict := RELATIONSHIPS.get(parent.__tablename__):
#         for child_table, rel in rels_dict.items():
#             _build_single_relationship(parent, rel)
#     return