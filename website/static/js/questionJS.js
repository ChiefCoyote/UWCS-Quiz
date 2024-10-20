var socketio = io()
socketio.emit("connectHost")

//May be able to on click remove player for bad names

var playerNumber = 0;

var questionCounter = 0;

var multAnswer = false;

var QnA = true;

let answerCounter = new Array();

function begin() {
    socketio.emit("begin")
}

function nextQuestion() {
    socketio.emit("nextQuestion");
}

function nextAnswer() {
    socketio.emit("nextAnswer");
}

function startRound() {
    questionCounter = 0;
    if(QnA){
        QnA = !QnA
        socketio.emit("nextQuestion");
    }
    else{
        QnA = !QnA
        socketio.emit("nextAnswer");
    }
}

function revealAnswer() {
    if(multAnswer){
        let questionChoicesAnswer = document.getElementById("questionChoicesAnswer");
        let questionChoicesReveal = document.getElementById("questionChoicesReveal");
        questionChoicesAnswer.style.display = "none";
        questionChoicesReveal.style.display = "";
    }
    else{
        let answerWrapper = document.getElementById("answerWrapper");
        answerWrapper.style.display = "";
    }

    let questionImageAnswer = document.getElementById("questionImageAnswer");
    let answerImage = document.getElementById("answerImage");

    if(answerImage.innerHTML === ''){}
    else{
        questionImageAnswer.style.display = "none";
        answerImage.style.display = "";
    }
    
    
}

function ping() {
    socketio.emit("ping");
}

socketio.on("showRound", (data) => {
    
    const roundTitle = document.getElementById("roundTitle");
    roundTitle.textContent = data.roundName;

    const roundImage = document.getElementById("roundImage");
    if(data.roundMedia === null){
        roundImage.style.display = 'none';
    }
    else{
        roundImage.style.display = '';
        roundImage.innerHTML = '';
        let filepath = "../../static/media/roundMedia/" + data.roundMedia;
        const mediaElement = createMediaElement(filepath);
        roundImage.appendChild(mediaElement);
    }
    
    const questionDisplay = document.getElementById("questionDisplay");
    questionDisplay.style.display = 'none';
    const showAnswers = document.getElementById("showAnswers");
    showAnswers.style.display = 'none';
    const joiningDisplay = document.getElementById("joiningDisplay");
    joiningDisplay.style.display = 'none';
    const roundDisplay = document.getElementById("roundDisplay");
    roundDisplay.style.display = '';
});

socketio.on("endOfRound", (data) => {
    const roundTitle = document.getElementById("roundTitle");
    roundTitle.value = data.roundAnswers;

    const roundImage = document.getElementById("roundImage");
    if(data.answerMedia === null){
        roundImage.style.display = 'none';
    }
    else{
        roundImage.style.display = '';
        roundImage.innerHTML = '';
        let filepath = "../../static/media/roundMedia/" + data.answerMedia;
        const mediaElement = createMediaElement(filepath);
        roundImage.appendChild(mediaElement);
    }
    
    const questionDisplay = document.getElementById("questionDisplay");
    questionDisplay.style.display = 'none';
    const showAnswers = document.getElementById("showAnswers");
    showAnswers.style.display = 'none';
    const joiningDisplay = document.getElementById("joiningDisplay");
    joiningDisplay.style.display = 'none';
    const roundDisplay = document.getElementById("roundDisplay");
    roundDisplay.style.display = '';
});

socketio.on("showNextQuestion", (data) => {
    questionCounter++;
    answerCounter = [];
    let playersAnswered = document.getElementById("playersAnswered");
    let answeredStatus = "Answered: " + answerCounter.length + " / " + playerNumber;
    playersAnswered.textContent = answeredStatus;
    const questionData = data.questionData;
    let questionNumber = document.getElementById("questionNumber");
    questionNumber.textContent = "Question " + questionCounter;

    let question = document.getElementById("question");
    if(questionData.text){
        question.textContent = questionData.text;
        question.style.display = "";
    }
    else{
        question.style.display = "none";
    }
    

    //console.log(questionData.text);
    let questionImage = document.getElementById("questionImage"); 

    if(questionData.media){              
        questionImage.innerHTML = '';
        let filepath = "../../static/media/questionMedia/" + questionData.media;
        const mediaElement = createMediaElement(filepath);
        questionImage.appendChild(mediaElement);
        questionImage.style.display = '';
    }
    else{
        questionImage.style.display = 'none';
    }

    if(questionData.multChoice){
        let questionChoices = document.getElementById("questionChoices");

        let choice1 = document.getElementById("choice1");
        let choice2 = document.getElementById("choice2");
        let choice3 = document.getElementById("choice3");
        let choice4 = document.getElementById("choice4");

        choice1.textContent = questionData.choices[0];
        choice2.textContent = questionData.choices[1];
        choice3.textContent = questionData.choices[2];
        choice4.textContent = questionData.choices[3];


        questionChoices.style.display = '';
    }
    else{
        let questionChoices = document.getElementById("questionChoices");
        questionChoices.style.display = 'none';
    }

    
    const showAnswers = document.getElementById("showAnswers");
    showAnswers.style.display = 'none';
    const joiningDisplay = document.getElementById("joiningDisplay");
    joiningDisplay.style.display = 'none';
    const roundDisplay = document.getElementById("roundDisplay");
    roundDisplay.style.display = 'none';
    const questionDisplay = document.getElementById("questionDisplay");
    questionDisplay.style.display = '';
});

