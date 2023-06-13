from flask import Flask, render_template, request
from flask_sqlalchemy import sqlalchemy
from sqlalchemy import create_engine

app = Flask(__name__)

engine = create_engine("postgresql+psycopg2://root:Qwerty123@localhost/VK")