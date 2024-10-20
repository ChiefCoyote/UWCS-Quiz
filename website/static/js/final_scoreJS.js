function showScore(button){
    const container = button.parentElement;

    const teamName = container.querySelector(".teamNameLeaderboard");

    if(teamName){
        teamName.classList.remove("hidden");
    }

    button.classList.add("hidden")
}