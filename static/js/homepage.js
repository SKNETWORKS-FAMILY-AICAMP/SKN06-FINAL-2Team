document.addEventListener("DOMContentLoaded", function () {
    const textElement = document.getElementById("typing-text");
    const imageElement = document.getElementById("image");

    // 문장과 이미지 배열
    const sentences = [
        '"패는 신이 주었지만, 어떻게 쓸 지는 내 자유다."',
        '"잊었나? 사랑한다고 했을텐데. 그쪽."',
        '"우리의 끝. 그것이 이 이야기의 진정한 마지막이야."',
        '"강자가 법이요, 힘이 정의다. 약자가 무슨 말을 보태겠느냐?"'
    ];

    const colors = ["#D8BFD8", "#FFB6C1", "#FFFACD", "#ADD8E6"]; 
    let index = 0;
    let isRight = false; 
    const margins = ["45%", "10%", "40%", "5%"]; 
    let charIndex = 0;
    let text = "";

    function typeSentence(sentence, i) {
        if (i === 0) {
            textElement.style.color = colors[index % colors.length]; // 랜덤 색상 적용
            textElement.style.marginLeft = margins[index]; // 문장별 위치 조정
            textElement.innerHTML = ""; // ✅ 새로운 문장 시작 시 텍스트 초기화
        }

        if (i < sentence.length) {
            textElement.innerHTML = sentence.substring(0, i + 1); // ✅ 커서 없이 타이핑 효과 적용
            setTimeout(() => typeSentence(sentence, i + 1), 60);
        } else {
            setTimeout(nextSentence, 2000); // 2초 후 다음 문장 출력
        }
    }

    function nextSentence() {
        index = (index + 1) % sentences.length;
        textElement.innerHTML = ""; // 텍스트 초기화

        // 이미지 변경 애니메이션 및 위치 변경
        imageElement.style.opacity = "0";
        setTimeout(() => {
            imageElement.src = `/static/img/homepage/homepage_character_${index + 1}.png`;
            imageElement.style.opacity = "1";

            // 이미지가 왼쪽, 오른쪽 번갈아가며 위치 변경
            if (isRight) {
                imageElement.classList.remove("right-position");
                imageElement.classList.add("left-position");
            } else {
                imageElement.classList.remove("left-position");
                imageElement.classList.add("right-position");
            }

            isRight = !isRight; // 위치를 번갈아가도록 변경
            typeSentence(sentences[index], 0);
        }, 500);
    }

    // 첫 시작은 왼쪽에서 시작
    imageElement.classList.add("left-position");
    textElement.classList.add("left-text");

    // 첫 문장 시작
    imageElement.src = "/static/img/homepage/homepage_character_1.png";
    imageElement.style.opacity = "1"; 
    textElement.style.marginLeft = margins[0]; // ✅ 첫 문장의 왼쪽 여백 적용
    typeSentence(sentences[0], 0);
});
