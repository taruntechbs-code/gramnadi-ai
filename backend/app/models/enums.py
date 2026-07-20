from enum import StrEnum


class EnterpriseType(StrEnum):
    AGRICULTURE = "agriculture"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    SERVICES = "services"
    FOOD_PROCESSING = "food_processing"
    HANDICRAFT = "handicraft"
    OTHER = "other"


class Sector(StrEnum):
    AGRICULTURE = "agriculture"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    SERVICES = "services"
    FOOD_AND_BEVERAGE = "food_and_beverage"
    HANDICRAFT = "handicraft"
    OTHER = "other"


class LoanType(StrEnum):
    TERM_LOAN = "term_loan"
    WORKING_CAPITAL = "working_capital"
    MICROFINANCE = "microfinance"
    KISAN_CREDIT_CARD = "kisan_credit_card"
    OTHER = "other"


class LoanStatus(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"
    OVERDUE = "overdue"
    DEFAULTED = "defaulted"
    SETTLED = "settled"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WeatherCondition(StrEnum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    HAZE = "haze"
    OTHER = "other"


class InterventionType(StrEnum):
    FINANCIAL_COUNSELLING = "financial_counselling"
    INVENTORY_ADJUSTMENT = "inventory_adjustment"
    WORKING_CAPITAL = "working_capital"
    LOAN_RESTRUCTURING = "loan_restructuring"
    MARKET_LINKAGE = "market_linkage"
    OTHER = "other"


class InterventionStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GraphNodeType(StrEnum):
    ENTERPRISE = "enterprise"
    SUPPLIER = "supplier"
    CUSTOMER = "customer"
    MARKET = "market"
    LENDER = "lender"
    GOVERNMENT_SCHEME = "government_scheme"
    OTHER = "other"
