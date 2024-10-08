from typing import Any, Optional

class Migration:
    def __init__(self, migration_id: int, species: str, start_date: str, status: str = "Scheduled") -> None:
        self.migration_id = migration_id
        self.species = species
        self.start_date = start_date
        self.status = status

    def get_migration_details(self) -> dict[str, Any]:
        pass

    def update_migration_details(self, **kwargs: Any) -> None:
        pass
