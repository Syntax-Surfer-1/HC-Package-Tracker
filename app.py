from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track():
    tracker_id = request.form.get('tracker_id', '').strip()
    url = f"https://mail.hackclub.com/letters/{tracker_id}"
    res = requests.get(url)

    if res.status_code != 200:
        return jsonify({"error": "Tracker ID not found!"}), 404

    soup = BeautifulSoup(res.text, "html.parser")

    # ✅ Title
    title_tag = soup.find("div", class_="title-bar-text")
    title = title_tag.get_text(strip=True) if title_tag else "No title"

    # ✅ Subtitle (Status)
    subtitle = "No status available"
    for p in soup.find_all("p"):
        b = p.find("b")
        if b and b.get_text(strip=True) == "Status:":
            subtitle = p.get_text(strip=True).replace("Status:", "").strip()
            break

    # ✅ Tracking History
    table = soup.find("table", class_="interactive")
    rows = table.find_all("tr")[1:] if table else []

    history = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) == 6:
            history.append({
                "time": cols[0].text.strip(),
                "description": cols[1].text.strip(),
                "location": cols[2].text.strip(),
                "facility": cols[3].text.strip(),
                "source": cols[4].text.strip(),
                "extra_info": cols[5].text.strip()
            })

    return jsonify({
        "tracker": tracker_id,
        "title": title,
        "subtitle": subtitle,
        "history": history
    })


if __name__ == "__main__":
    app.run(debug=True)
