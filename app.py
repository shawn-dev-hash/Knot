import customtkinter as ctk
import json
import webbrowser
import requests
from PIL import Image
from urllib.parse import urlparse
import os
from flask import Flask, request
import threading
import socket
import qrcode

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# ------------------ UTIL ------------------

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# ------------------ FAVICON ------------------

def fetch_favicon(url):
    domain = urlparse(url).netloc
    icon_path = f"icons/{domain}.png"

    if os.path.exists(icon_path):
        return icon_path

    try:
        favicon_url = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
        response = requests.get(favicon_url, timeout=5)

        if response.status_code == 200:
            with open(icon_path, "wb") as f:
                f.write(response.content)
            return icon_path
    except:
        pass

    return None

# ------------------ FLASK SERVER ------------------

flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        url = request.form.get("url")
        category = request.form.get("category")

        if name and url:
            if not url.startswith("http"):
                url = "https://" + url

            with open("links.json", "r") as file:
                links = json.load(file)

            links.append({
                "name": name,
                "url": url,
                "category": category
            })

            with open("links.json", "w") as file:
                json.dump(links, file, indent=4)

        return "<h2>Link Added ✅</h2><a href='/'>Add Another</a>"

    return """
    <h2>Add Link</h2>
    <form method="post">
        <input name="name" placeholder="Site Name" required><br><br>
        <input name="url" placeholder="URL" required><br><br>
        <select name="category">
            <option>Gaming</option>
            <option>Coding</option>
            <option>Study</option>
            <option>Streaming</option>
            <option>General</option>
        </select><br><br>
        <button type="submit">Add Link</button>
    </form>
    """

def start_server():
    flask_app.run(host="0.0.0.0", port=5000)

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# ------------------ QR ------------------

def generate_qr(ip):
    url = f"http://{ip}:5000"
    qr = qrcode.make(url)
    qr_path = "phone_qr.png"
    qr.save(qr_path)
    return qr_path

# ------------------ DATA ------------------

def load_links():
    for widget in scroll_frame.winfo_children():
        widget.destroy()

    with open("links.json", "r") as file:
        links = json.load(file)

    for index, link in enumerate(links):
        if current_filter.get() == "All" or link.get("category") == current_filter.get():
            create_link_card(index, link["name"], link["url"], link.get("category", "General"))

def add_link():
    name = name_entry.get()
    url = url_entry.get()
    category = category_var.get()

    if name and url:
        if not url.startswith("http"):
            url = "https://" + url

        with open("links.json", "r") as file:
            links = json.load(file)

        links.append({
            "name": name,
            "url": url,
            "category": category
        })

        with open("links.json", "w") as file:
            json.dump(links, file, indent=4)
        load_links()
        name_entry.delete(0, "end")
        url_entry.delete(0, "end")
        load_links()

def delete_link(index):
    with open("links.json", "r") as file:
        links = json.load(file)

    links.pop(index)

    with open("links.json", "w") as file:
        json.dump(links, file, indent=4)

    load_links()

def open_link(url):
    browser = webbrowser.get(f'"{BRAVE_PATH}" %s')
    browser.open(url)

# ------------------ CARD ------------------

def create_link_card(index, name, url, category):
    card = ctk.CTkFrame(scroll_frame, corner_radius=14)
    card.pack(fill="x", padx=10, pady=4)

    def on_enter(e):
        card.configure(fg_color="#2a2a2a")

    def on_leave(e):
        card.configure(fg_color="transparent")

    card.bind("<Enter>", on_enter)
    card.bind("<Leave>", on_leave)

    left_frame = ctk.CTkFrame(card, fg_color="transparent")
    left_frame.pack(side="left", padx=15, pady=8)

    row_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
    row_frame.pack(anchor="w")

    icon_path = fetch_favicon(url)

    if icon_path:
        try:
            img = Image.open(icon_path)
            icon = ctk.CTkImage(light_image=img, dark_image=img, size=(22, 22))
            icon_label = ctk.CTkLabel(row_frame, image=icon, text="")
            icon_label.pack(side="left", padx=(0, 10))
        except:
            pass

    name_label = ctk.CTkLabel(
        row_frame,
        text=name,
        font=ctk.CTkFont(size=16, weight="bold")
    )
    name_label.pack(side="left")

    category_label = ctk.CTkLabel(
        left_frame,
        text=category,
        font=ctk.CTkFont(size=12),
        text_color="#4cc9f0"
    )
    category_label.pack(anchor="w")

    button_frame = ctk.CTkFrame(card, fg_color="transparent")
    button_frame.pack(side="right", padx=15)

    open_btn = ctk.CTkButton(button_frame, text="Open", width=80, command=lambda: open_link(url))
    open_btn.pack(side="left", padx=6)

    delete_btn = ctk.CTkButton(
        button_frame,
        text="Delete",
        width=80,
        fg_color="#b00020",
        hover_color="#790000",
        command=lambda: delete_link(index)
    )
    delete_btn.pack(side="left", padx=6)

# ------------------ UI ------------------

import sys
import os

app = ctk.CTk()
app.title("Knot")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

try:
    app.iconbitmap(resource_path("knot.ico"))
except:
    pass

title = ctk.CTkLabel(app, text="Knot", font=ctk.CTkFont(size=26, weight="bold"))
title.pack(pady=20)

# QR Display
local_ip = get_local_ip()
qr_path = generate_qr(local_ip)
img = Image.open(qr_path)
qr_image = ctk.CTkImage(light_image=img, dark_image=img, size=(150, 150))
qr_label = ctk.CTkLabel(app, image=qr_image, text="")
qr_label.pack(pady=10)

input_frame = ctk.CTkFrame(app)
input_frame.pack(padx=20, pady=10, fill="x")

category_var = ctk.StringVar(value="General")

category_menu = ctk.CTkOptionMenu(
    input_frame,
    values=["Gaming", "Coding", "Study", "Streaming", "General"],
    variable=category_var
)
category_menu.pack(side="left", padx=10, pady=15)

name_entry = ctk.CTkEntry(input_frame, placeholder_text="Site Name")
name_entry.pack(side="left", expand=True, padx=10, pady=15)

url_entry = ctk.CTkEntry(input_frame, placeholder_text="URL")
url_entry.pack(side="left", expand=True, padx=10, pady=15)

add_button = ctk.CTkButton(app, text="Add Link", command=add_link)
add_button.pack(pady=10)

url_entry.bind("<Return>", lambda e: add_link())
name_entry.bind("<Return>", lambda e: add_link())

# FILTER

filter_frame = ctk.CTkFrame(app)
filter_frame.pack(pady=10)

current_filter = ctk.StringVar(value="All")
filter_buttons = {}

def set_filter(category):
    current_filter.set(category)

    for cat, btn in filter_buttons.items():
        if cat == category:
            btn.configure(fg_color="#1f6aa5")
        else:
            btn.configure(fg_color="#3a3a3a")

    load_links()

categories = ["All", "Gaming", "Coding", "Study", "Streaming", "General"]

for cat in categories:
    btn = ctk.CTkButton(
        filter_frame,
        text=cat,
        width=100,
        command=lambda c=cat: set_filter(c)
    )
    btn.pack(side="left", padx=5)
    filter_buttons[cat] = btn

scroll_frame = ctk.CTkScrollableFrame(app)
scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

set_filter("All")

app.mainloop()