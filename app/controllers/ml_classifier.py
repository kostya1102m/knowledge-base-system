import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sqlalchemy.orm import Session

from controllers.species import SpeciesController
from controllers.property import PropertyController
from controllers.value import ValueController
from controllers.description import DescriptionController
from controllers.assignment import AssignmentController


class MLClassifier:
    # ML-классификатор из множества подходящих видов выбирает наиболее вероятный.
    # Принцип работы:
    # 1. Из базы знаний строится обучающая выборка
    # 2. Каждый вид — класс, каждое свойство — признак (one-hot encoding)
    # 3. Обучается RandomForestClassifier
    # 4. На входные данные пользователя модель выдаёт вероятности каждого класса
    # 5. Из подходящих видов (прошедших логический фильтр) выбирается
    #    тот, у которого наибольшая вероятность по модели
    
    def __init__(self, session: Session):
        self.session = session
        self.species_ctrl = SpeciesController(session)
        self.property_ctrl = PropertyController(session)
        self.value_ctrl = ValueController(session)
        self.desc_ctrl = DescriptionController(session)
        self.assign_ctrl = AssignmentController(session)

        self.model: RandomForestClassifier | None = None
        self.species_id_to_idx: dict[int, int] = {}
        self.idx_to_species_id: dict[int, int] = {}
        self.feature_map: list[tuple[int, int]] = []  # [(property_id, value_id), ...]
        self.is_trained = False

    def train(self):
        all_species = self.species_ctrl.get_all()
        all_properties = self.property_ctrl.get_all()

        if not all_species or not all_properties:
            self.is_trained = False
            return

        self.feature_map = []
        for prop in all_properties:
            values = self.value_ctrl.get_for_property(prop.id)
            for val in values:
                self.feature_map.append((prop.id, val.id))

        n_features = len(self.feature_map)
        if n_features == 0:
            self.is_trained = False
            return

        
        self.species_id_to_idx = {}
        self.idx_to_species_id = {}
        for idx, sp in enumerate(all_species):
            self.species_id_to_idx[sp.id] = idx
            self.idx_to_species_id[idx] = sp.id

        n_species = len(all_species)

        X_rows = []
        y_rows = []

        for sp in all_species:
            sp_idx = self.species_id_to_idx[sp.id]
            described_props = self.desc_ctrl.get_described_properties(sp.id)
            described_prop_ids = {p.id for p in described_props}

            base_vector = np.zeros(n_features, dtype=np.float32)
            for i, (pid, vid) in enumerate(self.feature_map):
                if pid not in described_prop_ids:
                    continue
                assigned = self.assign_ctrl.get_values(sp.id, pid)
                assigned_ids = {v.id for v in assigned}
                if vid in assigned_ids:
                    base_vector[i] = 1.0

            X_rows.append(base_vector.copy())
            y_rows.append(sp_idx)

            rng = np.random.RandomState(sp.id)
            for _ in range(20):
                noisy = base_vector.copy()

                mask = rng.random(n_features) < rng.uniform(0.2, 0.6)
                noisy[mask] = 0.0
                X_rows.append(noisy)
                y_rows.append(sp_idx)

        X = np.array(X_rows)
        y = np.array(y_rows)


        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=None,
            random_state=42,
            class_weight='balanced'
        )
        self.model.fit(X, y)
        self.is_trained = True

    def predict_probabilities(self, user_input: dict[int, list[int]]) -> dict[int, float]:
        if not self.is_trained or self.model is None:
            return {}

        vector = np.zeros(len(self.feature_map), dtype=np.float32)
        for i, (pid, vid) in enumerate(self.feature_map):
            if pid in user_input and vid in user_input[pid]:
                vector[i] = 1.0

        probas = self.model.predict_proba(vector.reshape(1, -1))[0]

        result = {}
        for class_idx, prob in enumerate(probas):
            if class_idx in self.idx_to_species_id:
                species_id = self.idx_to_species_id[class_idx]
                result[species_id] = float(prob)

        return result

    def pick_best(self, matched_species_ids: list[int],
                  user_input: dict[int, list[int]]) -> tuple[int | None, dict[int, float]]:
        if not matched_species_ids:
            return None, {}

        probas = self.predict_probabilities(user_input)

        if not probas:
            return matched_species_ids[0], {}
        
        filtered = {
            sid: probas.get(sid, 0.0)
            for sid in matched_species_ids
        }

        if not filtered:
            return matched_species_ids[0], probas

        best_id = max(filtered, key=filtered.get)
        return best_id, probas