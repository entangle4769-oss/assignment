# 랜덤 술게임 사전

콘솔에서 술게임 35개를 목록, 검색, 조건 필터, 랜덤 추천으로 찾아보는 프로그램이다. 이번 업데이트로 메뉴 7번 AI 추천을 추가했다. 기획은 `api-plan.md`에 있다.

## 실행 방법

uv가 필요하다. Python 3.12 이상을 쓴다.

```
git clone https://github.com/entangle4769-oss/assignment
cd assignment
cp .env.example .env
uv sync
uv run python main.py
```

`.env`에는 한 줄을 넣는다. 키는 [Google AI Studio](https://aistudio.google.com/apikey)에서 무료로 발급받을 수 있다. 제출용 키는 icampus로 따로 냈고 저장소에는 올리지 않았다.

```
GEMINI_API_KEY=발급받은_키
```

모델을 바꾸려면 `WK5_MODEL=모델이름`을 추가한다. 기본값은 무료 등급을 제공하는 gemini-3.5-flash-lite이다. 키가 없어도 1~6번 메뉴는 그대로 동작하고, 7번만 안내 문구가 나온다.

## 파일 구성

```
main.py            메뉴 루프, 필터, 검색 등 기존 기능 + 7번 메뉴 연결
ai_recommend.py    Gemini API 호출 (새 파일)
games_data.py      게임 데이터 GAMES (35개)
api-plan.md        기획안
docs/ai-chat.md    AI와 나눈 대화 원문
pyproject.toml     의존성 (google-genai, python-dotenv)
.env.example       키 형식 예시
```

## 코드 설명

기존 코드는 `GAMES`(딕셔너리 리스트)를 `filter_games()`로 거르고 메뉴 번호에 맞는 함수를 부르는 구조다. 필터 상태는 `filters` 딕셔너리 하나(players, category, no_item_only)로 들고 다닌다.

추가한 부분은 main.py의 `ai_recommend()`와 ai_recommend.py다. `ai_recommend()`는 `filter_games()`로 후보를 거르고, 상황 문장을 입력받아 `recommend_by_ai()`를 부른 뒤 결과를 `print_game_detail()`로 출력한다. 걸어 둔 조건이 AI 추천에도 그대로 적용된다.

`recommend_by_ai()`는 후보 게임을 한 줄씩 적은 목록과 상황 문장을 `generate_content()`로 보낸다. 응답 형식은 구조화 출력으로 고정했다. `response_mime_type`을 JSON으로 두고 `response_json_schema`에 game_id와 reason을 적으면, 응답 텍스트가 항상 이 구조의 JSON으로 오므로 `json.loads()`로 바로 읽을 수 있다.

`pick_game()`은 그 JSON을 해석하고, game_id가 후보 목록에 실제로 있는지 확인한다. 모델이 목록에 없는 번호를 내면 AiError를 낸다. 키 없음, API 실패(무료 한도 초과 포함), 잘못된 응답과 번호는 모두 AiError로 모아서 main.py에서 메시지만 출력하고 메뉴로 돌아간다.

## 한계

무료 등급은 호출 횟수 제한이 있고 입력이 모델 개선에 쓰일 수 있으므로 개인정보를 적지 않는다. 추천은 모델의 판단이라 같은 입력에도 다른 게임이 나올 수 있다. 게임 규칙은 games_data.py의 문장을 그대로 믿고 쓰며 모델이 규칙의 정확성을 검증하지는 않는다. 호출마다 후보 전체(최대 35개)를 보내므로 게임 수가 크게 늘면 토큰이 늘어난다.
