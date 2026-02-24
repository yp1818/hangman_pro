# hangman_pro
🎮 Hangman Pro - A professional level-based word guessing game built with Flask &amp; SQLite3. Features 100+ levels, dynamic difficulty, and a powerful Admin Control Center (God Mode).
Hangman Pro: Level-Based Gaming Platform
Hangman Pro is a full-stack web application built with Flask and SQLite3. Unlike a basic word game, this project features a progressive 100-level system, a dynamic coin economy, and a robust Admin Control Center specifically designed for authorized administrators.

🚀 Features
🎮 Player Experience
Progressive Difficulty: Over 100 levels to unlock.

Dynamic Categories: Choose your category up to Level 10; after that, the game switches to a "Random Elite" mode to increase the challenge.

In-Game Economy: Earn coins by winning and use them to buy lives or hints.

User Dashboard: Real-time tracking of total scores, level progress, and game completions.

👑 Admin Powers (Virat Mode)
Cheat System: An exclusive "Auto-Win" toggle for the admin to bypass levels instantly.

User Management: Gift coins or skip levels for any registered user directly from the admin panel.

Application System: A built-in recruitment portal where users can apply to join the team, and the admin can approve or reject them with a single click.

🛠 Technical Highlights
Data Persistence: SQLite3 database ensures your level and coins are saved even after logging out.

Secure Auth: Password hashing using Werkzeug to protect user credentials.

Responsive UI: A modern dark-themed interface with glassmorphism effects.

🛠 Installation & Setup
Clone the Repository:

Bash
git clone https://github.com/yourusername/hangman-pro.git
cd hangman-pro
Install Dependencies:

Bash
pip install -r requirements.txt
Run the Application:

Bash
python app.py
Access the app at http://127.0.0.1:5000

📁 Project Structure
Plaintext
├── app.py              # Main Flask application logic (Admin & User routes)
├── models.py           # Database schema and helper functions
├── game_logic.py       # Hangman engine (lives, scoring, hints)
├── word_list.py        # Library of words categorized by difficulty
├── requirements.txt    # List of Python dependencies for deployment
├── Procfile            # Deployment configuration for Render/Heroku
├── templates/          # HTML files (Dashboard, Game, Admin Panel)
└── static/             # CSS styling and local images
☁️ Deployment
This project is configured for easy deployment on Render:

Connect your GitHub repository to Render.

Set the Build Command to: pip install -r requirements.txt.

Set the Start Command to: gunicorn app:app.

📝 Note on Admin Access
To access the Admin Control Center, register with the username "Virat". The system automatically grants administrative privileges to this specific username.
