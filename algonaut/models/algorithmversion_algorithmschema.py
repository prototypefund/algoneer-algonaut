from .base import Base, PkType

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref


class AlgorithmVersionAlgorithmSchema(Base):

    __tablename__ = "algorithmversion_algorithmschema"

    """
    Describes an algorithm version mapped to an algorithm schema.
    """

    algorithmversion_id = Column(
        PkType, ForeignKey("algorithmversion.id"), nullable=False
    )
    algorithmschema_id = Column(
        PkType, ForeignKey("algorithmschema.id"), nullable=False
    )

    algorithmversion = relationship(
        "AlgorithmVersion",
        backref=backref("schemas", cascade="all,delete,delete-orphan"),
        innerjoin=True,
    )
    algorithmschema = relationship(
        "AlgorithmSchema",
        backref=backref("versions", cascade="all,delete,delete-orphan"),
        innerjoin=True,
    )
