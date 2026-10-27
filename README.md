# Holberton Games - Portfolio Project C28

## Project Objective

Holberton Games is a web application designed to compile a collection of retro games. Developed as part of the C28 cohort portfolio project, the primary objective is to build a complete, functional web platform that integrates gameplay directly into the browser.

## Team

  - **David Dufont**: Backend Developer
  - **Dylan Serigba**: Frontend Developer

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
py -3.12 --version
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

---

*Project developed by the C28 cohort.*
