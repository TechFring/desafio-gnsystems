import requests
import os
from app import app as application
from flask import request, render_template
from bs4 import BeautifulSoup

# helper
from app.helper.HTMLtoJSONParser import HTMLtoJSONParser


# routes
@application.route("/", methods=["POST"])
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
        html_to_json = HTMLtoJSONParser(False)
        json = html_to_json.to_json(str(html))

        return json, status
    except KeyError:
        status = 500
        message = {"mensagem": "é necessário passar uma URL no corpo da requisição"}
        return message, status
    except requests.exceptions.MissingSchema:
        status = 500
        message = {"mensagem": "URL inválida"}
        return message, status

@application.route("/", defaults={"path": ""})
@application.route("/<path:path>")
def all(path):
    return render_template("index.html")


if __name__ == "__main__":
    application.run(debug=True)
