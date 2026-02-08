from flask import Flask, render_template, request, redirect
import sqlite3
import os
from psd_manager import ler_campos_psd, gerar_png

app = Flask(__name__)

UPLOAD_PSD = "static/psd_base"
FOTOS = "static/fotos"
GERADOS = "static/gerados"

for p in [UPLOAD_PSD, FOTOS, GERADOS]:
    if not os.path.exists(p):
        os.makedirs(p)

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS config (
        id INTEGER PRIMARY KEY,
        psd TEXT,
        area_foto TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def admin():
    return render_template("admin.html")

@app.route("/upload_psd", methods=["POST"])
def upload_psd():
    arquivo = request.files["psd"]
    caminho = os.path.join(UPLOAD_PSD, arquivo.filename)
    arquivo.save(caminho)

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM config")
    c.execute("INSERT INTO config (id, psd) VALUES (1, ?)", (arquivo.filename,))
    conn.commit()
    conn.close()

    return redirect("/configurar")

@app.route("/configurar")
def configurar():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT psd FROM config WHERE id=1")
    psd = c.fetchone()[0]
    conn.close()

    caminho = os.path.join(UPLOAD_PSD, psd)
    campos = ler_campos_psd(caminho)

    return render_template("configurar.html", campos=campos)

@app.route("/gerar")
def gerar():
    return render_template("gerar.html")

@app.route("/processar", methods=["POST"])
def processar():
    foto = request.files["foto"]
    foto_path = os.path.join(FOTOS, foto.filename)
    foto.save(foto_path)

    dados = {}

    for chave in request.form:
        dados[chave] = request.form[chave]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT psd, area_foto FROM config WHERE id=1")
    psd, area = c.fetchone()
    conn.close()

    area = eval(area)

    psd_path = os.path.join(UPLOAD_PSD, psd)
    saida = os.path.join(GERADOS, "resultado.png")

    gerar_png(psd_path, dados, foto_path, area, saida)

    return render_template("resultado.html", imagem=saida)

if __name__ == "__main__":
    app.run()
