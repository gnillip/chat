# Imports
from flask import Flask, render_template, redirect, abort, session, request
from pathlib import Path
import os, hashlib, json, datetime


#Vars
app = Flask(__name__)
app.secret_key = os.urandom(24)
PATH = Path(__file__).resolve().parent
STATIC = PATH / "static"
CHATS = PATH / "chats"
USER_PATH = PATH / "USER.json"

# Funcs
def NOW() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def read(PATH:str, isJson:bool) -> dict | list:
    """
    Docstring for read

    :return: if isJson -> dict  |/|  else -> list
    :rtype: dict | list
    """
    if not os.path.exists(PATH):
        return {} if isJson else []

    with open(PATH, "r") as data:

        if isJson:
            return json.load(data)
        else:
            return data.read().split("\n")

def write(PATH:str, contents:dict|list, isJson:bool) -> None:
    """
    Docstring for write
    
    :param contents: if isJson -> dict |/| else list
    :type contents: dict | list
    """

    if isJson and not isinstance(contents, dict):
        raise TypeError("Expected dict when isJson=True")
    if not isJson and not isinstance(contents, list):
        raise TypeError("Expected list when isJson=False")

    with open(PATH, "w") as data:

        if isJson:
            json.dump(contents, data, indent=4)
        else:
            for item in contents:
                data.write(item+"\n")

def security(username:str) -> tuple:
    """
    Docstring for security
    
    :param isAdmin: should the user be an admin?
    :type isAdmin: bool
    :return: status_code, message
    :rtype: tuple
    """
    if not username:
        return (403, "Not Logged in")
    
    USER = read(str(USER_PATH), True)
    if username not in USER:
        return (403, "User doesn't exists")
    
    if USER[username]["locked"]:
        return (403, "is Locked")

    return (200, "OK")


# routes
@app.route("/")
def __index():
    username = session.get("username")
    if not username:
        return render_template("index.html")
    else:
        sec = security(username)
        if sec[0] != 200:
            abort(sec[0], sec[1])
        return redirect("/auswahl")

@app.post("/login")
def __login():
    USER = read(str(USER_PATH), True)
    username = request.form["username"]
    password = request.form["password"]

    if username not in USER:
        return redirect("/")
    
    if USER[username]["password"] == hashlib.sha512(password.encode()).hexdigest():
        if USER[username]["locked"]:
            abort(403, "Your Account is Locked!")

        session["username"] = username
        return redirect("/auswahl")
    else:
        return redirect("/")

@app.post("/register")
def __register():
    USER = read(str(USER_PATH), True)
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]

    if username in USER:
        abort(401, "This User already exists!")
    
    if "_-_" in username:
        abort(401, "The Username cannot have an '_-_'")
    
    for tempUser, values in USER.items():
        if email == values["email"]:
            abort(401, "This Email has already an Account linked to it!")
    
    USER[username] = {
        "password": hashlib.sha512(password.encode()).hexdigest(),
        "email": email,
        "locked": False
    }
    write(str(USER_PATH), USER, True)
    session["username"] = username
    return redirect("/auswahl")

@app.get("/logout")
def __logout():
    session.clear()
    return redirect("/")

@app.get("/auswahl")
def __auswahl():
    username = session.get("username")
    sec = security(username)
    if sec[0] != 200:
        abort(sec[0], sec[1])
    
    USER = read(str(USER_PATH), True)
    return render_template("auswahl.html", username=username, user=USER.keys())

@app.post("/chat")
def __chat():
    username = session.get("username")
    sec = security(username)
    if sec[0] != 200:
        abort(sec[0], sec[1])
    
    USER = read(str(USER_PATH), True)
    user = request.form["user"]

    CHAT_NAME =  [user, username]
    CHAT_NAME.sort()
    CHAT_NAME = "_-_".join(CHAT_NAME)
    CHAT_PATH = CHATS / CHAT_NAME

    CHAT = read(CHAT_PATH, True)
    return render_template("chat.html", username=username, chat=CHAT, name=CHAT_NAME)

@app.post("/chat/send")
def __chat_send():
    username = session.get("username")
    sec = security(username)
    if sec[0] != 200:
        abort(sec[0], sec[1])
    
    chat_name = request.form["chat"]
    message = request.form["message"]

    CHAT = read(str(CHATS / chat_name), True)
    CHAT[NOW()] = message
    write(str(CHATS / chat_name), CHAT, True)
    return redirect("/auswahl")

if __name__ == "__main__":
    app.run("127.0.0.1", 5000, False)