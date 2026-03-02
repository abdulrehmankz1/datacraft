from flask import Flask, render_template, request, jsonify, send_file
import random
import csv
import os
import io
import json
from datetime import date, timedelta

try:
    from faker import Faker
    fake = Faker()
    HAS_FAKER = True
except ImportError:
    HAS_FAKER = False

app = Flask(__name__)

# ─── Data Generation Logic ────────────────────────────────────────────────────

def _random_date(start_str, end_str):
    start = date.fromisoformat(start_str)
    end = date.fromisoformat(end_str)
    delta = (end - start).days
    return str(start + timedelta(days=random.randint(0, delta)))

def generate_value(field, row_context, used_values):
    ftype = field["type"]
    fname = field["name"]

    if ftype == "int":
        val = random.randint(field.get("min", 0), field.get("max", 100))
    elif ftype == "float":
        decimals = field.get("decimals", 2)
        val = round(random.uniform(field.get("min", 0.0), field.get("max", 1.0)), decimals)
    elif ftype == "name_first":
        val = fake.first_name() if HAS_FAKER else random.choice(["Alice","Bob","Carol","David","Emma","Frank"])
    elif ftype == "name_last":
        val = fake.last_name() if HAS_FAKER else random.choice(["Smith","Johnson","Williams","Brown","Jones"])
    elif ftype == "email":
        val = fake.email() if HAS_FAKER else f"user{random.randint(100,999)}@example.com"
    elif ftype == "date":
        val = _random_date(field.get("start", "2000-01-01"), field.get("end", "2024-12-31"))
    elif ftype == "categorical":
        val = random.choice(field["categories"])
    elif ftype == "boolean":
        val = random.choice([True, False])
    elif ftype == "text":
        val = fake.paragraph(nb_sentences=field.get("sentences", 1)) if HAS_FAKER else "Sample text content here."
    elif ftype == "derived":
        template = field["template"]
        val = template
        for key, v in row_context.items():
            val = val.replace(f"{{{key}}}", str(v).lower().replace(" ", ""))
    else:
        val = ""

    if field.get("unique", False):
        attempts = 0
        while str(val) in used_values.get(fname, set()):
            attempts += 1
            if attempts > 10000:
                raise RuntimeError(f"Cannot generate unique value for '{fname}'")
            val = generate_value({**field, "unique": False}, row_context, used_values)

    used_values.setdefault(fname, set()).add(str(val))
    return val

def generate_data(schema):
    n_rows = schema["n_rows"]
    fields = schema["fields"]
    used_vals = {}
    rows = []
    for _ in range(n_rows):
        row = {}
        for field in fields:
            row[field["name"]] = generate_value(field, row, used_vals)
        rows.append(row)
    return rows

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        schema = request.get_json()
        if not schema or "fields" not in schema:
            return jsonify({"error": "Invalid schema"}), 400
        data = generate_data(schema)
        return jsonify({"success": True, "data": data, "count": len(data)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["POST"])
def download():
    try:
        schema = request.get_json()
        data = generate_data(schema)
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype="text/csv",
            as_attachment=True,
            download_name="synthetic_data.csv"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
