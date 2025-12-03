# client CLI entrypoint (interactive menu in French)

import argparse
from .client import ClientTaches

MENU = """
=== Gestionnaire de tâches partagé ===
1) Ajouter une tâche
2) Liste des tâches
3) Supprimer une tâche
4) Changer le statut d'une tâche
5) Quitter
Choix: """


def parse_args():
    parser = argparse.ArgumentParser(
        prog="client",
        description="Client CLI pour ServeurTaches"
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Adresse du serveur"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=9000,
        help="Port du serveur"
    )

    return parser.parse_args()


def pretty_print_tasks(tasks):
    if not tasks:
        print("Aucune tâche.")
        return

    for t in tasks:
        print(
            f"[{t['id']}] {t['titre']} "
            f"(statut={t.get('statut')}, auteur={t.get('auteur')}) - "
            f"{t.get('description', '')}"
        )


def main():
    args = parse_args()
    client = ClientTaches(host=args.host, port=args.port)

    while True:
        try:
            choice = input(MENU).strip()

            if choice == "1":
                titre = input("Titre: ").strip()
                description = input("Description: ").strip()
                auteur = input("Auteur (optionnel): ").strip() or None

                resp = client.add(titre, description, auteur)

                if resp.get("status") == "ok":
                    print("Tâche ajoutée:", resp.get("task"))
                else:
                    print("Erreur:", resp.get("error"))

            elif choice == "2":
                filtr_auteur = input("Filtrer par auteur (vide = tous): ").strip() or None
                filtr_statut = input("Statut (TODO/DOING/DONE) (vide = tous): ").strip() or None
                search = input("Recherche titre (vide = ignore): ").strip() or None

                resp = client.list(auteur=filtr_auteur, statut=filtr_statut, search_titre=search)

                if resp.get("status") == "ok":
                    pretty_print_tasks(resp.get("tasks", []))
                else:
                    print("Erreur:", resp.get("error"))

            elif choice == "3":
                tid = input("ID de la tâche à supprimer: ").strip()

                if not tid.isdigit():
                    print("ID invalide.")
                    continue

                resp = client.delete(int(tid))

                if resp.get("status") == "ok":
                    print("Supprimée.")
                else:
                    print("Erreur:", resp.get("error"))

            elif choice == "4":
                tid = input("ID de la tâche: ").strip()

                if not tid.isdigit():
                    print("ID invalide.")
                    continue

                statut = input("Nouveau statut (TODO/DOING/DONE): ").strip()

                resp = client.update_status(int(tid), statut)

                if resp.get("status") == "ok":
                    print("Statut mis à jour.")
                else:
                    print("Erreur:", resp.get("error"))

            elif choice == "5":
                print("Au revoir.")
                break

            else:
                print("Choix invalide.")

        except KeyboardInterrupt:
            print("\nInterrompu. Au revoir.")
            break


if __name__ == "__main__":
    main()
