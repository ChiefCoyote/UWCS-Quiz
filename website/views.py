from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from flask_socketio import join_room, leave_room, send, SocketIO
from . import db, socketio
from random import choice
from .models import *

views = Blueprint('views', __name__)

@views.route('/')
def home():
    session.clear()
    if current_user.is_authenticated and current_user.isVerified:
        return redirect(url_for("views.quizzes"))
    return render_template("home.html")


#
#   Routes for participants
#
@views.route('/join', methods=['POST', 'GET'])
def join():
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")

        if not name:
            flash('Please enter a name', category="danger")
            return render_template("participant/join.html", code = code, name = name)
        
        if len(name) < 3:
            flash('Your name must be at least 3 characters long!', category="danger")
            return render_template("participant/join.html", code = code, name = name)
        
        if not code:
            flash('Please enter a session code', category="danger")
            return render_template("participant/join.html", code = code, name = name)
        
        sessionID = QuizSession.query.filter_by(joinCode = code).first()
        if not sessionID:
            flash('Session code does not exist', category="danger")
            return render_template("participant/join.html", code = code, name = name)
        
        repeatName = Team.query.filter_by(sessionID = code, teamName = name).first()
        if repeatName:
            flash('A team already has this name', category="danger")
            return render_template("participant/join.html", code = code, name = name)
        
        newTeam = Team(teamName = name, sessionID = code)
        db.session.add(newTeam)
        db.session.commit()

        session["code"] = code
        session["name"] = name
        session["teamID"] = newTeam.teamID
        session["questionID"] = ""

        return redirect(url_for("views.answer"))

    return render_template("participant/join.html")

@views.route('/answer', methods = ['GET', 'POST'])
def answer():
    code = session.get("code")
    name = session.get("name")
    teamID = session.get("teamID")
    questionID = session.get("questionID")
    sessionID = QuizSession.query.filter_by(joinCode = code).first()

    if code is None or name is None or teamID is None or sessionID is None:
        return redirect(url_for("views.join"))
    
    if request.method == "POST":
        answer = request.form.get("answer")
        previousAnswer = TeamAnswer.query.filter_by(teamID = teamID, questionID = questionID).first()
        if previousAnswer:
            previousAnswer.answer = answer
            db.session.commit()
        else:
            teamAnswer = TeamAnswer(teamID = teamID, questionID = questionID, answer = answer)
            db.session.add(teamAnswer)
            db.session.commit()
    

    return render_template("participant/answer.html", code = code)



#
#   Route for markers
#
@views.route('/marker', methods=['POST', 'GET'])
def marker():

    if request.method == "POST":
        code = request.form.get("code")
        
        if not code:
            flash('Please enter a session code', category="danger")
            return render_template("participant/marker.html", code = code)
        
        sessionID = QuizSession.query.filter_by(joinCode = code).first()
        if not sessionID:
            flash('Session code does not exist', category="danger")
            return render_template("participant/marker.html", code = code)

        session["code"] = code
        ##ADD MARKER TO DB

    return render_template("participant/marker.html")


@views.route('/mark')
def mark():
    return render_template("participant/mark.html")



#
#   Routes for quiz hosts
#
@views.route('/quizzes')
def quizzes():
    if not (current_user.is_authenticated and current_user.isVerified):
        return redirect(url_for("auth.login"))
    

    return render_template("host/quizzes.html")

@views.route('/host_wait')
def host_wait():
    if not (current_user.is_authenticated and current_user.isVerified):
        return redirect(url_for("auth.login"))
    

    return render_template("host/host_wait.html")

@views.route('/question')
def question():
    if not (current_user.is_authenticated and current_user.isVerified):
        return redirect(url_for("auth.login"))
    
    
    return render_template("host/question.html")

@views.route('/final_score')
def final_score():
    if not (current_user.is_authenticated and current_user.isVerified):
        return redirect(url_for("auth.login"))
    
    
    return render_template("host/final_score.html")


@socketio.on("connectPlayer")
def connectPlayer():
    room = session.get("code")
    name = session.get("name")
    if not room or not name:
        return
    sessionID = QuizSession.query.filter_by(joinCode = room).first()
    if not sessionID:
        leave_room(room)
        return
    
    join_room(room)
    socketio.emit("logPlayer",{"name": name}, to=room)
    #join_room("ABCD")
    #foo = "steven"
    #bar = "ABCD"
    #print(f"{foo} joined room {bar}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("code")
    name = session.get("name")
    socketio.emit("disconnectPlayer", {"name": name}, to=room)
    leave_room(room)

@socketio.on("submitAnswer")
def submitAnswer():
    room = session.get("code")
    teamID = session.get("teamID")
    questionID = session.get("questionID")
    
    socketio.emit("submitAnswer", {"teamID": teamID, "questionID": questionID}, to=room)

@socketio.on("ping")
def ping(data):
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(joinCode = room).first()
    if not sessionID:
        return
    
    questionID = data["questionID"]
    socketio.emit("ping", {"questionID": questionID}, to=room)

@socketio.on("nextQuestion")
def nextQuestion(data):
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(joinCode = room).first()
    if not sessionID:
        return
    
    newQuestionID = data["newQuestionID"]
    socketio.emit("nextQuestion", {"newQuestionID": newQuestionID}, to=room)

@socketio.on("updateQuestionID")
def updateQuestionID(data):
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(joinCode = room).first()
    if not sessionID:
        return
    
    newQuestionID = data["newQuestionID"]
    session["questionID"] = newQuestionID