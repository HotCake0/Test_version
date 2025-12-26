import json
import requests
import os

# 팀 리스트 정의
red_team = {
    "joyjo2": "쪼이", "wkdghdtjr99": "여백이다", "niniming": "니니밍",
    "doki0818": "감자가비", "khj011219": "기찬하", "015234": "아눙",
    "isq1158": "구월이", "eun0333": "우미", "jjoasseo13": "죠아써", "kayooo": "용아리"
}

blue_team = {
    "rkdalstnld": "주드", "gtw0308": "황정민", "star124": "하밍",
    "villlo": "왜냐니", "toocat030": "또오냥", "xpdpfv2": "이지수",
    "rjsdnr115": "고채린", "yotsubakoe": "코에", "etwo22": "이투", "o0opha": "서라0"
}

# [추가] 진행팀(매니저) 리스트
manager_team = {
    "melodingding": "멜로딩딩"
}

def check_member_live(bj_id, bj_name):
    url = f"https://bjapi.afreecatv.com/api/{bj_id}/station"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        broad_data = data.get("broad")
        if broad_data:
            broad_no = broad_data.get("broad_no")
            return {
                "id": bj_id,
                "name": bj_name,
                "is_live": True,
                "title": broad_data.get('broad_title', ''),
                "viewers": broad_data.get('current_sum_viewer', 0),
                "thumbnail": f"https://liveimg.afreecatv.com/m/{broad_no}",
                "live_url": f"https://play.sooplive.co.kr/{bj_id}/{broad_no}"
            }
        return {"id": bj_id, "name": bj_name, "is_live": False}
    except:
        return {"id": bj_id, "name": bj_name, "is_live": False}

def save_team_status(team_dict, filename):
    results = []
    for bj_id, bj_name in team_dict.items():
        info = check_member_live(bj_id, bj_name)
        results.append(info)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"✅ {filename} 업데이트 완료!")

if __name__ == '__main__':
    save_team_status(red_team, 'red_team_status.json')
    save_team_status(blue_team, 'blue_team_status.json')
    # [추가] 진행팀 파일 생성
    save_team_status(manager_team, 'manager_status.json')
