from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import current_user
from flask_socketio import join_room, leave_room, send, SocketIO
from . import db, socketio
from random import choice
from .models import *
from collections import defaultdict
from sqlalchemy import desc
import string, time, math, uuid, os
from werkzeug.utils import secure_filename

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
        
        #Add the team to the db
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
        
        privateID = QuizSession.query.filter_by(privateID = code).first()
        if not privateID:
            flash('Session does not exist', category="danger")
            return render_template("participant/marker.html", code = code)
        

        session["code"] = privateID.sessionID
        print(privateID.sessionID)
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
        code = request.form.get('code') 
        #If a share code was inputted and isn't associated with the user, add it to their quizzes
        if (code):
            print(code)

            requestedQuiz = db.session.query(Quiz).filter(Quiz.shareCode == code).first()
            if requestedQuiz:

                exists = db.session.query(UserQuiz).filter(userID == userID, quizID == requestedQuiz.id)

                if exists:
                    flash("Quiz is already present", "danger")
                else:
                    userQuizTest = UserQuiz(userID = userID, quizID = requestedQuiz.id)
                    db.session.add(userQuizTest)
                    db.session.commit()
                    flash("Quiz successfully added", "success")
            else:
                flash("Quiz does not exist", "danger")
            return redirect(url_for("views.quizzes"))
        elif not quizID:
            return redirect(url_for("views.quizzes"))
        #If a quiz was selected, start the quiz
        else:
            session["quizID"] = quizID
            return redirect(url_for("views.question"))
            
    
    playerQuizzes = db.session.query(Quiz, UserQuiz).join(UserQuiz, UserQuiz.quizID == Quiz.id).filter(UserQuiz.userID == current_user.id).all()
    

    return render_template("host/quizzes.html", playerQuizzes = playerQuizzes)


@views.route('/custom', methods=["POST","GET"])
def custom():
    if not (current_user.is_authenticated and current_user.isVerified):
        return redirect(url_for("auth.login"))
    print("wowzers")
    userID = current_user.id

    quizData = []

    if request.method == "POST":
        formData = request.form
        convertData = formData.to_dict()
        #print(request.files["roundMediaInput-2"])
        #print(convertData)

        #First element of dict is the title
        quizTitle = convertData.pop("inputQuizTitle")


        roundLengths = []
        counter = 1


        #Find the number of questions in each round
        for key in convertData:
            if("inputRoundName" in key):
                #print(key)
                roundLengths.append(counter)
                counter = 1

            else:
                #print(key)
                counter = counter + 1
                print(counter)
        roundLengths.append(counter)
        roundLengths.pop(0)

        #print(roundLengths)

        roundSplits = []

        #Separate data into rounds
        for roundLength in roundLengths:
            round = []
            for i in range (roundLength):
                key = next(iter(convertData))
                value = convertData.pop(key)
                round.append((key, value))
            roundSplits.append(round)

        print(roundSplits)

        questionSplit = []

        #Separate data in rounds into individual questions
        for round in roundSplits:
            questionCollection = []
            question = []
            questionCounter = 0
            for input in round:
                inputName = input[0]
                inputNumber = inputName.split('-')[1]
                if(inputNumber == questionCounter):
                    question.append(input)
                elif(questionCounter != 0):
                    questionCollection.append(question)
                    questionCounter = inputNumber
                    question = []
                    question.append(input)
                else:
                    question.append(input)
                    questionCounter = inputNumber
            questionCollection.append(question)
            questionSplit.append(questionCollection)

        print(questionSplit)

        #Create quiz and link to user
        quiz = Quiz(name = quizTitle)
        db.session.add(quiz)
        db.session.commit()
        print(quiz.id)
        userQuiz = UserQuiz(userID = userID, quizID = quiz.id)
        db.session.add(userQuiz)
        db.session.commit()

        #Loop through data creating rounds
        for round in questionSplit:
            roundDetails = round.pop(0)

            key = roundDetails[0][0]
            keyNumber = key.split('-')[1]

            roundDict = dict(roundDetails)

            roundMedia = request.files["roundMediaInput-" + keyNumber]
            if(roundMedia.filename != ""):
                
                fileName = secure_filename(roundMedia.filename)
                fileExtension = os.path.splitext(fileName)[1]
                unique_filename = f"{uuid.uuid4().hex}_{os.path.splitext(fileName)[0]}{fileExtension}"
                roundMedia.save(os.path.join(current_app.config["ROUND_UPLOAD"], unique_filename))
            else:
                unique_filename = None

            newRound = Round(name = roundDict.get("inputRoundName-" + keyNumber), media = unique_filename)
            db.session.add(newRound)
            db.session.commit()

            quizRound = QuizRound(quizID = quiz.id, roundID = newRound.id)
            db.session.add(quizRound)
            db.session.commit()

            #Loop through round data creating questions
            for question in round:
                questionKey = question[0][0]
                questionKeyNumber = questionKey.split('-')[1]
                questionDetails = dict(question)

                if("textCheckbox-"+questionKeyNumber in questionDetails):
                    questionText = questionDetails.get("inputQuestion-" + questionKeyNumber)
                else:
                    questionText = None


                questionMedia = request.files["customQuestionInput-" + questionKeyNumber]
                answerMedia = request.files["customAnswerInput-" + questionKeyNumber]

                if(questionMedia.filename !=""):
                    fileName = secure_filename(questionMedia.filename)
                    fileExtension = os.path.splitext(fileName)[1]
                    unique_question_filename = f"{uuid.uuid4().hex}_{os.path.splitext(fileName)[0]}{fileExtension}"
                    questionMedia.save(os.path.join(current_app.config["QUESTION_UPLOAD"], unique_question_filename))
                else:
                    unique_question_filename = None

                if(answerMedia.filename !=""):
                    fileName = secure_filename(answerMedia.filename)
                    fileExtension = os.path.splitext(fileName)[1]
                    unique_answer_filename = f"{uuid.uuid4().hex}_{os.path.splitext(fileName)[0]}{fileExtension}"
                    answerMedia.save(os.path.join(current_app.config["QUESTION_UPLOAD"], unique_answer_filename))
                else:
                    unique_answer_filename = None

                
                
                if("multipleChoiceCheckbox-" + questionKeyNumber in questionDetails):
                    
                    choice1 = questionDetails.get("customChoiceAnswer1-" + questionKeyNumber)
                    choice2 = questionDetails.get("customChoiceAnswer2-" + questionKeyNumber)
                    choice3 = questionDetails.get("customChoiceAnswer3-" + questionKeyNumber)
                    choice4 = questionDetails.get("customChoiceAnswer4-" + questionKeyNumber)
                    choices = [choice1, choice2, choice3, choice4]

                    if("answer1-" + questionKeyNumber in questionDetails):
                        answer = "A: "+choice1
                    elif("answer2-" + questionKeyNumber in questionDetails):
                        answer = "B: "+choice2
                    elif("answer3-" + questionKeyNumber in questionDetails):
                        answer = "C: " + choice3
                    elif("answer4-" + questionKeyNumber in questionDetails):
                        answer = "D: "+choice4

                    newQuestion = Question(multChoice=True, text=questionText, media=unique_question_filename, answer=answer, answerMedia=unique_answer_filename)
                    newQuestion.set_data(choices)
                    db.session.add(newQuestion)
                    db.session.commit()

                else:
                    answer = questionDetails.get("customAnswer-" + questionKeyNumber)

                    newQuestion = Question(multChoice=False, text=questionText, media=unique_question_filename, answer=answer, answerMedia=unique_answer_filename)
                    db.session.add(newQuestion)
                    db.session.commit()

                roundQuestion = RoundQuestion(roundID = newRound.id, questionID = newQuestion.id)
                db.session.add(roundQuestion)
                db.session.commit()

                
        return redirect(url_for("views.quizzes"))


    


    return render_template("host/custom.html", quizData = quizData)


