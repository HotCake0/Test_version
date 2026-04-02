/**
 * 뉴스 섹션으로 스크롤
 */
function scrollToNews() {
    const newsSection = document.getElementById('newsSection');
    newsSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * 최상단으로 스크롤
 */
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * 더보기 / 접기 토글
 */
function toggleMore() {
    const extra = document.getElementById('patchExtra');
    const arrow = document.getElementById('moreArrow');
    const text = document.getElementById('moreBtnText');

    if (extra.classList.contains('hidden')) {
        extra.classList.remove('hidden');
        extra.classList.add('visible');
        arrow.classList.add('rotated');
        text.textContent = '접기';
    } else {
        extra.classList.remove('visible');
        extra.classList.add('hidden');
        arrow.classList.remove('rotated');
        text.textContent = '더보기';
    }
}

/**
 * 스크롤 시 헤더 스타일 변경
 */
window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

/**
 * 패치노트가 3개 이하면 더보기 버튼 숨김
 */
window.addEventListener('DOMContentLoaded', () => {
    const extra = document.getElementById('patchExtra');
    const moreBtnWrap = document.getElementById('moreBtnWrap');

    // patchExtra 안에 patch-note가 없으면 더보기 버튼 숨김
    const extraNotes = extra.querySelectorAll('.patch-note');
    if (extraNotes.length === 0) {
        moreBtnWrap.style.display = 'none';
    }
});
