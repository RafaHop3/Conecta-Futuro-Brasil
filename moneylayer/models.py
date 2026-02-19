from .database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

class SocialFund(Base):
    """Tabela de Controle de Fundos com Interesse Social"""
    __tablename__ = "social_funds"
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, index=True) # Ex: "Conecta Futuro"
    global_value = Column(Float, default=0.0) # Valor Global disponível
    social_impact_score = Column(Integer, default=100) # Score de impacto
    last_audit = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    """Registro imutável de movimentações financeiras"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    origin = Column(String) # Origem auditada pelo TheOrbeSystems
