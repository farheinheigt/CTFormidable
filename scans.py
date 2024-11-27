#!/usr/bin/env python3

import os
import subprocess
import sys
import shutil
from rich.console import Console

console = Console()

# Définir les binaires nécessaires et vérifier leur disponibilité
REQUIRED_TOOLS = [
    "rustscan",
    "nmap",
    "enum4linux-ng",
    "smbclient",
    "feroxbuster",
    "hakrawler",
    "ffuf",
    "wafw00f",
    "whatweb",
    "nikto",
    "wapiti",
    "nuclei",
    "arjun",
    "sstimap",
    "dalfox"
]

def check_tools_availability():
    """
    Vérifie la disponibilité de chaque outil nécessaire.
    """
    missing_tools = []
    for tool in REQUIRED_TOOLS:
        if not shutil.which(tool):
            missing_tools.append(tool)
            console.print(f"[red]Erreur : Le binaire '{tool}' est manquant. Veuillez l'installer.[/red]")

    if missing_tools:
        console.print("[red]Certains outils nécessaires ne sont pas disponibles. Veuillez les installer pour continuer.[/red]")
        sys.exit(1)

def load_env_variables():
    """
    Charge les variables d'environnement nécessaires pour l'exécution des scans.
    """
    env_variables = {
        "CTF_PLATFORM": os.getenv("CTF_PLATFORM"),
        "CTF_NAME": os.getenv("CTF_NAME"),
        "IP_SOURCE": os.getenv("IP_SOURCE"),
        "IP_CIBLE": os.getenv("IP_CIBLE"),
        "URL": os.getenv("URL"),
        "DOMAIN": os.getenv("DOMAIN"),
    }

    # Vérifier si toutes les variables sont disponibles
    for key, value in env_variables.items():
        if not value:
            console.print(f"[red]Erreur : La variable d'environnement '{key}' est absente. Veuillez vous assurer que le shell est bien configuré.[/red]")
            sys.exit(1)
    
    return env_variables

def run_command(command, description):
    """
    Exécute une commande shell et gère la sortie.

    Args:
        command (str): Commande à exécuter.
        description (str): Description de la commande en cours.

    Returns:
        str: Résultat de la commande exécutée.
    """
    console.print(f"[cyan]Exécution de : {description}[/cyan]")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            console.print(f"[red]Erreur lors de l'exécution de '{description}'.[/red]")
        return result.stdout.strip()
    except Exception as e:
        console.print(f"[red]Erreur lors de l'exécution de '{description}': {e}[/red]")
        return None

def port_scanning(ip_address):
    """
    Phase de scan des ports avec Rustscan et Nmap.
    """
    # Phase 1 : Scan rapide des ports avec Rustscan
    rustscan_command = f"rustscan --greppable --ulimit 5000 -a {ip_address}"
    rustscan_result = run_command(rustscan_command, "Rustscan")
    
    if not rustscan_result:
        console.print("[red]Aucun résultat de Rustscan. Fin de la phase de scan des ports.[/red]")
        return []

    # Extraire les ports ouverts de Rustscan
    open_ports = []
    for line in rustscan_result.splitlines():
        if "/open/" in line:
            port = line.split()[0]
            open_ports.append(port)
    
    console.print(f"[green]Ports ouverts trouvés : {', '.join(open_ports)}[/green]")

    # Phase 2 : Scan approfondi avec Nmap
    if open_ports:
        selected_ports = ",".join(open_ports)
        nmap_command = f"sudo nmap -vvv -sSCV -A --version-all -p{selected_ports} -Pn -T5 {ip_address}"
        run_command(nmap_command, "Nmap")

    return open_ports

def network_service_enumeration(ip_address, resources_dir):
    """
    Phase d'énumération des services réseaux.
    """
    # Enum4linux-ng pour l'énumération des services Windows
    enum_command = f"enum4linux-ng -A {ip_address} -oJ {resources_dir}/enum4linux.txt"
    run_command(enum_command, "Enum4linux-ng")

    # SMBClient si nécessaire
    smb_command = f"smbclient //{ip_address}/SHARE_NAME -U username -D SAMBA_DOWNLOAD -c 'prompt OFF; recurse ON; mget *'"
    run_command(smb_command, "SMBClient")

def web_enumeration(url, domain_name, resources_dir, fuzzwordlistdir, fuzzwordlistdns):
    """
    Phase d'énumération des services web.
    """
    # Feroxbuster pour les répertoires cachés
    feroxbuster_command = f"feroxbuster -w {fuzzwordlistdir} -u {url} -C 404 --auto-bail --no-state --extract-links --collect-words --collect-backups --collect-extensions -k"
    run_command(feroxbuster_command, "Feroxbuster")

    # Hakrawler pour découvrir les URLs
    hakrawler_command = f"echo {url} | hakrawler -subs -u -dr -insecure -json > {resources_dir}/hakrawler.json"
    run_command(hakrawler_command, "Hakrawler")

    # FFUF pour les sous-domaines et les vhosts
    vhosts_command = f"ffuf -u {url} -H Host:FUZZ -w {fuzzwordlistdns} -ac -c -mc all -fc 400 -or -o {resources_dir}/vhosts.txt"
    run_command(vhosts_command, "FFUF Vhosts")

    subdomain_command = f"ffuf -H \"Host:FUZZ.{domain_name}\" -u {url} -w {fuzzwordlistdns} -ac -c -ic -mc all -or -o {resources_dir}/subdomains.txt"
    run_command(subdomain_command, "FFUF Subdomains")

def main():
    """
    Fonction principale pour orchestrer l'exécution des outils.
    """
    # Vérifier la disponibilité des outils
    check_tools_availability()

    # Charger les variables d'environnement
    env_vars = load_env_variables()

    # Variables de configuration
    ip_address = env_vars["IP_CIBLE"]
    resources_dir = f"./{env_vars['CTF_NAME']}"
    url = env_vars["URL"]
    domain_name = env_vars["DOMAIN"]

    # Créer le répertoire de ressources s'il n'existe pas
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)

    # Phase 1: Scan des ports
    open_ports = port_scanning(ip_address)

    # Phase 2: Énumération des services réseau
    network_service_enumeration(ip_address, resources_dir)

    # Phase 3: Énumération des services web si des ports web ont été trouvés
    web_ports = [port for port in open_ports if port in ["80", "443", "8080", "8443"]]
    if web_ports:
        web_enumeration(url, domain_name, resources_dir, fuzzwordlistdir="/path/to/dir_wordlist", fuzzwordlistdns="/path/to/dns_wordlist")

if __name__ == "__main__":
    main()
