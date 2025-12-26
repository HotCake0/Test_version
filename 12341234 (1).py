import json
import requests
import os

# 1. 팀 리스트 정의 (문법 오류 수정 완료)
red_team = {
    "joyjo2": "쪼이",
    "wkdghdtjr99": "여백이다",
    "niniming": "니니밍",
    "doki0818": "감자가비",
    "khj011219": "기찬하",
    "015234": "아눙",
    "isq1158": "구월이",
    "eun0333": "우미",
    "jjoasseo13": "죠아써",
    "kayooo": "용아리"
}

blue_team = {
    "rkdalstnld": "주드",
    "gtw0308": "황정민",
    "star124": "하밍",
    "villlo": "왜냐니",
    "toocat030": "또오냥",
    "xpdpfv2": "이지수",
    "rjsdnr115": "고채린",
    "yotsubakoe": "코에",
    "etwo22": "이투",
    "o0opha": "서라0"
}

def check_member_live(bj_id, bj_name):
    """BJ의 방송 상태를 확인하는 함수"""
    url = f"https://bjapi.afreecatv.com/api/{bj_id}/station"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        broad_data = data.get("broad")
        
        if broad_data:
            broad_no = broad_data.get("broad_no")
            thumb_url = f"https://liveimg.afreecatv.com/m/{broad_no}"
            live_url = f"https://play.sooplive.co.kr/{bj_id}/{broad_no}"
            
            return {
                "id": bj_id,
                "name": bj_name,
                "is_live": True,
                "title": broad_data.get('broad_title', ''),
                "viewers": broad_data.get('current_sum_viewer', 0),
                "thumbnail": thumb_url,
                "live_url": live_url
            }
        else:
            return {"id": bj_id, "name": bj_name, "is_live": False}
    except Exception as e:
        print(f"Error {bj_name}({bj_id}): {e}")
        return {"id": bj_id, "name": bj_name, "is_live": False}

def save_team_status(team_dict, filename):
    """팀 데이터를 확인하고 파일로 저장하는 함수"""
    results = []
    team_name = "빨간팀" if "red" in filename else "파란팀"
    print(f"[{team_name}] 방송 상태 확인 중...")
    
    for bj_id, bj_name in team_dict.items():
        info = check_member_live(bj_id, bj_name)
        results.append(info)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"✅ {filename} 업데이트 완료!")

if __name__ == '__main__':
    # 빨간팀 처리
    save_team_status(red_team, 'red_team_status.json')
    
    # 파란팀 처리
    save_team_status(blue_team, 'blue_team_status.json')
    
    print("\n모든 작업이 완료되었습니다.")
