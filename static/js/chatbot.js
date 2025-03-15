// 프롤로그
document.addEventListener("DOMContentLoaded", function () {
    let modal = document.getElementById("prologue-modal");
    let chatContainer = document.getElementById("chat-container");
    let startChatBtn = document.getElementById("start-chat-btn");

    if (startChatBtn) {
        startChatBtn.addEventListener("click", function () {
            if (modal && chatContainer) {
                modal.style.display = "none";
                chatContainer.style.display = "block";
                setTimeout(() => {
                    chatContainer.scrollIntoView({ behavior: 'smooth' });
                }, 200);
            } else {
                console.error("모달 또는 채팅창 요소를 찾을 수 없습니다.");
            }
        });
    } else {
        console.error("'대화를 시작합니다' 버튼을 찾을 수 없습니다.");
    }
});

document.addEventListener("DOMContentLoaded", function () {
    // 프롤로그 이미지 추가할 리스트(이미지 배열)

    let index = 0; // 현재 이미지 인덱스
    const modalImage = document.querySelector("#prologue-modal img");

    function changeImage() {
        index = (index + 1) % images.length;
        modalImage.src = images[index];
    }

    // 5초마다 이미지 변경
    setInterval(changeImage, 3000);
});

// AI 및 사용자 응답 출력
function askChatbot() {
    const question = document.getElementById("question").value.trim();
    if (!question) return;

    const chatBox = document.getElementById("chat-box");
    const chatContainer = document.getElementById("chat-container");
    const userProfileImg = chatContainer.getAttribute("data-user-profile");
    const aiProfileImg = chatContainer.getAttribute("data-ai-profile");

    const userMessage = `
        <div class="chat-message user-message">
            <img src="${userProfileImg}" alt="User" class="profile-pic">
            <span class="message-text user-text">${question}</span>
        </div>`;
    chatBox.innerHTML += userMessage;
    document.getElementById("question").value = "";
    setTimeout(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 50);


    fetch(`?question=${encodeURIComponent(question)}`)
        .then(response => response.text())
        .then(data => {
            const aiMessageContent = sanitizeAIResponse(data);

            const aiMessage = `
                <div class="chat-message ai-message">
                    <img src="${aiProfileImg}" alt="AI" class="profile-pic">
                    <span class="message-text ai-text">${aiMessageContent}</span>
                </div>`;
            chatBox.innerHTML += aiMessage;
            setTimeout(() => {
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 50);
        })
        .catch(error => console.error("오류 발생:", error));
}

// AI 응답 포맷
function sanitizeAIResponse(data) {
    let cleanedData = data.replace(/<\/?p>/g, "").trim();
    cleanedData = cleanedData.replace(
        /<a /g,
        '<a target="_blank" rel="noopener noreferrer" '
    );
    cleanedData = cleanedData.replace(
        /<img /g,
        '<img style="max-width: 150px; max-height: 150px; display: block; margin: 5px 0;" '
    );
    cleanedData = cleanedData.replace(/\n{2,}/g, "\n");
    cleanedData = cleanedData.replace(/(<br\s*\/?>\s*){2,}/g, "<br>");
    return cleanedData;
}

