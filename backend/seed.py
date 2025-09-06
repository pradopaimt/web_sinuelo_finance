from sqlalchemy.orm import Session
from . import models

def seed_taxonomy(db: Session):
    if not db.query(models.Natureza).first():
        taxonomy = [
            {
                "code": "RO",
                "nome": "RECEITAS OPERACIONAIS",
                "contas": [
                    {"nome": "PECUÁRIA", "cats": ["VENDAS DE BOVINOS", "VENDAS DE OVINOS", "OUTRAS"]},
                    {"nome": "ALUGUÉIS E ARRENDAMENTOS", "cats": ["PASTOS"]},
                    {"nome": "AGRICULTURA", "cats": ["SOJA", "MILHO", "SORGO", "FENO"]},
                    {"nome": "OUTROS", "cats": ["INDENIZAÇÃO E REPAROS", "SERVIÇOS PRESTADOS", "SEGUROS", "VENDA DE EQUIPAMENTOS"]},
                ],
            },
            {
                "code": "RNO",
                "nome": "RECEITAS NÃO OPERACIONAIS",
                "contas": [
                    {"nome": "RECEITAS NÃO OPERACIONAIS", "cats": [
                        "EMPRÉSTIMOS TERCEIROS", "APORTE EDUARDO PAIM", "APORTE ROBERTO PAIM",
                        "JUROS E CORREÇÕES", "VENDA DE INSUMOS", "FINANCIAMENTO BANCÁRIO",
                        "CRÉDITOS EMPRESAS INSUMOS", "CRÉDITOS EMPRESAS MÁQUINAS", "OUTROS"
                    ]}
                ],
            },
            {
                "code": "DO",
                "nome": "DESPESAS OPERACIONAIS",
                "contas": [
                    {"nome": "MÃO DE OBRA", "cats": [
                        "SALÁRIOS","ENCARGOS E BENEFÍCIOS","MÃO DE OBRA EVENTUAL","ALIMENTAÇÃO",
                        "HORAS EXTRAS/DESC.REMUNERADO","UNIFORMES","SALÁRIO EDUARDO PAIM"
                    ]},
                    {"nome": "INSUMOS BOVINOS", "cats": [
                        "SAL MINERAL","RAÇÕES E SUPLEMENTAÇÃO","MEDICAMENTOS E VACINAS",
                        "MATERIAIS E FERRAMENTAS","INSEMINAÇÃO - SÊMEN","INSEMINAÇÃO - NITROGÊNIO",
                        "SERVIÇOS - IATF","FRETES","COMISSÕES","VETERINÁRIO E EXAMES","OUTROS"
                    ]},
                    {"nome": "INSUMOS OVINOS", "cats": [
                        "SAL MINERAL","RAÇÕES E SUPLEMENTAÇÃO","MEDICAMENTOS E VACINAS",
                        "MATERIAIS E FERRAMENTAS","FRETES","COMISSÕES","VETERINÁRIO E EXAMES","OUTROS"
                    ]},
                    {"nome": "MANUTENÇÃO DE INSTALAÇÕES", "cats": ["EMPREITEIROS", "INSUMO E MATERIAIS", "OUTROS"]},
                    {"nome": "PASTAGENS", "cats": ["SEMENTE E MUDAS","ADUBOS E FERTILIZANTES","DEFENSIVOS E HERBICIDAS","MATERIAIS E FERRAMENTAS","OUTROS"]},
                    {"nome": "MANUTENÇÃO DE MÁQUINAS E VEÍCULOS", "cats": [
                        "TRATOR MF 4275","TRATOR MF 4292","TRATOR CASE 180","TRATOR MF 65X",
                        "TRATOR JD 5078","PA XCMG ZL30BR","COLHETADEIRA 1550","COLHETADEIRA 7500",
                        "PLANTADEIRA MF","PULVERIZADOR 3000 ADVANCED","IMPLEMENTOS","VEÍCULOS",
                        "MOTO","DO-MANUTENÇÃO MÁQUINAS-INSUMOS","LUBRIFICANTES, FILTROS E GRAXAS","OUTROS"
                    ]},
                    {"nome": "GRÃOS", "cats": [
                        "SEMENTES","ADUBOS E FERTILIZANTES","INOCULANTES","ADUBOS FOLIARES",
                        "INSETICIDAS","FUNGICIDAS","HERBICIDAS","ÓLEO E REDUTOR DE PH","TRATAMENTO DE SEMENTE",
                        "MÃO-DE-OBRA","INSUMOS E MATERIAIS","SERV. TERCERIZADOS","TRANSPORTES E FRETES",
                        "ARMAZENAGEM E SECAGEM","ASSISTÊNCIA TÉCNICA","CORREÇÃO DO SOLO","DIVERSOS"
                    ]},
                    {"nome": "ADMINISTRATIVO", "cats": [
                        "IMPOSTO, TAXAS E LICENÇAS","ESCRITÓRIO","PROFISSIONAIS ESPECIALIZADOS",
                        "JUROS, MULTAS, CORREÇÕES e IOF","CARTÓRIO E REGISTROS","SEGUROS","ENERGIA",
                        "ALIMENTAÇÃO CASA SEDE","TELEFONE + INTERNET","ANIMAIS DOMÉSTICOS","COMBUSTÍVEL VEÍCULO",
                        "CURSOS E TREINAMENTOS","FUNRURAL/SENAR","DOAÇÕES","OUTROS",
                        "RAÇÕES E INSUMOS - AVES E SUÍNOS","COMBUSTÍVEL MÁQUINAS"
                    ]},
                ],
            },
            {
                "code": "DNO",
                "nome": "DESPESAS NÃO OPERACIONAIS",
                "contas": [
                    {"nome": "COMPRA DE SEMOVENTES", "cats": ["BOVINOS", "EQUINOS", "OVINOS", "FRETES E COMISSÕES"]},
                    {"nome": "INVESTIMENTO EM EXPANSÃO", "cats": ["MÁQUINAS","BENFEITORIAS","CERCAS","MOBILIÁRIO","FERRAMENTAS","CORREÇÃO DO SOLO"]},
                    {"nome": "FINANCIAMENTOS", "cats": [
                        "EMPRÉSTIMOS TERCEIROS","RETIRADAS ROBERTO PAIM","RETIRADAS EDUARDO PAIM",
                        "PAGAMENTOS EMPRESAS MÁQUINAS","PAGAMENTOS EMPRESAS INSUMOS",
                        "FINANC BANCÁRIO MÁQUINAS","FINANC BANCÁRIO CUSTEIO AGRÍCOLA/PECUÁRIO",
                        "FINANC BANCÁRIO INVESTIMENTOS","DESCONTOS, DEVOLUÇÃO E ACERTOS","OUTROS"
                    ]},
                ],
            },
        ]

        # 👇 loop no nível certo
        for nat in taxonomy:
            natureza = models.Natureza(code=nat["code"], nome=nat["nome"])
            db.add(natureza)
            for conta in nat["contas"]:
                c = models.Conta(nome=conta["nome"], natureza=natureza)
                db.add(c)
                for cat in conta["cats"]:
                    db.add(models.Categoria(nome=cat, conta=c))

    # centros default
    for nome_centro in ["Geral", "Soja", "Bovinos", "Ovinos"]:
        if not db.query(models.Centro).filter_by(nome=nome_centro).first():
            db.add(models.Centro(nome=nome_centro, area=0))

    # sócios default
    for nome in ["Eduardo Paim", "Roberto Paim"]:
        if not db.query(models.Socio).filter_by(nome=nome).first():
            db.add(models.Socio(nome=nome, saldo_inicial=0))

    db.commit()
