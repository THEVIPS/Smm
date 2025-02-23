from flask import Flask, render_template, request, jsonify from selenium import webdriver from selenium.webdriver.common.by import By from selenium.webdriver.chrome.service import Service from selenium.webdriver.chrome.options import Options import sqlite3 import threading import time

app = Flask(name)

def init_db(): with sqlite3.connect("panel.db") as conn: c = conn.cursor() c.execute('''CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, platform TEXT, action TEXT, amount INTEGER, url TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''') conn.commit()

def setup_driver(): options = Options() options.add_argument("--headless") options.add_argument("--disable-gpu") options.add_argument("--no-sandbox") options.add_argument("--disable-dev-shm-usage") service = Service("chromedriver") return webdriver.Chrome(service=service, options=options)

def automate_action(platform, action, amount, url): driver = setup_driver() driver.get(url) time.sleep(3)

try:
    if platform in ["Tiktok", "Instagram", "Twitter"]:
        buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Seguir') or contains(text(), 'Follow')]") if action == "seguidores" else driver.find_elements(By.XPATH, "//*[contains(text(), 'Me gusta') or contains(text(), 'Like')]")
        for btn in buttons[:amount]:
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(1)
    elif platform in ["Youtube", "Facebook"] and action == "visitas":
        time.sleep(amount * 2)
except Exception as e:
    print(f"Error en la automatización: {e}")
finally:
    driver.quit()

@app.route('/') def home(): return render_template("index.html")

@app.route('/send', methods=['POST']) def send(): platform = request.form['platform'] url = request.form['url'] action = request.form['action'] amount = int(request.form['amount'])

with sqlite3.connect("panel.db") as conn:
    c = conn.cursor()
    c.execute("INSERT INTO requests (platform, action, amount, url) VALUES (?, ?, ?, ?)", (platform, action, amount, url))
    conn.commit()

thread = threading.Thread(target=automate_action, args=(platform, action, amount, url))
thread.start()

return jsonify({"status": "success", "message": f"{amount} {action} enviados a {url} en {platform}"})

if name == 'main': init_db() app.run(debug=True)


