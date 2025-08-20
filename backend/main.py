"""
Backend API for the Sinuelo Finance application.

This service exposes a simple REST API implemented using FastAPI.  It uses
SQLite (via Python's built‑in ``sqlite3`` module) to persist data.  The
database schema models the same entities you manipulated in the browser
prototype: naturezas (types of financial flows), contas (accounts) and
categorias (sub‑accounts), centros de custo (cost centres), and
lançamentos (individual financial transactions).  A handful of helper
endpoints also provide aggregated summaries.

The design goal for this first iteration was to provide a thin layer
around a relational store so that the existing front‑end can be
incrementally adapted to call real endpoints rather than using
``localStorage``.  The seed data populates the database on first run so
that you begin with the same taxonomy that was defined in the prototype.
"""

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, APIRouter, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import sqlite3
import os
import pathlib

DB_NAME = os.environ.get("SINUELO_DB_NAME", "sinuelo.db")

# Router for API endpoints, prefixing all routes with /api
api = APIRouter(prefix="/api")

def get_connection() -> sqlite3.Connection:
    """Open a connection to the SQLite database with foreign keys enabled."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db() -> None:
    """Create tables if they do not exist and seed default data."""
    conn = get_connection()
    cur = conn.cursor()
    # Define schema
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS natureza (
            code TEXT PRIMARY KEY,
            nome TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS conta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            natureza_code TEXT NOT NULL,
            nome TEXT NOT NULL,
            FOREIGN KEY(natureza_code) REFERENCES natureza(code) ON DELETE CASCADE
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS categoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conta_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            FOREIGN KEY(conta_id) REFERENCES conta(id) ON DELETE CASCADE
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS centro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            area REAL NOT NULL DEFAULT 0
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS lancamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            natureza_code TEXT NOT NULL,
            conta_id INTEGER,
            categoria_id INTEGER,
            centro_id INTEGER,
            pagamento TEXT,
            descricao TEXT,
            ir INTEGER NOT NULL DEFAULT 0,
            valor REAL NOT NULL,
            anexo_nome TEXT,
            FOREIGN KEY(natureza_code) REFERENCES natureza(code) ON DELETE SET NULL,
            FOREIGN KEY(conta_id) REFERENCES conta(id) ON DELETE SET NULL,
            FOREIGN KEY(categoria_id) REFERENCES categoria(id) ON DELETE SET NULL,
            FOREIGN KEY(centro_id) REFERENCES centro(id) ON DELETE SET NULL
        )
        """
    )

    # Check if naturezas already exist; if not, seed default taxonomy
    cur.execute("SELECT COUNT(*) AS count FROM natureza")
    count = cur.fetchone()["count"]
    if count == 0:
        # Default taxonomy replicating the prototype's TAX_DEFAULT structure.
        taxonomy = [
            {
                "code": "RO",
                "nome": "RECEITAS OPERACIONAIS",
                "contas": [
                    {
                        "nome": "PECUÁRIA",
                        "cats": ["VENDAS DE BOVINOS", "VENDAS DE OVINOS", "OUTRAS"],
                    },
                    {
                        "nome": "ALUGUÉIS E ARRENDAMENTOS",
                        "cats": ["PASTOS"],
                    },
                    {
                        "nome": "AGRICULTURA",
                        "cats": ["SOJA", "MILHO", "SORGO", "FENO"],
                    },
                    {
                        "nome": "OUTROS",
                        "cats": [
                            "INDENIZAÇÃO E REPAROS",
                            "SERVIÇOS PRESTADOS",
                            "SEGUROS",
                            "VENDA DE EQUIPAMENTOS",
                        ],
                    },
                ],
            },
            {
                "code": "RNO",
                "nome": "RECEITAS NÃO OPERACIONAIS",
                "contas": [
                    {
                        "nome": "RECEITAS NÃO OPERACIONAIS",
                        "cats": [
                            "EMPRÉSTIMOS TERCEIROS",
                            "APORTE EDUARDO PAIM",
                            "APORTE ROBERTO PAIM",
                            "JUROS E CORREÇÕES",
                            "VENDA DE INSUMOS",
                            "FINANCIAMENTO BANCÁRIO",
                            "CRÉDITOS EMPRESAS INSUMOS",
                            "CRÉDITOS EMPRESAS MÁQUINAS",
                            "OUTROS",
                        ],
                    }
                ],
            },
            {
                "code": "DO",
                "nome": "DESPESAS OPERACIONAIS",
                "contas": [
                    {
                        "nome": "MÃO DE OBRA",
                        "cats": [
                            "SALÁRIOS",
                            "ENCARGOS E BENEFÍCIOS",
                            "MÃO DE OBRA EVENTUAL",
                            "ALIMENTAÇÃO",
                            "HORAS EXTRAS/DESC.REMUNERADO",
                            "UNIFORMES",
                            "SALÁRIO EDUARDO PAIM",
                        ],
                    },
                    {
                        "nome": "INSUMOS BOVINOS",
                        "cats": [
                            "SAL MINERAL",
                            "RAÇÕES E SUPLEMENTAÇÃO",
                            "MEDICAMENTOS E VACINAS",
                            "MATERIAIS E FERRAMENTAS",
                            "INSEMINAÇÃO - SÊMEN",
                            "INSEMINAÇÃO - NITROGÊNIO",
                            "SERVIÇOS - IATF",
                            "FRETES",
                            "COMISSÕES",
                            "VETERINÁRIO E EXAMES",
                            "OUTROS",
                        ],
                    },
                    {
                        "nome": "INSUMOS OVINOS",
                        "cats": [
                            "SAL MINERAL",
                            "RAÇÕES E SUPLEMENTAÇÃO",
                            "MEDICAMENTOS E VACINAS",
                            "MATERIAIS E FERRAMENTAS",
                            "FRETES",
                            "COMISSÕES",
                            "VETERINÁRIO E EXAMES",
                            "OUTROS",
                        ],
                    },
                    {
                        "nome": "MANUTENÇÃO DE INSTALAÇÕES",
                        "cats": ["EMPREITEIROS", "INSUMO E MATERIAIS", "OUTROS"],
                    },
                    {
                        "nome": "PASTAGENS",
                        "cats": [
                            "SEMENTE E MUDAS",
                            "ADUBOS E FERTILIZANTES",
                            "DEFENSIVOS E HERBICIDAS",
                            "MATERIAIS E FERRAMENTAS",
                            "OUTROS",
                        ],
                    },
                    {
                        "nome": "MANUTENÇÃO DE MÁQUINAS E VEÍCULOS",
                        "cats": [
                            "DO-MANUTENÇÃO MÁQUINAS-TRATOR MF 4275",
                            "DO-MANUTENÇÃO MÁQUINAS-TRATOR MF 4292",
                            "DO-MANUTENÇÃO MÁQUINAS-TRATOR CASE 180",
                            "DO-MANUTENÇÃO MÁQUINAS-TRATOR MF 65X",
                            "DO-MANUTENÇÃO MÁQUINAS-TRATOR JD 5078",
                            "DO-MANUTENÇÃO MÁQUINAS-PA XCMG ZL30BR",
                            "DO-MANUTENÇÃO MÁQUINAS-COLHEDadeira 1550",
                            "DO-MANUTENÇÃO MÁQUINAS-COLHEDadeira 7500",
                            "DO-MANUTENÇÃO MÁQUINAS-PLANTADEIRA MF",
                            "DO-MANUTENÇÃO MÁQUINAS-PULVERIZADOR 3000 ADVANCED",
                            "DO-MANUTENÇÃO MÁQUINAS-IMPLEMENTOS",
                            "DO-MANUTENÇÃO MÁQUINAS-VEÍCULOS",
                            "DO-MANUTENÇÃO MÁQUINAS-MOTO",
                            "DO-MANUTENÇÃO MÁQUINAS-INSUMOS",
                            "DO-MANUTENÇÃO MÁQUINAS-LUBRIFICANTES, FILTROS E GRAXAS",
                            "OUTROS",
                        ],
                    },
                    {
                        "nome": "GRÃOS",
                        "cats": [
                            "SEMENTES",
                            "ADUBOS E FERTILIZANTES",
                            "INOCULANTES",
                            "ADUBOS FOLIARES",
                            "INSETICIDAS",
                            "FUNGICIDAS",
                            "HERBICIDAS",
                            "ÓLEO E REDUTOR DE PH",
                            "TRATAMENTO DE SEMENTE",
                            "MÃO-DE-OBRA",
                            "INSUMOS E MATERIAIS",
                            "SERV. TERCERIZADOS",
                            "TRANSPORTES E FRETES",
                            "ARMAZENAGEM E SECAGEM",
                            "ASSISTÊNCIA TÉCNICA",
                            "CORREÇÃO DO SOLO",
                            "DIVERSOS",
                        ],
                    },
                    {
                        "nome": "ADMINISTRATIVO",
                        "cats": [
                            "IMPOSTO, TAXAS E LICENÇAS",
                            "ESCRITÓRIO",
                            "PROFISSIONAIS ESPECIALIZADOS",
                            "JUROS, MULTAS, CORREÇÕES e IOF",
                            "CARTÓRIO E REGISTROS",
                            "SEGUROS",
                            "ENERGIA",
                            "ALIMENTAÇÃO CASA SEDE",
                            "TELEFONE + INTERNET",
                            "ANIMAIS DOMÉSTICOS",
                            "COMBUSTÍVEL VEÍCULO",
                            "CURSOS E TREINAMENTOS",
                            "FUNRURAL/SENAR",
                            "DOAÇÕES",
                            "OUTROS",
                            "RAÇÕES E INSUMOS - AVES E SUÍNOS",
                            "COMBUSTÍVEL MÁQUINAS",
                        ],
                    },
                ],
            },
            {
                "code": "DNO",
                "nome": "DESPESAS NÃO OPERACIONAIS",
                "contas": [
                    {
                        "nome": "COMPRA DE SEMOVENTES",
                        "cats": ["BOVINOS", "EQUINOS", "OVINOS", "FRETES E COMISSÕES"],
                    },
                    {
                        "nome": "INVESTIMENTO EM EXPANSÃO",
                        "cats": ["MÁQUINAS", "BENFEITORIAS", "CERCAS", "MOBILIÁRIO", "FERRAMENTAS", "CORREÇÃO DO SOLO"],
                    },
                    {
                        "nome": "FINANCIAMENTOS",
                        "cats": [
                            "EMPRÉSTIMOS TERCEIROS",
                            "EMPRÉSTIMOS ROBERTO PAIM",
                            "EMPRÉSTIMOS EDUARDO PAIM",
                            "PAGAMENTOS EMPRESAS MÁQUINAS",
                            "PAGAMENTOS EMPRESAS INSUMOS",
                            "FINANC BANCÁRIO MÁQUINAS",
                            "FINANC BANCÁRIO CUSTEIO AGRÍCOLA/PECUÁRIO",
                            "FINANC BANCÁRIO INVESTIMENTOS",
                            "DESCONTOS, DEVOLUÇÃO E ACERTOS",
                            "OUTROS",
                        ],
                    },
                ],
            },
        ]

        # Insert naturezas
        for nat in taxonomy:
            cur.execute(
                "INSERT INTO natureza(code, nome) VALUES (?, ?)",
                (nat["code"], nat["nome"]),
            )
            # Insert contas and categorias
            for conta in nat["contas"]:
                cur.execute(
                    "INSERT INTO conta(natureza_code, nome) VALUES (?, ?)",
                    (nat["code"], conta["nome"]),
                )
                conta_id = cur.lastrowid
                for cat_name in conta["cats"]:
                    cur.execute(
                        "INSERT INTO categoria(conta_id, nome) VALUES (?, ?)",
                        (conta_id, cat_name),
                    )

        # Default centros de custo
        default_centros = ["Geral", "Soja", "Bovinos", "Ovinos"]
        for nome_centro in default_centros:
            cur.execute(
                "INSERT OR IGNORE INTO centro(nome, area) VALUES (?, 0)",
                (nome_centro,),
            )

    conn.commit()
    conn.close()

