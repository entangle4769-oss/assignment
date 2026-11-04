import random
import sys
from games_data import GAMES
from ai_recommend import AiError, recommend_by_ai

VALID_CATEGORIES = ["순발력", "눈치", "말빨", "운", "기억력"]

def filter_games(games, filters):
    result = []
    for g in games:
        if filters["players"] is not None:
            if not (g["min_players"] <= filters["players"] <= g["max_players"]):
                continue
        if filters["category"] is not None:
            if g["category"] != filters["category"]:
                continue
        if filters["no_item_only"]:
            if g["item"] != "없음":
                continue
        result.append(g)
    return result

def print_game_detail(g):
    print("-" * 40)
    print(f"번호: {g['id']}")
    print(f"이름: {g['name']}")
    print(f"종류: {g['category']}")
    print(f"인원: {g['min_players']}~{g['max_players']}명")
    print(f"준비물: {g['item']}")
    print(f"규칙: {g['rules']}")
    print("-" * 40)

def show_list(games, filters):
    matched = filter_games(games, filters)
    if not matched:
        print("\n조건에 맞는 게임이 없습니다.")
        return
    print(f"\n[전체 목록] ({len(matched)}개)")
    for g in matched:
        print(f"[{g['id']}] {g['name']} | 종류: {g['category']} | 인원: {g['min_players']}~{g['max_players']}명")

def search(games):
    word = input("\n검색할 단어를 입력하세요: ").strip()
    if not word:
        print("검색 결과가 없습니다.")
        return
    results = [g for g in games if word in g["name"] or word in g["rules"]]
    if not results:
        print("검색 결과가 없습니다.")
        return
    print(f"\n[검색 결과: '{word}'] ({len(results)}개)")
    for g in results:
        print(f"[{g['id']}] {g['name']} | 종류: {g['category']} | 인원: {g['min_players']}~{g['max_players']}명")

def configure_filters(games, filters):
    print("\n[조건 설정] (필요 없는 조건은 Enter를 눌러 넘어가세요)")
    p_in = input("1. 인원수를 입력하세요: ").strip()
    if p_in:
        if p_in.isdigit() and int(p_in) > 0:
            filters["players"] = int(p_in)
        else:
            print("올바른 숫자가 아니므로 인원수 조건은 건너뜁니다.")
            filters["players"] = None
    else:
        filters["players"] = None

    c_in = input("2. 게임 종류를 입력하세요 (순발력, 눈치, 말빨, 운, 기억력): ").strip()
    if c_in:
        if c_in in VALID_CATEGORIES:
            filters["category"] = c_in
        else:
            print("올바른 종류가 아니므로 게임 종류 조건은 건너뜁니다.")
            filters["category"] = None
    else:
        filters["category"] = None

    i_in = input("3. 준비물이 없는 게임만 보시겠습니까? (y/n): ").strip().lower()
    if i_in in ["y", "yes", "예"]:
        filters["no_item_only"] = True
    else:
        filters["no_item_only"] = False

    matched = filter_games(games, filters)
    print(f"\n조건 설정이 완료되었습니다. 조건에 맞는 게임: {len(matched)}개")

def clear_filters(filters):
    filters["players"] = None
    filters["category"] = None
    filters["no_item_only"] = False
    print("\n걸어 둔 조건이 모두 해제되었습니다.")

def recommend_random(games, filters):
    matched = filter_games(games, filters)
    if not matched:
        print("\n조건에 맞는 게임이 없습니다.")
        return
    chosen = random.choice(matched)
    print("\n[랜덤 추천]")
    print_game_detail(chosen)

def view_detail(games):
    num_in = input("\n자세히 볼 게임 번호를 입력하세요: ").strip()
    if not num_in.isdigit():
        print("올바른 게임 번호를 입력하세요.")
        return
    gid = int(num_in)
    target = next((g for g in games if g["id"] == gid), None)
    if not target:
        print("해당 번호의 게임이 없습니다. 다시 입력해 주세요.")
        return
    print_game_detail(target)

def ai_recommend(games, filters):
    matched = filter_games(games, filters)
    if not matched:
        print("\n조건에 맞는 게임이 없습니다.")
        return
    situation = input("\n상황을 자유롭게 적어 주세요 (예: 5명, 첫 만남이라 어색함): ").strip()
    if not situation:
        print("상황을 입력하지 않아 AI 추천을 건너뜁니다.")
        return
    try:
        game, reason = recommend_by_ai(situation, matched)
    except AiError as e:
        print(f"\n{e}")
        return
    print("\n[AI 추천]")
    print_game_detail(game)
    print(f"추천 이유: {reason}")

def main():
    filters = {"players": None, "category": None, "no_item_only": False}
    print("=" * 40)
    print("랜덤 술게임 사전")
    print(f"등록된 게임: {len(GAMES)}개")
    print("=" * 40)

    while True:
        print("\n[메뉴]")
        print("1. 전체 목록 보기")
        print("2. 검색")
        print("3. 조건 설정")
        print("4. 조건 해제")
        print("5. 랜덤 추천")
        print("6. 게임 자세히 보기")
        print("7. AI 추천")
        print("8. 종료")

        try:
            choice = input("메뉴 번호를 입력하세요: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n랜덤 술게임 사전을 종료합니다. 즐거운 모임 되세요!")
            break

        if choice == "1":
            show_list(GAMES, filters)
        elif choice == "2":
            search(GAMES)
        elif choice == "3":
            configure_filters(GAMES, filters)
        elif choice == "4":
            clear_filters(filters)
        elif choice == "5":
            recommend_random(GAMES, filters)
        elif choice == "6":
            view_detail(GAMES)
        elif choice == "7":
            ai_recommend(GAMES, filters)
        elif choice == "8":
            print("\n랜덤 술게임 사전을 종료합니다. 즐거운 모임 되세요!")
            break
        else:
            print("메뉴에 없는 번호이거나 잘못된 입력입니다. 다시 입력해 주세요.")

if __name__ == "__main__":
    main()
