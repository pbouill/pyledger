from enum import StrEnum


class AccountType(StrEnum):
    SAVINGS = "savings"
    CHEQUING = "chequing"
    CREDIT_CARD = "credit_card"
    LINE_OF_CREDIT = "line_of_credit"
    INVESTMENT = "investment"
    LOAN = "loan"
