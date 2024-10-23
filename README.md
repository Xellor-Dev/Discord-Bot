# Discord-Bot

![License](https://img.shields.io/github/license/Xellor-Dev/Discord-Bot)

## Description
A Python-based Discord bot tailored for Linux communities. This bot features profile management, package search on AUR, and Linux command tips, enhancing user interaction and server management.

## Features
- **Automated Moderation:** Automatically manages server activities and sends status updates when the bot is online.
- **Profile Management:** Allows users to create and update their profiles with various details including distro, DE/WM, browser, terminal, editor, programming language, shell, description, and image URL.
- **Badge Management:** Users can earn and display badges, which are stored and managed within the database.
- **Customizable Commands:** The bot supports various custom commands by loading extensions from different cogs (e.g., bot_info, linux, profiles, other).
- **Database Integration:** Uses SQLite for managing user profiles and badges, ensuring data persistence and consistency.
- **Presence and Status Updates:** The bot updates its presence and can send messages to a specific channel when it becomes ready, providing real-time status updates to server members.
- **Easy Extension Management:** The bot can easily load and manage different command sets by using a modular cog system.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/Xellor-Dev/Discord-Bot.git
```

2. Navigate to the project directory:
```bash
cd Discord-Bot
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

## Usage
```bash
python bot.py
```

## License
This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