# Pydantic models for API responses and requests
class NaturezaOut(BaseModel):
    code: str
    nome: str

class ContaOut(BaseModel):
    id: int
    natureza_code: str
    nome: str

class CategoriaOut(BaseModel):
    id: int
    conta_id: int
    nome: str

class CentroOut(BaseModel):
    id: int
    nome: str
    area: float

class LancamentoIn(BaseModel):
    data: str = Field(..., description="ISO date YYYY-MM-DD")
    natureza_code: str
    conta_id: Optional[int] = None
    categoria_id: Optional[int] = None
    centro_id: Optional[int] = None
    pagamento: Optional[str] = None
    descricao: Optional[str] = None
    ir: bool = False
    valor: float
    anexo_nome: Optional[str] = None

class LancamentoOut(BaseModel):
    id: int
    data: str
    natureza_code: str
    conta_id: Optional[int] = None
    categoria_id: Optional[int] = None
    centro_id: Optional[int] = None
    pagamento: Optional[str] = None
    descricao: Optional[str] = None
    ir: bool = False
    valor: float
    anexo_nome: Optional[str] = None

class SummaryItem(BaseModel):
    key: str
    receita: float
    despesa: float
    resultado: float
    percentual: float

class SummaryOut(BaseModel):
    totals: SummaryItem
    by_natureza: List[SummaryItem]
    by_conta: List[SummaryItem]
    by_categoria: List[SummaryItem]

