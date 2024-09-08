from . import db
from flask_login import UserMixin
import random
from string import ascii_uppercase

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(150), unique=True)
    passwordHash = db.Column(db.String(20))
    isVerified = db.Column(db.Boolean(), default = False)

class Quiz(db.Model):
    __tablename__ = "quizzes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    shareCode = db.Column(db.String, unique = True)

    def __init__(self, name):
        self.name = name
        self.shareCode = self.generate_share_code()
        
    def generate_share_code(self):
        while True:
            code = ""
            for _ in range(4):
                code += random.choice(ascii_uppercase)
            if not db.session.query(Quiz).filter_by(shareCode = code).first():
                return code

class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    multChoice = db.Column(db.Boolean(), default = False)
    text = db.Column(db.String(500))
    media = db.Column(db.String(50), default = None)
    choices = db.Column(db.String, default = None)
    answer = db.Column(db.String(255))
    shareCode = db.Column(db.String, unique = True)

    def __init__(self, multChoice, text, media, answer):
        self.multChoice = multChoice
        self.text = text
        self.media = media
        self.answer = answer
        self.shareCode = self.generate_share_code()

    def __init__(self, multChoice, text, answer):
        self.multChoice = multChoice
        self.text = text
        self.answer = answer
        self.shareCode = self.generate_share_code()
        
    def generate_share_code(self):
        while True:
            code = ""
            for _ in range(4):
                code += random.choice(ascii_uppercase)
            if not db.session.query(Question).filter_by(shareCode = code).first():
                return code
            
    def set_data(self, data_list):
        self.choices = '|'.join(data_list)

    def get_data(self):
        return self.choices.split('|')
    
class Round(db.Model):
    __tablename__ = "rounds"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    media = db.Column(db.String(50), default = None)
    shareCode = db.Column(db.String, unique = True)

    def __init__(self, name):
        self.name = name
        self.shareCode = self.generate_share_code()
        
    def generate_share_code(self):
        while True:
            code = ""
            for _ in range(4):
                code += random.choice(ascii_uppercase)
            if not db.session.query(Round).filter_by(shareCode = code).first():
                return code
            
class UserQuiz(db.Model):
    __tablename__ = "user_quizzes"
    userID = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    quizID = db.Column(db.Integer, db.ForeignKey('quizzes.id'), primary_key=True)

    user = db.relationship('User')
    quiz = db.relationship('Quiz')

class QuizRound(db.Model):
    __tablename__ = "quiz_rounds"
    quizID = db.Column(db.Integer, db.ForeignKey('quizzes.id'), primary_key=True)
    roundID = db.Column(db.Integer, db.ForeignKey('rounds.id'), primary_key=True)

    quiz = db.relationship('Quiz')
    round = db.relationship('Round')

class RoundQuestion(db.Model):
    __tablename__ = "round_questions"
    roundID = db.Column(db.Integer, db.ForeignKey('rounds.id'), primary_key=True)
    questionID = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)

    round = db.relationship('Round')
    question = db.relationship('Question')



class QuizSession(db.Model):
    __tablename__ = "sessions"
    sessionID = db.Column(db.String, primary_key=True)
    userID = db.Column(db.Integer, unique = True)
    quizID = db.Column(db.Integer)

    teams = db.relationship('Team', backref='session', cascade='all, delete-orphan')
    markers = db.relationship('Marker', backref='session', cascade='all, delete-orphan')

    def __init__(self, userID, quizID):
        self.sessionID = self.generate_join_code()
        self.userID = userID
        self.quizID = quizID
        
    def generate_join_code(self):
        while True:
            code = ""
            for _ in range(4):
                code += random.choice(ascii_uppercase)
            if not db.session.query(QuizSession).filter_by(sessionID = code).first():
                return code
            
class Team(db.Model):
    __tablename__ = "teams"
    teamID = db.Column(db.Integer, primary_key=True)
    teamName = db.Column(db.String(50), unique = True)
    sessionID = db.Column(db.Integer, db.ForeignKey('sessions.sessionID'))
    score = db.Column(db.Integer, default = 0)

    answers = db.relationship('TeamAnswer', backref='team', cascade='all, delete-orphan')

class TeamAnswer(db.Model):
    __tablename__ = "team_answers"
    teamID = db.Column(db.Integer, db.ForeignKey("teams.teamID"), primary_key=True)
    questionID = db.Column(db.Integer, db.ForeignKey("questions.id"), primary_key = True)
    answer = db.Column(db.String(300))

class Marker(db.Model):
    __tablename__ = "markers"
    markerID = db.Column(db.Integer, primary_key=True)
    sessionID = db.Column(db.Integer, db.ForeignKey('sessions.sessionID'))
    socketID = db.Column(db.String)
    active = db.Column(db.Boolean, default = False)
