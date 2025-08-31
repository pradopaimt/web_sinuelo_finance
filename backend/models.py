from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Numeric, Date
from sqlalchemy.orm import relationship
from .database import Base

class Natureza(Base):
    __tablename__ = "natureza"
    code = Column(String, primary_key=True)
    nome = Column(String, nullable=False)
    contas = relationship("Conta", back_populates="natureza", cascade="all, delete")

class Conta(Base):
    __tablename__ = "conta"
    id = Column(Integer, primary_key=True, index=True)
    natureza_code = Column(String, ForeignKey("natureza.code"), nullable=False)
    nome = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)   
    natureza = relationship("Natureza", back_populates="contas")
    categorias = relationship("Categoria", back_populates="conta", cascade="all, delete")

class Categoria(Base):
    __tablename__ = "categoria"
    id = Column(Integer, primary_key=True, index=True)
    conta_id = Column(Integer, ForeignKey("conta.id"), nullable=False)
    nome = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)   
    conta = relationship("Conta", back_populates="categorias")

class Centro(Base):
    __tablename__ = "centro"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, nullable=False)
    area = Column(Numeric, default=0)

class Lancamento(Base):
    __tablename__ = "lancamento"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False)
    natureza_code = Column(String, ForeignKey("natureza.code"), nullable=False)
    conta_id = Column(Integer, ForeignKey("conta.id"))
    categoria_id = Column(Integer, ForeignKey("categoria.id"))
    centro_id = Column(Integer, ForeignKey("centro.id"))
    pagamento = Column(String)
    descricao = Column(String)
    fornecedor_cliente = Column(String)
    ir = Column(Boolean, default=False)
    valor = Column(Numeric, nullable=False)
    anexo_nome = Column(String, nullable=True)
