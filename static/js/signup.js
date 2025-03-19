document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    
    form.addEventListener("submit", function (event) {
        const password1 = document.getElementById("password1").value;
        const password2 = document.getElementById("password2").value;
        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const birthday = new Date(document.getElementById("birthday").value);
        const today = new Date();
        const age = today.getFullYear() - birthday.getFullYear();

        // 닉네임 특수문자 체크
        const specialCharPattern = /[!@#$%^&*(),.?":{}|<>]/;
        if (specialCharPattern.test(username)) {
            alert("닉네임에 특수문자는 사용할 수 없습니다.");
            event.preventDefault();
        }

        // 이메일 형식 체크
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailPattern.test(email)) {
            alert("올바른 이메일 형식이 아닙니다.");
            event.preventDefault();
        }

        // 비밀번호 일치 확인
        if (password1 !== password2) {
            alert("비밀번호가 일치하지 않습니다.");
            event.preventDefault();
        }

        // 비밀번호 복잡성 체크
        if (
            password1.length < 8 ||
            !/[a-z]/.test(password1) ||
            !/[0-9]/.test(password1) ||
            !/[!@#$%^&*(),.?":{}|<>]/.test(password1)
        ) {
            alert("비밀번호는 8자 이상이며, 소문자, 숫자, 특수문자를 포함해야 합니다.");
            event.preventDefault();
        }

        // 나이 제한 (만 8세 이상, 120세 이하)
        if (age < 8 || age > 120) {
            alert("만 8세 이상 120세 이하만 가입 가능합니다.");
            event.preventDefault();
        }
    });
});
