from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, field_validator

Category = Literal["Food", "Transport", "Shopping", "Bills", "Education", "Health", "Entertainment", "Housing", "Salary", "Transfers", "Savings", "Other"]

class Transaction(BaseModel):
    date: date
    description: str = Field(min_length=1, max_length=300)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    type: Literal["income", "expense", "refund"]
    category: str = Field(default="Other", min_length=1, max_length=60)
    payment_method: str | None = Field(default=None, max_length=50)

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Description cannot be blank")
        return value

class CategorizeRequest(BaseModel):
    description: str = Field(min_length=1, max_length=300)
    merchant: str | None = Field(default=None, max_length=120)

class CategoryPrediction(BaseModel):
    category: str
    confidence: float
    method: str
    needs_review: bool

class AnalyzeRequest(BaseModel):
    transactions: list[Transaction] = Field(max_length=5000)

class AskRequest(AnalyzeRequest):
    question: str = Field(min_length=2, max_length=500)

