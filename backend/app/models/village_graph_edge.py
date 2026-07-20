from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as orm_relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.village_graph_node import VillageGraphNode


class VillageGraphEdge(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "village_graph_edges"
    __table_args__ = (
        UniqueConstraint(
            "source_node",
            "target_node",
            "relationship",
            name="uq_village_graph_edges_connection",
        ),
        Index("ix_village_graph_edges_source_target", "source_node", "target_node"),
        CheckConstraint(
            "source_node <> target_node",
            name="ck_village_graph_edges_distinct_nodes",
        ),
        CheckConstraint(
            "weight >= 0", name="ck_village_graph_edges_weight_non_negative"
        ),
    )

    source_node: Mapped[UUID] = mapped_column(
        ForeignKey("village_graph_nodes.id", ondelete="CASCADE"), nullable=False
    )
    target_node: Mapped[UUID] = mapped_column(
        ForeignKey("village_graph_nodes.id", ondelete="CASCADE"), nullable=False
    )
    relationship: Mapped[str] = mapped_column(String(120), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)

    source: Mapped["VillageGraphNode"] = orm_relationship(
        foreign_keys=[source_node], back_populates="outgoing_edges"
    )
    target: Mapped["VillageGraphNode"] = orm_relationship(
        foreign_keys=[target_node], back_populates="incoming_edges"
    )
