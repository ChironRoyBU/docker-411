from typing import Optional
from wildlife_tracker.habitat_management.habitat import Habitat  


class MigrationPath:
    def __init__(self, path_id: int, start_location: str, destination: str, duration: Optional[int] = None) -> None:
        self.path_id = path_id
        self.start_location = start_location
        self.destination = destination
        self.duration = duration

    def create_migration_path(self, path_id: int, species: str, start_location: Habitat, destination: Habitat, duration: Optional[int] = None,) -> MigrationPath:
        pass

    def remove_migration_path(self, path_id: int) -> None:
        pass

    def get_migration_path_by_id(self, path_id: int) -> MigrationPath:
        pass

    def get_migration_paths(self) -> List[MigrationPath]:
        pass

    def get_migration_paths_by_destination(self, destination: Habitat) -> List[MigrationPath]:
        pass

    def get_migration_paths_by_species(self, species: str) -> List[MigrationPath]:
        pass

    def get_migration_paths_by_start_location(self, start_location: Habitat) -> List[MigrationPath]:
        pass

    def get_migration_path_details(self, path_id: int) -> dict:
        pass

    def update_migration_path_details(self, path_id: int, kwargs: Any) -> None:
        pass
