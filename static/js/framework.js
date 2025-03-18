function selectModel(url) {
    window.location.href = url;
}


function alertLogin() {
    alert('pixary에 회원가입 하시면 더 많은 모델을 사용하실 수 있습니다.');
}


// 캐러셀 환경 설정
const carousel = document.querySelector(".carousel");
let scrollAmount = 0;
let scrollMax = carousel.scrollWidth - carousel.clientWidth;

function scrollNext() {
    if (scrollAmount < scrollMax) {
        scrollAmount += 300;
        carousel.scrollTo({ left: scrollAmount, behavior: "smooth" });
    }
}
function scrollPrev() {
    if (scrollAmount > 0) {
        scrollAmount -= 300;
        carousel.scrollTo({ left: scrollAmount, behavior: "smooth" });
    }
}

// 움직이기
document.addEventListener("DOMContentLoaded", function () {
    const images = document.querySelectorAll(".carousel img");
    const prevBtn = document.querySelector(".prev-btn");
    const nextBtn = document.querySelector(".next-btn");

    
    let index = 0;
    const totalImages = images.length;
    if (totalImages === 0) {
        return;
    }

    const imgWidth = images[0].offsetWidth + 20;

    nextBtn.addEventListener("click", function () {
        if (index < totalImages - 8) {
            index++;
            carousel.style.transform = `translateX(-${index * imgWidth}px)`;
        }
    });

    prevBtn.addEventListener("click", function () {
        if (index > 0) {
            index--;
            carousel.style.transform = `translateX(-${index * imgWidth}px)`;
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const modelItems = document.querySelectorAll(".model-item");

    // 🔹 로컬스토리지에서 마지막으로 선택한 모델 가져오기
    const selectedModel = localStorage.getItem("selectedModel");

    if (selectedModel) {
        modelItems.forEach(item => {
            if (item.dataset.name === selectedModel) {
                item.classList.add("active");
            }
        });
    }

    modelItems.forEach(item => {
        item.addEventListener("click", function () {
            // 모든 원에서 active 클래스 제거
            modelItems.forEach(i => i.classList.remove("active"));

            // 클릭한 원에 active 클래스 추가
            this.classList.add("active");

            // 🔹 선택한 모델을 localStorage에 저장
            localStorage.setItem("selectedModel", this.dataset.name);
        });
    });

    // 🔹 버튼 동작 (추천 캐러셀 토글 기능)
    const carouselContainer = document.querySelector(".recommendation-section");
    const toggleBtn = document.getElementById("toggleCarouselBtn");

    carouselContainer.style.height = "0px";

    toggleBtn.addEventListener("click", function () {
        if (carouselContainer.style.height === "0px") {
            carouselContainer.style.height = "280px";
            carouselContainer.style.padding = "10px 0px 0px 0px";
        } else {
            carouselContainer.style.height = "0px";
            carouselContainer.style.padding = "0";
        }
    });
});