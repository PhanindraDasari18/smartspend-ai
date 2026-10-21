from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from statistics import median
from app.schemas import Transaction

CENT = Decimal("0.01")
def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)

def summarize(transactions: list[Transaction]) -> dict:
    income = sum((t.amount for t in transactions if t.type == "income"), Decimal(0))
    gross = sum((t.amount for t in transactions if t.type == "expense"), Decimal(0))
    refunds = sum((t.amount for t in transactions if t.type == "refund"), Decimal(0))
    net_expenses = gross - refunds
    cashflow = income - net_expenses
    return {"income": money(income), "gross_expenses": money(gross), "refunds": money(refunds), "net_expenses": money(net_expenses), "net_cash_flow": money(cashflow), "savings_rate": money(cashflow / income * 100) if income > 0 else None}

def category_totals(transactions: list[Transaction]) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = defaultdict(Decimal)
    for t in transactions:
        if t.type == "expense": totals[t.category] += t.amount
        elif t.type == "refund": totals[t.category] -= t.amount
    return {k: money(v) for k, v in totals.items()}

def anomalies(transactions: list[Transaction]) -> list[dict]:
    by_cat: dict[str, list[Transaction]] = defaultdict(list)
    for t in transactions:
        if t.type == "expense": by_cat[t.category].append(t)
    result = []
    for cat, rows in by_cat.items():
        if len(rows) < 5: continue
        values = [float(t.amount) for t in rows]
        med = median(values); mad = median([abs(v-med) for v in values])
        threshold = med + max(3 * mad, med * 1.5, 100)
        for t in rows:
            if float(t.amount) > threshold:
                result.append({"date": t.date.isoformat(), "description": t.description, "amount": money(t.amount), "category": cat, "reason": f"This is well above the {cat} historical median of ₹{med:,.2f}; review if unexpected."})
    return result

def answer(question: str, transactions: list[Transaction]) -> str:
    q = question.lower(); summary = summarize(transactions); cats = category_totals(transactions)
    if "most" in q or "highest" in q:
        if not cats: return "There are no expense records in the supplied period to compare."
        name, amount = max(cats.items(), key=lambda item: item[1])
        return f"{name} is the highest net-spending category at ₹{amount:,.2f} across the supplied transactions."
    if "food" in q:
        amount = cats.get("Food", Decimal(0))
        return f"Net Food spending across the supplied transactions is ₹{amount:,.2f}."
    if "refund" in q:
        return f"Refunds in the supplied transactions total ₹{summary['refunds']:,.2f}; they reduce net expenses, not income."
    if "cash flow" in q or "cashflow" in q or "save" in q:
        return f"Net cash flow is ₹{summary['net_cash_flow']:,.2f} (income ₹{summary['income']:,.2f} less net expenses ₹{summary['net_expenses']:,.2f})."
    if "spend" in q or "expense" in q:
        return f"Net expenses across the supplied transactions are ₹{summary['net_expenses']:,.2f}, including ₹{summary['gross_expenses']:,.2f} gross expenses and ₹{summary['refunds']:,.2f} refunds."
    if "review" in q or "unusual" in q:
        found = anomalies(transactions)
        if not found: return "No unusual expenses were identified. Category history may be too limited to flag anomalies."
        return f"{len(found)} expense(s) stand out against category history. Review: " + "; ".join(f"{a['description']} ₹{a['amount']:,.2f}" for a in found[:5])
    return "I can answer questions about spending, Food, the highest category, refunds, net cash flow, savings, and unusual expenses. The answer uses only the transactions supplied for this request."
