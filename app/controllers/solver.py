from sqlalchemy.orm import Session
from models.entities import Species, Property, PossibleValue
from controllers.species import SpeciesController
from controllers.description import DescriptionController
from controllers.assignment import AssignmentController
from controllers.ml_classifier import MLClassifier


class SolverController:
    #решатель задач — метод опровержения гипотез.
    #Для каждого вида проверяем: все ли введённые пользователем значения
    #совместимы с допустимыми значениями этого вида.
    #если хотя бы одно свойство не совпадает — вид опровергнут.

    def __init__(self, session: Session):
        self.session = session
        self.species_ctrl = SpeciesController(session)
        self.desc_ctrl = DescriptionController(session)
        self.assign_ctrl = AssignmentController(session)

    def solve(self, user_input: dict[int, list[int]]) -> list[dict]:
        results = []

        for species in self.species_ctrl.get_all():
            described = self.desc_ctrl.get_described_properties(species.id)
            described_ids = {p.id for p in described}

            matched = True
            details = []

            for prop_id, user_val_ids in user_input.items():
                if not user_val_ids:
                    continue

                prop = self.session.get(Property, prop_id)
                user_vals = self.session.query(PossibleValue).filter(
                    PossibleValue.id.in_(user_val_ids)
                ).all()

                if prop_id not in described_ids:
                    details.append({
                        'property': prop,
                        'user_values': user_vals,
                        'species_values': [],
                        'match': None,
                        'note': 'Свойство не в описании вида'
                    })
                    continue

                sp_vals = self.assign_ctrl.get_values(species.id, prop_id)
                sp_val_ids = {v.id for v in sp_vals}

                is_match = bool(set(user_val_ids) & sp_val_ids)

                if not is_match:
                    matched = False

                details.append({
                    'property': prop,
                    'user_values': user_vals,
                    'species_values': sp_vals,
                    'match': is_match,
                    'note': ''
                })

            results.append({
                'species': species,
                'matched': matched,
                'details': details
            })

        results.sort(key=lambda r: (not r['matched'], r['species'].name))
        return results