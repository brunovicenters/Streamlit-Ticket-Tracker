import streamlit_authenticator as stauth
import os, json
from dotenv import load_dotenv

load_dotenv()

users_list = json.loads(os.environ["USERS_JSON"])

# 2. build the dict expected by stauth
user_dict = {
    u["username"]: {"name": u["name"], "password": u["password"]}
    for u in users_list
}


credentials = {
    "credentials": {
        "usernames": user_dict
    },
    "cookie": {
        "name": "splitit_auth",
        "key": os.getenv("COOKIE_SECRET"),
        "expiry_days": 1
    }
}

authenticator = stauth.Authenticate(
    credentials["credentials"],
    credentials["cookie"]["name"],
    credentials["cookie"]["key"],
    credentials["cookie"]["expiry_days"],
)

