from json import load, dump, loads, dumps, JSONDecodeError
from threading import Lock
from traceback import print_exc
from os.path import exists
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from concurrent.futures import ThreadPoolExecutor

from model import Tache

class GestionnaireTaches:
    def __init__(self, persist_path=None, persist=False) -> None:
        self._lock = Lock()
        self._tasks = {}
        self._next_id = 1

        self.persist = persist
        self.persist_path = persist_path

        if self.persist and self.persist_path:
            self._load_from_file()

    def _load_from_file(self) -> None:
        """Load tasks from JSON file if exists."""
        try:
            if self.persist_path and exists(self.persist_path):
                with open(self.persist_path, "r", encoding="utf-8") as f:
                    data = load(f)

                saved_tasks = data.get("tasks", [])

                with self._lock:
                    self._tasks = {
                        int(t["id"]): Tache.from_dict(t)
                        for t in saved_tasks
                    }
                    self._next_id = max(self._tasks.keys(), default=0) + 1

        except Exception:
            print_exc()

    def _save_to_file(self) -> None:
        """Persist tasks to JSON file atomically."""
        if not (self.persist and self.persist_path):
            return

        with self._lock:
            data = {"tasks": [t.to_dict() for t in self._tasks.values()]}

        try:
            with open(self.persist_path, "w", encoding="utf-8") as f:
                dump(data, f, indent=2)

        except Exception:
            print_exc()

    def add_task(self, titre, description="", auteur=None) -> Tache:
        """Add and return a new Tache."""
        with self._lock:
            t = Tache(self._next_id, titre, description, "TODO", auteur)
            self._tasks[self._next_id] = t
            self._next_id += 1
            self._save_to_file()
            return t

    def list_tasks(
        self,
        filtre_auteur=None,
        filtre_statut=None,
        search_titre=None
    ) -> list[Tache]:
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

    def delete_task(self, task_id) -> bool:
        """Delete a task by ID. Return True if deleted."""
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                self._save_to_file()
                return True
            return False

    def update_status(self, task_id, statut) -> bool:
        """Update the status of a task. Return True if updated."""
        with self._lock:
            t = self._tasks.get(task_id)
            if not t:
                return False

            t.statut = statut
            self._save_to_file()
            return True

    def get_task(self, task_id) -> Tache | None:
        """Return a task or None."""
        with self._lock:
            return self._tasks.get(task_id)




class ServeurTaches:
    """
        Simple TCP server that accepts JSON line-delimited commands.
        Each request is a JSON object followed by newline.
    """
    def __init__(self, host="0.0.0.0", port=9000, manager=None, max_workers=8)-> None:
        """
        Initialize server.
        :param host: host to bind
        :param port: port to bind
        :param manager: GestionnaireTaches instance
        :param max_workers: thread pool size
        """
        self.host = host
        self.port = port
        self.manager = manager or GestionnaireTaches()

        self._sock = socket(AF_INET, SOCK_STREAM)
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._running = False

    def start(self)-> None:
        """Start listening for incoming connections."""
        self._sock.bind((self.host, self.port))
        self._sock.listen()
        self._running = True

        print(f"ServeurTaches listening on {self.host}:{self.port}")

        try:
            while self._running:
                conn, addr = self._sock.accept()
                print(f"Client connected: {addr}")
                self._executor.submit(self._handle_client, conn)
        except KeyboardInterrupt:
            print("Server interrupted (CTRL+C).")
        finally:
            self.stop()

    def stop(self)-> None:
        """Shutdown server and thread pool."""
        self._running = False
        try:
            self._sock.close()
        except Exception:
            pass


        self._executor.shutdown(wait=True)
        print("Server stopped.")

    def _handle_client(self, conn)-> None:
        """Handle one client connection; read lines and process JSON commands."""
        with conn:
            try:
                buffer = b""
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break

                    buffer += data

                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        if not line.strip():
                            continue

                        try:
                            request = loads(line.decode("utf-8"))
                        except JSONDecodeError:
                            conn.sendall((dumps({"status": "error", "error": "invalid_json"}) + "\n").encode())
                            continue

                        response = self._process_request(request)
                        conn.sendall((dumps(response) + "\n").encode())
            except Exception:
                print_exc()

    def _process_request(self, req)-> dict:
        """
        Process a single request dict and return response dict.
        Supported actions: add, list, delete, update_status
        Supports optional filters for list: auteur, statut, search_titre
        """
        action = req.get("action")

        try:
            if action == "add":
                titre = req.get("titre")
                if not titre:
                    return {"status": "error", "error": "missing_titre"}

                t = self.manager.add_task(
                    titre=titre,
                    description=req.get("description", ""),
                    auteur=req.get("auteur")
                )
                return {"status": "ok", "task": t.to_dict()}

            elif action == "list":
                tasks = self.manager.list_tasks(
                    req.get("auteur"),
                    req.get("statut"),
                    req.get("search_titre")
                )
                return {"status": "ok", "tasks": [t.to_dict() for t in tasks]}

            elif action == "delete":
                tid = req.get("id")
                if tid is None:
                    return {"status": "error", "error": "missing_id"}

                if self.manager.delete_task(int(tid)):
                    return {"status": "ok"}
                return {"status": "error", "error": "not_found"}

            elif action == "update_status":
                tid = req.get("id")
                statut = req.get("statut")

                if tid is None or statut is None:
                    return {"status": "error", "error": "missing_id_or_statut"}

                if self.manager.update_status(int(tid), statut):
                    return {"status": "ok"}
                return {"status": "error", "error": "not_found"}

            else:
                return {"status": "error", "error": "unknown_action"}

        except Exception:
            print_exc()
            return {"status": "error", "error": "server_exception"}
