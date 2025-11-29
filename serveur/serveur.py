from time import time

class Tache():
    """
    Class representing a single task.

    Attributes:
        id (int): Unique identifier for the task.
        titre (str): Short title of the task.
        description (str): Detailed description of the task.
        statut (str): Current status of the task. Can be "TODO", "DOING", or "DONE".
        auteur (str | None): Name of the task's author.
        created_at (float): Timestamp when the task was created (Unix time).
    """

    def __init__(self, id, titre, description="", statut="TODO", auteur=None, created_at=None):
        self.id = int(id)
        self.titre = str(titre)
        self.description = str(description)
        self.statut = str(statut)
        self.auteur = auteur
        # Use current time if created_at is missing
        self.created_at = float(created_at) if created_at is not None else time()

    def to_dict(self) -> dict:
        """
        Convert the task object to a dictionary suitable for JSON serialization.

        Returns:
            dict: Dictionary with all task attributes.
        """
        return {
            "id": self.id,
            "titre": self.titre,
            "description": self.description,
            "statut": self.statut,
            "auteur": self.auteur,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "Tache":
        """
        Create a Tache object from a dictionary.

        Args:
            data (dict): Dictionary containing task data.

        Returns:
            Tache: New instance of Tache with data from the dictionary.
        """
        # Safely handle missing created_at
        return Tache(
            id=data["id"],
            titre=data["titre"],
            description=data.get("description", ""),
            statut=data.get("statut", "TODO"),
            auteur=data.get("auteur"),
            created_at=data.get("created_at", time())
        )
    

