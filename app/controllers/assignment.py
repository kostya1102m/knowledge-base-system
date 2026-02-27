from sqlalchemy import select, and_, delete
from sqlalchemy.orm import Session
from models.entities import (
    PossibleValue,
    species_property_value_association
)


class AssignmentController:

    def __init__(self, session: Session):
        self.session = session

    def get_values(self, species_id: int, property_id: int) -> list[PossibleValue]:
        rows = self.session.execute(
            select(species_property_value_association.c.value_id).where(
                and_(
                    species_property_value_association.c.species_id == species_id,
                    species_property_value_association.c.property_id == property_id
                )
            )
        ).fetchall()
        ids = [r[0] for r in rows]
        if not ids:
            return []
        return self.session.query(PossibleValue).filter(
            PossibleValue.id.in_(ids)
        ).all()

    def set_value(self, species_id: int, property_id: int,
                  value_id: int, checked: bool):
        if checked:
            existing = self.session.execute(
                select(species_property_value_association).where(
                    and_(
                        species_property_value_association.c.species_id == species_id,
                        species_property_value_association.c.property_id == property_id,
                        species_property_value_association.c.value_id == value_id
                    )
                )
            ).first()
            if not existing:
                self.session.execute(
                    species_property_value_association.insert().values(
                        species_id=species_id,
                        property_id=property_id,
                        value_id=value_id
                    )
                )
        else:
            self.session.execute(
                delete(species_property_value_association).where(
                    and_(
                        species_property_value_association.c.species_id == species_id,
                        species_property_value_association.c.property_id == property_id,
                        species_property_value_association.c.value_id == value_id
                    )
                )
            )
        self.session.commit()