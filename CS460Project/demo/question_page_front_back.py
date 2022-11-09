import sqlite3 as db
from random import sample
from multiprocessing import Value
from tabnanny import check
from flask import Flask, redirect, render_template, url_for, request, g, session
from database import connect_to_database, getDatabase
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


def read_txt(text):

    file1 = open(text, 'r')
    Lines = file1.readlines()

    question_lst = []
    for line in Lines:
        line = line.strip()
        question_lst.append(line.split(','))

    return question_lst


read_txt('answers.txt')


def make_q_table():
    question_lst = read_txt('answers.txt')

    conn = db.connect('quizapp.db')
    cn = conn.cursor()
    # cn.execute('''CREATE TABLE questions(question_id INTEGER PRIMARY KEY,question varchar(255),correct varchar(255),fake_1 varchar(255),fake_2 varchar(255),fake_3 varchar(255),UNIQUE(question))''')

    # specify columns and insert values
    cn.executemany(
        'INSERT OR IGNORE INTO questions(question, correct, fake_1, fake_2,fake_3) VALUES(?,?,?,?,?)', question_lst)
    cn.execute('COMMIT')
    for row in cn.execute('SELECT * FROM questions'):
        print(row)
    cn.close()
    conn.close()


def get_row_from_question():
    # this function pulls a random question
    conn = db.connect('quizapp.db')
    # conn.row_factory = lambda cursor, row: row[0]
    cn = conn.cursor()

    row = cn.execute('''select *
                            from questions
                            order by RANDOM() LIMIT 1;''').fetchall()

    # for r in row:

    return row
# print(get_row_from_question())


def shuffle_answers(question):

    for field in question:

        correct_choice = field[2]
        # print(get_question_text(question))
        field = [field[2], field[3], field[4], field[5]]

        random_answer_arrange = sample(field, 4)
        print('fields', random_answer_arrange)
        # desired_answer = position of A in field
        desired_pos = random_answer_arrange.index(field[0])
        print('a', random_answer_arrange,
              'this is the deisred position', desired_pos)

    return random_answer_arrange, desired_pos


@ app.route('/youranswercorrect', methods=["POST", "GET"])
def youranswercorrect():
    if "count" in session:
        count = session["count"]
    if request.method == "POST":
        if request.form['submit_button'] == 'Submit':
            count += 1
            return redirect(url_for('displayquestion'))


@ app.route('/youranswerincorrect', methods=["POST", "GET"])
def youranswerincorrect():
    if "count" in session:
        count = session["count"]
    if request.method == "POST":
        if request.form['submit_button'] == 'Submit':
            count += 1
            return redirect(url_for('displayquestion'))


def check_answer(user_answer, desired_pos, question_id, user_id, correct, seen):

    # answers, desired_pos= shuffle_answers(question)
    answers = {0: 'A',
               1: 'B',
               2: 'C',
               3: 'D'}

    # user_answer = formresponse()
    if str(user_answer) == str(answers[desired_pos]):
        # score = session['score']
        # score += 1
        update_exists_correct(correct, seen, question_id, user_id)
        # return youranswercorrect()
        return render_template("correctresponse.html")
    else:
        update_exists_wrong(correct, seen, question_id, user_id)
        return render_template("incorrectresponse.html")


# print(check_answer())
def get_question_text(question):
    for field in question:
        return field[1]  # returns the question text only


@ app.teardown_appcontext
def close_database(error):
    if hasattr(g, 'quizapp_db'):
        g.quizapp_db.close()


def get_current_user():
    user_result = None
    if 'user' in session:
        user = session['user']
        db = getDatabase()
        user_cursor = db.execute("select * from users where name = ?", [user])
        user_result = user_cursor.fetchone()
    return user_result


@ app.route('/')
def index():
    user = get_current_user()
    return render_template("home.html", user=user)


def update_exists_correct(correct, seen, question_id, user_id):
    conn = db.connect('quizapp.db')
    conn.row_factory = lambda cursor, row: row[0]
    cn = conn.cursor()
    new_correct, new_seen = correct+1, seen+1

    # update row in accuracy +1, +1
    cn.execute('''UPDATE accuracy SET correct = (?), seen = (?)
                Where question_id = (?) AND user_id = (?)''',
               (new_correct, new_seen, question_id, user_id))
    conn.commit()
    cn.close()
    conn.close()


