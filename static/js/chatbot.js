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
    const modalImage = document.querySelector("#prologue-modal img");

    if (typeof images === "undefined" || !Array.isArray(images) || images.length === 0) {
        console.warn("images 변수가 정의되지 않았거나 비어 있음. 이미지 변경을 생략합니다.");
        return;
    }

    let index = 0;

    function changeImage() {
        index = (index + 1) % images.length;
        modalImage.src = images[index];
    }

    setInterval(changeImage, 3000);
});

document.addEventListener("DOMContentLoaded", function () {
    const questionInput = document.getElementById("question");
    if (!questionInput) {
        console.error("입력 필드를 찾을 수 없습니다.");
        return;
    }

    questionInput.addEventListener("keypress", function (event) {
        if (event.keyCode === 13) {
            askChatbot();
        }
    });
});

function fixKakaoThumbnailUrl(url) {
    // 🔹 카카오페이지 이미지 URL을 변환하는 함수
    if (url.includes("kid=")) {
        const kidValue = new URL(url).searchParams.get("kid");
        return `https://dn-img-page.kakao.com/download/resource?kid=${kidValue}`;
    }
    return url; // 변환이 필요 없는 경우 그대로 반환
}

// AI 및 사용자 응답 출력
function askChatbot() {
    const questionInput = document.getElementById("question");
    if (!questionInput) {
        console.error("🚨 입력 필드(#question`)를 찾을 수 없습니다.");
        return;
    }

    const question = questionInput.value.trim();
    if (!question) {
        console.warn("🚨 질문이 입력되지 않았으므로 요청을 보내지 않습니다.");
        return;
    }

    console.log("📌 사용자 질문:", question);

    const chatBox = document.getElementById("chat-box");
    const chatContainer = document.getElementById("chat-container");
    const userProfileImg = chatContainer.getAttribute("data-user-profile");
    const aiProfileImg = chatContainer.getAttribute("data-ai-profile");

    // 🔹 사용자 메시지 추가
    const userMessage = document.createElement("div");
    userMessage.classList.add("chat-message", "user-message");

    const userProfileImage = document.createElement("img");
    userProfileImage.src = userProfileImg;
    userProfileImage.alt = "User";
    userProfileImage.classList.add("profile-pic");

    const userMessageText = document.createElement("span");
    userMessageText.classList.add("message-text", "user-text");
    userMessageText.textContent = question;

    userMessage.appendChild(userProfileImage);
    userMessage.appendChild(userMessageText);
    chatBox.appendChild(userMessage);

    questionInput.value = ""; // 입력 필드 초기화

    setTimeout(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 50);

    let loadingMessageDiv = document.createElement("div");
    loadingMessageDiv.classList.add("chat-message", "ai-message");

    const aiProfileImage = document.createElement("img");
    aiProfileImage.src = aiProfileImg;
    aiProfileImage.alt = "AI";
    aiProfileImage.classList.add("profile-pic");

    const aiMessageText = document.createElement("span");
    aiMessageText.classList.add("message-text", "ai-text", "loading-message");
    aiMessageText.innerHTML = `
        <span class="loading-spinner"></span> AI가 답변을 작성 중입니다...
    `;

    loadingMessageDiv.appendChild(aiProfileImage);
    loadingMessageDiv.appendChild(aiMessageText);
    chatBox.appendChild(loadingMessageDiv);

    // 🔹 EventSource를 사용하여 실시간 응답 수신
    const eventSource = new EventSource(`?question=${encodeURIComponent(question)}`);

    let isFirstResponse = true; // 🔹 첫 번째 응답인지 확인

    eventSource.onmessage = function (event) {
        console.log("📌 받은 AI 응답:", event.data);

        if (event.data === "[DONE]") {
            console.log("📌 AI 응답 완료, 스트리밍 종료");
            eventSource.close();
            return;
        }
        
        // 🔹 AI 응답을 HTML로 변환
        const parser = new DOMParser();
        const parsedHtml = parser.parseFromString(event.data, "text/html");

        // 🔹 이미지 크기 조정 (모든 <img> 태그의 너비를 150px로 설정)
        parsedHtml.querySelectorAll("img").forEach(img => {
            img.style.width = "150px";
            img.style.height = "auto";
        });

        parsedHtml.querySelectorAll("a").forEach(link => {
            let href = link.getAttribute("href");
            if (href.includes("kid=")) {
                const imageUrl = fixKakaoThumbnailUrl(href);

                // 🔹 새로운 `<img>` 태그 생성
                const imgElement = document.createElement("img");
                imgElement.src = imageUrl;
                imgElement.alt = "썸네일 이미지";
                imgElement.style.width = "150px";
                imgElement.style.height = "auto";

                // 🔹 `<a>` 태그를 `<img>` 태그로 대체
                link.replaceWith(imgElement);
            } else {
                // 🔹 `kid=`가 없는 일반 링크는 유지
                link.setAttribute("target", "_blank");
                link.setAttribute("rel", "noopener noreferrer");
            }
        });

        const formattedResponse = parsedHtml.body.innerHTML;

        if (isFirstResponse) {
            // 🔹 첫 번째 응답이면 기존 로딩 메시지를 응답으로 대체
            aiMessageText.innerHTML = formattedResponse;
            aiMessageText.classList.remove("loading-message"); // 스타일 제거
            isFirstResponse = false;
        } else {
            // 🔹 두 번째 응답부터는 새로운 채팅 박스를 추가
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

        setTimeout(() => {
            chatBox.scrollTop = chatBox.scrollHeight;
        }, 50);
    };

    eventSource.onerror = function (error) {
        console.error("🚨 스트리밍 오류 발생:", error);
        eventSource.close();

        setTimeout(() => {
            askChatbot(); // 🔹 다시 실행하여 자동 복구
        }, 3000); // 3초 후 재연결
    };
}