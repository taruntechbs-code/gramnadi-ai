from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_type
from app.models.enums import GraphNodeType

if TYPE_CHECKING:
    from app.models.enterprise import Enterprise
    from app.models.village_graph_edge import VillageGraphEdge


class VillageGraphNode(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "village_graph_nodes"
    __table_args__ = (Index("ix_village_graph_nodes_enterprise", "enterprise_id"),)

    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey("enterprises.id", ondelete="CASCADE"), nullable=False
    )
    node_type: Mapped[GraphNodeType] = mapped_column(
        enum_type(GraphNodeType, "graph_node_type_enum"), nullable=False
    )

    enterprise: Mapped["Enterprise"] = relationship(back_populates="graph_nodes")
    outgoing_edges: Mapped[list["VillageGraphEdge"]] = relationship(
        foreign_keys="VillageGraphEdge.source_node",
        back_populates="source",
        cascade="all, delete-orphan",
    )
    incoming_edges: Mapped[list["VillageGraphEdge"]] = relationship(
        foreign_keys="VillageGraphEdge.target_node",
        back_populates="target",
        cascade="all, delete-orphan",
    )
