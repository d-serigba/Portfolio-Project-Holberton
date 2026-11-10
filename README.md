# Holberton Games - Portfolio Project C29

## Project Objective

Holberton Games is a web application designed to compile a collection of retro games. Developed as part of the C29 cohort portfolio project, the primary objective is to build a complete, functional web platform that integrates gameplay directly into the browser.

## Team

  - **David Dufont**: Backend Developer
  - **Dylan Serigba**: Frontend Developer
  - **Yonnhi Marcellus**: Security Devloper

## Games Included

  - **"Arnaud's Bizarre Adventure"**: A Zelda-like adventure game.
  - **Metroidvania**: An exploration game inspired by Metroid and Castlevania.
  - **Versus Fighting**: A combat game inspired by fighting classics.
  - **Hotline Miami Clone**: A top-down action game (in progress).
  - **City Runner**: 2D side-scrolling platformer (coming soon).

## Tech Stack

### Frontend
  - **HTML / CSS / JavaScript**: Web interface and API calls to the backend.

### Backend & Tools
  - **Python 3.12**: Core language.
  - **Pygame**: Game engine.
  - **Flask**: Backend framework.
  - **SQLite & SQLAlchemy**: Local database and ORM.
  - **MySQL (PyMySQL)**: Optional data storage.
  - **JWT (Flask-JWT-Extended)**: User authentication.
  - **Flask-CORS**: Frontend/backend communication.

## Prerequisites

Before starting, make sure you have:

| Requirement | Details |
|---|---|
| **Operating system** | Windows 10 / 11 (the launcher is a `.bat` file) |
| **Python 3.12** | Download at https://www.python.org/downloads/ |
| **Python Launcher (`py`)** | Included with the Windows installer, keep the option checked |
| **pip** | Included with Python |
| **Git** | To clone the repository (https://git-scm.com/) |
| **Web browser** | Chrome, Edge or Firefox |
| **Internet connection** | Needed for the pixel font (Google Fonts) |
| **Port 5000 free** | Used by the Flask API |

> During Python installation, check **"Add python.exe to PATH"** and **"py launcher"**.

Check your installation in a terminal:

```bash
python3 --version
```
It must display `Python 3.12.x`.

## Requirements

`docs/api/requirements.txt` must contain:

```text
Flask==3.0.2
Flask-SQLAlchemy==3.1.1
Flask-JWT-Extended==4.6.0
Flask-Cors
PyMySQL==1.1.0
cryptography==42.0.5
pygame==2.6.1
requests==2.31.0
```

## Installation & Usage (step by step)

### 1. Get the project

```bash
git clone https://github.com/<your-account>/Portfolio-Project-Holberton.git
cd Portfolio-Project-Holberton
```

### 2. Install dependencies (once only)

```bash
py -3.12 -m pip install -r docs/api/requirements.txt
```

### 3. Launch the platform

Double-click **`launch_hub.bat`** at the root of the project.

This will automatically:
1. Open a console window running the **Flask API**
2. Serve the website on `http://127.0.0.1:5000`

### 4. Open the website

Open your browser at:

```
http://127.0.0.1:5000
```

You land on the **home page** of Holberton Games.

### 5. Create an account / Log in

- **First visit**: click on the register option, choose a username and a password.
- **Already have an account**: enter your username and password and log in.

Each user has their own session, and their password is stored securely (hashed) in the database.

### 6. Play

1. Click on the card of an available game.
2. On the game page, click the launch button.
3. The game opens in a **Pygame window**, already connected with your account. No command to type.

Games marked *coming soon* are not playable yet.

### 7. Log out

Click **Logout** on the website. Closing the browser tab also logs you out automatically.

### 8. Stop the platform

Close the API console window (or press `CTRL+C` inside it).

## Troubleshooting

| Problem | Solution |
|---|---|
| `py` is not recognized | Reinstall Python 3.12 with the "py launcher" option |
| `ModuleNotFoundError` | Run step 2 again |
| Page does not load | Check that the API console is still open and that port 5000 is free |
| Game does not launch (404) | Check that the game folder exists in `docs/` |
| Error 401 when sending a score | Your session expired, log out and log in again |
| `InsecureKeyLengthWarning` in the console | Harmless; use a JWT secret key of 32+ characters in `config.py` to remove it |

## Project Structure

```text
Portfolio-Project-Holberton/
├── launch_hub.bat          # One-click launcher
└── docs/
    ├── api/                # Flask API (app.py, routes/, templates/, static/)
    ├── fighter_games/      # Versus Fighting
    ├── metroidvania/       # Metroidvania
    ├── zelda-like/         # Arnaud's Bizarre Adventure
    ├── design/             # Design documents
    ├── main.py             # Pygame hub
    └── login_screen.py     # Pygame login screen
```
## Data diagram 

<img width="2352" height="1401" alt="data_diagram 3" src="https://github.com/user-attachments/assets/eb42497c-6dda-4ed2-86ca-aee44b4a49d4" />

## Global architecture of the project

<img width="1187" height="768" alt="Global architecture2" src="https://github.com/user-attachments/assets/117b35cf-ff90-42c2-87f5-f7603e0fbe64" />

## Global architecture draft version

<img width="377" height="436" alt="Global architecture" src="https://github.com/user-attachments/assets/a1a91add-2a56-4c96-8005-e508a94525cb" />

## User parkour

<img width="1126" height="1318" alt="diagramme parcours utilisateur" src="https://github.com/user-attachments/assets/146b9d93-cf65-43b2-8d88-5eb1acdb9479" />

## Back-end and front-end connection

<img width="667" height="1399" alt="diagramme connex front back" src="https://github.com/user-attachments/assets/5e634394-39e4-43e6-bd06-b274cddf8f52" />

## Data management

<img width="859" height="666" alt="diagramme gestion des données" src="https://github.com/user-attachments/assets/856cd936-37df-4786-a101-0fb3e0f8bdcd" />

## Challenges

- Envoi des scores sans erreur visible :
Problème : le score était calculé mais l'appel à l'API partait sans que rien ne remonte dans le terminal.
Solution : ajout de print du statut et du détail de la réponse HTTP pour voir immédiatement ce que l'API renvoie.

- Session perdue ou mal chargée : 
Problème : le token était écrasé par des valeurs vides ou anciennes avant l'envoi, ce qui provoquait des 401.
Solution : lecture et écriture du token centralisées dans un seul fichier token.json, via _charger_token et _sauvegarder_token.

- Erreur 422 sur la route des scores :
Problème : Flask rejetait le payload (erreur 422) à cause d'un nom de champ différent de celui attendu (temps ou temps_jeu).
Solution : alignement des noms de champs du payload sur ceux attendus par la route Flask.

- Score non pris en compte côté classement : 
Problème : les points envoyés ne s'affichaient pas dans le menu de sélection malgré une réponse 200 sur le classement.
Solution : correction de l'URL du classement pour qu'elle corresponde à la route Flask, avec filtrage sur le jeu courant.

- Dépendance du score à la sauvegarde locale :
Problème : le calcul du score reposait sur state.etat, donc une save vide ou incomplète donnait un score faux.
Solution : ajout d'une vérification de l'état avant le calcul.

## Future updates

Make the fourth game playable (the Hotline Miami clone)

---

*Project developed by the C29   cohort.*

By 
David Dufont, github : dufontdd

Dylan Serigba, github : d-serigba

Yonnhi Marcellus, github : youri47