app = FastAPI(title="Sinuelo Finance API")

# Allow cross-origin requests so the front-end can call the API from a browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup() -> None:
    """Initialize the database on startup."""
    init_db()

# All routes are registered on the `api` router, which is prefixed with "/api"
@api.get("/naturezas", response_model=List[NaturezaOut])
def list_naturezas() -> List[NaturezaOut]:
    """Return all naturezas."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT code, nome FROM natureza ORDER BY code")
    rows = [NaturezaOut(code=row["code"], nome=row["nome"]) for row in cur.fetchall()]
    conn.close()
    return rows

@api.get("/naturezas/{code}/contas", response_model=List[ContaOut])
def list_contas_for_natureza(code: str = Path(..., description="Natureza code")) -> List[ContaOut]:
    conn = get_connection()
    cur = conn.cursor()
    # Validate natureza exists
    cur.execute("SELECT 1 FROM natureza WHERE code=?", (code,))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Natureza not found")
    cur.execute(
        "SELECT id, natureza_code, nome FROM conta WHERE natureza_code=? ORDER BY nome",
        (code,),
    )
    rows = [ContaOut(id=row["id"], natureza_code=row["natureza_code"], nome=row["nome"]) for row in cur.fetchall()]
    conn.close()
    return rows

@api.get("/contas/{conta_id}/categorias", response_model=List[CategoriaOut])
def list_categorias_for_conta(conta_id: int = Path(..., description="Conta ID")) -> List[CategoriaOut]:
    conn = get_connection()
    cur = conn.cursor()
    # Validate conta exists
    cur.execute("SELECT 1 FROM conta WHERE id=?", (conta_id,))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Conta not found")
    cur.execute(
        "SELECT id, conta_id, nome FROM categoria WHERE conta_id=? ORDER BY nome",
        (conta_id,),
    )
    rows = [CategoriaOut(id=row["id"], conta_id=row["conta_id"], nome=row["nome"]) for row in cur.fetchall()]
    conn.close()
    return rows

@api.get("/centros", response_model=List[CentroOut])
def list_centros() -> List[CentroOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, area FROM centro ORDER BY nome")
    rows = [CentroOut(id=row["id"], nome=row["nome"], area=row["area"]) for row in cur.fetchall()]
    conn.close()
    return rows

@api.post("/centros", response_model=CentroOut)
def create_centro(centro: CentroOut) -> CentroOut:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO centro(nome, area) VALUES (?, ?)",
            (centro.nome, centro.area),
        )
        centro_id = cur.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Centro already exists")
    # Return the created centre
    created = CentroOut(id=centro_id, nome=centro.nome, area=centro.area)
    conn.close()
    return created

@api.post("/lancamentos", response_model=LancamentoOut, status_code=201)
def create_lancamento(item: LancamentoIn) -> LancamentoOut:
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Insert into lancamento; ir stored as int 0/1
        cur.execute(
            """
            INSERT INTO lancamento(
                data, natureza_code, conta_id, categoria_id, centro_id,
                pagamento, descricao, ir, valor, anexo_nome
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.data,
                item.natureza_code,
                item.conta_id,
                item.categoria_id,
                item.centro_id,
                item.pagamento,
                item.descricao,
                1 if item.ir else 0,
                item.valor,
                item.anexo_nome,
            ),
        )
        conn.commit()
        lanc_id = cur.lastrowid
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    # Fetch and return the created lancamento
    cur.execute("SELECT * FROM lancamento WHERE id=?", (lanc_id,))
    row = cur.fetchone()
    conn.close()
    return LancamentoOut(
        id=row["id"],
        data=row["data"],
        natureza_code=row["natureza_code"],
        conta_id=row["conta_id"],
        categoria_id=row["categoria_id"],
        centro_id=row["centro_id"],
        pagamento=row["pagamento"],
        descricao=row["descricao"],
        ir=bool(row["ir"]),
        valor=row["valor"],
        anexo_nome=row["anexo_nome"],
    )

