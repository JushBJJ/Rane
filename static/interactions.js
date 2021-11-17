lastElement = null;


// Wait till the file is selected
document.getElementById("file").addEventListener("change", function () {
    // Get the file
    var file = document.getElementById("file").value;

    // Check if file value is not empty
    if (file != "") {
        toggleOption("upload_box");

        // Change #filename to the selected file name
        // remove C:\fakepath\ from the file name
        document.getElementById("filename").innerHTML = file.replace("C:\\fakepath\\", "");

        // Disable the send button
        document.getElementById("send").disabled = true;
    }
});

function toggleSettings() {
    document.getElementById("settings").classList.toggle("is-hidden")
}

function toggleOption(id) {;
    element = document.getElementById(id);
    
    if (lastElement == element) {
        element.classList.toggle("hidden");
        lastElement = null;
    }
    else if(lastElement!=null){
        lastElement.classList.toggle("hidden");
        lastElement = element;

        element.classList.toggle("hidden");
    }
    else {
        element.classList.toggle("hidden")
        lastElement = element;
    }
}

function uploadFile() {
    document.getElementById("file").click();
}

function cancelUpload() {
    document.getElementById("file").value = "";
    document.getElementById("send").disabled = false;
    toggleOption("upload_box");
}