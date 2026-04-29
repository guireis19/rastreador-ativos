from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# O SQLite cria um arquivo chamado "banco_teste.db" na sua pasta.
# Não precisa de usuário, senha ou extensão extra!
conn_str = "sqlite:///./banco_teste.db"

engine = create_engine(conn_str, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# A estrutura da tabela (seu modelo UML)
class HistoricoPreco(Base):
    __tablename__ = "historico_precos"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20))
    preco = Column(Float)
    data_consulta = Column(DateTime, default=datetime.now)

# Função para criar o banco e a tabela
def criar_tabelas():
    Base.metadata.create_all(bind=engine)
    print("---------------------------------------")
    print("SUCESSO: Banco de dados SQLite criado!")
    print("---------------------------------------")

if __name__ == "__main__":
    criar_tabelas()