@api.get("/lancamentos", response_model=List[LancamentoOut])
def list_lancamentos(
    start_date: Optional[str] = Query(None, description="Start date ISO YYYY-MM-DD inclusive"),
    end_date: Optional[str] = Query(None, description="End date ISO YYYY-MM-DD inclusive"),
    centro_id: Optional[int] = Query(None, description="Filter by centro ID"),
    ir_only: Optional[bool] = Query(False, description="Filter by IR-only flag"),
) -> List[LancamentoOut]:
    conn = get_connection()
    cur = conn.cursor()
    # Build query dynamically
    query = "SELECT * FROM lancamento WHERE 1=1"
    params: List[Any] = []
    if start_date:
        query += " AND data >= ?"
        params.append(start_date)
    if end_date:
        query += " AND data <= ?"
        params.append(end_date)
    if centro_id:
        query += " AND centro_id = ?"
        params.append(centro_id)
    if ir_only:
        query += " AND ir = 1"
    query += " ORDER BY data DESC, id DESC"
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    conn.close()
    return [
        LancamentoOut(
            id=row["id"],
            data=row["data"],
            natureza_code=row["natureza_code"],
            conta_id=row["conta_id"],
            categoria_id=row["categoria_id"],
            centro_id=row["centro_id"],
            pagamento=row["pagamento"],
            descricao=row["descricao"],
            ir=bool(row["ir"]),
            valor=row["valor"],
            anexo_nome=row["anexo_nome"],
        )
        for row in rows
    ]

