from sqlalchemy import delete
from sqlalchemy.orm import Session
from models.entities import (
    Species,
    species_property_association,
    species_property_value_association
)


class SpeciesController:

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Species]:
        return self.session.query(Species).order_by(Species.name).all()

    def add(self, name: str) -> Species | None:
        name = name.strip()
        if not name:
            return None
        if self.session.query(Species).filter(Species.name == name).first():
            return None
        species = Species(name=name)
        self.session.add(species)
        self.session.commit()
        return species

    def remove(self, species_id: int):
        self.session.execute(
            delete(species_property_value_association).where(
                species_property_value_association.c.species_id == species_id
            )
        )
        self.session.execute(
            delete(species_property_association).where(
                species_property_association.c.species_id == species_id
            )
        )
        obj = self.session.get(Species, species_id)
        if obj:
            self.session.delete(obj)
        self.session.commit()