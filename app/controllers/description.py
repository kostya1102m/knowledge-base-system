from sqlalchemy import select, and_, delete
from sqlalchemy.orm import Session
from models.entities import (
    Species, Property,
    species_property_association,
    species_property_value_association
)


class DescriptionController:

    def __init__(self, session: Session):
        self.session = session

    def get_described_properties(self, species_id: int) -> list[Property]:
        species = self.session.get(Species, species_id)
        if species is None:
            return []
        return species.described_properties

    def set_property(self, species_id: int, property_id: int, checked: bool):
        if checked:
            existing = self.session.execute(
                select(species_property_association).where(
                    and_(
                        species_property_association.c.species_id == species_id,
                        species_property_association.c.property_id == property_id
                    )
                )
            ).first()
            if not existing:
                self.session.execute(
                    species_property_association.insert().values(
                        species_id=species_id,
                        property_id=property_id
                    )
                )
        else:
            self.session.execute(
                delete(species_property_association).where(
                    and_(
                        species_property_association.c.species_id == species_id,
                        species_property_association.c.property_id == property_id
                    )
                )
            )
            self.session.execute(
                delete(species_property_value_association).where(
                    and_(
                        species_property_value_association.c.species_id == species_id,
                        species_property_value_association.c.property_id == property_id
                    )
                )
            )
        self.session.commit()