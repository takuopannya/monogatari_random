import requests
from bs4 import BeautifulSoup
import random
import json
import os
import tkinter as tk
from tkinter import messagebox
import webbrowser
from charset_normalizer import detect

# キャッシュファイル名
CACHE_FILE = "links_cache.json"

def scrape_and_cache_links(url):
    """
    指定したURLからリンクをスクレイピングし、キャッシュに保存する。
    """
    try:
        # ウェブページを取得
        response = requests.get(url)
        
        # エンコーディングを自動検出
        detected = detect(response.content)
        response.encoding = detected['encoding']
        
        # BeautifulSoupで解析
        soup = BeautifulSoup(response.text, "html.parser")

        # すべてのリンクを抽出
        links = []
        for item in soup.find_all("a", href=True):
            link_text = item.text.strip()
            link_url = item['href']
            if link_text and link_url:
                # 相対URLをフルURLに変換
                full_url = requests.compat.urljoin(url, link_url)
                links.append({"text": link_text, "url": full_url})
        
        # キャッシュに保存 (日本語対応)
        with open(CACHE_FILE, "w", encoding="utf-8") as file:
            json.dump(links, file, ensure_ascii=False, indent=4)

        return links
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return []

def load_links_from_cache():
    """
    キャッシュからリンクを読み込む。
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return None

def fetch_links():
    """
    キャッシュが存在しない場合はスクレイピングし、存在する場合はキャッシュを読み込む。
    """
    url = "https://www.lib.agu.ac.jp/yousojiten/00.htm"
    links = load_links_from_cache()
    if links is None:
        links = scrape_and_cache_links(url)
    return links

def on_start_button_click():
    """
    スタートボタンがクリックされたときにランダムなお題を表示する。
    """
    num_topics = int(spinbox.get())  # ユーザーが選択した数を取得
    links = fetch_links()
    if links and len(links) >= num_topics:
        random_links = random.sample(links, num_topics)
        result = "\n".join([f"{i+1}. {link['text']} ({link['url']})" for i, link in enumerate(random_links)])
        messagebox.showinfo("ランダムリンク", result)

        # クリック可能なリンクとして保持
        global clickable_links
        clickable_links = random_links
        update_link_buttons()
    else:
        messagebox.showerror("エラー", "リンクが十分に取得できませんでした。")

def open_link(index):
    """
    指定されたリンクをブラウザで開く。
    """
    if clickable_links and 0 <= index < len(clickable_links):
        webbrowser.open(clickable_links[index]['url'])

def update_link_buttons():
    """
    ランダムに選ばれたリンクのボタンを更新する。
    """
    for i, button in enumerate(link_buttons):
        if i < len(clickable_links):
            button.config(text=clickable_links[i]['text'], command=lambda idx=i: open_link(idx))
            button.pack(pady=5)
        else:
            button.pack_forget()

# グローバル変数
clickable_links = []
link_buttons = []

# GUI作成
root = tk.Tk()
root.title("物語要素辞典ランダム選択")
root.geometry("500x500")

# ラベル
label = tk.Label(root, text="ランダムに選択するお題の数を指定してください", font=("Arial", 12))
label.pack(pady=10)

# スピンボックス（1～5を選択可能）
spinbox = tk.Spinbox(root, from_=1, to=5, font=("Arial", 12), width=5)
spinbox.pack(pady=10)

# スタートボタン
start_button = tk.Button(root, text="スタート", font=("Arial", 12), command=on_start_button_click)
start_button.pack(pady=10)

# リンクボタン
for _ in range(5):  # 最大5つのリンクを表示するためボタンを5つ用意
    button = tk.Button(root, text="", font=("Arial", 10), command=lambda: None, wraplength=400, anchor="w")
    link_buttons.append(button)

# メインループ
root.mainloop()
