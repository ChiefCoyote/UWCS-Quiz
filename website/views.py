from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/join')
def join():
    return render_template("join.html")

@views.route('/participant_wait')
def participant_wait():
    return render_template("participant_wait.html")

@views.route('/answer')
def answer():
    return render_template("answer.html")

@views.route('/quizzes')
def quizzes():
    return render_template("quizzes.html")

@views.route('/host_wait')
def host_wait():
    return render_template("host_wait.html")

@views.route('/question')
def question():
    return render_template("question.html")

@views.route('/mark')
def mark():
    return render_template("mark.html")

@views.route('/final_score')
def final_score():
    return render_template("final_score.html")
