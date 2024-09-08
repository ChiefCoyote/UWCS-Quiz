from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from flask_socketio import join_room, leave_room, send, SocketIO
from . import db, socketio
from random import choice
from .models import *
from collections import defaultdict
import string, time

views = Blueprint('views', __name__)

@views.route('/')
def home():
    name = session.get("name")
    code = session.get("code")
    markID = session.get("markID")
    if name and code:
        db.session.query(Team).filter(Team.sessionID == code, Team.teamName == name).delete()
        db.session.commit()

    if markID and code:
        db.session.query(Marker).filter(Marker.sessionID == code, Marker.markerID == markID).delete()
        db.session.commit()

    session.clear()
    if current_user.is_authenticated and current_user.isVerified:
        return redirect(url_for("views.quizzes"))
    return render_template("home.html")


#
#   Routes for participants
#
@views.route('/join', methods=['POST', 'GET'])
def join():
    name = session.get("name")
    code = session.get("code")
    markID = session.get("markID")
    if name and code:
        db.session.query(Team).filter(Team.sessionID == code, Team.teamName == name).delete()
        db.session.commit()

    if markID and code:
        db.session.query(Marker).filter(Marker.sessionID == code, Marker.markerID == markID).delete()
        db.session.commit()


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
    started = False
    sessionID = QuizSession.query.filter_by(sessionID = code).first()

    if code is None or name is None or teamID is None or sessionID is None:
        return redirect(url_for("views.join"))
    
    if request.method == "POST":
        started = True
        answer = request.form.get("answer")
        previousAnswer = TeamAnswer.query.filter_by(teamID = teamID, questionID = questionID).first()
        if previousAnswer:
            previousAnswer.answer = answer
            db.session.commit()
        else:
            teamAnswer = TeamAnswer(teamID = teamID, questionID = questionID, answer = answer)
            db.session.add(teamAnswer)
            db.session.commit()
    

    return render_template("participant/answer.html", code = code, started = started)



#
#   Route for markers
#
@views.route('/marker', methods=['POST', 'GET'])
def marker():
    name = session.get("name")
    code = session.get("code")
    markID = session.get("markID")
    if name and code:
        db.session.query(Team).filter(Team.sessionID == code, Team.teamName == name).delete()
        db.session.commit()

    if markID and code:
        db.session.query(Marker).filter(Marker.sessionID == code, Marker.markerID == markID).delete()
        db.session.commit()

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
        print("mewos")
        return redirect(url_for("views.mark"))

    return render_template("participant/marker.html")





@views.route('/mark')
def mark():
    code = session.get("code")

    if code is None:
        return redirect(url_for("views.marker"))
    
    



    return render_template("participant/mark.html")



#
#   Routes for quiz hosts
#
@views.route('/quizzes', methods=["POST", "GET"])
def quizzes():
    if not (current_user.is_authenticated and current_user.isVerified):
        return redirect(url_for("auth.login"))
    
    session["code"] = ""
    userID = current_user.id
    inProgress = db.session.query(QuizSession).filter(QuizSession.userID == userID).first()

    if inProgress:
        db.session.query(QuizSession).filter(QuizSession.userID == userID).delete()
        db.session.commit()

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
        roundToMedia = defaultdict(list)
        
        for quiz, round, question, quizround, roundquestion in quizQuestions:
            roundID = round.id
            roundName = round.name
            roundMedia = round.media
            questionID = question.id
            roundToQuestions[roundID].append(questionID)
            roundToNames[roundID] = roundName
            roundToMedia[roundID] = roundMedia

        questionIDList = list(roundToQuestions.values())
        roundNamesList = list(roundToNames.values())
        roundMediaList = list(roundToMedia.values())

        session["QuestionIDs"] = questionIDList
        session["AnswerIDs"] = []
        session["AnswerMedia"] = ""
        session["RoundNames"] = roundNamesList
        session["RoundAnswers"] = ""
        session["RoundMedia"] = roundMediaList

        newSession = QuizSession(userID = current_user.id, quizID = quizID)
        db.session.add(newSession)
        db.session.commit()

        code = newSession.sessionID
        session["code"] = code
    
    
    return render_template("host/question.html", code = code)

@views.route('/final_score')
def final_score():
    if not (current_user.is_authenticated and current_user.isVerified):
        return redirect(url_for("auth.login"))
    
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    while True:
        answers = db.session.query(Team, TeamAnswer).join(TeamAnswer, Team.teamID == TeamAnswer.teamID).filter(Team.sessionID == room).first()
        marking = db.session.query(Marker).filter(Marker.sessionID == room, Marker.active == True).first()

        if(answers or marking):
            time.sleep(5)
        else:
            break

    
    scores = db.session.query(Team.teamName, Team.score).filter(Team.sessionID == room).order_by(Team.score).all()

    ##Reset Everything
    db.session.query(QuizSession).filter_by(QuizSession.sessionID == room).delete()
    db.session.commit()
    session.clear()

    
    return render_template("host/final_score.html", scores = scores)


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

