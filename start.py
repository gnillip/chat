import hashlib, json, os

USER = {
    "root": {
        "password": hashlib.sha512(b"chatRoot").hexdigest(),
        "email": None,
        "locked": False
    }
}

with open("./USER.json", "w") as UserData:
    json.dump(USER, UserData, indent=4)

if os.path.exists("./chats"):
    for element in os.listdir("./chats"):
        os.remove("./chats/"+element)
else:
    os.mkdir("./chats")