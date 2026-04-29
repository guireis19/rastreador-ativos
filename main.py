import os
import yfinance as yf
from flask import Flask, render_template, request, redirect, flash
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

app = Flask(__name__)
app.secret_key = "reis_tech_chave_secreta" # ESSENCIAL para o feedback funcionar

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# O Render consegue ler o arquivo .db que você subiu no GitHub
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

# --- LÓGICA DE BUSCA (YFINANCE) ---
def buscar_e_salvar(ticker_escolhido):
    try:
        acao = yf.Ticker(ticker_escolhido)
        # Tenta buscar o preço atual usando fast_info
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

# --- ROTAS ---
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

# --- INICIALIZAÇÃO PARA O RENDER (MUITO IMPORTANTE) ---
if __name__ == "__main__":
    # 1. Pegamos a porta que o Render nos dá (variável de ambiente)
    # 2. Se estiver rodando no seu PC, ele usa a 5000 como padrão
    port = int(os.environ.get("PORT", 5000))
    
    # 3. host='0.0.0.0' é o que permite o link externo funcionar
    # 4. debug=False é o recomendado para quando o site está no ar
    app.run(host='0.0.0.0', port=port, debug=False)