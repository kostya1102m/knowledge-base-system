from models.base import init_db, get_session, ENGINE
from models.entities import (
    Base, Species, Property, PossibleValue,
    species_property_association,
    species_property_value_association
)
from models.seed import seed_demo_data