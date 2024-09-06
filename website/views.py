from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from flask_socketio import join_room, leave_room, send, SocketIO
from . import db, socketio
from random import choice
from .models import *
from collections import defaultdict
import string

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
        
        sessionID = QuizSession.query.filter_by(sessionID = code).first()
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
    sessionID = QuizSession.query.filter_by(sessionID = code).first()

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
        
        sessionID = QuizSession.query.filter_by(sessionID = code).first()
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
@views.route('/quizzes', methods=["POST", "GET"])
def quizzes():
    if not (current_user.is_authenticated and current_user.isVerified):
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        quizID = request.form.get("selectedQuizID")
        if not quizID:
            return redirect(url_for("views.quizzes"))
        else:
            session["quizID"] = quizID
            return redirect(url_for("views.question"))
            
    
    playerQuizzes = db.session.query(Quiz, UserQuiz).join(UserQuiz, UserQuiz.quizID == Quiz.id).filter(UserQuiz.userID == current_user.id).all()
    

    return render_template("host/quizzes.html", playerQuizzes = playerQuizzes)

@views.route('/question')
def question():
    if not (current_user.is_authenticated and current_user.isVerified):
        return redirect(url_for("auth.login"))
    
    quizID = session.get("quizID")
    if not quizID:
        return redirect(url_for("views.quizzes"))
    
    code = session.get("code")
    if not code:
        quizQuestions = db.session.query(Quiz, Round, Question, QuizRound, RoundQuestion
                                        ).join(QuizRound, QuizRound.quizID == Quiz.id
                                            ).join(Round, Round.id == QuizRound.roundID
                                                ).join(RoundQuestion, RoundQuestion.roundID == Round.id
                                                    ).join(Question, Question.id == RoundQuestion.questionID).filter(Quiz.id == quizID).all()
        
        roundToQuestions = defaultdict(list)
        roundToNames = defaultdict(list)
        
        for quiz, round, question, quizround, roundquestion in quizQuestions:
            roundID = round.id
            roundName = round.name
            questionID = question.id
            roundToQuestions[roundID].append(questionID)
            roundToNames[roundID] = roundName

        questionIDList = list(roundToQuestions.values())
        roundNamesList = list(roundToNames.values())

        session["QuestionIDs"] = questionIDList
        session["RoundNames"] = roundNamesList

        newSession = QuizSession(quizID = quizID)
        db.session.add(newSession)
        db.session.commit()

        code = newSession.sessionID
        session["code"] = code
    
    
    return render_template("host/question.html", code = code)

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
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        leave_room(room)
        return
    
    join_room(room)
    socketio.emit("logPlayer",{"name": name}, to=room)

@socketio.on("connectHost")
def connectHost():
    room = session.get("code")
    if not room:
        return
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        leave_room(room)
        return
    
    join_room(room)
    

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
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    questionID = data["questionID"]
    socketio.emit("ping", {"questionID": questionID}, to=room)

@socketio.on("nextQuestion")
def nextQuestion(data):
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    newQuestionID = data["newQuestionID"]
    socketio.emit("nextQuestion", {"newQuestionID": newQuestionID}, to=room)

@socketio.on("updateQuestionID")
def updateQuestionID(data):
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    newQuestionID = data["newQuestionID"]
    session["questionID"] = newQuestionID

