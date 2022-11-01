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
    #cn.execute('''CREATE TABLE questions(question_id INTEGER PRIMARY KEY,question varchar(255),correct varchar(255),fake_1 varchar(255),fake_2 varchar(255),fake_3 varchar(255),UNIQUE(question))''')

    # specify columns and insert values
    cn.executemany(
        'INSERT OR IGNORE INTO questions(question, correct, fake_1, fake_2,fake_3) VALUES(?,?,?,?,?)', question_lst)
    cn.execute('COMMIT')
    for row in cn.execute('SELECT * FROM questions'):
        print(row)
    cn.close()
    conn.close()


"""
def get_random_question(): # for the user interfce
    conn = db.connect('user_accuracy.db')
    cn = conn.cursor()

    for i in range(10):
        questions = cn.execute('select question from questions order by RANDOM() LIMIT 10;')
        for question in questions:
            
            print(question[0])
            user_answer = input() # waits for click on screen

            correct_choice = cn.execute('select correct from questions where question = (?);',question)


#print(get_random_question())

"""


def get_row_from_question():
    # this function pulls a random question
    conn = db.connect('quizapp.db')
    #conn.row_factory = lambda cursor, row: row[0]
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


@app.route('/formresponse', methods=['POST', 'GET'])
def formresponse():
    if request.method == 'POST':
        user_ans = request.form.get('flexRadioDefault')
    return user_ans


def check_answer(user_answer, desired_ans):
    # this function displays the question, answers,
    # and checks the user input
    # without using the question table

    ## question = get_row_from_question()

    # for field in question:
    """
        correct_choice = field[2]
        #print(get_question_text(question))
        field = [field[2],field[3],field[4],field[5]]

        random_answer_arrange = sample(field,4)
        print(random_answer_arrange)
        # desired_answer = position of A in field
        desired_pos = random_answer_arrange.index(field[2])
    """

    #answers, desired_pos= shuffle_answers(question)
    answers = {0: 'A',
               1: 'B',
               2: 'C',
               3: 'D'}

    user_answer = formresponse()
    if str(usr_answer) == str(answers[desired_ans]):
        return True
    else:
        return False
    """
    if desired_pos == 0:
        if user_answer == 'A':
            return True
        else:
            return False
    elif desired_pos == 1:
        if user_answer == 'B':
            return True
        else:
            return False

    elif desired_pos == 2:
        if user_answer == 'C':
            return True
        else:
            return False

    elif desired_pos == 3:
        if user_answer == 'D':
            return True
        else:
            return False
    
    
    """


# print(check_answer())
def get_question_text(question):
    for field in question:
        return field[1]  # returns the question text only


"""

def game_loop():
    

    
    
    # connect to the databse
    conn = db.connect('quizapp.db')
    conn.row_factory = lambda cursor, row: row[0]
    cn = conn.cursor()

    # get the user
    # get the user_id of the loged in user
    user_id = 3

    # initiate j
    j=0
     
    while j < 10:
        # get a (full) random question
        question = get_row_from_question()
        answers, desired_pos= shuffle_answers(question)
        
        #get question_id from question[0]
        for field in question:
            #print(field)
            question_id = field[0]
        question_text = get_question_text(question)
        print('This is the question from the new function', question_text)        
                
        
        #check if the question is in accuracy
        exists = cn.execute('''SELECT count(1) FROM accuracy
                WHERE user_id = (?) AND  question_id = (?)''',(user_id, question_id)).fetchall()
        
        
        
            #print("does not exist")
        #else: print("exists")

        
        #if it is NOT:
        if exists[0] == 0:
            print('new row')
            #print(question[0])
            #check the answer
            
            answer = check_answer(question,desired_pos)

            #if answer TRUE:
            if answer == True:
                values = [question_id, user_id, 1, 1]
                #add a row in accuracy +1, +1
                cn.execute('''INSERT INTO accuracy
                            (question_id, user_id, correct, seen)
                            VALUES (?,?,?,?)''', values)
                conn.commit()
                j += 1
            #if answer FALSE:
            else:
                values = [question_id, user_id, 0, 1]
                #add a row in accuracy +0, +1
                cn.execute('''INSERT INTO accuracy (question_id, user_id, correct, seen)
                            VALUES (?,?,?,?)''', values)
                conn.commit()
                j += 1
            

        #if it is in accuracy:
        
        else:
            for i in question:
                print(i)
            print('the row already exists')
            conn.row_factory = lambda cursor, row: row[0]
            correct = cn.execute('''select correct from accuracy
                            where question_id = (?) AND user_id = (?)''',
                               (question_id, user_id)).fetchall()
                        
            seen = cn.execute('''select seen from accuracy
                            where question_id = (?) AND user_id = (?)''',
                               (question_id, user_id)).fetchall()
            
            
            
            #check the accuracy using question_id, user_id
            accuracy = correct[0]/seen[0]
            
            #if accuracy < .6:
            if accuracy < .6 or seen[0] <= 20:
                
                #check answer
                if request.method == "POST":
                    user_answer = request.form['flexRadioDefault']
                    #answer = check_answer(question,desired_pos)
                    answer = check_answer(user_answer, answers[desired_pos])
                
                #if  answer TRUE:
                if answer:
                    new_correct = correct[0]+1
                    new_seen = seen[0]+1
                    
                    #update row in accuracy +1, +1
                    cn.execute('''UPDATE accuracy SET correct = (?), seen = (?)
                                Where question_id = (?) AND user_id = (?)''',
                               (new_correct, new_seen, question_id, user_id))
                    conn.commit()
                    j += 1
                    
                #if answer FALSE
                else:
                    new_correct = correct[0]
                    new_seen = seen[0]+1
                    #update row in accuracy +0, +1
                    cn.execute('''UPDATE accuracy SET correct = (?), seen = (?)
                                Where question_id = (?) AND user_id = (?)''',
                               (new_correct, new_seen, question_id, user_id))
                    conn.commit()
                    j += 1
                    
            #else: ((meaning accuracy >= .6)
            else:
                continue 
                
print(game_loop())"""


@app.teardown_appcontext
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


@app.route('/')
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
    new_correct, new_seen = correct[0], seen[0]+1

    # update row in accuracy +0, +1
    cn.execute('''UPDATE accuracy SET correct = (?), seen = (?)
                Where question_id = (?) AND user_id = (?)''',
               (new_correct, new_seen, question_id, user_id))
    conn.commit()
    cn.close()
    conn.close()


@app.route('/quiz', methods=["POST", "GET"])
def quiz():
    # connect to the databse
    conn = db.connect('quizapp.db')
    conn.row_factory = lambda cursor, row: row[0]
    cn = conn.cursor()

    # get the user
    # get the user_id of the loged in user
    user_id = 3

    # initiate j
    ### j = 0

    # while j < 10:

    # get a (full) random question
    question = get_row_from_question()
    answers, desired_pos = shuffle_answers(question)

    # get question_id from question[0]
    for field in question:
        # print(field)
        question_id = field[0]

    exists = cn.execute('''SELECT count(1) FROM accuracy
            WHERE user_id = (?) AND  question_id = (?)''', (user_id, question_id)).fetchall()

    if exists[0] == 0:

        question_text = get_question_text(question)
        answer = check_answer(question, desired_pos)

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


@app.route('/login', methods=["POST", "GET"])
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


@app.route('/register', methods=["POST", "GET"])
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


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
