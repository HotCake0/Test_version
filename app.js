// ★ Sir가 Firebase Console에서 확인 후 교체
const FIREBASE_URL = 'https://goraecity-default-rtdb.asia-southeast1.firebasedatabase.app/';

// ─────────────────────────────────────────
// 상태
// ─────────────────────────────────────────
let allMembers = {};    // { bj_id: { name, is_live, title, viewers, thumbnail, live_url } }
let selectedIds = [];  // 현재 선택된 멤버 ID 목록 (최대 4)
let headerMode = 'expanded'; // expanded | collapsed | hidden

// ─────────────────────────────────────────
// Firebase에서 데이터 가져오기
// ─────────────────────────────────────────
async function fetchData() {
    try {
        // members와 status 병렬로 fetch
        const [membersRes, statusRes] = await Promise.all([
            fetch(`${FIREBASE_URL}/members.json`),
            fetch(`${FIREBASE_URL}/status.json`)
        ]);

        const members = await membersRes.json();
        const status  = await statusRes.json();

        if (!members) return;

        // members + status 합치기
        allMembers = {};
        for (const [bj_id, info] of Object.entries(members)) {
            const s = status?.[bj_id] || {};
            allMembers[bj_id] = {
                id: bj_id,
                name: info.name,
                is_live: s.is_live || false,
                title: s.title || '',
                viewers: s.viewers || 0,
                thumbnail: s.thumbnail || '',
                live_url: s.live_url || ''
            };
        }

        renderWaitingRoom();
        renderHeaderList();

    } catch (e) {
        console.error('데이터 불러오기 실패:', e);
    }
}

// ─────────────────────────────────────────
// 대기실 렌더링
// ─────────────────────────────────────────
function renderWaitingRoom() {
    const grid = document.getElementById('wr-grid');
    const liveMembers = Object.values(allMembers).filter(m => m.is_live);

    if (liveMembers.length === 0) {
        grid.innerHTML = `
            <div style="grid-column:1/-1; text-align:center; color:rgba(255,255,255,0.3); padding: 60px 0;">
                <div style="font-size:3rem; margin-bottom:16px;">🐳</div>
                <div style="font-size:1rem; font-weight:600;">현재 방송 중인 멤버가 없습니다.</div>
            </div>
        `;
        return;
    }

    // 시청자 수 내림차순 정렬
    liveMembers.sort((a, b) => b.viewers - a.viewers);

    grid.innerHTML = liveMembers.map(m => `
        <div class="wr-card" onclick="selectFromWaiting('${m.id}')">
            <img
                src="${m.thumbnail}"
                alt="${m.name}"
                onerror="this.src='https://via.placeholder.com/320x180/141414/444?text=LIVE'"
            />
            <span class="wr-badge">LIVE</span>
            <div class="wr-info">
                <div class="wr-name">${m.name}</div>
                <div class="wr-title-text">${m.title || '방송 중'}</div>
                <div class="wr-viewers">👁 ${m.viewers.toLocaleString()}명 시청 중</div>
            </div>
        </div>
    `).join('');
}

// ─────────────────────────────────────────
// 헤더 멤버 리스트 렌더링
// ─────────────────────────────────────────
function renderHeaderList() {
    const list = document.getElementById('member-list');
    const liveMembers = Object.values(allMembers).filter(m => m.is_live);

    if (liveMembers.length === 0) {
        list.innerHTML = `<span style="color:rgba(255,255,255,0.3); font-size:0.85rem; line-height:50px;">방송 중인 멤버 없음</span>`;
        return;
    }

    liveMembers.sort((a, b) => b.viewers - a.viewers);

    list.innerHTML = liveMembers.map(m => {
        const isActive = selectedIds.includes(m.id);
        return `
            <div class="member-item ${isActive ? 'active' : ''}" onclick="toggleMember('${m.id}')">
                <img
                    class="member-thumb"
                    src="${m.thumbnail}"
                    alt="${m.name}"
                    onerror="this.src='https://via.placeholder.com/140x79/141414/444?text=${encodeURIComponent(m.name)}'"
                />
                <div class="member-info">
                    <div class="member-name">${m.name}</div>
                    <div class="member-status">👁 ${m.viewers.toLocaleString()}</div>
                </div>
            </div>
        `;
    }).join('');
}

