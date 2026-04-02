/**
 * 뉴스(패치노트) 페이지 표시
 */
function showNews() {
    const mainPage = document.getElementById('mainPage');
    const newsPage = document.getElementById('newsPage');
    
    // 메인 사라짐
    mainPage.style.opacity = '0';
    setTimeout(() => {
        mainPage.style.display = 'none';
        
        // 뉴스 나타남
        newsPage.style.display = 'flex';
        setTimeout(() => {
            newsPage.style.opacity = '1';
        }, 50);
    }, 400);
}

/**
 * 메인 페이지 표시
 */
function showMain() {
    const mainPage = document.getElementById('mainPage');
    const newsPage = document.getElementById('newsPage');

    // 뉴스 사라짐
    newsPage.style.opacity = '0';
    setTimeout(() => {
        newsPage.style.display = 'none';
        
        // 메인 나타남
        mainPage.style.display = 'flex';
        setTimeout(() => {
            mainPage.style.opacity = '1';
        }, 50);
    }, 400);
}

// 윈도우 로드 시 애니메이션 효과 (선택사항)
window.onload = () => {
    document.getElementById('mainPage').style.opacity = '1';
};
