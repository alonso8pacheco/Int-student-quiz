import sqlite3 as db
from random import sample

def read_txt(text):
    
    file1 = open(text,'r')
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
    cn.executemany('INSERT OR IGNORE INTO questions(question, correct, fake_1, fake_2,fake_3) VALUES(?,?,?,?,?)', question_lst)
    cn.execute('COMMIT')
    for row in cn.execute('SELECT * FROM questions'):
        print(row)
    cn.close()
    conn.close()
make_q_table()

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

    
    #for r in row:
    print('row',row)
    return row
#print(get_row_from_question())
      
    
  

#print(get_row_from_question())

def check_answer(question):
    # this function displays the question, answers,
    # and checks the user input
    # without using the question table
    
    ## question = get_row_from_question()
    
    for field in question:
        
        correct_choice = field[2]
        print(field[1])
        field = [field[2],field[3],field[4],field[5]]
        
        random_answer_arrange = sample(field,4)
        print(random_answer_arrange)
        # desired_answer = position of A in field
        desired_pos = random_answer_arrange.index(' A')

        user_answer = input().strip()

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
        
        
        
        
        

#print(check_answer())

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
        
        #get question_id from question[0]
        for field in question:
            #print(field)
            question_id = field[0]
        
            
        
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
            
            answer = check_answer(question)

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
            if accuracy < .6 or seen[0] <= 4:
                
                #check answer
                answer = check_answer(question)
                
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
                
print(game_loop())