// ─────────────────────────────────────────
// 대기실에서 멤버 선택
// ─────────────────────────────────────────
function selectFromWaiting(bj_id) {
    if (!selectedIds.includes(bj_id)) {
        if (selectedIds.length >= 4) {
            // 가장 먼저 선택된 것 제거
            selectedIds.shift();
        }
        selectedIds.push(bj_id);
    }
    hideWaitingRoom();
    renderGrid();
    renderHeaderList();
    updateSelectedCount();
}

// ─────────────────────────────────────────
// 헤더에서 멤버 토글
// ─────────────────────────────────────────
function toggleMember(bj_id) {
    if (selectedIds.includes(bj_id)) {
        // 이미 선택된 경우 제거
        selectedIds = selectedIds.filter(id => id !== bj_id);
    } else {
        if (selectedIds.length >= 4) {
            alert('최대 4개까지 동시 시청 가능합니다.');
            return;
        }
        selectedIds.push(bj_id);
    }
    renderGrid();
    renderHeaderList();
    updateSelectedCount();
}

// ─────────────────────────────────────────
// 비디오 그리드 렌더링
// ─────────────────────────────────────────
function renderGrid() {
    const grid = document.getElementById('view-grid');
    const count = selectedIds.length;

    if (count === 0) {
        grid.className = 'grid-1';
        grid.innerHTML = `
            <div class="empty-msg">
                <h2>화면을 선택해주세요</h2>
                <button onclick="showWaitingRoom()">대기실 열기</button>
            </div>
        `;
        return;
    }

    // 그리드 클래스 설정
    grid.className = `grid-${count}`;

    grid.innerHTML = selectedIds.map(bj_id => {
        const m = allMembers[bj_id];
        if (!m) return '';

        // SOOP 임베드 URL
        const embedUrl = `https://play.sooplive.co.kr/${m.id}?embedded=1&auto_play=true`;

        return `
            <div class="video-wrapper">
                <iframe
                    src="${embedUrl}"
                    allowfullscreen
                    scrolling="no"
                ></iframe>
                <button class="close-btn" onclick="removeStream('${m.id}')" title="닫기">✕</button>
            </div>
        `;
    }).join('');
}

// ─────────────────────────────────────────
// 스트림 제거
// ─────────────────────────────────────────
function removeStream(bj_id) {
    selectedIds = selectedIds.filter(id => id !== bj_id);
    renderGrid();
    renderHeaderList();
    updateSelectedCount();
}

// ─────────────────────────────────────────
// 선택 카운트 업데이트
// ─────────────────────────────────────────
function updateSelectedCount() {
    document.getElementById('selected-count').textContent = selectedIds.length;
}

// ─────────────────────────────────────────
// 대기실 표시 / 숨김
// ─────────────────────────────────────────
function showWaitingRoom() {
    document.getElementById('waiting-room').classList.remove('hidden');
}

function hideWaitingRoom() {
    document.getElementById('waiting-room').classList.add('hidden');
}

// ─────────────────────────────────────────
// 헤더 모드 전환 (expanded → collapsed → hidden → expanded)
// ─────────────────────────────────────────
function toggleHeaderMode() {
    const header = document.getElementById('main-header');
    const btn = document.getElementById('toggle-view-btn');

    if (headerMode === 'expanded') {
        headerMode = 'collapsed';
        header.className = 'collapsed';
        btn.textContent = '▶ 더보기';
    } else if (headerMode === 'collapsed') {
        headerMode = 'hidden';
        header.className = 'hidden';
        btn.textContent = '◀ 펼치기';
    } else {
        headerMode = 'expanded';
        header.className = 'expanded';
        btn.textContent = '🔽 접기';
    }
}

// ─────────────────────────────────────────
// 60초마다 자동 갱신
// ─────────────────────────────────────────
fetchData();
setInterval(fetchData, 60 * 1000);
