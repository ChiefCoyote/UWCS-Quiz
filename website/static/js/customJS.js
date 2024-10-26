/*
 *  JavaScript to control custom.html, the webpage used by a host to create a new quiz.
 * 
 */

//Total number of quiz, round and question detail screens
var elementCounter = 2;


const customPreview = document.getElementById("customPreview");
customPreview.addEventListener('change', function(event){
    const target = event.target;

    //When a media file is uploaded, display a preview on screen
    if (target.classList.contains('mediaInput')) {
        const file = target.files[0];
        const preview = target.previousElementSibling;
        preview.innerHTML = '';
        if(file){
            const fileType = file.type;
            if(fileType.startsWith('image/')){
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                preview.appendChild(img);
            } else if(fileType.startsWith('audio/')) {
                const audio = document.createElement('audio');
                audio.controls = true;
                audio.src = URL.createObjectURL(file);
                preview.appendChild(audio);
            } else if(fileType.startsWith('video/')) {
                const video = document.createElement('video');
                video.controls = true;
                video.src = URL.createObjectURL(file);
                preview.appendChild(video);
            }
        }
    }

    //If a checkbox is exclusive, deselect all sibling checkboxes
    else if (target.classList.contains('exclusive')) {
        const parentContainer = target.closest('.customChoices');
        const checkboxes = parentContainer.querySelectorAll('.exclusive');

        if (target.checked) {
            checkboxes.forEach(box => {
                if (box !== target) {
                    box.checked = false;
                }
            });
        } else if(!target.checked) {
            target.checked = true;
        }
    }

    //Display different sections of the input form depending on the checkboxes a user selects
    else if (target.classList.contains('checkboxType')){
        const parentContainer = target.closest('.customQuestion');
        console.log(target.name);
        let individualName = target.name;
        let parts = individualName.split("-");
        let name = parts[0];
        

        //Question text
        if (name == 'textCheckbox'){

            let questionText = parentContainer.querySelector('#inputQuestion');
            if(target.checked){
                questionText.style.display = "";
            }else{
                questionText.style.display = "none";
            }
        
        //Media for the question
        }else if(name == "questionMediaCheckbox"){

            let questionImage = parentContainer.querySelector("#customQuestionImage");
            if(target.checked){
                questionImage.style.display = "";
            }else{
                questionImage.style.display = "none";
            }
        
        //media for the answer
        }else if(name == "answerMediaCheckbox"){

            let questionImage = parentContainer.querySelector("#customAnswerImage");
            if(target.checked){
                questionImage.style.display = "";
            }else{
                questionImage.style.display = "none";
            }
        
        //Multiple choice answer or not
        }else if(name == "multipleChoiceCheckbox"){
            let multChoice = parentContainer.querySelector("#customChoices");
            let textAnswer = parentContainer.querySelector("#customAnswer");

            if(target.checked){
                multChoice.style.display = "";
                textAnswer.style.display = "none";
            }else{
                multChoice.style.display = "none";
                textAnswer.style.display = "";
            }
        }
    }
});

//Clicking on a quiz, round or question displays the specific preview and form input.
function showPreview(selector) {
    let id = selector.id;
    let parts = id.split("-");
    let key = parts[1];

    let previewKey = "preview-" + key;

    let previewContainer = document.getElementById("customPreview");
    let previews = previewContainer.children;

    for (let preview of previews) {
        if(preview.id == "preview-1"){
            preview.style.display = "none";
        } else{
            let questions = preview.children;
            for (let question of questions){
                question.style.display = "none";
            }
        }
        
    }

    let selectedPreview = document.getElementById(previewKey);
    selectedPreview.style.display = "";
}

