import shutil
import os
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import database, schemas, auth_utils
from services import ia_module

# 1. Configuration de la sécurité
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# 2. Initialisation de l'application
app = FastAPI(title="DermAI API")

# 3. Création des tables au démarrage
database.Base.metadata.create_all(bind=database.engine)

# 4. Configuration des dossiers pour les images
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

def validate_image(file: UploadFile):
    # Vérification de l'extension 
    allowed_extensions = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Format d'image non supporté (JPG/PNG uniquement)")
    
    # Simulation de vérification de taille (ex: max 5 Mo) 
    # (On pourrait lire la taille réelle ici si nécessaire)

#  ROUTES 

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
def read_root():
    return {"message": "DermAI Backend est opérationnel"}

#  AUTHENTIFICATION 

@app.post("/api/auth/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(database.User).filter(database.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    hashed_pwd = auth_utils.hash_password(user.password)
    new_user = database.User(email=user.email, password_hash=hashed_pwd)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(database.User).filter(database.User.email == form_data.username).first()
    
    if not user or not auth_utils.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=403, detail="Identifiants invalides")
    
    access_token = auth_utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

#  ANALYSE ET HISTORIQUE 

@app.post("/api/analyze")
async def analyze_skin(
    duration: str = Form(...),  
    pain: int = Form(...),
    itching: int = Form(...),
    bleeding: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    token: str = Depends(oauth2_scheme)

):
    # 1. Validation de l'image (Tâche Sprint 3) 
    validate_image(image)

    # 2. Identification utilisateur
    email = auth_utils.get_current_user_email(token)
    user = db.query(database.User).filter(database.User.email == email).first()

    try:
        # 3. Sauvegarde sécurisée
        file_path = f"uploads/{image.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # 4. Calculs IA (Sprint 5 - Formule 0.6/0.4) [cite: 148]
        score_vision = 0.7  # Sera remplacé par Personne 3
        score_nlp = ia_module.analyze_symptoms(duration, pain, itching, bleeding)
        score_final = ia_module.calculate_fusion(score_vision, score_nlp)

        # 5. Risque et Recommandation (Sprint 5) [cite: 149, 150]
        risk_lv, recommendation = ia_module.get_risk_level(score_final)

        # 6. Enregistrement
        new_analysis = database.Analysis(
            user_id=user.id,
            image_path=file_path,
            duration=duration,
            pain=pain,
            itching=itching,
            bleeding=bleeding,
            score_image=score_vision,
            score_symptoms=score_nlp,
            score_global=score_final,
            risk_level=risk_lv,
            recommendation_text=recommendation
        )
        
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)
        return new_analysis

    except Exception as e:
        # Gestion des erreurs imprévues pour éviter le crash du serveur 
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse : {str(e)}")

@app.get("/api/analyses")
def get_user_history(
    limit: int = 10,  
    offset: int = 0,
    db: Session = Depends(database.get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Récupère la liste des analyses avec pagination 
    """
    # 1. Identifier l'utilisateur via le Token
    email = auth_utils.get_current_user_email(token)
    user = db.query(database.User).filter(database.User.email == email).first()

    # 2. Appliquer la pagination à la requête SQL
    # L'ordre est important : filter -> order_by -> offset -> limit -> all
    history = db.query(database.Analysis).filter(
        database.Analysis.user_id == user.id
    ).order_by(
        database.Analysis.created_at.desc()
    ).offset(offset).limit(limit).all() 

    return history

@app.delete("/api/analyses/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(database.get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Supprime une analyse spécifique 
    """
    # 1. Identifier l'utilisateur via le Token
    email = auth_utils.get_current_user_email(token)
    user = db.query(database.User).filter(database.User.email == email).first()

    # 2. Chercher l'analyse dans la base
    # On vérifie l'ID de l'analyse ET qu'elle appartient bien à l'utilisateur connecté
    analysis = db.query(database.Analysis).filter(
        database.Analysis.id == analysis_id,
        database.Analysis.user_id == user.id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analyse non trouvée ou accès refusé")

    # 3. Supprimer le fichier image physique du dossier 'uploads'
    if os.path.exists(analysis.image_path):
        os.remove(analysis.image_path)

    # 4. Supprimer l'entrée dans la base de données
    db.delete(analysis)
    db.commit()

    return {"message": "Analyse et image supprimées avec succès"}

@app.post("/api/analyze/vision")
async def analyze_vision_only(
    image: UploadFile = File(...),
    token: str = Depends(oauth2_scheme)
):
    """
    Endpoint dédié à l'analyse d'image seule 
    """
    # 1. Valider l'image 
    validate_image(image)

    # 2. Sauvegarder temporairement pour l'analyse
    file_path = f"uploads/temp_{image.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # 3. Appel au futur modèle de la Personne 3 
    # Pour l'instant, on garde la simulation à 0.7 [cite: 58, 82]
    score_vision = 0.7 

    return {
        "score_vision": score_vision,
        "status": "Analyse d'image réussie",
        "message": "En attente du modèle réel de la Personne 3"
    }

@app.post("/api/analyze/nlp")
async def analyze_symptoms_only(
    duration: str,
    pain: int,
    itching: int,
    bleeding: int,
    token: str = Depends(oauth2_scheme)
):
    """
    Endpoint dédié à l'analyse des symptômes uniquement 
    """
    # Appel au module IA simulé (sera remplacé par le travail de la Personne 4) [cite: 63, 115]
    score_nlp = ia_module.analyze_symptoms(duration, pain, itching, bleeding)

    return {
        "score_symptoms": score_nlp,
        "status": "Analyse des symptômes réussie",
        "message": "En attente de l'intégration finale DistilBERT"
    }

@app.get("/api/analyses/{analysis_id}")
def get_analysis_detail(
    analysis_id: int,
    db: Session = Depends(database.get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Récupère les détails d'une analyse spécifique par son ID 
    """
    # 1. Identifier l'utilisateur via le Token [cite: 49]
    email = auth_utils.get_current_user_email(token)
    user = db.query(database.User).filter(database.User.email == email).first()

    # 2. Chercher l'analyse et vérifier l'appartenance à l'utilisateur [cite: 18]
    analysis = db.query(database.Analysis).filter(
        database.Analysis.id == analysis_id,
        database.Analysis.user_id == user.id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analyse non trouvée ou accès refusé")

    return analysis

