from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal


# -----------------------------
# Natureza
# -----------------------------
class NaturezaBase(BaseModel):
    code: str
    nome: str


class NaturezaCreate(NaturezaBase):
    pass


class NaturezaUpdate(BaseModel):
    nome: Optional[str] = None


class NaturezaOut(NaturezaBase):
    class Config:
        orm_mode = True


# -----------------------------
# Conta
# -----------------------------
class ContaBase(BaseModel):
    natureza_code: str
    nome: str


class ContaCreate(ContaBase):
    pass


class ContaUpdate(BaseModel):
    nome: Optional[str] = None
    ativo: Optional[bool] = None

class ContaOut(ContaBase):
    id: int
    ativo: bool
    class Config:
        orm_mode = True

# -----------------------------
# Categoria
# -----------------------------
class CategoriaBase(BaseModel):
    conta_id: int
    nome: str


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = None
    ativo: Optional[bool] = None

class CategoriaOut(CategoriaBase):
    id: int
    ativo: bool
    class Config:
        orm_mode = True


# -----------------------------
# Centro
# -----------------------------
class CentroBase(BaseModel):
    nome: str
    area: Decimal


class CentroCreate(CentroBase):
    pass


class CentroUpdate(BaseModel):
    nome: Optional[str] = None
    area: Optional[Decimal] = None


class CentroOut(CentroBase):
    id: int

    class Config:
        orm_mode = True


# -----------------------------
# Lançamento
# -----------------------------
class LancamentoBase(BaseModel):
    data: date
    natureza_code: str
    conta_id: Optional[int] = None
    categoria_id: Optional[int] = None
    centro_id: Optional[int] = None
    pagamento: Optional[str] = None
    descricao: Optional[str] = None
    fornecedor_cliente: Optional[str] = None
    dre: bool = False
    ir_eduardo: bool = False   
    ir_roberto: bool = False 
    valor: Decimal
    anexo_nome: Optional[str] = None


class LancamentoCreate(LancamentoBase):
    pass


class LancamentoUpdate(BaseModel):
    data: Optional[date] = None
    natureza_code: Optional[str] = None
    conta_id: Optional[int] = None
    categoria_id: Optional[int] = None
    centro_id: Optional[int] = None
    pagamento: Optional[str] = None
    descricao: Optional[str] = None
    fornecedor_cliente: Optional[str] = None
    dre: Optional[bool] = None
    ir_eduardo: Optional[bool] = None  
    ir_roberto: Optional[bool] = None
    valor: Optional[Decimal] = None
    anexo_nome: Optional[str] = None


class LancamentoOut(LancamentoBase):
    id: int

    class Config:
        orm_mode = True