@views.route('/question')
def question():
    if not (current_user.is_authenticated and current_user.isVerified):
        return redirect(url_for("auth.login"))
    
    quizID = session.get("quizID")
    if not quizID:
        return redirect(url_for("views.quizzes"))
    
    code = session.get("code")
    privateCode = session.get("privateCode")
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
        privateCode = newSession.privateID
        print("render Private:")
        print(privateCode)
        session["code"] = code
        session["privateCode"] = privateCode
    
    
    return render_template("host/question.html", code = code, privateCode = privateCode)

@views.route('/final_score')
def final_score():
    if not (current_user.is_authenticated and current_user.isVerified):
        return redirect(url_for("auth.login"))
    
    room = session.get("code")
    sessionID = QuizSession.query.filter_by(sessionID = room).first()
    if not sessionID:
        return
    
    socketio.emit("playerLeave")
    
    scores = db.session.query(Team.teamName, Team.score).filter(Team.sessionID == room).order_by(desc(Team.score)).all()

    #Remove all data from the database relating to the specific instance of the quiz being run
    db.session.query(QuizSession).filter(QuizSession.sessionID == room).delete()
    db.session.commit()
    session.clear()

    
    return render_template("host/final_score.html", scores = scores)


#
#   Socket Responses
# 
@socketio.on("connectPlayer")
def connectPlayer():
    print("Player joined")
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
    
    marker = Marker(sessionID = code, socketID = data["socketID"])
    print(data["socketID"])
    db.session.add(marker)
    db.session.commit()

    session["markID"] = marker.markerID

    session["markingData"] = []
    

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

    #Split all questions that need marking between the connected markers and send them.
    for marker in markers:
        questionSubList = []
        for _ in range(math.ceil(questionCount / markerCount)):
            if(markQuestions[0]):
                questionSubList.append(questionList.pop(0))
        print(marker.socketID)
        socketio.emit("newMarking", questionSubList, to=marker.socketID)



    #If no questions left end the round
    if(questionIDs[0] == []):
        questionIDs.pop(0)
        session["QuestionIDs"] = questionIDs
        roundAnswers = session.get("RoundAnswers")
        answerMedia = session.get("AnswerMedia")
        socketio.emit("endOfRound", {"roundAnswers": roundAnswers, "answerMedia": answerMedia}, to=room)
    #Send the next questions data
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
    #If no answers left, end the round
    if(answerIDs == []):
        socketio.emit("newRound", to=room)#
    #Send the next answers details
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
                    'answer': answerData.answer,
                    'answerMedia': answerData.answerMedia
                }
            else:

                answerDataConvert = {
                    'id': answerData.id,
                    'multChoice': answerData.multChoice,
                    'text': answerData.text,
                    'media': answerData.media,
                    'choices': answerData.choices,
                    'answer': answerData.answer,
                    'answerMedia': answerData.answerMedia
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

#
#   Marked questions change the teams score   
#
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
        print("well thats not right")
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