def update_exists_wrong(correct, seen, question_id, user_id):
    conn = db.connect('quizapp.db')
    conn.row_factory = lambda cursor, row: row[0]
    cn = conn.cursor()
    new_correct, new_seen = correct, seen+1

    # update row in accuracy +0, +1
    cn.execute('''UPDATE accuracy SET correct = (?), seen = (?)
                Where question_id = (?) AND user_id = (?)''',
               (new_correct, new_seen, question_id, user_id))
    conn.commit()
    cn.close()
    conn.close()


"""
def formresponse():
    if request.method == 'POST':
        user_ans = request.form.get('flexRadioDefault')
    return user_ans
"""


@ app.route('/postanswer', methods=["POST", "GET"])
def postanswer():
    if "desired_pos" in session:
        desired_pos = session["desired_pos"]
        if request.method == "POST":
            answer = request.form['flexRadioDefault']

    if "question_id" in session:
        question_id = session["question_id"]

    if "user_id" in session:
        user_id = session["user_id"]

    if "correct" in session:
        correct = session["correct"]

    if "seen" in session:
        seen = session["seen"]

    # if check_answer:
        # return render_template(correct_answer.html)
    # , youranswer()
    return check_answer(answer, desired_pos, question_id, user_id, correct, seen)


@ app.route('/displayquestion', methods=["POST", "GET"])
def displayquestion():  # makes the form and a new function receives the form results
    # check the accuracy databse before displaying the question
    user = get_current_user()
    count = 0
    i = 0
    while i < 10:

        i += 1
        user = get_current_user()
        conn = db.connect('quizapp.db')
        conn.row_factory = lambda cursor, row: row[0]
        cn = conn.cursor()
        question = get_row_from_question()

        user_id = 3
        question_id = question[0][0]
        # for field in question:
        # print(field)
        # question_id = field[0]

        # question_id = question[0][0]
        # connects to the accuracy table
        exists = cn.execute('''SELECT count(1) FROM accuracy
                            WHERE user_id = (?) AND  question_id = (?)''', (user_id, question_id)).fetchall()

        # get a (full) random question

        answers, desired_pos = shuffle_answers(question)

        # checks the accuracy to decide whether to show the question
        correct = cn.execute('''select correct from accuracy
                            where question_id = (?) AND user_id = (?)''',
                             (question_id, user_id)).fetchall()

        seen = cn.execute('''select seen from accuracy
                        where question_id = (?) AND user_id = (?)''',
                          (question_id, user_id)).fetchall()

        # score = 0
        # session['score'] = score

        accuracy = correct[0]/seen[0]
        answer_a = answers[0]
        answer_b = answers[1]
        answer_c = answers[2]
        answer_d = answers[3]

        # correct = answers[desired_pos]

        # desired_pos session
        session['desired_pos'] = desired_pos

        # question_id session
        session['question_id'] = question_id

        # user_id session
        session['user_id'] = user_id

        # correct session
        session['correct'] = correct[0]

        # seen session
        session['seen'] = seen[0]

        # count session
        session['count'] = count

        # make a new column called active in the question database named current,
        # have it empty or null or 0,
        # update the column whenever a question is asked with a value of 1
        if accuracy < .6:
            i += 1
            return render_template("displayquestion.html",
                                   exists=exists, question=question,
                                   answers=answers, desired_pos=desired_pos,
                                   accuracy=accuracy, answer_a=answer_a,
                                   answer_b=answer_b, answer_c=answer_c,
                                   answer_d=answer_d, question_id=question_id,
                                   user=user, count=count)
        else:
            continue
    # after question 10
    return render_template("score.html")
    # Here we call the score template! 10 questions have been answered

    # only display the question if accuracy is <= .6 or if seen is < 4/5 ## done!

    # save the user answer ## done!

    # check the answer in a different function (?) by using session in postanswer
    # make a new page that shows whether the answer was correct


