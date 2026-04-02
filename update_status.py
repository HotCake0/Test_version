import json
import asyncio
import aiohttp
import os
import firebase_admin
from firebase_admin import credentials, db

# ─────────────────────────────────────────
# Firebase 초기화
# ─────────────────────────────────────────
def initialize_firebase():
    if not firebase_admin._apps:
        key_json = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
        cred = credentials.Certificate(key_json)
        firebase_admin.initialize_app(cred, {
            # ★ Sir가 Firebase Console에서 확인 후 교체
            'databaseURL': 'https://YOUR_PROJECT_ID-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })

# ─────────────────────────────────────────
# Firebase에서 멤버 목록 불러오기
# ─────────────────────────────────────────
def fetch_members() -> dict:
    """
    Firebase members 노드에서 { bj_id: { name: "..." }, ... } 형태로 반환
    """
    ref = db.reference('members')
    data = ref.get()
    if not data:
        print("⚠️  Firebase members 노드가 비어있습니다.")
        return {}
    return data  # { "bach023": { "name": "울산큰고래" }, ... }

# ─────────────────────────────────────────
# 단일 멤버 방송 상태 확인 (비동기)
# ─────────────────────────────────────────
async def check_member_live(session: aiohttp.ClientSession, bj_id: str, bj_name: str) -> dict:
    url = f"https://bjapi.afreecatv.com/api/{bj_id}/station"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=7)) as resp:
            data = await resp.json(content_type=None)
            broad_data = data.get("broad")

            if broad_data:
                broad_no = broad_data.get("broad_no")
                return {
                    "id": bj_id,
                    "name": bj_name,
                    "is_live": True,
                    "title": broad_data.get("broad_title", ""),
                    "viewers": broad_data.get("current_sum_viewer", 0),
                    "thumbnail": f"https://liveimg.afreecatv.com/m/{broad_no}",
                    "live_url": f"https://play.sooplive.co.kr/{bj_id}/{broad_no}"
                }
            else:
                return {"id": bj_id, "name": bj_name, "is_live": False}

    except Exception as e:
        print(f"  ✗ [{bj_name}] 오류: {e}")
        return {"id": bj_id, "name": bj_name, "is_live": False}

# ─────────────────────────────────────────
# 전체 멤버 병렬 처리
# ─────────────────────────────────────────
async def check_all_members(members: dict) -> dict:
    """
    members: { bj_id: { name: "..." }, ... }
    100명 이상 대응 - 50명씩 청크로 나눠서 병렬 처리 (API 부하 분산)
    """
    items = [(bj_id, info["name"]) for bj_id, info in members.items()]
    results = {}
    chunk_size = 50  # 한 번에 처리할 최대 동시 요청 수

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            print(f"  → {i+1}~{i+len(chunk)}번 멤버 확인 중...")

            tasks = [check_member_live(session, bj_id, bj_name) for bj_id, bj_name in chunk]
            chunk_results = await asyncio.gather(*tasks)

            for result in chunk_results:
                results[result["id"]] = result

            # 청크 간 짧은 딜레이 (API 부하 방지)
            if i + chunk_size < len(items):
                await asyncio.sleep(0.5)

    return results

# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
if __name__ == '__main__':
    initialize_firebase()

    print("📋 멤버 목록 불러오는 중...")
    members = fetch_members()
    print(f"  → 총 {len(members)}명 로드 완료")

    print("\n📡 방송 상태 확인 중...")
    results = asyncio.run(check_all_members(members))

    # 방송 중인 멤버 수 출력
    live_count = sum(1 for v in results.values() if v.get("is_live"))
    print(f"\n✅ 완료: {live_count}/{len(results)}명 방송 중")

    print("\n🔥 Firebase 업데이트 중...")
    try:
        ref = db.reference('status')
        ref.set(results)
        print("  → Firebase 업데이트 완료!")
    except Exception as e:
        print(f"  ✗ Firebase 전송 실패: {e}")
