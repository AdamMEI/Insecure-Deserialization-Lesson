import pickle
import cookie_manager
import base64

class Comment:
    def __init__(self, text, username):
        self.text = text
        self.username = username

# Save comments (serialize)
def save_comments(comments):
    cookie_manager.save_cookie("comments", base64.b64encode(pickle.dumps(comments)).decode("utf-8"))

# Load comments (deserialize)
def load_comments():
    cookie = base64.b64decode(cookie_manager.get_cookie("comments"))
    if cookie:
        return pickle.loads(cookie)
    return []

#print(base64.b64encode(pickle.dumps([Comment("I liked it!", "Sharon"), Comment("I thought the ending was bad.", "Jeff")])).decode("utf-8"))