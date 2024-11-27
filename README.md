# CTFacile - Outils d'Automatisation de Pentest

## Description du Projet

**CTFacile** est un projet visant à automatiser les tâches répétitives et redondantes de pentest dans des environnements de Capture The Flag (CTF). Le programme vise à faciliter la configuration de l'environnement d'un pentester et l'exécution d'outils populaires pour l'énumération des services, la recherche de vulnérabilités et le dépassement des limites des sécurités courantes.

Le projet inclut :
- Un script pour configurer facilement l'environnement shell à l'aide de variables d'environnement exportées.
- Un wrapper pour gérer la connexion VPN, le nettoyage de l'environnement après les tests, et l'automatisation du chargement des variables nécessaires.
- Un script de scan automatisé (à partir des outils populaires comme Nmap, Rustscan, Enum4Linux, etc.) qui lance les analyses en fonction de la configuration et des ports détectés.

## Prérequis

Avant de lancer le projet, assure-toi que les outils suivants sont installés sur ta machine :

- [Python 3.6+](https://www.python.org/downloads/)
- [Pipx](https://pipxproject.github.io/pipx/installation/)
- [Gum](https://github.com/charmbracelet/gum) : Pour faciliter l'interaction utilisateur.
- Les outils de pentest populaires (les binaires) :
  - Rustscan
  - Nmap
  - Enum4Linux-ng
  - Feroxbuster
  - FFUF
  - Hakrawler
  - Nikto
  - Wapiti
  - Nuclei
  - Et bien d'autres...

Assure-toi également d'avoir configuré correctement un client VPN supportant les fichiers OpenVPN (étant donné que l'environnement de test pourrait être réseauté).

## Installation

1. Clone ce projet à partir de GitHub :
   ```bash
   git clone https://github.com/votre-utilisateur/ctfacile.git
   cd ctfacile
   ```

2. Installe les dépendances du projet :
   ```bash
   pipx install ./
   ```

3. Configure ton environnement :
   Lancement du script d'installation qui installera CTFacile et vérifiera la présence des outils requis :
   ```bash
   ./CTFacile_install.sh
   ```

## Utilisation

### Lancement Initial

Pour commencer, tu dois exécuter le script principal qui configurera l'environnement de travail :

```bash
./CTFacile.sh
```

Le script te proposera plusieurs options :
- Lancer un CTF et configurer l'environnement.
- Restaurer l'environnement après avoir terminé un CTF.
- Configurer les répertoires des fichiers CTF et des fichiers VPN.
- Quitter l'application.

### Fonctionnalités Clés

1. **Configuration Environnementale** :
   Le script configurera ton environnement en utilisant un fichier `.env_ctfacile.sh` qui contiendra des variables d'environnement critiques pour les futures opérations (comme l'adresse IP cible ou la plateforme CTF utilisée).

2. **Lancement d'Outils Automatisés** :
   Après configuration, le script `scans.py` peut être exécuté pour lancer une série de scans de manière automatisée. Il regroupe des outils populaires tels que Rustscan, Nmap, Enum4Linux, FFUF, etc. Les scans seront lancés de manière conditionnelle, en fonction des résultats des phases précédentes.

3. **Nettoyage de l'Environnement** :
   Une fois le CTF terminé, le script te permet de nettoyer l'environnement, en désinitialisant les variables d'environnement, en déconnectant le VPN, et en nettoyant le fichier `/etc/hosts`.

### Exemple d'Utilisation

Voici un exemple de flux de travail typique :

1. Lance CTFacile avec `./CTFacile.sh`.
2. Choisis l'option pour configurer un nouvel environnement CTF.
3. Fournis les détails nécessaires tels que la plateforme CTF, le nom du CTF, et l'adresse IP cible.
4. Une fois configuré, lance les différents scans avec le script `scans.py` pour explorer les vulnérabilités.
5. Une fois le CTF terminé, utilise `./CTFacile.sh` pour restaurer l'environnement à son état initial.

## Problèmes Courants

- **Erreur : Binaire Manquant** : Si un des outils n'est pas trouvé sur le système, tu dois l'installer pour pouvoir continuer.
- **VPN Non Connecté** : Assure-toi que le fichier OpenVPN est présent et correctement configuré pour éviter les problèmes de connexion.

## Contributions

Les contributions sont les bienvenues! Si tu souhaites ajouter un outil, améliorer l'automatisation des scans ou ajouter des nouvelles fonctionnalités, n'hésite pas à créer une pull request ou à soumettre des issues pour discuter des changements possibles.

## Avertissement

Ce projet est destiné à être utilisé exclusivement à des fins éducatives et dans des environnements autorisés. Toute utilisation non autorisée de ces outils peut être illégale.

## License

Ce projet est sous licence MIT. Pour plus de détails, réfère-toi au fichier LICENSE.

## Contact

Pour toute question ou suggestion, n'hésite pas à contacter l'équipe du projet.

