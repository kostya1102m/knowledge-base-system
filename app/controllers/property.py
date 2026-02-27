from sqlalchemy import delete
from sqlalchemy.orm import Session
from models.entities import (
    Property,
    species_property_association,
    species_property_value_association
)


class PropertyController:

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Property]:
        return self.session.query(Property).order_by(Property.name).all()

    def add(self, name: str) -> Property | None:
        name = name.strip()
        if not name:
            return None
        if self.session.query(Property).filter(Property.name == name).first():
            return None
        prop = Property(name=name)
        self.session.add(prop)
        self.session.commit()
        return prop

    def remove(self, property_id: int):
        self.session.execute(
            delete(species_property_value_association).where(
                species_property_value_association.c.property_id == property_id
            )
        )
        self.session.execute(
            delete(species_property_association).where(
                species_property_association.c.property_id == property_id
            )
        )
        obj = self.session.get(Property, property_id)
        if obj:
            self.session.delete(obj)
        self.session.commit()