from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from flask_socketio import join_room, leave_room, send, SocketIO
from . import db, socketio
from random import choice
from .models import *
from collections import defaultdict
import string, time, math

views = Blueprint('views', __name__)

@views.route('/favicon.ico')
def favicon():
    return redirect("/static/UWCSLOGO.svg")

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
        session["questionID"] = 0
        print("bumbarasclaat")

        return redirect(url_for("views.answer"))

    return render_template("participant/join.html")

@views.route('/answer', methods = ['GET', 'POST'])
def answer():
    code = session.get("code")
    name = session.get("name")
    teamID = session.get("teamID")
    started = False
    submittedAnswer = ""
    sessionID = QuizSession.query.filter_by(sessionID = code).first()

    teamQuestion = Team.query.filter(Team.teamID == teamID).first()
    if(teamQuestion):
        questionID = teamQuestion.questionID

    if code is None or name is None or teamID is None or sessionID is None:
        print("Youre slimy")
        return redirect(url_for("views.join"))
    
    if request.method == "POST":
        started = True
        answer = request.form.get("answer")
        submittedAnswer = answer
        previousAnswer = TeamAnswer.query.filter(TeamAnswer.teamID == teamID, TeamAnswer.questionID == questionID).first()
        if previousAnswer:
            previousAnswer.answer = answer
            db.session.commit()
        else:
            teamAnswer = TeamAnswer(teamID = teamID, questionID = questionID, answer = answer)
            db.session.add(teamAnswer)
            db.session.commit()
    

    return render_template("participant/answer.html", code = code, started = started, submittedAnswer = submittedAnswer)



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
        return redirect(url_for("views.mark"))

    return render_template("participant/marker.html")





@views.route('/mark')
def mark():
    code = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = code).first()

    if code is None or sessionID is None:
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
    
    socketio.emit("playerLeave")
    
    scores = db.session.query(Team.teamName, Team.score).filter(Team.sessionID == room).order_by(Team.score).all()

    ##Reset Everything
    db.session.query(QuizSession).filter(QuizSession.sessionID == room).delete()
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
    print("maybe?")
    if name:
        socketio.emit("disconnectPlayer", {"name": name}, to=room)

    if markID:
        db.session.query(Marker).filter(Marker.sessionID == room, Marker.markerID == markID).delete()
        db.session.commit()

        markingData = session.get("markingData")
        session["markingData"] = []

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
    temp = session.get("questionID")
    print(temp)
    socketio.emit("submitAnswer", {"teamID": teamID}, to=room)

@socketio.on("ping")
def ping():
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    answerIDs = session.get("AnswerIDs")
    if answerIDs != []:
        questionID = answerIDs[-1]
        socketio.emit("ping", {"questionID": questionID}, to=room)
    

@socketio.on("nextQuestion")
def nextQuestion():
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    questionIDs = session.get("QuestionIDs")
    answerIDs = session.get("AnswerIDs")

    markQuestions = db.session.query(TeamAnswer).join(Team, TeamAnswer.teamID == Team.teamID).filter(Team.sessionID == room).all()
    questionCount = len(markQuestions)
    questionList = []
    for question in markQuestions:
        markQuestionsConvert = {
                    'teamID': question.teamID,
                    'questionID': question.questionID,
                    'answer': question.answer
                }
        questionList.append(markQuestionsConvert)

    subquery = db.session.query(Team.teamID).filter(Team.sessionID == room).subquery()
    db.session.query(TeamAnswer).filter(TeamAnswer.teamID.in_(subquery)).delete()
    db.session.commit()

    markers = db.session.query(Marker).filter_by(sessionID = room).all()
    markerCount = len(markers)
    print(questionList)
    ###########ADD QUESTIONS TO ALL THE MARKERS
    for marker in markers:
        questionSubList = []
        for _ in range(math.ceil(questionCount / markerCount)):
            if(markQuestions[0]):
                questionSubList.append(questionList.pop(0))
        print(marker.socketID)
        socketio.emit("newMarking", questionSubList, to=marker.socketID)




    if(questionIDs[0] == []):
        questionIDs.pop(0)
        session["QuestionIDs"] = questionIDs
        roundAnswers = session.get("RoundAnswers")
        answerMedia = session.get("AnswerMedia")
        socketio.emit("endOfRound", {"roundAnswers": roundAnswers, "answerMedia": answerMedia}, to=room)
    else:
        questionID = questionIDs[0].pop(0)
        answerIDs.append(questionID)
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
            print(questionID)
            socketio.emit("nextQuestion", {"newQuestionID": questionID}, to=room)
    

@socketio.on("nextAnswer")
def nextAnswer():
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return 
    
    answerIDs = session.get("AnswerIDs")
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


@socketio.on("addNewMarking")
def addNewMarking(data):
    room = session.get("code")
    markID = session.get("markID")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    markingData = session.get("markingData")
    for question in data:
        markingData.append(question)
    
    print(markingData)
    session["markingData"] = markingData

    marker = db.session.query(Marker).filter(Marker.markerID == markID).first()
    marker.active = True
    db.session.commit()

@socketio.on("markNext")
def markNext():
    room = session.get("code")
    markID = session.get("markID")
    print("this is")
    print(markID)
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    socketID = db.session.query(Marker.socketID).filter_by(markerID = markID).first()[0]
    markingData = session.get("markingData")

    if(markingData == []):
        marker = db.session.query(Marker).filter_by(markerID = markID).first()
        marker.active = False
        db.session.commit()

        socketio.emit("updateMark",{"switch": "false", "teamID": "", "question": "","answer": "", "questionAnswer": ""}, to=socketID)
    else:
        nextMark = markingData.pop(0)
        session["markingData"] = markingData
        print(nextMark)
        question = db.session.query(Question).filter_by(id = nextMark["questionID"]).first()
        questionAnswer = question.answer
        questionText = question.text

        socketio.emit("updateMark",{"switch": "true", "teamID": nextMark["teamID"], "question": questionText,"answer": nextMark["answer"], "questionAnswer": questionAnswer}, to=socketID)

@socketio.on("checkMark")
def checkMark():
    if not (current_user.is_authenticated and current_user.isVerified):
        return redirect(url_for("auth.login"))
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return  

    answers = db.session.query(Team, TeamAnswer).join(TeamAnswer, Team.teamID == TeamAnswer.teamID).filter(Team.sessionID == room).first()
    marking = db.session.query(Marker).filter(Marker.sessionID == room, Marker.active == True).first()

    if(answers or marking):
        socketio.emit("scoreboard", {"switch": "false"})
    else:
        socketio.emit("scoreboard", {"switch": "true"})


@socketio.on("correct")
def correct(data):
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    teamID = data["teamID"]
    team = db.session.query(Team).filter_by(teamID = teamID).first()
    if team:
        team.score += 1
        db.session.commit()

@socketio.on("incorrect")
def incorrect(data):
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    teamID = data["teamID"]
    team = db.session.query(Team).filter_by(teamID = teamID).first()
    if team:
        team.score -= 0
        db.session.commit()

@socketio.on("updateQuestionID")
def updateQuestionID(data):
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    newQuestionID = data["newQuestionID"]
    print(newQuestionID)
    session["questionID"] = newQuestionID
    session.modified = True
    tempTeam = db.session.query(Team).filter(Team.teamID == session.get("teamID")).first()
    tempTeam.questionID = newQuestionID
    db.session.commit()
    temp = session.get("questionID")
    print(str(temp) +  " a questionID!!")

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

        socketio.emit("showRound", {"roundName" : roundName, "roundMedia": roundMedia}, to=room)


