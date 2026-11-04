"""Claude API로 현재 상황에 맞는 술게임을 고르는 모듈."""

import os

import anthropic
from dotenv import load_dotenv

DEFAULT_MODEL = "claude-sonnet-5-5"

SYSTEM = (
    "너는 술자리 게임을 추천하는 도우미다. 사용자가 적은 상황(인원, 분위기, 장소, 준비물 등)을 보고 "
    "목록에 있는 게임 중 하나만 고른다. 목록에 없는 게임은 추천하지 않는다. "
    "reason에는 그 게임을 고른 이유를 한두 문장으로 쓴다."
)

RECOMMEND_TOOL = {
    "name": "recommend_game",
    "description": "목록에서 고른 게임 하나와 그 이유를 제출한다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "game_id": {"type": "integer", "description": "목록에 있는 게임의 번호(id)"},
            "reason": {"type": "string", "description": "추천 이유 한두 문장"},
        },
        "required": ["game_id", "reason"],
    },
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


def pick_game(response, games):
    """응답의 도구 호출에서 게임 번호를 꺼내 목록에 있는 게임인지 확인한다."""
    for block in response.content:
        if block.type == "tool_use" and block.name == "recommend_game":
            game_id = block.input.get("game_id")
            game = next((g for g in games if g["id"] == game_id), None)
            if game is None:
                raise AiError("AI가 목록에 없는 게임을 골랐습니다. 다시 시도해 주세요.")
            return game, block.input.get("reason", "")
    raise AiError("AI 응답에서 추천 결과를 찾지 못했습니다. 다시 시도해 주세요.")


def get_client():
    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise AiError("ANTHROPIC_API_KEY가 없습니다. .env 파일에 키를 넣어 주세요. (README 참고)")
    return anthropic.Anthropic()


def recommend_by_ai(situation, games, client=None):
    """situation(자유 문장)과 후보 게임 목록을 보내 (게임, 이유)를 돌려받는다."""
    if client is None:
        client = get_client()
    model = os.environ.get("WK5_MODEL", DEFAULT_MODEL)
    try:
        response = client.messages.create(
            model=model,
            max_tokens=500,
            system=SYSTEM,
            tools=[RECOMMEND_TOOL],
            tool_choice={"type": "tool", "name": "recommend_game"},
            messages=[
                {
                    "role": "user",
                    "content": f"<games>\n{build_catalog(games)}\n</games>\n\n상황: {situation}",
                }
            ],
        )
    except anthropic.APIError as e:
        raise AiError(f"API 호출에 실패했습니다: {e}") from e
    return pick_game(response, games)
