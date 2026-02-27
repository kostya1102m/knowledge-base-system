from sqlalchemy import (
    Column, Integer, String, ForeignKey, Table, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

species_property_association = Table(
    'species_property_description',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('species_id', Integer,
           ForeignKey('species.id', ondelete='CASCADE'), nullable=False),
    Column('property_id', Integer,
           ForeignKey('properties.id', ondelete='CASCADE'), nullable=False),
    UniqueConstraint('species_id', 'property_id', name='uq_species_property')
)

species_property_value_association = Table(
    'species_property_values',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('species_id', Integer,
           ForeignKey('species.id', ondelete='CASCADE'), nullable=False),
    Column('property_id', Integer,
           ForeignKey('properties.id', ondelete='CASCADE'), nullable=False),
    Column('value_id', Integer,
           ForeignKey('possible_values.id', ondelete='CASCADE'), nullable=False),
    UniqueConstraint('species_id', 'property_id', 'value_id',
                     name='uq_species_prop_val')
)


class Species(Base):
    __tablename__ = 'species'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True)

    described_properties = relationship(
        'Property',
        secondary=species_property_association,
        back_populates='described_species',
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Species(id={self.id}, name='{self.name}')>"


class Property(Base):
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True)

    possible_values = relationship(
        'PossibleValue',
        back_populates='property',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    described_species = relationship(
        'Species',
        secondary=species_property_association,
        back_populates='described_properties',
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Property(id={self.id}, name='{self.name}')>"


class PossibleValue(Base):
    __tablename__ = 'possible_values'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    property_id = Column(Integer,
                         ForeignKey('properties.id', ondelete='CASCADE'),
                         nullable=False)

    property = relationship('Property', back_populates='possible_values')

    __table_args__ = (
        UniqueConstraint('name', 'property_id', name='uq_value_property'),
    )

    def __repr__(self):
        return f"<PossibleValue(id={self.id}, name='{self.name}')>"