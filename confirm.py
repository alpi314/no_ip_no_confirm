import re

import requests
from bs4 import BeautifulSoup


def extract_login_token(session):
    url = "https://www.noip.com/"
    r = session.get(url)
    if r.status_code == 200:
        print("ok")
        soup = BeautifulSoup(r.text, 'html.parser')
        token = soup.find('input', {'name': '_token'})['value']
        return token
    raise Exception("Could not extract login token")



def login(session, username, password):
    url = "https://www.noip.com/login"
    payload = {
        'username': username,
        'password': password,
        '_token': extract_login_token(session),
    }
    r = session.post(url, data=payload)
    if r.status_code == 200:
        print("logged in")
        return True
    raise Exception("Could not login")

if __name__ == "__main__":
    session = requests.Session()
    logged_ing = login(session, "", "")
    print(logged_ing)
    if logged_ing:
        r = session.get("https://my.noip.com/dynamic-dns")
        print(r.status_code)
        soup = BeautifulSoup(r.text, 'html.parser')
        print(soup.find_all('a', attrs={'data-original-title': True}))