import os
import io
import csv
import random
from datetime import date, timedelta
from flask import Flask, render_template, request, jsonify, send_file

try:
    from faker import Faker
    fake = Faker()
    HAS_FAKER = True
except ImportError:
    HAS_FAKER = False

app = Flask(__name__)

# ─── Helpers ──────────────────────────────────────────────────────────────────

FALLBACK_FIRST = ["Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Hassan", "Sara", "Umar"]
FALLBACK_LAST  = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Khan", "Ahmed", "Ali", "Malik"]

def _random_date(start_str: str, end_str: str) -> str:
    try:
        start = date.fromisoformat(start_str)
        end   = date.fromisoformat(end_str)
        if end < start:
            start, end = end, start
        return str(start + timedelta(days=random.randint(0, (end - start).days)))
    except ValueError:
        return str(date.today())


# ─── Core Generator ───────────────────────────────────────────────────────────

def generate_value(field: dict, row_context: dict, used_values: dict):
    ftype = field.get("type", "")
    fname = field.get("name", "field")

    if ftype == "int":
        lo = int(field.get("min", 0))
        hi = int(field.get("max", 100))
        if lo > hi: lo, hi = hi, lo
        val = random.randint(lo, hi)

    elif ftype == "float":
        lo       = float(field.get("min", 0.0))
        hi       = float(field.get("max", 1.0))
        decimals = max(0, int(field.get("decimals", 2)))
        if lo > hi: lo, hi = hi, lo
        val = round(random.uniform(lo, hi), decimals)

    elif ftype == "name_first":
        val = fake.first_name() if HAS_FAKER else random.choice(FALLBACK_FIRST)

    elif ftype == "name_last":
        val = fake.last_name() if HAS_FAKER else random.choice(FALLBACK_LAST)

    elif ftype == "email":
        val = fake.email() if HAS_FAKER else f"user{random.randint(100, 999)}@example.com"

    elif ftype == "date":
        val = _random_date(
            field.get("start", "2000-01-01"),
            field.get("end",   "2024-12-31")
        )

    elif ftype == "categorical":
        cats = field.get("categories", [])
        val  = random.choice(cats) if cats else "N/A"

    elif ftype == "boolean":
        val = random.choice([True, False])

    elif ftype == "text":
        sentences = max(1, int(field.get("sentences", 1)))
        val = (
            fake.paragraph(nb_sentences=sentences)
            if HAS_FAKER
            else ("Sample text content. " * sentences).strip()
        )

    elif ftype == "derived":
        template = field.get("template", "")
        val = template
        for key, v in row_context.items():
            val = val.replace(f"{{{key}}}", str(v).lower().replace(" ", ""))

    else:
        val = ""

    # ── Uniqueness enforcement ──
    if field.get("unique", False):
        seen = used_values.setdefault(fname, set())
        attempts = 0
        while str(val) in seen:
            attempts += 1
            if attempts > 10_000:
                raise RuntimeError(
                    f"Cannot generate a unique value for field '{fname}' after 10,000 attempts. "
                    "Try a larger min/max range or reduce the number of rows."
                )
            val = generate_value({**field, "unique": False}, row_context, used_values)

    used_values.setdefault(fname, set()).add(str(val))
    return val


def generate_data(schema: dict) -> list:
    n_rows = max(1, min(int(schema.get("n_rows", 10)), 50_000))
    fields = schema.get("fields", [])

    if not fields:
        raise ValueError("Schema must include at least one field.")

    used_vals: dict = {}
    rows = []

    for _ in range(n_rows):
        row = {}
        for field in fields:
            if not field.get("name", "").strip():
                continue
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
        schema = request.get_json(force=True, silent=True)
        if not schema:
            return jsonify({"error": "Invalid or missing JSON body."}), 400
        if "fields" not in schema:
            return jsonify({"error": "Schema must include a 'fields' list."}), 400

        data = generate_data(schema)
        return jsonify({"success": True, "data": data, "count": len(data)})

    except (ValueError, RuntimeError) as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {str(e)}"}), 500


@app.route("/download", methods=["POST"])
def download():
    try:
        schema = request.get_json(force=True, silent=True)
        if not schema:
            return jsonify({"error": "Invalid or missing JSON body."}), 400

        data = generate_data(schema)
        if not data:
            return jsonify({"error": "No data was generated."}), 422

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        output.seek(0)

        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="datacraft_export.csv"
        )

    except (ValueError, RuntimeError) as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {str(e)}"}), 500


@app.route("/health")
def health():
    """Health check endpoint for Render, Railway, and other platforms."""
    return jsonify({"status": "ok", "faker_available": HAS_FAKER}), 200


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
