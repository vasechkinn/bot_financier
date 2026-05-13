from typing import List
from pydantic import BaseModel, Field, field_validator

class IncomeOp(BaseModel):
    summa: float = Field(gt=0, description='сумма должна быть больше 0')
    category: str = 'другое'
    purpose: str = 'на мечту'

    @field_validator('category')
    @classmethod
    def valid_category(cls, category_: str) -> str:
        allowed = ("еда", "развлечения", "отдых", "зарплата", "другое")

        if category_ not in allowed:
            raise ValueError(f"возможные категории: {', '.join(allowed)}")
        
        return category_
    
class ExpenseOp(BaseModel):
    summa: float = Field(gt=0, description='сумма должна быть больше 0')
    category: str = 'другое'
    purpose: str = 'на мечту'

    @field_validator('category')
    @classmethod
    def valid_category(cls, category_: str) -> str:
        allowed = ("еда", "развлечения", "отдых", "подарок", "другое")

        if category_ not in allowed:
            raise ValueError(f"возможные категории: {', '.join(allowed)}")
        
        return category_
    
def check_message(args: list[str]) -> dict:
    
    summa = args[0].strip() if len(args) > 0 else ''
    category = args[1].strip() if len(args) > 1 else ''
    purpose = args[2].strip() if len(args) > 2 else ''

    return {
        'summa': summa,
        'category': category,
        'purpose': purpose
    }