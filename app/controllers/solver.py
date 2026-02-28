from sqlalchemy.orm import Session
from models.entities import Species, Property, PossibleValue
from controllers.species import SpeciesController
from controllers.description import DescriptionController
from controllers.assignment import AssignmentController
from controllers.ml_classifier import MLClassifier


class SolverController:
    #решатель задач — метод опровержения гипотез (логический фильтр + ML-ранжирование:
    # 1. логический фильтр (метод опровержения гипотез) — отсеивает невозможные виды
    # 2. ml-классификатор — из оставшихся выбирает наиболее вероятный
    # ).
    #Для каждого вида проверяем: все ли введённые пользователем значения
    #совместимы с допустимыми значениями этого вида.
    #если хотя бы одно свойство не совпадает — вид опровергнут.

    def __init__(self, session: Session):
        self.session = session
        self.species_ctrl = SpeciesController(session)
        self.desc_ctrl = DescriptionController(session)
        self.assign_ctrl = AssignmentController(session)
        self.ml = MLClassifier(session)

        self.ml.train()

    def retrain(self):
        self.ml.train()

    def solve(self, user_input: dict[int, list[int]]) -> dict:
        all_results = []
        matched_ids = []

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

            if matched:
                matched_ids.append(species.id)

            all_results.append({
                'species': species,
                'matched': matched,
                'probability': 0.0,
                'is_best': False,
                'details': details
            })

        best_id, probabilities = self.ml.pick_best(matched_ids, user_input)

        for r in all_results:
            sid = r['species'].id
            r['probability'] = probabilities.get(sid, 0.0)
            r['is_best'] = (sid == best_id)

        all_results.sort(key=lambda r: (
            not r['matched'],       
            not r['is_best'],       
            -r['probability'],      
            r['species'].name
        ))

        best_species = None
        if best_id is not None:
            best_species = self.session.get(Species, best_id)

        return {
            'all_results': all_results,
            'best_species': best_species,
            'matched_count': len(matched_ids)
        }