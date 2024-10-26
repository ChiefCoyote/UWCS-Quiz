/*
 *  JavaScript to control mark.html, the webpage used by markers to mark the answers given by players
 * 
 */

var socketio = io.connect();
//Check every 10 seconds for new questions to mark
sleep(10000).then(()=> {
    markNext();
});


socketio.on("connect", function() {
    socketio.emit("connectMarker", {"socketID": socketio.id});
    console.log(socketio.id);
}); 

socketio.on("newMarking", (data) => {
    socketio.emit("addNewMarking", data);
});


socketio.on("updateMark", (data) => {
    if(data.switch == "false"){
        sleep(5000).then(() =>{
            socketio.emit("markNext");
        });
    }
    else{
        updateMarkPage(data);
    }
});

//Display details of the next answer to be marked
function updateMarkPage(data){
    document.getElementById("teamID").textContent = data.teamID;
    document.getElementById("askedQuestion").textContent = data.question;
    document.getElementById("correctAnswer").textContent = data.questionAnswer;
    document.getElementById("response").textContent = data.answer;
    document.getElementById("markingAnswer").style.display = "";
    document.getElementById("waiting").style.display = "none";
};

function sleep(time){
    return new Promise(resolve => setTimeout(resolve, time));
}

function markCorrect(){
    let teamID = document.getElementById("teamID").textContent;
    socketio.emit("correct", {"teamID": teamID});
    markNext();
};

function markIncorrect(){
    let teamID = document.getElementById("teamID").textContent;
    socketio.emit("incorrect", {"teamID": teamID});
    markNext();
};

function markNext(){
    document.getElementById("markingAnswer").style.display = "none";
    document.getElementById("waiting").style.display = "";
    socketio.emit("markNext");
};