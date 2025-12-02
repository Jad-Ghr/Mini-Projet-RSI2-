# server CLI entrypoint

from argparse import ArgumentParser , Namespace
from serveur import ServeurTaches, GestionnaireTaches

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 9000


def parse_args() -> Namespace:
    parser = ArgumentParser(
        prog="server",
        description="Serveur de gestionnaire de tâches"
    )

    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help="Adresse à écouter"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Port à utiliser"
    )

    parser.add_argument(
        "--persist",
        action="store_true",
        help="Activer la sauvegarde des tâches dans un fichier"
    )

    parser.add_argument(
        "--persist-path",
        default="tasks.json",
        help="Chemin du fichier de sauvegarde"
    )

    return parser.parse_args()


def main():
    """Start server with CLI args."""
    args = parse_args()

    manager = GestionnaireTaches(
        persist_path=args.persist_path,
        persist=args.persist
    )

    server = ServeurTaches(
        host=args.host,
        port=args.port,
        manager=manager
    )

    server.start()


if __name__ == "__main__":
    main()
