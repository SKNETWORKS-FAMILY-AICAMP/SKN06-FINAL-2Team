function selectModel(url) {
    window.location.href = url;
}


function alertLogin() {
    alert('pixary에 회원가입 하시면 더 많은 모델을 사용하실 수 있습니다.');
}


// 캐러셀 환경 설정
const carousel = document.querySelector(".carousel");
if (carousel) {
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

// 모델 선택 및 캐러셀 폴드
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ JS 실행됨! (ChatModel:", ChatModel, ")");
    const modelItems = document.querySelectorAll(".model-item");
    const basicModel = document.querySelector(".model-item[data-name='기본']");
    const selectedModel = localStorage.getItem("selectedModel");
    if (ChatModel === "basic_na") {
        modelItems.forEach(item => item.classList.remove("active"));
        if (basicModel) {
            basicModel.classList.add("active");
        }
    }
    else if (selectedModel) {
        modelItems.forEach(item => {
            if (item.dataset.name === selectedModel) {
                item.classList.add("active");
            }
        });
    }
    modelItems.forEach(item => {
        item.addEventListener("click", function () {
            if (ChatModel === "basic_na") {
                return;
            }
            modelItems.forEach(i => i.classList.remove("active"));
            this.classList.add("active");
            localStorage.setItem("selectedModel", this.dataset.name);
        });
    });

    const carouselContainer = document.querySelector(".recommendation-section");
    const toggleBtn = document.getElementById("toggleCarouselBtn");
    if (carousel) {
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
    }
});