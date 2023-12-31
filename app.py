from flask import Flask, render_template, session, redirect
from flask_bs4 import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_moment import Moment
from datetime import datetime
import json
import requests

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'bnhj^&*(IUGCH(*YT9uyhghji(*&YHJ'
moment = Moment(app)
date = datetime.now()

class LoginForm(FlaskForm):
    """
    Formularz logowania
    """
    userLogin = StringField('Nazwa użytkownika:', validators=[DataRequired()])
    userPass = PasswordField('Hasło:', validators=[DataRequired()])
    submit = SubmitField('Zaloguj')

class Subject(FlaskForm):
    """formularz dodawania przedmiotu"""
    subject = StringField('Nazwa przedmiotu:', validators=[DataRequired()])
    submit = SubmitField('Dodaj')

def countAverage(subjectValue, termValue):
    """funkcja obliczająca średnie ocen"""
    with open('data/grades.json') as gradesFile:
        grades = json.load(gradesFile)
        gradesFile.close()
    sumGrades = 0
    lenght = 0
    if subjectValue == "" and termValue == "":
        for subject, terms in grades.items():
            for term, categories in terms.items():
                for category, grades in categories.items():
                    if category == 'answer' or category == 'quiz' or category == 'test':
                        for grade in grades:
                            sumGrades += grade
                            lenght += 1
    else:
        for subject, terms in grades.items():
            if subject == subjectValue:
                for term, categories in terms.items():
                    if term == termValue:
                        for category, grades in categories.items():
                            if category == 'answer' or category == 'quiz' or category == 'test':
                                for grade in grades:
                                    sumGrades += grade
                                    lenght += 1
    if lenght != 0:
        return round(sumGrades / lenght, 2)

totalAverage = {}
def yearlyAverage(subjectValue, termValue):
    with open('data/grades.json', encoding='utf-8') as gradesFile:
        grades = json.load(gradesFile)
        gradesFile.close()
    sumGrades = 0
    lenght = 0
    if termValue == '':
        for subject, terms in grades.items():
            if subject == subjectValue:
                for term, categories in terms.items():
                    for category, grades in categories.items():
                        if category == 'answer' or category == 'quiz' or category == 'test':
                            for grade in grades:
                                sumGrades += grade
                                lenght += 1
                                totalAverage[subject] = round(sumGrades / lenght, 2)
    if lenght != 0:
        return round(sumGrades / lenght, 2)


@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/logIn', methods=['POST', 'GET'])
def logIn():
    login = LoginForm()
    with open('data/users.json') as usersFile:
        users = json.load(usersFile)
        usersFile.close()
    if login.validate_on_submit():
        userLogin = login.userLogin.data
        userPass = login.userPass.data
        if userLogin == users['userLogin'] and userPass == users['userPass']:
            session['userLogin'] = userLogin
            session['firstName'] = users['firstName']
            return redirect('dashboard')
    return render_template('login.html', title='Logowanie', login=login)

@app.route('/logOut')
def logOut():
    session.pop('userLogin')
    return redirect('logIn')

@app.route('/dashboard')
def dashboard():
    with open('data/grades.json') as gradesFile:
        grades = json.load(gradesFile)
        gradesFile.close()
    weatherSource = requests.get('https://danepubliczne.imgw.pl/api/data/synop/station/krakow')
    weather = json.load(weatherSource.content)
    return render_template('dashboard.html', title='Dashboard', userLogin=session.get('userLogin'), firstName=session.get('firstName'), date=date, grades=grades, countAverage=countAverage, yearlyAverage=yearlyAverage, weather=weather)

@app.route('/addSubject', methods=['POST', 'GET'])
def addSubject():
    addSubject = Subject()
    if addSubject.validate_on_submit():
        with open('data/grades.json', encoding='utf-8') as gradesFile:
            grades = json.load(gradesFile)
            gradesFile.close()
            subject = addSubject.subject.data
            grades[subject] = {
                'term1': {'answer': [], 'quiz': [], 'test': [], 'interim': 0},
                'term2': {'answer': [], 'quiz': [], 'test': [], 'interim': 0, 'yearly': 0}
            }
        with open('data/grades.json', 'w', encoding='utf-8') as gradesFile:
            json.dump(grades, gradesFile)
            gradesFile.close()
            return redirect('dashboard')
    return render_template('add-subject.html', title='Dodaj przedmiot', userLogin=session.get('userLogin'), firstName=session.get('firstName'), date=date, addSubject=addSubject)

@app.errorhandler(404)
def pageNotFound(e):
    return render_template('404.html', title='Nie ma takiej strony', userLogin=session.get('userLogin'), firstName=session.get('firstName')), 404

@app.errorhandler(500)
def serverError(e):
    return render_template('500.html', title='Wewnętrzny błąd serwera', userLogin=session.get('userLogin'), firstName=session.get('firstName')), 500


if __name__ == '__main__':
    app.run(debug=True)