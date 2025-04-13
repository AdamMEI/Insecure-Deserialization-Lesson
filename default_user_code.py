import pickle
import cookie_manager
import base64

class Comment:
    def __init__(self, text, username):
        self.text = text
        self.username = username

# Save comments (serialize)
def save_comments(comments):
    encoded_comments = base64.b64encode(pickle.dumps(comments)).decode("utf-8")
    cookie_manager.save_cookie("comments", encoded_comments)

# Load comments (deserialize)
def load_comments():
    cookie = cookie_manager.get_cookie("comments")
    decoded_cookie = base64.b64decode(cookie)
    if decoded_cookie:
        return pickle.loads(decoded_cookie)
    return []