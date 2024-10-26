/*
 *  JavaScript to control quizzes.html, the webpage that displays all the quizzes a host has access to. Can also launch a quiz from here.
 * 
 */

function selectQuiz(quizID) {
    const selectedQuizID = document.getElementById("selectedQuizID");
    selectedQuizID.value = quizID;

    const allQuizzes = document.querySelectorAll('.quizChoice');
    allQuizzes.forEach(quiz => quiz.classList.remove('selected'));

    const thisQuiz = document.getElementById('quiz-' + quizID);
    thisQuiz.classList.add("selected");

    const quizStart = document.getElementById("quizStart");
    quizStart.disabled = false;
}

function importQuiz() {
    $('#codeModal').modal('show');
}