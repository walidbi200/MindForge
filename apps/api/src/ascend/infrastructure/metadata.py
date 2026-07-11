from sqlmodel import SQLModel

# This file serves as the permanent metadata location for Alembic.
# All domain models should be imported here when they are created, 
# so Alembic can detect them for autogenerating migrations.

metadata = SQLModel.metadata
