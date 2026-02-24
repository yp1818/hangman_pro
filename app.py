from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import random  # Naya logic ke liye zaroori hai
from game_logic import Hangman
from models import (
    init_db, create_user, get_user, update_score_and_level, 
    verify_password, get_user_stats, record_login, save_application,
    restart_user_game
)
from word_list import word

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database initialization on startup
init_db()

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if get_user(username):
            return "User already exists! <a href='/register'>Try again</a>"
        create_user(username, password)
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = get_user(username)
        if user and verify_password(user[2], password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            # Tracking login details
            record_login(user[0], user[1], request.remote_addr)
            
            # Application check on login (Permanent Persistence)
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM applications WHERE name = ?", (user[1],))
            session["applied"] = True if cursor.fetchone() else False
            conn.close()
            
            return redirect(url_for("dashboard"))
        return "Invalid credentials! <a href='/login'>Try again</a>"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    # LEVEL SYNC FIX: Dashboard load par hamesha DB se stats uthayenge
    stats = get_user_stats(session["user_id"])
    
    if stats is None:
        session.clear()
        return redirect(url_for("login"))
        
    # 100 Levels Victory Check
    if stats[2] > 100:
        return render_template("victory.html", username=session["username"], completions=stats[3])
        
    return render_template("dashboard.html", username=session["username"], categories=word.keys(), 
                            total_score=stats[0], coins=stats[1], level=stats[2], completions=stats[3])

@app.route("/restart_game", methods=["POST"])
def restart():
    if "user_id" in session:
        restart_user_game(session["user_id"])
    return redirect(url_for("dashboard"))

@app.route("/apply", methods=["POST"])
def apply():
    if "user_id" in session:
        if session.get("applied"):
             return redirect(url_for("dashboard"))

        name = request.form.get("name")
        email = request.form.get("email")
        reason = request.form.get("reason")
        
        save_application(name, email, reason)
        session["applied"] = True
        
    return redirect(url_for("dashboard"))

@app.route("/start", methods=["POST"])
def start_game():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    # Fresh level fetch for starting game
    stats = get_user_stats(session["user_id"])
    current_level = stats[2] if stats else 1
    
    if current_level > 10:
        category = random.choice(list(word.keys()))
    else:
        category = request.form.get("category")
    
    difficulty = request.form.get("difficulty", "Medium")
    game = Hangman(category, difficulty)
    game.level = current_level 
    
    session["game"] = game.__dict__
    return redirect(url_for("game"))

@app.route("/game", methods=["GET", "POST"])
def game():
    if "user_id" not in session or "game" not in session:
        return redirect(url_for("dashboard"))

    game_data = session["game"]
    game = Hangman(game_data['category'], game_data['difficulty'])
    game.__dict__ = game_data

    if request.method == "POST":
        action = request.form.get("action")
        
        # ADMIN CHEAT: Level Sync Fix included
        if action == "auto_win" and session.get("username", "").lower() == "virat":
            game.guessed = set(game.secret_word.lower())
            game.score += 100
            update_score_and_level(session["user_id"], game.score, True)
            
            # DB se naya level fetch karke sync kar rahe hain
            new_stats = get_user_stats(session["user_id"])
            game.level = new_stats[2]
            
            session["game"] = game.__dict__
            session.modified = True 
            return "SUCCESS" 

        if action == "guess":
            letter = request.form.get("letter")
            if letter:
                game.guess(letter.lower())
        elif action == "hint":
            game.use_hint()
        elif action == "buy_life":
            stats = get_user_stats(session["user_id"])
            if stats[1] >= 20:
                game.lives += 1
                conn = sqlite3.connect("database.db")
                conn.execute("UPDATE users SET coins = coins - 20 WHERE id=?", (session["user_id"],))
                conn.commit()
                conn.close()
        
        # Syncing session state
        session["game"] = game.__dict__
        
        if game.is_over():
            win = game.lives > 0
            update_score_and_level(session["user_id"], game.score, win)
            
            # Game screen par bhi level update dikhe
            new_stats = get_user_stats(session["user_id"])
            game.level = new_stats[2]
            session["game"] = game.__dict__
    
    return render_template("game.html", game=game)

# --- ADMIN FEATURES (Virat Power) ---

@app.route("/admin/panel")
def admin_panel():
    if "user_id" not in session or session.get("username", "").lower() != "virat":
        return "Unauthorized! Admin access only."
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, total_score, level, coins, completions FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template("admin_panel.html", users=users)

@app.route("/admin/skip_level", methods=["POST"])
def skip_level():
    if "user_id" not in session or session.get("username", "").lower() != "virat":
        return "Unauthorized"
    
    update_score_and_level(session["user_id"], 50, True) 
    return redirect(url_for("dashboard"))

@app.route("/admin/applications")
def view_applications():
    if "user_id" not in session or session.get("username", "").lower() != "virat":
        return "Unauthorized! access denied."

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications ORDER BY id DESC")
    apps = cursor.fetchall()
    conn.close()

    return render_template("admin_applications.html", applications=apps)

@app.route("/admin/add_coins", methods=["POST"])
def add_coins():
    if "user_id" not in session or session.get("username", "").lower() != "virat":
        return "Unauthorized"
    
    # HTML se 'username' aa raha hai, isliye username ke basis par update karenge
    target_username = request.form.get("username")
    coins_to_add = request.form.get("coins", type=int)
    
    if target_username and coins_to_add:
        conn = sqlite3.connect("database.db")
        conn.execute("UPDATE users SET coins = coins + ? WHERE username = ?", (coins_to_add, target_username))
        conn.commit()
        conn.close()
    
    return redirect(url_for("view_applications"))

@app.route("/admin/skip_level_user", methods=["POST"])
def skip_level_user():
    if "user_id" not in session or session.get("username", "").lower() != "virat":
        return "Unauthorized"
    
    target_username = request.form.get("username")
    if target_username:
        conn = sqlite3.connect("database.db")
        conn.execute("UPDATE users SET level = level + 1 WHERE username = ?", (target_username,))
        conn.commit()
        conn.close()
    
    return redirect(url_for("view_applications"))

@app.route("/admin/delete_application", methods=["POST"])
def delete_application():
    if "user_id" not in session or session.get("username", "").lower() != "virat":
        return "Unauthorized"
    
    app_id = request.form.get("app_id")
    if app_id:
        conn = sqlite3.connect("database.db")
        conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        conn.commit()
        conn.close()
    
    return redirect(url_for("view_applications"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)