const quotes = [
    '"이 몸이 직접 고른 웹툰이다. 감히 거절할 생각은 하지 마!"',
    '"영애, 북부의 혹독한 추위에도 불꽃처럼 타오르는 이 이야기 한 번 살펴보시겠습니까?"',
    '"첫사랑이 나오는 웹소설을 찾는다고요? ...하아, 왜 하필 첫사랑이죠?"',
    '"강자가 법이요, 힘이 정의다. 약자가 무슨 말을 보태겠느냐?"',
    '"우리, 할 얘기가 있지 않아요? 오늘 저녁 어때요."'
];

let currentQuoteIndex = 0;
let quoteElement = document.getElementById("quote");
let text = "";
let charIndex = 0;
let typingSpeed = 50; // 타이핑 속도 (밀리초)

function typeText() {
    if (charIndex < text.length) {
        quoteElement.innerHTML += text.charAt(charIndex);
        charIndex++;
        setTimeout(typeText, typingSpeed);
    } else {
        setTimeout(nextQuote, 2000); // 2초 대기 후 다음 문구 출력
    }
}

function nextQuote() {
    quoteElement.innerHTML = ""; // 이전 문구 삭제
    currentQuoteIndex = (currentQuoteIndex + 1) % quotes.length; // 다음 문구로 변경
    text = quotes[currentQuoteIndex]; // 새 문구 가져오기
    charIndex = 0;
    typeText();
}

// 첫 번째 문장 시작
text = quotes[currentQuoteIndex];
typeText();