@ app.route('/quiz', methods=["POST", "GET"])
def quiz():

    # get the user
    # get the user_id of the loged in user
    user_id = 3

    # initiate j
    # j = 0

    # while j < 10:

    # get question_id from question[0]
    # for field in question:
    # print(field)
    #question_id = field[0]

    #question_id = question[0[0]]
    exists = cn.execute('''SELECT count(1) FROM accuracy
            WHERE user_id = (?) AND  question_id = (?)''', (user_id, question_id)).fetchall()

    if request.method == 'POST':
        user_answer = request.form.get('flexRadioDefault')

    # = formresponse()
    if exists[0] == 0:

        question_text = get_question_text(question)
        answer = check_answer(user_answer, desired_pos)

        if answer == True:
            values = [question_id, user_id, 1, 1]
            # add a row in accuracy +1, +1
            cn.execute('''INSERT INTO accuracy
                        (question_id, user_id, correct, seen)
                        VALUES (?,?,?,?)''', values)
            conn.commit()

        else:
            values = [question_id, user_id, 0, 1]
            # add a row in accuracy +0, +1
            cn.execute('''INSERT INTO accuracy (question_id, user_id, correct, seen)
                        VALUES (?,?,?,?)''', values)
            conn.commit()

    else:
        question_text = get_question_text(question)
        # get the vlaues of correct and seen
        conn.row_factory = lambda cursor, row: row[0]
        correct = cn.execute('''select correct from accuracy
                        where question_id = (?) AND user_id = (?)''',
                             (question_id, user_id)).fetchall()

        seen = cn.execute('''select seen from accuracy
                        where question_id = (?) AND user_id = (?)''',
                          (question_id, user_id)).fetchall()

        accuracy = correct[0]/seen[0]

        if accuracy < .6:  # or seen[0] <= 4:

            answer = check_answer(question, desired_pos)

            if answer == True:

                update_exists_correct(correct, seen, question_id, user_id)

            else:

                update_exists_wrong(correct, seen, question_id, user_id)

        # else: ((meaning accuracy >= .6)
        # else:
            # continue

    answer_a = answers[0]
    answer_b = answers[1]
    answer_c = answers[2]
    answer_d = answers[3]
    correct = answers[desired_pos]
    """
        if request.method == "POST":
            answer = request.form['flexRadioDefault']
            if answer == correct:
                return 'True'
            else:
                return 'False'
        """
    return render_template("quiz.html", question_text=question_text, answer_a=answer_a, answer_b=answer_b, answer_c=answer_c, answer_d=answer_d, correct=correct, question_id=question_id, desired_pos=desired_pos)


@ app.route('/login', methods=["POST", "GET"])
def login():
    user = get_current_user()
    error = None
    if request.method == "POST":
        db = getDatabase()
        name = request.form['name']
        password = request.form['password']
        fetchedperson_cursor = db.execute(
            "select * from users where name = ?", [name])
        personfromdatabase = fetchedperson_cursor.fetchone()

        if personfromdatabase:
            if check_password_hash(personfromdatabase['password'], password):
                session['user'] = personfromdatabase['name']
                return redirect(url_for('index'))
            else:
                error = "Username or password did not match. Try again."
               # return render_template('login.html', error = error)
        else:
            error = "Username or password did not match. Try again."
           # return redirect(url_for('login'))
    return render_template("login.html", user=user, error=error)


@ app.route('/register', methods=["POST", "GET"])
def register():
    user = get_current_user()
    error = None
    if request.method == "POST":
        db = getDatabase()
        name = request.form['name']
        password = request.form['password']

        user_fetcing_cursor = db.execute(
            "select * from users where name = ?", [name])
        existing_user = user_fetcing_cursor.fetchone()

        if existing_user:
            error = "Username already taken, Please choose another name"
            return render_template("register.html", error=error)

        hashed_password = generate_password_hash(password, method='sha256')

        db.execute("insert into users (name, password, player, admin) values (?,?,?,?)", [
                   name, hashed_password, '0', '0'])
        db.commit()
        session['user'] = name
        return redirect(url_for('index'))

    return render_template("register.html", user=user)


@ app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
