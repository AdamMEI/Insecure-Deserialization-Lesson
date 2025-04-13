import docker
import textwrap
import os
import pickle
import uuid
import tempfile
import json
import base64
import codecs

COMMENTS_FILE = "comments.pkl"
SEPARATOR = ";.,"

class Comment:
    def __init__(self, text, username):
        self.text = text
        self.username = username

declaration = """
import pickle
import base64
import os
import json
"""

load_end_code = """
    
comments_list = load_comments()
if not isinstance(comments_list, list):
    print("[]")
else:
    json_list = []
    for comment in comments_list:
        json_list.append({"text": comment.text, "username": comment.username})
    print(json.dumps(json_list))
"""

save_end_code = """

save_comments([comments])
"""

cookie_manager_code = """
cookieDict = [cookies]

def save_cookie(key, value):
    print(key + ";" + value)

def get_cookie(key):
    return cookieDict[key]
"""

# base 64 encoded comments
default_comments = "gASVggAAAAAAAABdlCiMCF9fbWFpbl9flIwHQ29tbWVudJSTlCmBlH2UKIwEdGV4dJSMC0kgbGlrZWQgaXQhlIwIdXNlcm5hbWWUjAZTaGFyb26UdWJoAymBlH2UKGgGjB1JIHRob3VnaHQgdGhlIGVuZGluZyB3YXMgYmFkLpRoCIwESmVmZpR1YmUu"

def load_comments(cookies, user_code):
    code = declaration + user_code + load_end_code

    cookies = dict(cookies)
    if "comments" not in cookies:
        cookies["comments"] = default_comments

    cookieDict = "{"
    for key, value in cookies.items():
        key = key.replace("\"", "\\\"")
        value = value.replace("\"", "\\\"")
        cookieDict += f'"{key}":"{value}",'
    cookieDict = cookieDict[:-1] # trim last comma
    cookieDict += "}"
    cookieDict = cookieDict.replace("\n", "")
    cookie_code = cookie_manager_code.replace("[cookies]", cookieDict)

    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "script.py")
        with open(file_path, "w") as f:
            f.write(code)

        file_path = os.path.join(tmp, "cookie_manager.py")
        with open(file_path, "w") as f:
            f.write(cookie_code)

        client = docker.from_env()

        container = client.containers.run(
            "python:3.9",
            f"python /app/script.py",
            volumes={tmp: {"bind": "/app", "mode": "ro"}},
            remove=True,
            stdout=True,
        )

    # returns a json string of a list of dicts
    return codecs.decode(container.decode(), 'unicode_escape')

def save_comments(response, user_code, comments):
    comments_str = "["
    for i in range(len(comments)):
        comment = comments[i]
        comments_str += f'Comment("{comment["text"]}", "{comment["username"]}")'
        if i != len(comments) - 1:
            comments_str += ", "
    comments_str += "]"
    code = declaration + user_code + save_end_code.replace("[comments]", comments_str)
    cookie_code = cookie_manager_code.replace("[cookies]", "{}")

    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "script.py")
        with open(file_path, "w") as f:
            f.write(code)

        file_path = os.path.join(tmp, "cookie_manager.py")
        with open(file_path, "w") as f:
            f.write(cookie_code)

        client = docker.from_env()

        container = client.containers.run(
            "python:3.9",
            f"python /app/script.py",
            volumes={tmp: {"bind": "/app", "mode": "ro"}},
            remove=True,
            stdout=True,
        )
    output = container.decode()
    key, value = output.split(";", 1)
    print(output)
    response.set_cookie(key, value)