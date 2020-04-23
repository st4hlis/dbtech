from fastapi import FastAPI
import sqlite3
import json

connection = sqlite3.connect("movies.sqlite")
app  = FastAPI()