socketio.on("showNextAnswer", (data) => {
    questionCounter++;
    const questionData = data.questionData
    let answerNumber = document.getElementById("answerNumber");
    answerNumber.textContent = "Question " + questionCounter;

    let questionAnswer = document.getElementById("questionAnswer");

    if(questionData.text){
        questionAnswer.textContent = questionData.text;
        questionAnswer.style.display = "";
    }
    else{
        questionAnswer.style.display = "none";
    }

    let questionImageAnswer = document.getElementById("questionImageAnswer");
    let answerImage = document.getElementById("answerImage");
    

    if(questionData.media){
        questionImageAnswer.innerHTML = '';
        let filepath = "../../static/media/questionMedia/" + questionData.media;
        const mediaElement = createMediaElement(filepath);
        questionImageAnswer.appendChild(mediaElement);
        questionImageAnswer.style.display = '';
    }
    else{
        questionImageAnswer.style.display = 'none';
    }

    if(questionData.answerMedia){
        answerImage.innerHTML = '';
        let filepath = "../../static/media/questionMedia/" + questionData.answerMedia;
        const mediaElement = createMediaElement(filepath);
        answerImage.appendChild(mediaElement);
        answerImage.style.display = 'none';
    }
    else{
        if(questionData.media){
            answerImage.innerHTML = '';
            let filepath = "../../static/media/questionMedia/" + questionData.media;
            const mediaElement = createMediaElement(filepath);
            answerImage.appendChild(mediaElement);
            answerImage.style.display = 'none';
        }
        else{
            answerImage.innerHTML = '';
            answerImage.style.display = 'none';
        }
    }

    if(questionData.multChoice){
        multAnswer = true;
        let answerWrapper = document.getElementById("answerWrapper");
        answerWrapper.style.display = 'none'

        let questionChoicesAnswer = document.getElementById("questionChoicesAnswer");

        let answerA = document.getElementById("answerA");
        let answerB = document.getElementById("answerB");
        let answerC = document.getElementById("answerC");
        let answerD = document.getElementById("answerD");

        answerA.textContent = questionData.choices[0];
        answerB.textContent = questionData.choices[1];
        answerC.textContent = questionData.choices[2];
        answerD.textContent = questionData.choices[3];


        questionChoicesAnswer.style.display = '';


        let questionChoicesReveal = document.getElementById("questionChoicesReveal");

        let answerAReveal = document.getElementById("answerAReveal");
        let answerBReveal = document.getElementById("answerBReveal");
        let answerCReveal = document.getElementById("answerCReveal");
        let answerDReveal = document.getElementById("answerDReveal");

        let questionChoiceA = document.getElementById("questionChoiceA");
        let questionChoiceB = document.getElementById("questionChoiceB");
        let questionChoiceC = document.getElementById("questionChoiceC");
        let questionChoiceD = document.getElementById("questionChoiceD");

        answerAReveal.textContent = questionData.choices[0];
        answerBReveal.textContent = questionData.choices[1];
        answerCReveal.textContent = questionData.choices[2];
        answerDReveal.textContent = questionData.choices[3];

        console.log(questionData.answer);
        let qAnswer = questionData.answer.split(":")[0];
        switch(qAnswer){
            case "A":
                console.log("A");
                questionChoiceA.classList.add("multChoiceAnswer");
                questionChoiceB.classList.remove("multChoiceAnswer");
                questionChoiceC.classList.remove("multChoiceAnswer");
                questionChoiceD.classList.remove("multChoiceAnswer");

                break;
            case "B":
                console.log("B");
                questionChoiceB.classList.add("multChoiceAnswer");
                questionChoiceA.classList.remove("multChoiceAnswer");
                questionChoiceC.classList.remove("multChoiceAnswer");
                questionChoiceD.classList.remove("multChoiceAnswer");
                break;
            case "C":
                console.log("C");
                questionChoiceC.classList.add("multChoiceAnswer");
                questionChoiceB.classList.remove("multChoiceAnswer");
                questionChoiceA.classList.remove("multChoiceAnswer");
                questionChoiceD.classList.remove("multChoiceAnswer");
                break;
            case "D":
                console.log("D");
                questionChoiceD.classList.add("multChoiceAnswer");
                questionChoiceB.classList.remove("multChoiceAnswer");
                questionChoiceC.classList.remove("multChoiceAnswer");
                questionChoiceA.classList.remove("multChoiceAnswer");
                break;
            default:
                console.log("NOTHING");
                break;
        }


        questionChoicesReveal.style.display = 'none';



    }
    else{
        multAnswer = false
        let questionChoicesAnswer = document.getElementById("questionChoicesAnswer");
        questionChoicesAnswer.style.display = 'none';

        let questionChoicesReveal = document.getElementById("questionChoicesReveal");
        questionChoicesReveal.style.display = 'none';

        let answer = document.getElementById("answer");
        console.log(questionData.answer);
        answer.textContent = questionData.answer;

        let answerWrapper = document.getElementById("answerWrapper");
        answerWrapper.style.display = 'none';
    }

    
    const joiningDisplay = document.getElementById("joiningDisplay");
    joiningDisplay.style.display = 'none';
    const roundDisplay = document.getElementById("roundDisplay");
    roundDisplay.style.display = 'none';
    const questionDisplay = document.getElementById("questionDisplay");
    questionDisplay.style.display = 'none';
    const showAnswers = document.getElementById("showAnswers");
    showAnswers.style.display = '';

});

