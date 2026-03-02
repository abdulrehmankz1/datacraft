# DataCraft — Synthetic Data Generator

> A lightweight, web-based tool for generating realistic synthetic datasets from a visual schema builder. No database. No complex setup. Just run and generate.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)
![Faker](https://img.shields.io/badge/Faker-24.0-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## Overview

**DataCraft** is a browser-based synthetic data generator built with Python and Flask. It lets you visually define a data schema — fields, types, constraints — and instantly generate hundreds or thousands of rows of realistic fake data. Export as CSV or JSON with one click.

Built for developers, data scientists, and QA engineers who need realistic test data fast.

---

## Features

- **Visual Schema Builder** — Add, configure, and remove fields through a clean UI — no code needed
- **10 Supported Field Types** — `int`, `float`, `name_first`, `name_last`, `email`, `date`, `categorical`, `boolean`, `text`, `derived`
- **Smart Constraints** — Set min/max ranges, decimal precision, date ranges, and category lists
- **Derived Fields** — Generate values from other fields (e.g. build email from `{first_name}.{last_name}`)
- **Uniqueness Enforcement** — Mark any field as unique to prevent duplicate values
- **Live Preview Table** — See generated data instantly in the browser (up to 200 rows previewed)
- **Export Options** — Download as `.csv` or `.json` with a single click
- **Zero Frontend Dependencies** — Pure HTML, CSS, and JavaScript — no React, no npm

---

## Project Structure

```
datacraft/
├── app.py                  # Flask backend — routes, data generation logic
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Full frontend (single-file UI)
├── output/                 # Optional: local CSV output folder
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/abdulrehmankz1/datacraft.git
cd datacraft

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Then open your browser and visit:

```
http://localhost:5000
```

---

## How to Use

1. **Set row count** — Choose how many rows you want to generate (1 to 10,000)
2. **Add fields** — Click **Add Field**, enter a name, and select a type
3. **Configure constraints** — Set min/max, categories, date ranges, etc.
4. **Generate** — Click **Generate Data** to produce your dataset
5. **Preview** — Review the output in the live table
6. **Export** — Download as CSV or JSON

---

## Supported Field Types

| Type | Description | Options |
|------|-------------|---------|
| `int` | Random integer | min, max, unique |
| `float` | Random decimal number | min, max, decimals |
| `name_first` | Realistic first name | — |
| `name_last` | Realistic last name | — |
| `email` | Random email address | — |
| `date` | Random date string | start, end |
| `categorical` | One value from a list | categories (comma-separated) |
| `boolean` | True or False | — |
| `text` | Random paragraph | sentences |
| `derived` | Built from other fields | template (e.g. `{first_name}@mail.com`) |

---

## Deploying to the Web

### Render.com (Recommended — Free)

```bash
# Add to requirements.txt
gunicorn==21.2.0
```

Create a `Procfile` in the root:

```
web: gunicorn app:app
```

Update `app.py` to read the port from environment:

```python
import os
app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
```

Then push to GitHub and connect the repo on [render.com](https://render.com).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Data Generation | Faker |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Export | Python `csv` module, JSON |

---

## Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

**Abdul Rehman**
GitHub: [@abdulrehmankz1](https://github.com/abdulrehmankz1)

---

*Built with Python & Flask*