function createRound(button){
    let selectors = document.getElementById("customQuiz");
    let previews = document.getElementById("customPreview");

    let newRoundSelector = `

        <div class="customSelectRound">
            <div class="selectQuiz" id="selector-${elementCounter}" onclick="showPreview(this)" style="margin-left:1vw; font-weight:bold;">Round</div>
            <div class="dropdown">
                <i class="fa fa-plus dropdown-toggle addCustom" name="newQuestion" id="newQuestion" data-bs-toggle="dropdown"></i>
                <ul class="dropdown-menu">
                    <li><button class="dropdown-item" onclick="createQuestion(this)">Create Question</button></li>
                    <li><button class="dropdown-item" onclick="importQuestion()" disabled>Import Question</button></li>
                </ul>
            </div>
            <i class="fa fa-trash deleteCustom" onclick="deleteRound(this)"></i>
        </div>

    `;

    let selector = document.createElement('div');
    selector.className = 'customRoundSelector';
    selector.innerHTML = newRoundSelector;
    selectors.appendChild(selector);

    let newRoundPreview = `
        <div class="customRound" id="preview-${elementCounter}" style="display: none;">
            <div class="roundName" id="roundName">
                <input type="text" class="inputRoundName centered-input" id="inputRoundName" name="inputRoundName-${elementCounter}" placeholder="Round Name">
            </div>

            <div class="roundMedia" id="roundMedia">
                <div class="preview" id="roundMediaPreview"></div>
                <input type="file" accept=".jpg, .jpeg, .png, .gif, .mp4, .mov, .wav, .mp3" class="mediaInput" name="roundMediaInput-${elementCounter}" id="roundMediaInput">
            </div>
        </div>
    `;

    let preview = document.createElement('div');
    preview.className = "customRoundContainer";
    preview.innerHTML = newRoundPreview;
    previews.appendChild(preview);

    elementCounter += 1;

    attachEventListeners();
}

function createQuestion(button){
    let round = button.closest(".customRoundSelector");
    
    let temp = button.closest(".dropdown");
    let selectorID = temp.previousElementSibling;
    let id = selectorID.id;
    let parts = id.split("-");
    let key = parts[1];
    let previewKey = "preview-" + key;

    let previewRound = document.getElementById(previewKey);
    roundContainer = previewRound.closest(".customRoundContainer");

    let newQuestionSelector = `

        <div class="customSelectQuestion">
            <div class="selectQuiz" id="selector-${elementCounter}" onclick="showPreview(this)" style="margin-left: 2vw; font-weight:bold;">Question</div>
            <i class="fa fa-trash deleteCustom" onclick="deleteQuestion(this)"></i>
        </div>

    `;
    let selector = document.createElement('div');
    selector.className = "customQuestion"
    selector.innerHTML = newQuestionSelector;
    round.appendChild(selector);

    let newQuestionPreview = `
        <div class="customQuestionInputs">
            <div class="customQuestionInfo">
                <input type="text" class="inputQuestion centered-input" id="inputQuestion" placeholder="Question..." name="inputQuestion-${elementCounter}">
                <div class = "customMedia">
                    <div class="customQuestionImage" id="customQuestionImage" style="display: none;">
                        <div class="previewQuestion" id="questionImagePreview"></div>
                        <input type="file" accept=".jpg, .jpeg, .png, .gif, .mp4, .mov, .wav, .mp3" class="mediaInput" name="customQuestionInput-${elementCounter}" id="customQuestionInput">
                        
                    </div>

                    <div class="customAnswerImage" id="customAnswerImage" style="display: none;">
                        <div class="previewQuestion" id="answerImagePreview"></div>
                        <input type="file" accept=".jpg, .jpeg, .png, .gif, .mp4, .mov, .wav, .mp3" class="mediaInput" name="customAnswerInput-${elementCounter}" id="customAnswerInput">
                        
                    </div>
                </div>
            </div>
        
            <div class="customChoices" id="customChoices" style="display: none;">
                
                <div class="customCorrectAnswer">
                    <div class="customChoice">
                        A:&nbsp;  <input type="text" class="customChoiceAnswer" placeholder="Answer 1" name="customChoiceAnswer1-${elementCounter}">
                    </div>
                    <input type="checkbox" class="exclusive" name="answer1-${elementCounter}" checked>
                </div>
                
                <div class="customCorrectAnswer">
                    <div class="customChoice">
                        B:&nbsp;  <input type="text" class="customChoiceAnswer" placeholder="Answer 2" name="customChoiceAnswer2-${elementCounter}">
                    </div>
                    <input type="checkbox" class="exclusive" name="answer2-${elementCounter}">
                </div>

                <div class="customCorrectAnswer">
                    <div class="customChoice">
                        C:&nbsp;  <input type="text" class="customChoiceAnswer" placeholder="Answer 3" name="customChoiceAnswer3-${elementCounter}">
                    </div>
                    <input type="checkbox" class="exclusive" name="answer3-${elementCounter}">
                </div>

                <div class="customCorrectAnswer">
                    <div class="customChoice">
                        D:&nbsp;  <input type="text" class="customChoiceAnswer" placeholder="Answer 4" name="customChoiceAnswer4-${elementCounter}">
                    </div>
                    <input type="checkbox" class="exclusive" name="answer4-${elementCounter}">
                </div>
            </div>


            <div class="customAnswer" id="customAnswer">
                <input type="text" class="answerInput centered-input" placeholder="Answer..." name="customAnswer-${elementCounter}">
            </div>
        </div>

        <div class="questionType">
            <div class="typeLabel">Question Text:&nbsp; <input type="checkbox" name="textCheckbox-${elementCounter}" class="checkboxType" checked></div>

            <div class="typeLabel">Question Media:&nbsp; <input type="checkbox" name="questionMediaCheckbox-${elementCounter}" class="checkboxType"></div>

            <div class="typeLabel">Separate Answer Media:&nbsp; <input type="checkbox" name="answerMediaCheckbox-${elementCounter}" class="checkboxType"></div>

            <div class="typeLabel">Multiple Choice:&nbsp; <input type="checkbox" name="multipleChoiceCheckbox-${elementCounter}" class="checkboxType"></div>
        </div>

    `;

    let preview = document.createElement('div');
    preview.className = "customQuestion";
    let previewID = "preview-" + elementCounter;
    preview.id = previewID;
    preview.style.display = "none";
    preview.innerHTML = newQuestionPreview;
    roundContainer.appendChild(preview);

    elementCounter += 1;

    attachEventListeners();

}

