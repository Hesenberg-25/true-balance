# 💰 True Balance

A modern, interactive **financial tracking web application** built with [Streamlit](https://streamlit.io/). Track your expenses, set monthly budgets, and run financial calculations — all in one place.

---

## ✨ Features

| Module | What you can do |
|---|---|
| 🏠 **Dashboard** | Overview of total expenses, budget remaining, category breakdown, and recent transactions |
| 📊 **Expense Tracker** | Add expenses, filter by month/category, view pie charts, bar charts, and a spending heatmap |
| 💰 **Budget Tracker** | Set monthly budgets, compare budget vs actual spending with visual alerts |
| 🧮 **Interest Calculator** | Simple Interest, Compound Interest, Loan Amortization, Income Tax, and SIP calculators |

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Hesenberg-25/true-balance.git
cd true-balance

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
streamlit run streamlit_app.py
```

The app will open automatically in your default browser at **http://localhost:8501**.

---

## 📁 File Structure

```
true-balance/
├── streamlit_app.py        # Main app entry point — dashboard & navigation
├── expense_tracker.py      # Expense tracking module
├── budget_tracker.py       # Budget management module
├── interest_calculator.py  # Financial calculators (SI, CI, Loan, Tax, SIP)
├── requirements.txt        # Python dependencies
├── .gitignore              # Excludes CSV data files & cache
└── README.md               # This file
```

> **Data files** (`Expenses.csv`, `Budget.csv`) are created automatically in the project directory when you first add data and are excluded from version control via `.gitignore`.

---

## 🗂️ CSV Structure

### Expenses.csv
| Column | Description |
|---|---|
| Date | Entry date (YYYY-MM-DD) |
| Month | Short month name (Jan–Dec) |
| Category | One of: Food, Transport, Household, Education, Health, Utilities, Other |
| Amount | Expense amount in ₹ |

### Budget.csv
| Column | Description |
|---|---|
| Month | Short month name (Jan–Dec) |
| Budget | Monthly budget amount in ₹ |

---

## 🧮 Interest Calculator Details

- **Simple Interest** — SI = (P × R × T) / 100
- **Compound Interest** — A = P × (1 + r/n)^(n×t) with yearly / half-yearly / quarterly / monthly compounding
- **Loan Amortization** — EMI schedule with month-by-month principal/interest/balance breakdown
- **Income Tax (India)** — New tax regime with ₹75,000 standard deduction and progressive slabs (0 – 30%)
- **SIP** — Systematic Investment Plan future value with growth chart

---

## 🛠️ Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web application framework |
| `pandas` | Data manipulation and CSV I/O |
| `plotly` | Interactive charts and graphs |

---

