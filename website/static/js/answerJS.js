var socketio = io()
socketio.emit("connectPlayer")

if({{started | lower}}){
    activeAnswer();
}

const submitAnswer = () => {
    let answer = document.getElementById("answer").value;
    console.log(answer)
    document.getElementById("currentAnswer").textContent = answer;
    socketio.emit("submitAnswer");
};

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


socketio.on("ping", (data) => {
    activeAnswer();
    socketio.emit("updateQuestionID", {"newQuestionID": data.questionID})
});

socketio.on("nextQuestion", (data) => {
    clearAnswer();
    console.log("woof");
    console.log(data.newQuestionID);
    socketio.emit("updateQuestionID", {"newQuestionID": data.newQuestionID})
    activeAnswer();
    const button = document.getElementById("submit-btn");
    button.disabled = false;
});

socketio.on("endOfRound", (data) => {
    clearAnswer();
    const button = document.getElementById("submit-btn");
    button.disabled = true;
});

socketio.on("endOfQuestions", function() {
    document.getElementById("answerScreen").style.display = "none";
    document.getElementById("endScreen").style.display = "";
});

socketio.on("playerLeave", function() {
    window.location.replace("/");
});