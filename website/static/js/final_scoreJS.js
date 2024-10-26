/*
 *  JavaScript to control fianl_score.html, the webpage that displays the final scoreboard
 */

function showScore(button){
    const container = button.parentElement;

    const teamName = container.querySelector(".teamNameLeaderboard");

    if(teamName){
        teamName.classList.remove("hidden");
    }

    button.classList.add("hidden")
}