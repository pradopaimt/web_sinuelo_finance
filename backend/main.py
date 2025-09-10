from fastapi import Query, FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import pathlib, os, io, base64
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from fastapi import Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from . import models, schemas
from .database import SessionLocal, engine, get_db
from .seed import seed_taxonomy
from sqlalchemy import extract, func
from datetime import datetime, date
from babel.dates import format_date

# dentro do extrato_socio
mes = format_date(l.data, "MMMM/yyyy", locale="pt_BR")

app = FastAPI(title="Sinuelo Finance API")

# monta estáticos em /static

static_dir = pathlib.Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")
        
@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse(static_dir / "index.html")
    
# ---- Configuração OAuth ----
CLIENT_SECRETS_FILE = "credentials.json" 
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
REDIRECT_URI = "https://sinuelo-finance-api.fly.dev/oauth2callback"
TOKEN_FILE = "token.json"

user_credentials = None

creds_b64 = os.environ.get("GOOGLE_OAUTH_CREDENTIALS_BASE64")
if creds_b64:
    creds_json = base64.b64decode(creds_b64).decode("utf-8")
    with open(CLIENT_SECRETS_FILE, "w") as f:
        f.write(creds_json)

def load_credentials():
    global user_credentials
    if os.path.exists(TOKEN_FILE):
        user_credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
@app.on_event("startup")
def startup_event():
    # insere naturezas/contas/categorias se não existir
    db = SessionLocal()
    seed_taxonomy(db)
    db.close()
    # tenta carregar credenciais salvas
    load_credentials() 

@app.get("/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    return RedirectResponse(authorization_url)

@app.get("/oauth2callback")
def oauth2callback(request: Request):
    global user_credentials
    state = request.query_params.get("state")
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=state
    )
    auth_response = str(request.url).replace("http://", "https://")
    flow.fetch_token(authorization_response=auth_response)
    user_credentials = flow.credentials
    # salva token para persistir entre reinícios
    with open(TOKEN_FILE, "w") as token:
        token.write(user_credentials.to_json())
    return {"status": "Autenticado com sucesso!"}

@app.get("/api/naturezas", response_model=list[schemas.NaturezaOut])
def list_naturezas(db: Session = Depends(get_db)):
    return db.query(models.Natureza).all()

@app.get("/api/naturezas/{code}/contas", response_model=list[schemas.ContaOut])
def list_contas(code: str, db: Session = Depends(get_db)):
    nat = db.query(models.Natureza).filter(models.Natureza.code == code).first()
    if not nat:
        raise HTTPException(status_code=404, detail="Natureza não encontrada")
    return [c for c in nat.contas if c.ativo]

# ---- Upload de arquivo ----
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    global user_credentials
    if not user_credentials:
        raise HTTPException(status_code=401, detail="Usuário não autenticado. Acesse /authorize primeiro.")

    contents = await file.read()
    media = MediaIoBaseUpload(io.BytesIO(contents), mimetype=file.content_type)
    file_metadata = {"name": file.filename,  "parents": ["1DyLOUlFknjZszui8sy5mb8tSvsXO0SlT"]}

    service = build("drive", "v3", credentials=user_credentials)
    f = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name, webViewLink"
    ).execute()

    return {"id": f["id"], "name": f["name"], "url": f["webViewLink"]}

