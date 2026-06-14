import csv
import os
from datetime import date

FILENAME = "kadai.csv"

def load_kadai():
    kadai_list = []
    if os.path.exists(FILENAME):
        with open(FILENAME, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                kadai_list.append(row)
    return kadai_list

def save_kadai(kadai_list):
    with open(FILENAME, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["課題名", "科目", "締め切り", "完了", "優先度"])
        writer.writeheader()
        writer.writerows(kadai_list)

def sort_by_deadline(kadai_list):
    return sorted(kadai_list, key=lambda x: x["締め切り"])

def print_kadai(kadai_list, filter_subject=None):
    if filter_subject:
        target = [k for k in kadai_list if k["科目"] == filter_subject]
    else:
        target = kadai_list

    if len(target) == 0:
        print("該当する課題はありません。")
        return

    title = f"--- {filter_subject}の課題一覧 ---" if filter_subject else "--- 課題一覧（締め切り順）---"
    print(f"\n{title}")
    today = date.today()
    priority_icon = {"高": "🔴", "中": "🟡", "低": "🟢"}
    for i, kadai in enumerate(target, 1):
        kanryo = "✓" if kadai["完了"] == "True" else " "
        deadline = kadai["締め切り"]
        priority = kadai.get("優先度", "中")
        icon = priority_icon.get(priority, "🟡")
        try:
            days_left = (date.fromisoformat(deadline) - today).days
            if kadai["完了"] == "True":
                nokori = "完了済み"
            elif days_left < 0:
                nokori = "期限切れ"
            elif days_left == 0:
                nokori = "今日まで！"
            else:
                nokori = f"あと{days_left}日"
        except:
            nokori = ""
        print(f"{i}. [{kanryo}] {icon} [{kadai['科目']}] {kadai['課題名']} (締め切り: {deadline} / {nokori})")

def check_alerts(kadai_list):
    today = date.today()
    alerts = []
    for kadai in kadai_list:
        if kadai["完了"] == "True":
            continue
        try:
            days_left = (date.fromisoformat(kadai["締め切り"]) - today).days
            if 0 <= days_left <= 3:
                alerts.append((kadai, days_left))
        except:
            pass
    return alerts

def get_subjects(kadai_list):
    subjects = []
    for kadai in kadai_list:
        if kadai["科目"] not in subjects:
            subjects.append(kadai["科目"])
    return subjects

def input_priority():
    print("優先度を選んでください: 1: 高  2: 中  3: 低")
    p = input("番号を入力: ")
    return {"1": "高", "2": "中", "3": "低"}.get(p, "中")

def search_kadai(kadai_list,keyword):
    result = []
    for kadai in kadai_list:
        if keyword in kadai["課題名"]:
            result.append(kadai)
    return result
        
kadai_list = load_kadai()

# 起動時にアラートチェック
alerts = check_alerts(kadai_list)
if alerts:
    print("\n⚠️  締め切りが近い課題があります！")
    for kadai, days_left in alerts:
        if days_left == 0:
            print(f"  🔴 【今日まで】[{kadai['科目']}] {kadai['課題名']}")
        elif days_left == 1:
            print(f"  🔴 【明日まで】[{kadai['科目']}] {kadai['課題名']}")
        else:
            print(f"  🟡 【あと{days_left}日】[{kadai['科目']}] {kadai['課題名']}")

while True:
    print("\n--- 課題管理ツール ---")
    print("1: 課題を追加")
    print("2: 課題一覧を見る")
    print("3: 科目でフィルタリング")
    print("4: 課題を検索する")
    print("5: 課題を編集する")
    print("6: 課題を完了にする")
    print("7: 課題を削除する")
    print("8: 終了")

    choice = input("番号を選んでください: ")

    if choice == "1":
        name = input("課題名: ")
        subject = input("科目名: ")
        deadline = input("締め切り日 (例: 2025-07-01): ")
        priority = input_priority()
        kadai_list.append({"課題名": name, "科目": subject, "締め切り": deadline, "完了": "False", "優先度": priority})
        kadai_list = sort_by_deadline(kadai_list)
        save_kadai(kadai_list)
        print("追加して保存しました！")

    elif choice == "2":
        print_kadai(kadai_list)

    elif choice == "3":
        subjects = get_subjects(kadai_list)
        if not subjects:
            print("課題がまだありません。")
        else:
            print("\n登録されている科目：")
            for i, subject in enumerate(subjects, 1):
                print(f"{i}. {subject}")
            num = input("絞り込む科目の番号を入力: ")
            try:
                idx = int(num) - 1
                print_kadai(kadai_list, filter_subject=subjects[idx])
            except:
                print("無効な番号です。")

    elif choice == "4":
        keyword = input("検索キーワードを入力: ")
        result = search_kadai(kadai_list,keyword)
        if not result:
            print("該当する課題が見つかりませんでした")
        else:
            print(f"\n---「{keyword}」の検索結果---")
            today = date.today()
            priority_icon = {"高": "🔴", "中": "🟡", "低": "🟢"}
            for i, kadai in enumerate(result,1):
                icon = priority_icon.get(kadai.get("優先度","中"),"🟡")
                print(f"{i}. {icon} [{kadai['科目']}] {kadai['課題名']} (締め切り:{kadai['締め切り']})")

    elif choice == "5":
        print_kadai(kadai_list)
        num = input("編集する番号を入力: ")
        try:
            idx = int(num) - 1
            kadai = kadai_list[idx]
            print(f"\n現在の内容: [{kadai['科目']}] {kadai['課題名']} / 締め切り: {kadai['締め切り']} / 優先度: {kadai.get('優先度', '中')}")
            print("変更しない項目はそのままEnterを押してね")
            new_name = input(f"課題名 ({kadai['課題名']}): ")
            new_subject = input(f"科目名 ({kadai['科目']}): ")
            new_deadline = input(f"締め切り日 ({kadai['締め切り']}): ")
            print(f"優先度 (現在: {kadai.get('優先度', '中')})")
            new_priority = input_priority()
            if new_name:
                kadai["課題名"] = new_name
            if new_subject:
                kadai["科目"] = new_subject
            if new_deadline:
                kadai["締め切り"] = new_deadline
            kadai["優先度"] = new_priority
            kadai_list = sort_by_deadline(kadai_list)
            save_kadai(kadai_list)
            print("編集しました！")
        except:
            print("無効な番号です。")

    elif choice == "6":
        print_kadai(kadai_list)
        num = input("完了にする番号を入力: ")
        try:
            idx = int(num) - 1
            kadai_list[idx]["完了"] = "True"
            save_kadai(kadai_list)
            print("完了にしました！")
        except:
            print("無効な番号です。")

    elif choice == "7":
        print_kadai(kadai_list)
        num = input("削除する番号を入力: ")
        try:
            idx = int(num) - 1
            deleted = kadai_list.pop(idx)
            save_kadai(kadai_list)
            print(f"「{deleted['課題名']}」を削除しました！")
        except:
            print("無効な番号です。")

    elif choice == "8":
        print("終了します。")
        break