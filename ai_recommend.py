"""Gemini API(무료 등급)로 현재 상황에 맞는 술게임을 고르는 모듈."""

import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.5-flash-lite"

SYSTEM = (
    "너는 술자리 게임을 추천하는 도우미다. 사용자가 적은 상황(인원, 분위기, 장소, 준비물 등)을 보고 "
    "목록에 있는 게임 중 하나만 고른다. 목록에 없는 게임은 추천하지 않는다. "
    "reason에는 그 게임을 고른 이유를 한두 문장으로 쓴다."
)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "game_id": {"type": "integer", "description": "목록에 있는 게임의 번호(id)"},
        "reason": {"type": "string", "description": "추천 이유 한두 문장"},
    },
    "required": ["game_id", "reason"],
}


class AiError(Exception):
    """AI 추천을 할 수 없을 때 사용자에게 보여 줄 메시지를 담는 예외."""


def build_catalog(games):
    lines = []
    for g in games:
        lines.append(
            f"{g['id']} | {g['name']} | {g['category']} | {g['min_players']}~{g['max_players']}명 "
            f"| 준비물: {g['item']} | {g['rules']}"
        )
    return "\n".join(lines)


def pick_game(response_text, games):
    """응답 JSON에서 게임 번호를 꺼내 목록에 있는 게임인지 확인한다."""
    try:
        data = json.loads(response_text or "")
        game_id = data["game_id"]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise AiError("AI 응답에서 추천 결과를 찾지 못했습니다. 다시 시도해 주세요.") from e
    game = next((g for g in games if g["id"] == game_id), None)
    if game is None:
        raise AiError("AI가 목록에 없는 게임을 골랐습니다. 다시 시도해 주세요.")
    return game, data.get("reason", "")


def get_client():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise AiError("GEMINI_API_KEY가 없습니다. .env 파일에 키를 넣어 주세요. (README 참고)")
    return genai.Client(api_key=api_key)


def recommend_by_ai(situation, games, client=None):
    """situation(자유 문장)과 후보 게임 목록을 보내 (게임, 이유)를 돌려받는다."""
    if client is None:
        client = get_client()
    model = os.environ.get("WK5_MODEL", DEFAULT_MODEL)
    try:
        response = client.models.generate_content(
            model=model,
            contents=f"<games>\n{build_catalog(games)}\n</games>\n\n상황: {situation}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                response_mime_type="application/json",
                response_json_schema=RESPONSE_SCHEMA,
            ),
        )
    except Exception as e:  # API 오류와 네트워크 오류 모두 메뉴로 돌아가게 한다.
        raise AiError(f"API 호출에 실패했습니다: {e}") from e
    return pick_game(response.text, games)