# ---- Contas → Categorias ----
@app.get("/api/contas/{conta_id}/categorias", response_model=list[schemas.CategoriaOut])
def list_categorias(conta_id: int, db: Session = Depends(get_db)):
    conta = db.query(models.Conta).filter_by(id=conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return [cat for cat in conta.categorias if cat.ativo]


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

@app.put("/api/contas/{conta_id}/inativar", response_model=schemas.ContaOut)
def inativar_conta(conta_id: int, db: Session = Depends(get_db)):
    conta = db.query(models.Conta).filter_by(id=conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    conta.ativo = False
    db.commit()
    db.refresh(conta)
    return conta
    
@app.post("/api/contas", response_model=schemas.ContaOut)
def create_conta(conta: schemas.ContaCreate, db: Session = Depends(get_db)):
    nat = db.query(models.Natureza).filter(models.Natureza.code == conta.natureza_code).first()
    if not nat:
        raise HTTPException(status_code=404, detail="Natureza não encontrada")
    
    obj = models.Conta(
        nome=conta.nome,
        natureza_code=nat.code,
        ativo=True
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.put("/api/categorias/{cat_id}/inativar", response_model=schemas.CategoriaOut)
def inativar_categoria(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(models.Categoria).filter_by(id=cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    cat.ativo = False
    db.commit()
    db.refresh(cat)
    return cat

@app.post("/api/categorias", response_model=schemas.CategoriaOut)
def create_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    # precisa associar a conta
    conta = db.query(models.Conta).filter(models.Conta.id == categoria.conta_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    obj = models.Categoria(
        nome=categoria.nome,
        conta_id=conta.id,
        ativo=True
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# ---------- Rotas de Sócios ---------- #

@app.post("/api/socios/", response_model=schemas.SocioResponse)
def create_socio(socio: schemas.SocioCreate, db: Session = Depends(get_db)):
    db_socio = models.Socio(nome=socio.nome, saldo_inicial=socio.saldo_inicial)
    db.add(db_socio)
    db.commit()
    db.refresh(db_socio)
    return db_socio

@app.get("/api/socios/", response_model=list[schemas.SocioResponse])
def list_socios(db: Session = Depends(get_db)):
    return db.query(models.Socio).all()

@app.put("/api/socios/{socio_id}/saldo_inicial", response_model=schemas.SocioResponse)
def update_saldo_inicial(socio_id: int, saldo: schemas.SocioUpdateSaldo, db: Session = Depends(get_db)):
    socio = db.query(models.Socio).filter(models.Socio.id == socio_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Sócio não encontrado")
    socio.saldo_inicial = saldo.saldo_inicial
    db.commit()
    db.refresh(socio)
    return socio

@app.get("/api/socios/{socio_id}/extrato")
def extrato_socio(
    socio_id: int,
    start: str = Query(None, description="Data inicial no formato YYYY-MM"),
    end: str = Query(None, description="Data final no formato YYYY-MM"),
    db: Session = Depends(get_db)
):
    socio = db.query(models.Socio).filter(models.Socio.id == socio_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Sócio não encontrado")

    # converter strings YYYY-MM em datas
    try:
        start_date = datetime.strptime(start, "%Y-%m").date() if start else date(2000, 1, 1)
        end_date = datetime.strptime(end, "%Y-%m").date() if end else date.today()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato inválido, use YYYY-MM")

    # mapeamento simples pelo nome do sócio
    if "EDUARDO" in socio.nome.upper():
        categoria_aporte = "APORTE EDUARDO PAIM"
        categoria_retirada = "RETIRADAS EDUARDO PAIM"
    elif "ROBERTO" in socio.nome.upper():
        categoria_aporte = "APORTE ROBERTO PAIM"
        categoria_retirada = "RETIRADAS ROBERTO PAIM"
    else:
        raise HTTPException(status_code=400, detail="Sócio sem mapeamento de aportes/retiradas")

    # buscar lançamentos no período
    lancs = (
        db.query(models.Lancamento)
        .filter(models.Lancamento.data >= start_date, models.Lancamento.data <= end_date)
        .all()
    )

    from collections import defaultdict
    resumo = defaultdict(lambda: {"entradas": 0, "saidas": 0})
    
    for l in lancs:
        mes = l.data.strftime("%B/%Y")

        cat = None
        if l.categoria_id:
            cat = db.query(models.Categoria).filter(models.Categoria.id == l.categoria_id).first()

        if cat and cat.nome.upper() == categoria_aporte:
            resumo[mes]["entradas"] += float(l.valor)
        elif cat and cat.nome.upper() == categoria_retirada:
            resumo[mes]["saidas"] += float(l.valor)

    # ordenar meses
    saldo = float(socio.saldo_inicial or 0)
    resultado = []
    for mes in sorted(resumo.keys(), key=lambda m: datetime.strptime(m, "%B/%Y")):
        entradas = resumo[mes]["entradas"]
        saidas = resumo[mes]["saidas"]
        saldo += entradas - saidas
        resultado.append({
            "mes": mes,
            "entradas": entradas,
            "saidas": saidas,
            "saldo": saldo
        })

    return {
        "socio": socio.nome,
        "saldo_inicial": float(socio.saldo_inicial or 0),
        "periodo": {"inicio": str(start_date), "fim": str(end_date)},
        "extrato": resultado
    }