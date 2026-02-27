from sqlalchemy import delete
from sqlalchemy.orm import Session
from models.entities import (
    PossibleValue,
    species_property_value_association
)


class ValueController:

    def __init__(self, session: Session):
        self.session = session

    def get_for_property(self, property_id: int) -> list[PossibleValue]:
        return self.session.query(PossibleValue).filter(
            PossibleValue.property_id == property_id
        ).order_by(PossibleValue.name).all()

    def add(self, property_id: int, name: str) -> PossibleValue | None:
        name = name.strip()
        if not name:
            return None
        exists = self.session.query(PossibleValue).filter(
            PossibleValue.property_id == property_id,
            PossibleValue.name == name
        ).first()
        if exists:
            return None
        val = PossibleValue(name=name, property_id=property_id)
        self.session.add(val)
        self.session.commit()
        return val

    def remove(self, value_id: int):
        self.session.execute(
            delete(species_property_value_association).where(
                species_property_value_association.c.value_id == value_id
            )
        )
        obj = self.session.get(PossibleValue, value_id)
        if obj:
            self.session.delete(obj)
        self.session.commit()