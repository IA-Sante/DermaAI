from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# L'URL de connexion (on pourra l'automatiser plus tard avec le .env)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/dermai_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODÈLES DE LA BASE DE DONNÉES (Cf. Cahier des charges) ---

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True) # [cite: 141]
    email = Column(String, unique=True, index=True) # [cite: 142]
    password_hash = Column(String) # [cite: 143]
    created_at = Column(DateTime, default=datetime.datetime.utcnow) # [cite: 144]

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, index=True) # [cite: 146]
    user_id = Column(Integer, ForeignKey("users.id")) # [cite: 147]
    image_path = Column(String) # [cite: 148]
    
    # Symptômes (Besoins fonctionnels BF2)
    duration = Column(String) # [cite: 149]
    pain = Column(Integer) # [cite: 150]
    itching = Column(Integer) # [cite: 151]
    bleeding = Column(Integer) # [cite: 152]
    
    # Résultats de l'IA (Module Vision + NLP)
    score_image = Column(Float) # [cite: 153]
    score_symptoms = Column(Float) # [cite: 154]
    score_global = Column(Float) # [cite: 155]
    risk_level = Column(String) # [cite: 156]
    recommendation_text = Column(String) # [cite: 157]
    created_at = Column(DateTime, default=datetime.datetime.utcnow) # [cite: 158]

    

# Fonction pour créer les tables physiquement
def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()