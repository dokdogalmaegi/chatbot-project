import requests
from requests.auth import HTTPBasicAuth
import json

# Confluence 정보 설정
CONFLUENCE_BASE_URL = "https://crscube.atlassian.net/wiki"
PAGE_ID = "3774583295"  # 대상 페이지 ID
USERNAME = "jylim@crscube.co.kr"
API_TOKEN = "ATATT3xFfGF08spkceGySeO2bGZWiAjb6pxdBp5DL9UVqKiIByYaUMuZPC1gbldqnS_iqKwVyYzFw1umd54qqFMfvF3LP4WVa7LZ8s2ORuEi9AThm0lZX2mi2gdCz2H_bD4_MWd0iV8dVJkGc4MreGK5jibaYRPpTgr2FUkDadhpucum4V0mJeY=054816A2"

# REST API URL
url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{PAGE_ID}?expand=body.storage"

# API 요청
response = requests.get(
    url,
    auth=HTTPBasicAuth(USERNAME, API_TOKEN),
    headers={"Accept": "application/json"}
)

# 결과 처리
if response.status_code == 200:
    data = response.json()
    html_content = data["body"]["storage"]["value"]

    with open("./conversation_history.json", "r", encoding="utf-8") as f:
        messages = json.load(f)
        
        # 대화 기록에 Confluence 페이지 내용을 추가
        messages.append({
            "role": "system",
            "content": f"다음은 ITEM 단위 status 기술 문서입니다. 이 정보를 바탕으로 사용자 질문에 답변하세요.\n{html_content}"
        })

        with open("conversation_history.json", "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)


else:
    print(f"Failed to fetch page content: {response.status_code}")
    print(response.text)
