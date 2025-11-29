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
    


import json
import os
import threading
import traceback

class GestionnaireTaches () :
    def __init__(self, persist_path=None, persist=False):
        self._lock = threading.Lock()
        self._tasks = {}
        self._next_id = 1

        self.persist = persist
        self.persist_path = persist_path

        if self.persist and self.persist_path:
            self._load_from_file()

    def _load_from_file(self):
        """Load tasks from JSON file if exists."""
        try:
            if os.path.exists(self.persist_path):
                with open(self.persist_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                saved_tasks = data.get("tasks", [])

                with self._lock:
                    self._tasks = {int(t["id"]): Tache.from_dict(t) for t in saved_tasks}
                    self._next_id = max(self._tasks.keys(), default=0) + 1

        except Exception:
            traceback.print_exc()

    def _save_to_file(self):
        """Persist tasks to JSON file atomically."""
        if not (self.persist and self.persist_path):
            return

        with self._lock:
            data = {
                "tasks": [t.to_dict() for t in self._tasks.values()]
            }

        try:
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        except Exception:
            traceback.print_exc()


    def add_task(self, titre, description="", auteur=None):
        """Add and return a new Tache."""
        with self._lock:
            t = Tache(self._next_id, titre, description, "TODO", auteur)
            self._tasks[self._next_id] = t
            self._next_id += 1
            self._save_to_file()
            return t
        
    def list_tasks(self, filtre_auteur=None, filtre_statut=None, search_titre=None):
        """Return list of tasks, optionally filtered."""
        with self._lock:
            tasks = list(self._tasks.values())

        if filtre_auteur:
            tasks = [t for t in tasks if t.auteur == filtre_auteur]

        if filtre_statut:
            tasks = [t for t in tasks if t.statut == filtre_statut]

        if search_titre:
            tasks = [t for t in tasks if search_titre.lower() in t.titre.lower()]

        tasks.sort(key=lambda t: t.id)
        return tasks
    
    def delete_task(self, task_id):
        """Delete a task by id. Return True if deleted."""
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                self._save_to_file()
                return True
            return False
    
    def update_status(self, task_id, statut):
        """Update the status of a task. Return True if updated."""

        with self._lock:
            t = self._tasks.get(task_id)
            if not t:
                return False

            t.statut = statut
            self._save_to_file()
            return True
        
    
    def get_task(self, task_id):
        """Return a task or None."""
        with self._lock:
            return self._tasks.get(task_id)
        