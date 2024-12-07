#!/usr/bin/env python3

import os
import sys
import argparse
import requests
import pyperclip
import subprocess
import shutil
from rich.console import Console
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import tempfile

console = Console()

def check_dependencies():
    """
    Vérifie si les outils externes nécessaires sont installés.
    """
    for tool in ["mods", "gum"]:
        if not shutil.which(tool):
            raise FileNotFoundError(f"[red bold]L'outil '{tool}' n'est pas installé. Veuillez l'installer pour continuer.[/red bold]")

def validate_and_format_url(url):
    """
    Valide et formate l'URL en ajoutant 'http://' si aucun schéma n'est présent.
    """
    if not urlparse(url).scheme:
        url = f"http://{url}"
    return url

def generate_http_request_and_response(url):
    """
    Génère une requête HTTP erronée et capture la réponse, avec détection dynamique des champs de formulaire.

    Args:
        url (str): URL cible.

    Returns:
        tuple: Contenu brut de la requête HTTP et de la réponse HTTP.
    """
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port or ("443" if parsed_url.scheme == "https" else "80")
    path = parsed_url.path or "/"

    try:
        # Récupérer le code source HTML de la page cible
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html_source = response.text

        # Utiliser BeautifulSoup pour analyser le formulaire HTML
        soup = BeautifulSoup(html_source, "html.parser")
        form = soup.find("form")
        if not form:
            raise ValueError("Aucun formulaire trouvé sur la page.")

        # Extraire les noms des champs de formulaire
        fields = {input_tag.get("name"): "test" for input_tag in form.find_all("input") if input_tag.get("name")}
        if not fields:
            raise ValueError("Aucun champ de formulaire détecté.")

        # Construire le corps de la requête à partir des champs détectés
        data = "&".join(f"{k}={v}" for k, v in fields.items())
        headers = {
            "Host": f"{host}:{port}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Envoyer une requête POST avec les données simulées
        post_response = requests.post(url, data=data, headers=headers, timeout=10)

        # Construire la requête brute
        http_request = f"POST {path} HTTP/1.1\n" + \
                       "\n".join(f"{k}: {v}" for k, v in headers.items()) + \
                       f"\n\n{data}"

        # Construire la réponse brute
        http_response = f"HTTP/{post_response.raw.version / 10 if hasattr(post_response.raw, 'version') else 1.1} {post_response.status_code} {post_response.reason}\n" + \
                        "\n".join(f"{k}: {v}" for k, v in post_response.headers.items()) + \
                        f"\n\n{post_response.text}"

        return http_request, http_response
    except requests.RequestException as e:
        console.print(f"[red]Erreur lors de la requête HTTP : {e}[/red]")
        return None, None
    except Exception as e:
        console.print(f"[red]Erreur : {e}[/red]")
        return None, None

def generate_prompt_for_username(http_request, http_response, prototype):
    """
    Génère un prompt pour le bruteforce de l'utilisateur.

    Args:
        http_request (str): Contenu brut de la requête HTTP.
        http_response (str): Contenu brut de la réponse HTTP.
        prototype (str): Prototype de commande Hydra.

    Returns:
        str: Prompt complet pour l'IA.
    """
    return (
        "On souhaite bruteforcer le champ de saisie du nom d'utilisateur avec un mot de passe fixe 'TEST'.\n\n"
        f"Voici les détails de la requête et de la réponse HTTP échouée :\n"
        f"1. Requête HTTP :\n{http_request}\n\n"
        f"2. Réponse HTTP :\n{http_response}\n\n"
        "Identifie et retourne uniquement les champs suivants, séparés par `###` :\n"
        "- Le nom du champ pour le nom d'utilisateur.\n"
        "- Le nom du champ pour le mot de passe.\n"
        "- La chaîne indiquant l'échec d'authentification.\n\n"
        "Retourne uniquement ces informations sous la forme : champ_username###champ_password###message_derreur\n"
        "Ne retourne aucun texte explicatif ou format Markdown."
    )


def generate_prompt_for_password(http_request, http_response, prototype, username):
    """
    Génère un prompt pour le bruteforce du mot de passe.

    Args:
        http_request (str): Contenu brut de la requête HTTP.
        http_response (str): Contenu brut de la réponse HTTP.
        prototype (str): Prototype de commande Hydra.
        username (str): Nom d'utilisateur fixe pour l'attaque.

    Returns:
        str: Prompt complet pour l'IA.
    """
    return (
        f"On souhaite bruteforcer le champ de saisie du mot de passe pour un utilisateur fixe '{username}'.\n\n"
        f"Voici les détails de la requête et de la réponse HTTP échouée :\n"
        f"1. Requête HTTP :\n{http_request}\n\n"
        f"2. Réponse HTTP :\n{http_response}\n\n"
        "Identifie et retourne uniquement les champs suivants, séparés par `###` :\n"
        "- Le nom du champ pour le nom d'utilisateur.\n"
        "- Le nom du champ pour le mot de passe.\n"
        "- La chaîne indiquant l'échec d'authentification.\n\n"
        "Retourne uniquement ces informations sous la forme : champ_username###champ_password###message_derreur\n"
        "Ne retourne aucun texte explicatif ou format Markdown."
    )


def analyze_page_with_http(prompt, verbose=False):
    """
    Analyse une page en combinant les requêtes et les réponses HTTP pour générer une commande Hydra.
    """
    try:
        # Écrire le prompt dans un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as prompt_file:
            prompt_file.write(prompt.encode())
            prompt_file_path = prompt_file.name

        # Exécuter la commande mods avec le fichier prompt
        mods_command = f"mods -m expert-secu --api ollama -P \"$(cat {prompt_file_path})\""
        if verbose:
            console.print(f"[yellow]Commande mods exécutée :[/yellow] {mods_command}")
        result = subprocess.run(
            mods_command,
            shell=True,
            capture_output=True,
            text=True,
            env=os.environ
        )

        if result.returncode != 0:
            console.print(f"[red]Erreur (stderr) de mods :[/red]\n{result.stderr}")
            raise Exception(f"Erreur 'mods': {result.stderr.strip()}")

        if verbose:
            console.print(f"[yellow]Sortie complète de mods :[/yellow]\n{result.stdout}")
        return result.stdout.strip()
    finally:
        if 'prompt_file_path' in locals() and os.path.exists(prompt_file_path):
            os.remove(prompt_file_path)

def ask_action_with_gum():
    choices = ["username", "password"]
    try:
        result = subprocess.run(
            ["gum", "choose"] + choices,
            text=True,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            check=True
        )
        return result.stdout.strip()
    except FileNotFoundError:
        console.print("[yellow]⚠️  Gum n'est pas installé. Mode non interactif activé.[/yellow]")
        return console.input("Choisissez une action (username/password) : ").strip()

def gum_input_with_fallback(prompt_text, placeholder="Entrée ici"):
    """
    Utilise 'gum input' pour demander une entrée utilisateur ou bascule en mode fallback si gum n'est pas disponible.

    Args:
        prompt_text (str): Le texte du prompt à afficher.
        placeholder (str): Le texte du placeholder pour 'gum input'.

    Returns:
        str: La chaîne saisie par l'utilisateur.
    """
    try:
        # Utilise gum input pour une expérience utilisateur enrichie
        result = subprocess.run(
            ["gum", "input", "--placeholder", placeholder],
            text=True,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            check=True
        )
        return result.stdout.strip()
    except FileNotFoundError:
        # Fallback si gum n'est pas installé
        console.print("[yellow]⚠️  Gum n'est pas installé. Mode non interactif activé.[/yellow]")
        return console.input(f"{prompt_text} : ").strip()
    except Exception as e:
        # Gestion des erreurs générales
        console.print(f"[red]Erreur avec gum : {e}. Bascule en mode non interactif.[/red]")
        return console.input(f"{prompt_text} : ").strip()

def extract_path_from_url(url):
    """
    Extrait le chemin depuis l'URL spécifiée. Si aucun chemin explicite n'est présent, retourne '/'.

    Args:
        url (str): URL cible.

    Returns:
        str: Chemin extrait.
    """
    parsed_url = urlparse(url)
    return parsed_url.path if parsed_url.path else "/"


def main():
    parser = argparse.ArgumentParser(description="Wrapper pour générer des commandes Hydra.")
    parser.add_argument("--url", required=True, help="URL cible (http:// ou https://)")
    parser.add_argument("--verbose", action="store_true", help="Affiche des informations détaillées pour le débogage.")
    args = parser.parse_args()

    check_dependencies()

    url = validate_and_format_url(args.url)

    if args.verbose:
        console.print(f"[blue]Mode verbose activé. URL cible : {url}[/blue]")

    console.print("[cyan]Sélectionnez une action (username ou password) :[/cyan]")
    action = ask_action_with_gum()

    # Extraire le chemin exact depuis l'URL
    parsed_url = urlparse(url)
    path = parsed_url.path or "/"

    if action == "password":
        username = gum_input_with_fallback(
            prompt_text="Entrez le nom d'utilisateur fixe pour le bruteforce du mot de passe",
            placeholder="Nom d'utilisateur"
        )
        if not username:
            console.print("[red]Erreur : Aucun nom d'utilisateur fourni.[/red]")
            sys.exit(1)

    prototype = (
        f'hydra -L $DICOS/Seclists/rockyou.txt -p TEST $URL:$PORT http-post-form "{path}:£champ_username=^USER^&£champ_password=TEST:F=£message_derreur" -V'
        if action == "username" else
        f'hydra -l {username} -P $DICOS/Seclists/rockyou.txt $URL:$PORT http-form-post "{path}:£champ_username={username}&£champ_password=^PASS^:F=£message_derreur" -Vf'
    )

    http_request, http_response = generate_http_request_and_response(url)
    if not http_request or not http_response:
        console.print("[red]Impossible de générer la requête ou la réponse HTTP.[/red]")
        return

    if action == "username":
        prompt = generate_prompt_for_username(http_request, http_response, prototype)
    else:  # action == "password"
        prompt = generate_prompt_for_password(http_request, http_response, prototype, username)

    if args.verbose:
        console.print(f"[yellow]Prompt généré :[/yellow]\n{prompt}")

    try:
        mods_output = analyze_page_with_http(prompt, verbose=args.verbose)
        if not mods_output.strip():
            raise ValueError("La sortie de mods est vide.")

        # Extraire les valeurs retournées par mods
        try:
            champ_username, champ_password, message_derreur = mods_output.strip().split("###")
        except ValueError:
            console.print("[red]Erreur : La sortie de mods ne contient pas trois champs séparés par `###`.[/red]")
            sys.exit(1)

        # Remplacer les placeholders dans le prototype
        hydra_command = prototype.replace("£champ_username", champ_username.strip()) \
                                 .replace("£champ_password", champ_password.strip()) \
                                 .replace("£message_derreur", message_derreur.strip())

        if args.verbose:
            console.print(f"[yellow]Commande Hydra générée :[/yellow]\n{hydra_command}")

        console.print(f"[green]Commande Hydra générée :[/green] {hydra_command}")
        pyperclip.copy(hydra_command)
    except Exception as e:
        console.print(f"[red bold]Erreur :[/red bold] {e}")




if __name__ == "__main__":
    main()
