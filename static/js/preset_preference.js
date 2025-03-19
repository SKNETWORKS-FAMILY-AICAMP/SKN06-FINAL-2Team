document.addEventListener("DOMContentLoaded", function () {
    let notification = document.querySelector(".notification-box");
    let overlay = document.querySelector(".overlay");

    setTimeout(() => {
        notification.style.opacity = "0";
        overlay.style.opacity = "0";
        setTimeout(() => {
            notification.remove();
            overlay.remove();
        }, 500);
    }, 3000);
});

function toggleSelection(element, contentId) {
    let checkbox = element.querySelector(".hidden-checkbox");

    if (checkbox.checked) {
        checkbox.checked = false;
        element.classList.remove("selected");
    } else {
        checkbox.checked = true;
        element.classList.add("selected");
    }
}

document.getElementById("preference-form").onsubmit = function(event) {
    event.preventDefault();
    
    let selectedWorks = [...document.querySelectorAll("input[name='works']:checked")]
    .map(input => input.value.trim())
    .filter(value => value !== "");
    
    if (selectedWorks.length === 0) {
        alert("최소한 하나의 작품을 선택해주세요!");
        return;
    }

    let loadingOverlay = document.getElementById("loadingOverlay");
    if (loadingOverlay) {
        loadingOverlay.style.display = "flex";
    }
    let formData = new FormData();
    selectedWorks.forEach(work => formData.append("works", work));

    fetch("/account/preset_preference/", {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect) {
            window.location.href = data.redirect;
        } else if (data.error) {
            document.getElementById("loadingOverlay").classList.add("hidden");
            alert(data.error);
        }
    })
    .catch(error => {
        document.getElementById("loadingOverlay").classList.add("hidden");
        console.error("Error:", error)});
};