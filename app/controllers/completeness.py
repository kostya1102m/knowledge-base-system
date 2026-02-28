from sqlalchemy.orm import Session
from controllers.species import SpeciesController
from controllers.property import PropertyController
from controllers.description import DescriptionController
from controllers.value import ValueController
from controllers.assignment import AssignmentController


class CompletenessController:

    def __init__(self, session: Session):
        self.session = session
        self.species_ctrl = SpeciesController(session)
        self.property_ctrl = PropertyController(session)
        self.desc_ctrl = DescriptionController(session)
        self.val_ctrl = ValueController(session)
        self.assign_ctrl = AssignmentController(session)

    def check(self) -> list[str]:
        errors = []
        all_species = self.species_ctrl.get_all()

        if not all_species:
            errors.append("В базе знаний нет ни одного вида китов.")
            return errors
        
        properties = self.property_ctrl.get_all()

        if not properties:
            errors.append("В базе знаний нет ни одного свойства.")
            return errors
        
        for property in properties:
            values = self.val_ctrl.get_for_property(property.id)

            if not values:
                errors.append(
                    f"Свойство «{property.name}»: множество возможных "
                    f"значений пусто."
                )

        for species in all_species:
            described = self.desc_ctrl.get_described_properties(species.id)

            if not described:
                errors.append(
                    f"Вид «{species.name}»: описание свойств пусто."
                )
                continue

            for prop in described:
                possible = self.val_ctrl.get_for_property(prop.id)
                if not possible:
                    errors.append(
                        f"Вид «{species.name}», свойство «{prop.name}»: "
                        f"множество возможных значений пусто."
                    )
                    continue

                assigned = self.assign_ctrl.get_values(species.id, prop.id)
                if not assigned:
                    errors.append(
                        f"Вид «{species.name}», свойство «{prop.name}»: "
                        f"не задано ни одного значения."
                    )
                    continue

                possible_ids = {v.id for v in possible}
                assigned_ids = {v.id for v in assigned}
                if assigned_ids - possible_ids:
                    errors.append(
                        f"Вид «{species.name}», свойство «{prop.name}»: "
                        f"значения выходят за пределы возможных."
                    )

        return errors