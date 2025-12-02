# Class: ClientTaches
# Responsibilities: connect to server, send JSON requests, parse responses

import socket
import json


class ClientTaches:
    """
    TCP client used by CLI to interact with ServeurTaches.
    Protocol: send JSON object followed by newline; receive JSON object followed by newline.
    """

    def __init__(self, host="127.0.0.1", port=9000, timeout=5.0)-> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def _send(self, payload) -> dict:
        """Send payload (a dict) and return JSON response (as dict)."""
        data = json.dumps(payload) + "\n"

        with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
            sock.sendall(data.encode("utf-8"))

            buffer = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                if b"\n" in buffer:
                    line, _ = buffer.split(b"\n", 1)
                    try:
                        return json.loads(line.decode("utf-8"))
                    except json.JSONDecodeError:
                        return {"status": "error", "error": "invalid_response"}

        return {"status": "error", "error": "no_response"}

    def add(self, titre, description="", auteur=None)-> dict:
        return self._send({
            "action": "add",
            "titre": titre,
            "description": description,
            "auteur": auteur
        })

    def list(self, auteur=None, statut=None, search_titre=None)-> dict:
        req = {"action": "list"}

        if auteur:
            req["auteur"] = auteur
        if statut:
            req["statut"] = statut
        if search_titre:
            req["search_titre"] = search_titre

        return self._send(req)

    def delete(self, task_id)-> dict:
        return self._send({
            "action": "delete",
            "id": task_id
        })

    def update_status(self, task_id, statut)-> dict:
        return self._send({
            "action": "update_status",
            "id": task_id,
            "statut": statut
        })
