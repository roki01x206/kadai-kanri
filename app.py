from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from datetime import date

app = Flask(__name__)
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

@app.route("/")
def index():
    kadai_list = load_kadai()
    kadai_list = sort_by_deadline(kadai_list)
    today = date.today()
    for kadai in kadai_list:
        if kadai["完了"] == "True":
            kadai["残り"] = "完了済み"
        else:
            try:
                days_left = (date.fromisoformat(kadai["締め切り"]) - today).days
                if days_left < 0:
                    kadai["残り"] = "期限切れ"
                elif days_left == 0:
                    kadai["残り"] = "今日まで！"
                else:
                    kadai["残り"] = f"あと{days_left}日"
            except:
                kadai["残り"] = ""
    kadai_with_index = list(enumerate(kadai_list))
    return render_template("index.html", kadai_with_index=kadai_with_index, today=today)

@app.route("/add", methods=["POST"])
def add():
    kadai_list = load_kadai()
    kadai_list.append({
        "課題名": request.form["name"],
        "科目": request.form["subject"],
        "締め切り": request.form["deadline"],
        "完了": "False",
        "優先度": request.form["priority"]
    })
    save_kadai(sort_by_deadline(kadai_list))
    return redirect(url_for("index"))

@app.route("/complete/<int:idx>")
def complete(idx):
    kadai_list = load_kadai()
    kadai_list[idx]["完了"] = "True"
    save_kadai(kadai_list)
    return redirect(url_for("index"))

@app.route("/delete/<int:idx>")
def delete(idx):
    kadai_list = load_kadai()
    kadai_list.pop(idx)
    save_kadai(kadai_list)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)