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

@app.route('/') def home(): return ''' <!DOCTYPE html> <html lang="es"> <head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>Panel de Automatización</title> <style> body { font-family: Arial, sans-serif; background-color: #1e1e1e; color: white; text-align: center; padding: 50px; } .container { max-width: 400px; margin: auto; background: #2c2c2c; padding: 20px; border-radius: 10px; } select, input, button { width: 100%; padding: 10px; margin: 10px 0; border: none; border-radius: 5px; } button { background-color: #ff4c4c; color: white; font-weight: bold; cursor: pointer; } </style> </head> <body> <div class="container"> <h2>Panel de Automatización</h2> <form id="automationForm"> <label for="platform">Plataforma:</label> <select id="platform" name="platform"> <option value="Tiktok">Tiktok</option> <option value="Telegram">Telegram</option> <option value="Youtube">Youtube</option> <option value="Facebook">Facebook</option> <option value="Instagram">Instagram</option> <option value="Twitter">Twitter</option> </select> <label for="url">Enlace:</label> <input type="text" id="url" name="url" required> <label for="action">Acción:</label> <select id="action" name="action"> <option value="visitas">Visitas</option> <option value="seguidores">Seguidores</option> <option value="likes">Likes</option> </select> <label for="amount">Cantidad:</label> <input type="number" id="amount" name="amount" min="1" required> <button type="submit">Enviar</button> </form> <p id="result"></p> </div> <script> document.getElementById("automationForm").addEventListener("submit", function(event) { event.preventDefault(); let formData = new FormData(this); fetch("/send", { method: "POST", body: formData }) .then(response => response.json()) .then(data => { document.getElementById("result").textContent = data.message; }); }); </script> </body> </html> '''

@app.route('/send', methods=['POST']) def send(): platform = request.form['platform'] url = request.form['url'] action = request.form['action'] amount = int(request.form['amount'])

with sqlite3.connect("panel.db") as conn:
    c = conn.cursor()
    c.execute("INSERT INTO requests (platform, action, amount, url) VALUES (?, ?, ?, ?)", (platform, action, amount, url))
    conn.commit()

thread = threading.Thread(target=automate_action, args=(platform, action, amount, url))
thread.start()

return jsonify({"status": "success", "message": f"{amount} {action} enviados a {url} en {platform}"})

if name == 'main': init_db() app.run(debug=True)