@api.delete("/lancamentos/{lanc_id}", status_code=204)
def delete_lancamento(lanc_id: int = Path(..., description="Lancamento ID")) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM lancamento WHERE id=?", (lanc_id,))
    conn.commit()
    conn.close()
    return None

def _aggregate(rows: List[sqlite3.Row], key_func) -> Dict[str, Dict[str, float]]:
    """
    Helper to aggregate receita and despesa per key.  The ``key_func`` extracts
    a grouping key from each row.
    """
    result: Dict[str, Dict[str, float]] = {}
    for row in rows:
        key = key_func(row)
        if key is None:
            continue
        if key not in result:
            result[key] = {"receita": 0.0, "despesa": 0.0}
        # Naturezas starting with R (RO/RNO) are receitas; D (DO/DNO) are despesas
        if row["natureza_code"].startswith("R"):
            result[key]["receita"] += row["valor"]
        else:
            result[key]["despesa"] += row["valor"]
    return result

@api.get("/summary", response_model=SummaryOut)
def get_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    centro_id: Optional[int] = Query(None),
    ir_only: Optional[bool] = Query(False),
) -> SummaryOut:
    """Return aggregated totals by natureza, conta and categoria along with overall totals."""
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM lancamento WHERE 1=1"
    params: List[Any] = []
    if start_date:
        query += " AND data >= ?"
        params.append(start_date)
    if end_date:
        query += " AND data <= ?"
        params.append(end_date)
    if centro_id:
        query += " AND centro_id = ?"
        params.append(centro_id)
    if ir_only:
        query += " AND ir = 1"
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    conn.close()
    # Overall totals
    total_receita = sum(row["valor"] for row in rows if row["natureza_code"].startswith("R"))
    total_despesa = sum(row["valor"] for row in rows if row["natureza_code"].startswith("D"))
    total_result = total_receita - total_despesa
    # Aggregations
    by_nat = _aggregate(rows, lambda r: r["natureza_code"])
    by_conta = _aggregate(rows, lambda r: str(r["conta_id"]) if r["conta_id"] else None)
    by_cat = _aggregate(rows, lambda r: str(r["categoria_id"]) if r["categoria_id"] else None)
    # Convert to SummaryItem list with percentages
    def build_items(mapping: Dict[str, Dict[str, float]]) -> List[SummaryItem]:
        items = []
        for key, data in mapping.items():
            receita = data["receita"]
            despesa = data["despesa"]
            resultado = receita - despesa
            perc = (resultado / total_result * 100) if total_result != 0 else 0.0
            items.append(
                SummaryItem(
                    key=key,
                    receita=receita,
                    despesa=despesa,
                    resultado=resultado,
                    percentual=perc,
                )
            )
        # Sort descending by result magnitude
        items.sort(key=lambda x: x.resultado, reverse=True)
        return items
    summary = SummaryOut(
        totals=SummaryItem(
            key="TOTAL",
            receita=total_receita,
            despesa=total_despesa,
            resultado=total_result,
            percentual=100.0,
        ),
        by_natureza=build_items(by_nat),
        by_conta=build_items(by_conta),
        by_categoria=build_items(by_cat),
    )
    return summary

# Include the API router and serve static files (index.html and assets)
app.include_router(api)
static_dir = pathlib.Path(__file__).resolve().parents[1]  # project root containing index.html
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