@socketio.on("connectMarker")
def connectMarker(data):
    code = session.get("code")
    if not code:
        return
    
    sessionID = QuizSession.query.filter_by(sessionID = code).first()
    if not sessionID:
        leave_room(code)
        return
    
    join_room(code)
    
    ##ADD MARKER TO 
    marker = Marker(sessionID = code, socketID = data["socketID"])
    print(data["socketID"])
    db.session.add(marker)
    db.session.commit()

    session["markID"] = marker.markerID

    session["markingData"] = []
    #{"teamID": teamID, "questionID": questionID, "answer": answer}
    

@socketio.on("disconnect")
def disconnect():
    room = session.get("code")
    name = session.get("name")
    markID = session.get("markID")
    if name:
        socketio.emit("disconnectPlayer", {"name": name}, to=room)

    if markID:
        db.session.query(Marker).filter(Marker.sessionID == room, Marker.markID == markID).delete()
        db.session.commit()

        markingData = session.get("markingData")

        for question in markingData:
            print("skibidi")
            reAddAnswer = TeamAnswer(teamID = question.teamID, questionID = question.questionID, answer = question.answer)
            db.session.add(reAddAnswer)
            db.session.commit()



    leave_room(room)

@socketio.on("submitAnswer")
def submitAnswer():
    room = session.get("code")
    teamID = session.get("teamID")
    
    socketio.emit("submitAnswer", {"teamID": teamID}, to=room)

@socketio.on("ping")
def ping():
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    questionID = session.get("AnswerIDs")[-1]
    socketio.emit("ping", {"questionID": questionID}, to=room)

@socketio.on("nextQuestion")
def nextQuestion():
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    questionIDs = session.get("QuestionIDs")
    answerIDs = session.get("AnswerIDs")

    markQuestions = db.session.query(TeamAnswer).filter_by(sessionID = room).all()
    ###########ADD QUESTIONS TO ALL THE MARKERS


    if(questionIDs[0] == []):
        questionIDs.pop(0)
        session["QuestionIDs"] = questionIDs
        roundAnswers = session.get("RoundAnswers")
        answerMedia = session.get("AnswerMedia")
        socketio.emit("endOfRound", {"roundAnswers": roundAnswers, "answerMedia": answerMedia}, to=room)
    else:
        questionID = questionIDs[0].pop(0)
        print(questionID)
        answerIDs.append(questionID)
        print(answerIDs)
        session["QuestionIDs"] = questionIDs
        session["AnswerIDs"] = answerIDs

        questionData = Question.query.filter_by(id = questionID).first()
        if questionData:
            if questionData.multChoice:
                questionDataConvert = {
                    'id': questionData.id,
                    'multChoice': questionData.multChoice,
                    'text': questionData.text,
                    'media': questionData.media,
                    'choices': questionData.get_data()
                }
            else:

                questionDataConvert = {
                    'id': questionData.id,
                    'multChoice': questionData.multChoice,
                    'text': questionData.text,
                    'media': questionData.media,
                    'choices': questionData.choices
                }
            socketio.emit("showNextQuestion", {"questionData": questionDataConvert}, to=room)
            socketio.emit("nextQuestion", {"newQuestionID": questionID}, to=room)
    

@socketio.on("nextAnswer")
def nextAnswer():
    print("Meow")
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return 
    
    answerIDs = session.get("AnswerIDs")
    print(answerIDs)
    if(answerIDs == []):
        socketio.emit("newRound", to=room)
    else:
        answerID = answerIDs.pop(0)
        session["AnswerIDs"] = answerIDs

        answerData = Question.query.filter_by(id = answerID).first()
        if answerData:
            if answerData.multChoice:
                answerDataConvert = {
                    'id': answerData.id,
                    'multChoice': answerData.multChoice,
                    'text': answerData.text,
                    'media': answerData.media,
                    'choices': answerData.get_data(),
                    'answer': answerData.answer
                }
            else:

                answerDataConvert = {
                    'id': answerData.id,
                    'multChoice': answerData.multChoice,
                    'text': answerData.text,
                    'media': answerData.media,
                    'choices': answerData.choices,
                    'answer': answerData.answer
                }
            socketio.emit("showNextAnswer", {"questionData": answerDataConvert}, to=room)



@socketio.on("updateQuestionID")
def updateQuestionID(data):
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    newQuestionID = data["newQuestionID"]
    session["questionID"] = newQuestionID

@socketio.on("begin")
def begin():
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    roundNames = session.get("RoundNames")
    if(roundNames == []):
        socketio.emit("endOfQuestions", to=room)
    else:
        roundName = roundNames.pop(0)
        session["RoundAnswers"] = roundName
        session["RoundNames"] = roundNames

        roundMedias = session.get("RoundMedia")
        roundMedia = roundMedias.pop(0)
        session["RoundMedia"] = roundMedias
        session["AnswerMedia"] = roundMedia

        print(roundName)

        socketio.emit("showRound", {"roundName" : roundName, "roundMedia": roundMedia}, to=room)


