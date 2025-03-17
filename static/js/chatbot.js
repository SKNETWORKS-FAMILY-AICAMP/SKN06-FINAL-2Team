var chatModel = "{{ chat_model }}";  // Django에서 넘긴 모델 값 사용

function getChatHistoryKey() {
    return `chat_history_${chatModel}`;
}

function loadChatHistory() {
    const chatBox = document.getElementById("chat-box");
    if (!chatBox) {
        console.error("🚨 채팅 박스를 찾을 수 없습니다.");
        return;
    }

    const chatHistoryKey = getChatHistoryKey();
    const chatHistory = JSON.parse(localStorage.getItem(chatHistoryKey)) || [];

    chatBox.innerHTML = "";
    chatHistory.forEach(msg => {
        const isAI = msg.startsWith("AI:");
        const messageClass = isAI ? "ai-message" : "user-message";
        const textClass = isAI ? "ai-text" : "user-text";  // 🔹 추가된 부분
        const profileImg = isAI
            ? document.getElementById("chat-container").getAttribute("data-ai-profile") 
            : document.getElementById("chat-container").getAttribute("data-user-profile");

        chatBox.innerHTML += `
            <div class="chat-message ${messageClass}">
                <img src="${profileImg}" class="profile-pic">
                <span class="message-text ${textClass}">${msg.replace("AI:", "").replace("User:", "")}</span>
            </div>`;
    });

    chatBox.scrollTop = chatBox.scrollHeight;
}


function saveChatHistory(message, isAI = false) {
    const chatHistoryKey = getChatHistoryKey();
    let chatHistory = JSON.parse(localStorage.getItem(chatHistoryKey)) || [];
    const prefix = isAI ? "AI: " : "User: ";
    chatHistory.push(prefix + message);
    localStorage.setItem(chatHistoryKey, JSON.stringify(chatHistory));
}

function hasPrologueModal() {
    return document.getElementById("prologue-modal") !== null;
}

document.addEventListener("DOMContentLoaded", function () {
    if (hasPrologueModal()) {
        let modal = document.getElementById("prologue-modal");
        let chatContainer = document.getElementById("chat-container");
        let startChatBtn = document.getElementById("start-chat-btn");
        let sessionKey = `prologueShown_${chatModel}`;

        if (!sessionStorage.getItem(sessionKey)) {
            modal.style.display = "flex";
            chatContainer.style.display = "none";
        } else {
            modal.style.display = "none";
            chatContainer.style.display = "block";
            loadChatHistory();
        }

        if (startChatBtn) {
            startChatBtn.addEventListener("click", function () {
                modal.style.display = "none";
                chatContainer.style.display = "block";
                sessionStorage.setItem(sessionKey, "true");
                setTimeout(() => {
                    chatContainer.scrollIntoView({ behavior: 'smooth' });
                }, 200);
                loadChatHistory();
            });
        }
    } else {
        loadChatHistory();
    }
});

function askChatbot() {
    const questionInput = document.getElementById("question");
    if (!questionInput) return console.error("입력 필드를 찾을 수 없습니다.");

    const question = questionInput.value.trim();
    if (!question) return console.warn("질문이 입력되지 않았으므로 요청을 보내지 않습니다.");

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
    saveChatHistory(question, false);

    questionInput.value = "";
    setTimeout(() => { chatBox.scrollTop = chatBox.scrollHeight; }, 50);

    let loadingMessageDiv = document.createElement("div");
    loadingMessageDiv.classList.add("chat-message", "ai-message");

    const aiProfileImage = document.createElement("img");
    aiProfileImage.src = aiProfileImg;
    aiProfileImage.alt = "AI";
    aiProfileImage.classList.add("profile-pic");

    const aiMessageText = document.createElement("span");
    aiMessageText.classList.add("message-text", "ai-text", "loading-message");
    aiMessageText.innerHTML = `<span class="loading-spinner"></span> AI가 답변을 작성 중입니다...`;

    loadingMessageDiv.appendChild(aiProfileImage);
    loadingMessageDiv.appendChild(aiMessageText);
    chatBox.appendChild(loadingMessageDiv);

    const eventSource = new EventSource(`?question=${encodeURIComponent(question)}`);

    let isFirstResponse = true;

    eventSource.onmessage = function (event) {

        if (event.data === "[DONE]") {
            eventSource.close();
            return;
        }

        const parser = new DOMParser();
        const parsedHtml = parser.parseFromString(event.data, "text/html");

        parsedHtml.querySelectorAll("img").forEach(img => {
            img.style.width = "150px";
            img.style.height = "auto";
        });

        parsedHtml.querySelectorAll("a").forEach(link => {
            let href = link.getAttribute("href");
            link.setAttribute("target", "_blank");
            link.setAttribute("rel", "noopener noreferrer");
        });

        const formattedResponse = parsedHtml.body.innerHTML;

        if (isFirstResponse) {
            aiMessageText.innerHTML = formattedResponse;
            aiMessageText.classList.remove("loading-message");
            isFirstResponse = false;
        } else {
            const newAiMessageDiv = document.createElement("div");
            newAiMessageDiv.classList.add("chat-message", "ai-message");

            const newAiProfileImage = document.createElement("img");
            newAiProfileImage.src = aiProfileImg;
            newAiProfileImage.alt = "AI";
            newAiProfileImage.classList.add("profile-pic");

            const newAiMessageText = document.createElement("span");
            newAiMessageText.classList.add("message-text", "ai-text");
            newAiMessageText.innerHTML = formattedResponse;

            newAiMessageDiv.appendChild(newAiProfileImage);
            newAiMessageDiv.appendChild(newAiMessageText);
            chatBox.appendChild(newAiMessageDiv);
        }

        saveChatHistory(event.data, true);
        setTimeout(() => { chatBox.scrollTop = chatBox.scrollHeight; }, 50);
    };

    eventSource.onerror = function (error) {
        console.error("스트리밍 오류 발생:", error);
        eventSource.close();
        setTimeout(() => { askChatbot(); }, 3000);
    };
}
