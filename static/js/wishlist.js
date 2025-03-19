// (2) 저장 버튼 클릭 → 폼 제출 시 '로딩 중' 오버레이 표시
document.addEventListener('DOMContentLoaded', () => {
const wishlistForm = document.getElementById('wishlistForm');
const loadingOverlay = document.getElementById('loadingOverlay');

wishlistForm.addEventListener('submit', () => {
    // 폼 전송 직후 로딩 오버레이 표시
    loadingOverlay.classList.remove('hidden');
});
});
function toggleDelete(iconElement) {
    // iconElement는 위의 <img class="delete-icon"> 태그
    // 같은 wishlist-item 내부의 체크박스 찾기
    const parentItem = iconElement.closest('.wishlist-item');
    const checkbox = parentItem.querySelector('.delete-checkbox');
    const nonclick = iconElement.getAttribute('data-non-click');
    const click = iconElement.getAttribute('data-click');

    // 체크박스 상태 on/off 전환
    checkbox.checked = !checkbox.checked;

    // 체크박스가 켜지면 bin_checked, 꺼지면 bin
    if (checkbox.checked) {
        iconElement.src = click;
    } else {
        iconElement.src = nonclick;
    }
}