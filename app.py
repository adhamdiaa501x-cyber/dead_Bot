import sqlite3
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder=".")

# دالة مساعدة للاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # عشان نقدر نرجع النتائج كـ Dictionary يسهل التعامل معاه
    return conn

def normalize_bool(value, default):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
    return default

def normalize_target_level(value, default):
    try:
        normalized = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(18, normalized))

@app.route("/")
def index():
    # قراءة القلاع/الحسابات من قاعدة البيانات مباشرة
    conn = get_db_connection()
    accounts = conn.execute('SELECT * FROM accounts').fetchall()
    conn.close()
    
    # تحويل البيانات لشكل مناسب يعرضه الـ Template
    castles_data = {}
    for acc in accounts:
        castles_data[f"castle_{acc['id']}"] = {
            "name": acc['account_name'],
            "game_id": acc['game_id'],
            "status": acc['status'],
            "auto_shield": True,  # قيم افتراضية مؤقتة لحد ما نضيف أعمدة الإعدادات لو حابين
            "gather_resources": True,
            "target_level": 18
        }
        
    return render_template("index.html", castles=castles_data)

@app.route("/api/update_config", methods=["POST"])
def update_config():
    data = request.get_json(silent=True) or {}
    castle_id_str = data.get("castle_id")
    
    if not castle_id_str:
        return jsonify({"status": "error", "message": "معرف القلعة غير موجود!"}), 400

    # استخراج الرقم من castle_1 مثلاً
    try:
        acc_id = int(castle_id_str.replace("castle_", ""))
    except ValueError:
        return jsonify({"status": "error", "message": "معرف القلعة غير صحيح!"}), 400

    conn = get_db_connection()
    account = conn.execute('SELECT * FROM accounts WHERE id = ?', (acc_id,)).fetchone()
    
    if not account:
        conn.close()
        return jsonify({"status": "error", "message": "القلعة مش موجودة في قاعدة البيانات!"}), 404

    # هنا ممكن نحدث الحالة أو الإعدادات في قاعدة البيانات
    # كمثال، هنحدث حالة الـ status بناء على البيانات الواردة لو وجدت
    new_status = data.get("status", account['status'])
    
    conn.execute('UPDATE accounts SET status = ? WHERE id = ?', (new_status, acc_id))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "تم تحديث إعدادات القلعة وحفظها في قاعدة البيانات بنجاح يا فنان!",
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)