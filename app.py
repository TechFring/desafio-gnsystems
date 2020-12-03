import requests
import os
from flask import Flask, request
from bs4 import BeautifulSoup

# helper
from app.helper.HTMLtoJSONParser import HTMLtoJSONParser


app = Flask(__name__)

# routes
@app.route("/", methods=["POST"])
def main():
    try:
        body = request.get_json()
        status = 200
        url = body["url"]

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        html = soup.find("html")
        json = HTMLtoJSONParser.to_json(str(html))

        return json, status
    except KeyError:
        status = 500
        message = {"mensagem": "é necessário passar uma URL no corpo da requisição"}
        return message, status
    except requests.exceptions.MissingSchema:
        status = 500
        message = {"mensagem": "URL inválida"}
        return message, status


if __name__ == "__main__":
    app.run(threaded=True, port=5000)
