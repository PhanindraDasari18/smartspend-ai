from datetime import date
from decimal import Decimal
from app.schemas import Transaction
from app.services.finance import summarize, anomalies
from app.ml.categorizer import predict_category
from app.services.finance import answer

def tx(amount, kind="expense", category="Food", desc="meal", day=1):
    return Transaction(date=date(2026, 10, day), description=desc, amount=Decimal(str(amount)), type=kind, category=category)

def test_refunds_are_not_income_and_totals_are_decimal():
    result = summarize([tx("100.10"), tx("20.00", "refund"), tx("200", "income", "Salary")])
    assert result == {"income": Decimal("200.00"), "gross_expenses": Decimal("100.10"), "refunds": Decimal("20.00"), "net_expenses": Decimal("80.10"), "net_cash_flow": Decimal("119.90"), "savings_rate": Decimal("59.95")}

def test_zero_income_rate_is_none():
    assert summarize([tx(20)])["savings_rate"] is None

def test_merchant_rules_and_review_fallback():
    assert predict_category("Swiggy order").category == "Food"
    assert predict_category("misc payment").needs_review

def test_anomaly_requires_history():
    assert anomalies([tx(100), tx(150)]) == []

def test_assistant_uses_calculated_values():
    assert "₹100.00" in answer("How much did I spend?", [tx(100)])
