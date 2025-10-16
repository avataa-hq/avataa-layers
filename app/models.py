from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import (
    declarative_base,
)
from sqlmodel import SQLModel, Field, Relationship

Base = declarative_base(
    metadata=SQLModel.metadata
)


class FolderBase(SQLModel):
    name: str = Field(index=True, unique=True)
    parent_id: Optional[int] = Field(
        default=None, index=True
    )


class Folder(FolderBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
    )
    parent_id: Optional[int] = Field(
        sa_column=Column(
            Integer,
            ForeignKey(
                column="folder.id",
                ondelete="CASCADE",
            ),
            default=None,
        )
    )
    created_by: str = Field(nullable=False)
    modified_by: str = Field(nullable=False)
    creation_date: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )
    modification_date: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

    layers: List["Layer"] = Relationship(
        back_populates="folder",
        sa_relationship_kwargs={
            "cascade": "all, delete",
            "order_by": "Layer.id",
        },
    )


class LayerBase(SQLModel):
    name: str = Field(index=True, unique=True)


class Layer(LayerBase, table=True):
    id: Optional[int] = Field(
        default=None,
        nullable=False,
        primary_key=True,
    )

    folder_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey(
                column="folder.id",
                ondelete="CASCADE",
            ),
            index=True,
        )
    )
    file_link: str = Field(nullable=False)
    created_by: str = Field(nullable=False)
    modified_by: str = Field(nullable=False)
    creation_date: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

    folder: Folder = Relationship(
        back_populates="layers"
    )
