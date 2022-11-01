import sqlite3
from flask import g


def connect_to_database():

    sql = sqlite3.connect(
        "/Users/toniatonia/Desktop/School/Classes/CS /Year 4/CS 460/Int-student-quiz-main/CS460Project/demo/quizapp.db")
    sql.row_factory = sqlite3.Row
    return sql


def getDatabase():
    if not hasattr(g, "quizapp_db"):
        g.quizapp_db = connect_to_database()
    return g.quizapp_db
