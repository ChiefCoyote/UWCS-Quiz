/*
 *  JavaScript to control answer.html, the webpage used by players to submit answers to the questions
 * 
 */


var socketio = io()
socketio.emit("connectPlayer")

if({{started | lower}}){
    activeAnswer();
}

//Set the current player guess to the input and send a message to the server letting the host know the question has been answered.
const submitAnswer = () => {
    let answer = document.getElementById("answer").value;
    document.getElementById("currentAnswer").textContent = answer;
    socketio.emit("submitAnswer");
};

//Switch the displayed screen to the answer screen and activate the button, allowing users to submit an answer.
function activeAnswer() {
    const answerScreen = document.getElementById('answerScreen');
    const waiting = document.getElementById('waiting')
    const endScreen = document.getElementById('endScreen')
    const button = document.getElementById("submit-btn");
    button.disabled = false;
    if (window.getComputedStyle(answerScreen).display === 'none') {
        answerScreen.style.display = '';
        waiting.style.display = 'none';
        endScreen.style.display = 'none';
    }
}

function clearAnswer() {
    document.getElementById("currentAnswer").textContent = ""
    var answerForm = document.getElementById('answerForm');
    answerForm.reset();
}

//If client has fallen behind, update to display correct screen and set the question being answered to the current one.
//data contains the current questionID of the question being answered
socketio.on("ping", (data) => {
    activeAnswer();
    socketio.emit("updateQuestionID", {"newQuestionID": data.questionID})
});

//Clear the current answer, update to the next question being answered.
//data contains the next questionID to be answered
socketio.on("nextQuestion", (data) => {
    clearAnswer();
    socketio.emit("updateQuestionID", {"newQuestionID": data.newQuestionID})
    activeAnswer();
    const button = document.getElementById("submit-btn");
    button.disabled = false;
});

//At the end of a round, disable the button whilst the answers are being displayed
socketio.on("endOfRound", (data) => {
    clearAnswer();
    const button = document.getElementById("submit-btn");
    button.disabled = true;
});

//At the end of the quiz, display the final screen.
socketio.on("endOfQuestions", function() {
    document.getElementById("answerScreen").style.display = "none";
    document.getElementById("endScreen").style.display = "";
});

//If a player gets disconnected from the room, return to the homepage
socketio.on("playerLeave", function() {
    window.location.replace("/");
});