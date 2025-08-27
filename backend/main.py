from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, SessionLocal
from .seed import seed_taxonomy
from fastapi.staticfiles import StaticFiles
import pathlib
from fastapi import UploadFile, File, APIRouter
import io
import os, json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

app = FastAPI(title="Sinuelo Finance API")

static_dir = pathlib.Path(__file__).resolve().parent.parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

# ---- Configuração do Google Drive ----
import base64

raw_secret = os.getenv("GOOGLE_SERVICE_KEY")
if not raw_secret:
    raise RuntimeError("GOOGLE_SERVICE_KEY não configurado")

decoded = base64.b64decode(raw_secret).decode("utf-8")
creds_dict = json.loads(decoded)

creds = service_account.Credentials.from_service_account_info(creds_dict)
drive_service = build("drive", "v3", credentials=creds)

FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER") 

# Dependency para injetar sessão em cada request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    # insere naturezas/contas/categorias se não existir
    db = SessionLocal()
    seed_taxonomy(db)
    db.close()

@app.get("/api/naturezas", response_model=list[schemas.NaturezaOut])
def list_naturezas(db: Session = Depends(get_db)):
    return db.query(models.Natureza).all()

@app.get("/api/naturezas/{code}/contas", response_model=list[schemas.ContaOut])
def list_contas(code: str, db: Session = Depends(get_db)):
    nat = db.query(models.Natureza).filter(models.Natureza.code == code).first()
    if not nat:
        raise HTTPException(status_code=404, detail="Natureza não encontrada")
    return nat.contas

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    media = MediaIoBaseUpload(io.BytesIO(contents), mimetype=file.content_type)
    file_metadata = {"name": file.filename, "parents": [FOLDER_ID]} if FOLDER_ID else {"name": file.filename}
    f = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name, webViewLink"
    ).execute()
    drive_service.permissions().create(
    fileId=f["id"],
    body={"type": "anyone", "role": "reader"}
    ).execute()
    
    return {"id": f["id"], "name": f["name"], "url": f["webViewLink"]}
    
# ---- Contas → Categorias ----
@app.get("/api/contas/{conta_id}/categorias", response_model=list[schemas.CategoriaOut])
def list_categorias(conta_id: int, db: Session = Depends(get_db)):
    conta = db.query(models.Conta).filter_by(id=conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return conta.categorias


# ---- Centros ----
@app.get("/api/centros", response_model=list[schemas.CentroOut])
def list_centros(db: Session = Depends(get_db)):
    return db.query(models.Centro).all()

@app.post("/api/centros", response_model=schemas.CentroOut)
def create_centro(centro: schemas.CentroCreate, db: Session = Depends(get_db)):
    obj = models.Centro(nome=centro.nome, area=centro.area)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/centros/{centro_id}")
def delete_centro(centro_id: int, db: Session = Depends(get_db)):
    centro = db.query(models.Centro).filter_by(id=centro_id).first()
    if not centro:
        raise HTTPException(status_code=404, detail="Centro não encontrado")
    db.delete(centro)
    db.commit()
    return {"detail": "Centro removido"}


# ---- Lançamentos ----
@app.get("/api/lancamentos", response_model=list[schemas.LancamentoOut])
def list_lancamentos(db: Session = Depends(get_db)):
    return db.query(models.Lancamento).all()

@app.post("/api/lancamentos", response_model=schemas.LancamentoOut)
def create_lancamento(l: schemas.LancamentoCreate, db: Session = Depends(get_db)):
    obj = models.Lancamento(**l.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.put("/api/lancamentos/{lanc_id}", response_model=schemas.LancamentoOut)
def update_lancamento(lanc_id: int, l: schemas.LancamentoUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.Lancamento).filter_by(id=lanc_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    for field, value in l.dict(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/lancamentos/{lanc_id}")
def delete_lancamento(lanc_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Lancamento).filter_by(id=lanc_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    db.delete(obj)
    db.commit()
    return {"detail": "Lançamento removido"}
