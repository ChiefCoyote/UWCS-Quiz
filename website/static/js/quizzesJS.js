function selectQuiz(quizID) {
    const selectedQuizID = document.getElementById("selectedQuizID");
    selectedQuizID.value = quizID;

    const allQuizzes = document.querySelectorAll('.quizChoice');
    allQuizzes.forEach(quiz => quiz.classList.remove('selected'));

    const thisQuiz = document.getElementById('quiz-' + quizID);
    thisQuiz.classList.add("selected");

    const quizStart = document.getElementById("quizStart");
    quizStart.disabled = false;

    console.log(selectedQuizID.value);
}

function importQuiz() {
    $('#codeModal').modal('show');
}