from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from axiom.db.engine import get_db
from axiom.db.models import Rule
from axiom.models.schemas import RuleSchema, RuleCreateSchema, RuleUpdateSchema

router = APIRouter(prefix="/api", tags=["rules"])

@router.get("/rules", response_model=list[RuleSchema])
def api_list_rules(db: Session = Depends(get_db)):
    return db.query(Rule).filter(Rule.active == True).order_by(Rule.priority, Rule.id).all()

@router.post("/rules", response_model=RuleSchema, status_code=201)
def api_create_rule(payload: RuleCreateSchema, db: Session = Depends(get_db)):
    rule = Rule(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.put("/rules/{rule_id}", response_model=RuleSchema)
def api_update_rule(rule_id: int, payload: RuleUpdateSchema, db: Session = Depends(get_db)):
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)
    db.commit()
    db.refresh(rule)
    return rule

@router.delete("/rules/{rule_id}")
def api_delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"deleted": True, "rule_id": rule_id}