function deleteRound(button){
    idElement = button.previousElementSibling.previousElementSibling;
    let id = idElement.id;
    let parts = id.split("-");
    let key = parts[1];

    let roundContainer = button.closest(".customRoundSelector");
    roundContainer.remove();

    previewKey = "preview-" + key;
    let preview = document.getElementById(previewKey).parentElement;
    preview.remove();
}

function deleteQuestion(button){
    idElement = button.previousElementSibling;
    let id = idElement.id;
    let parts = id.split("-");
    let key = parts[1];

    let questionContainer = button.closest(".customQuestion");
    questionContainer.remove();

    previewKey = "preview-" + key;
    let preview = document.getElementById(previewKey);
    preview.remove();
}

//All quizzes must have a title before being created
function submitData(){
    var fail = false
    let quizTitle = document.getElementById("inputQuizTitle");
    if(quizTitle.value == ""){
        let warning = document.createElement('div');
        warning.innerHTML = `
            <span>Please enter a title for the quiz!</span>
            <button type="button" class="btn-close alert-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        warning.classList = "alert alert-danger alert-dismissible fade show text-center m-2 alert-overlay";
        warning.role = "alert";

        let parent = document.getElementById("customise");
        parent.prepend(warning);
        fail = true;
    } 

    if(!fail){
        document.getElementById("customPreview").submit();
    }

}

function attachEventListeners() {
    const fileInputs = document.querySelectorAll(".mediaInput");

    fileInputs.forEach(input => {
        input.removeEventListener('change', onFileChange);
        input.addEventListener('change', onFileChange);
    });
}

function onFileChange(event){
    validateFileInput(event.target);
}

//Only allow the upload of certain file types
function validateFileInput(input) {
    const allowedExtentions = ["jpg", "jpeg", "png", "gif", "mp4", "mp3", "wav", "mov"];
    const files = input.files;
    if (files.length > 0) {
        const file = files[0];
        const fileExtension = file.name.split('.').pop().toLowerCase();

        if(!allowedExtentions.includes(fileExtension)){
            let warning = document.createElement('div');
            warning.innerHTML = `
                <span>File type not recognised!</span>
                <button type="button" class="btn-close alert-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            warning.classList = "alert alert-danger alert-dismissible fade show text-center m-2 alert-overlay";
            warning.role = "alert";

            let parent = document.getElementById("customise");
            parent.prepend(warning);
            input.value = "";
        }
    }
}

attachEventListeners();