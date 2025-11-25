"""Feature configurations for the model."""

# Target variable
TARGET = "SalePrice"

# All features used in the model
FEATURES = [
    "LotArea",
    "YearBuilt",
    "YearRemodAdd",
    "YrSold",
    "OverallQual",
    "OverallCond",
]

# Categorical features
CAT_FEATURES = []

# Ordinal features
ORD_FEATURES = []

# Numerical features (after feature engineering)
NUM_FEATURES = [
    "LotArea",
    "LotAge",
    "OverallQual",
    "OverallCond",
    "YearsSinceRemod",
]
