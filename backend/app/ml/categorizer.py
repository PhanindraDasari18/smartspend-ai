import re
from app.schemas import CategoryPrediction
from app.ml.training_data import SYNTHETIC_EXAMPLES

RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Food", ("swiggy", "zomato", "restaurant", "cafe", "grocery", "bigbasket", "blinkit")),
    ("Transport", ("uber", "ola", "metro", "petrol", "fuel", "irctc", "rapido")),
    ("Shopping", ("amazon", "flipkart", "myntra", "shopping")),
    ("Bills", ("electricity", "recharge", "broadband", "water bill", "jio", "airtel")),
    ("Education", ("course", "college", "tuition", "udemy")),
    ("Health", ("pharmacy", "hospital", "doctor", "apollo")),
    ("Entertainment", ("netflix", "movie", "spotify", "hotstar")),
    ("Housing", ("rent", "maintenance")),
    ("Salary", ("salary", "payroll")),
]
_model = None

def _classifier():
    global _model
    if _model is None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import make_pipeline
            x, y = zip(*SYNTHETIC_EXAMPLES)
            _model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode"), LogisticRegression(max_iter=500, random_state=17))
            _model.fit(x, y)
        except Exception:
            return None
    return _model

def evaluate_synthetic_model() -> dict:
    """Return a real held-out evaluation; never present synthetic scores as user-data performance."""
    from sklearn.model_selection import train_test_split
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
    x, y = zip(*SYNTHETIC_EXAMPLES)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=17, stratify=y)
    model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode"), LogisticRegression(max_iter=500, random_state=17))
    model.fit(x_train, y_train)
    predicted = model.predict(x_test)
    labels = sorted(set(y))
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, predicted, average="macro", zero_division=0)
    return {"dataset": "synthetic demonstration examples; not representative of users", "split": "stratified 75/25, random_state=17", "precision_macro": float(precision), "recall_macro": float(recall), "f1_macro": float(f1), "labels": labels, "confusion_matrix": confusion_matrix(y_test, predicted, labels=labels).tolist()}

def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", text.lower()).strip()

def predict_category(description: str, merchant: str | None = None) -> CategoryPrediction:
    text = normalize(f"{description} {merchant or ''}")
    for category, terms in RULES:
        if any(term in text for term in terms):
            return CategoryPrediction(category=category, confidence=0.94, method="merchant_rule", needs_review=False)
    model = _classifier()
    if model is None:
        return CategoryPrediction(category="Other", confidence=0.35, method="fallback", needs_review=True)
    try:
        probabilities = model.predict_proba([text])[0]
        index = int(probabilities.argmax())
        confidence = float(probabilities[index])
        return CategoryPrediction(category=str(model.classes_[index]), confidence=confidence, method="tfidf_logistic_regression_synthetic", needs_review=confidence < 0.62)
    except Exception:
        return CategoryPrediction(category="Other", confidence=0.35, method="fallback", needs_review=True)
