import yfinance as yf
from flask import Flask, render_template, request, redirect, flash
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

app = Flask(__name__)
app.secret_key = "reis_tech_chave_secreta" # ESSENCIAL para o feedback funcionar

# Configuração do Banco de Dados
engine = create_engine('sqlite:///banco_teste.db')
Base = declarative_base()

class HistoricoPreco(Base):
    __tablename__ = 'historico_precos'
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10))
    preco = Column(Float)
    data_consulta = Column(DateTime, default=datetime.now)

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def buscar_e_salvar(ticker_escolhido):
    try:
        acao = yf.Ticker(ticker_escolhido)
        # Tenta buscar o preço atual
        info = acao.fast_info
        preco_agora = info['last_price']
        
        if preco_agora is None or preco_agora == 0:
            return False

        db = SessionLocal()
        novo_registro = HistoricoPreco(ticker=ticker_escolhido.upper(), preco=preco_agora)
        db.add(novo_registro)
        db.commit()
        db.close()
        return True
    except Exception:
        return False

@app.route("/", methods=["GET", "POST"])
def index():
    db = SessionLocal()
    
    if request.method == "POST":
        ticker = request.form.get("ticker").strip().upper()
        if ticker:
            sucesso = buscar_e_salvar(ticker)
            if sucesso:
                flash(f"Ativo {ticker} adicionado com sucesso!", "success")
            else:
                flash(f"Erro: Não encontramos o ticker '{ticker}'.", "error")
        return redirect("/")

    # Busca o histórico ordenado pelo mais recente
    historico = db.query(HistoricoPreco).order_by(HistoricoPreco.data_consulta.desc()).all()
    db.close()
    return render_template("index.html", historico=historico)

if __name__ == "__main__":
    app.run(debug=True)