socketio.on("newRound", function(){
    socketio.emit("begin");
});

socketio.on("logPlayer", (data) => {
    let player = document.getElementById(data.name);
    if(!player){
        let newPlayer = document.createElement("div");
        newPlayer.className = "participant";
        newPlayer.id = data.name;
        newPlayer.textContent = data.name;

        let participants = document.getElementById("participants");
        participants.appendChild(newPlayer)
        playerNumber++;
        let playerCount = document.getElementById("playerCount");
        playerCount.textContent = playerNumber;
        let playersAnswered = document.getElementById("playersAnswered");
        let answeredStatus = "Answered: " + answerCounter.length + " / " + playerNumber;
        playersAnswered.textContent = answeredStatus;
    }
});

socketio.on("disconnectPlayer", (data) => {
    let player = document.getElementById(data.name);
    if(player){
        player.remove()
        playerNumber--;
        let playerCount = document.getElementById("playerCount");
        playerCount.textContent = playerNumber;
    }
});

socketio.on("endOfQuestions", function() {
    const joiningDisplay = document.getElementById("joiningDisplay");
    joiningDisplay.style.display = 'none';
    const roundDisplay = document.getElementById("roundDisplay");
    roundDisplay.style.display = 'none';
    const questionDisplay = document.getElementById("questionDisplay");
    questionDisplay.style.display = 'none';
    const showAnswers = document.getElementById("showAnswers");
    showAnswers.style.display = 'none';
    const waitingScreen = document.getElementById("waitingScreen");
    waitingScreen.style.display = '';

    socketio.emit("checkMark");
    
});

socketio.on("submitAnswer", (data) => {
    if(!answerCounter.includes(data.teamID)){
        answerCounter.push(data.teamID);
        let playersAnswered = document.getElementById("playersAnswered");
        let answeredStatus = "Answered: " + answerCounter.length + " / " + playerNumber;
        playersAnswered.textContent = answeredStatus;
    }
});

function sleep(time){
    return new Promise(resolve => setTimeout(resolve, time));
}


socketio.on("scoreboard", (data) => {
    if(data.switch == "false"){
        sleep(5000).then(() =>{
            socketio.emit("checkMark");
        });
    }
    else{
        window.location.replace("/final_score");
    }
});

function createMediaElement(filePath){
    const fileExtension = filePath.split('.').pop().toLowerCase();

    let mediaElement;

    if (fileExtension === 'jpg' || fileExtension === 'jpeg' || fileExtension === 'png' || fileExtension === 'gif') {
        mediaElement = document.createElement('img');
        mediaElement.src = filePath;
    
    } else if (fileExtension === 'mp4' || fileExtension === 'webm') {
        mediaElement = document.createElement('video');
        mediaElement.src = filePath;
        mediaElement.controls = true;

    } else if (fileExtension === 'mp3' || fileExtension === 'wav') {
        mediaElement = document.createElement('audio');
        mediaElement.src = filePath;
        mediaElement.controls = true;

    } else {
        mediaElement = document.createElement('p');
        mediaElement.textContent = 'Unsupported media type';
    }

    return mediaElement;
};

function displayCode(){
    let hidden = document.getElementById("hideCode");
    let shown = document.getElementById("showCode");

    if(hidden.style.display == "none"){
        hidden.style.display = "";
        shown.style.display = "none";
    }else{
        hidden.style.display = "none";
        shown.style.display = "";
    }
}