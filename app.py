from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from io import BytesIO
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Função para criar e conectar ao banco de dados SQLite
def create_db():
    conn = sqlite3.connect('escala.db')
    cursor = conn.cursor()
    
    # Criação das tabelas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Colaboradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            horas_semanais INTEGER,
            papel TEXT,
            excecoes TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Escala (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE,
            horario_inicio TIME,
            horario_fim TIME,
            colaborador_id INTEGER,
            folga BOOLEAN,
            FOREIGN KEY (colaborador_id) REFERENCES Colaboradores(id)
        )
    ''')
    conn.commit()
    
    # Inserção de dados de teste
    insert_test_data(conn)
    
    return conn

# Função para inserir dados de teste
def insert_test_data(conn):
    cursor = conn.cursor()
    
    # Inserir colaboradores
    colaboradores = [
        ("Luis Filipe (Responsável de Loja)", 40, "full-time", None),
        ("Elisamara", 40, "full-time", None),
        ("José Rafael", 40, "full-time", None),
        ("Mayara", 40, "full-time", None),
        ("Bárbara (35 horas)", 35, "part-time", None),
        ("Temporária", 40, "full-time", None)
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO Colaboradores (nome, horas_semanais, papel, excecoes)
        VALUES (?, ?, ?, ?)
    ''', colaboradores)
    conn.commit()

# Função para sugerir escalas automáticas com base nas regras do projeto
def gerar_escala():
    conn = create_db()
    cursor = conn.cursor()
    
    # Obter colaboradores
    cursor.execute("SELECT id, nome, horas_semanais, papel FROM Colaboradores")
    colaboradores = cursor.fetchall()

    # Lógica de distribuição
    hoje = datetime.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())  # Segunda-feira da semana atual
    dias_semana = [inicio_semana + timedelta(days=i) for i in range(6)]  # Segunda a sábado

    escala = []
    finais_de_semana = []

    for colaborador in colaboradores:
        id_colaborador, nome, horas_semanais, papel = colaborador
        horas_por_dia = 8 if papel == "full-time" else 7

        total_horas = 0
        folgas_restantes = 2
        escala_colaborador = []

        for dia in dias_semana:
            if folgas_restantes > 0 and (dia.weekday() != 5 or papel == "part-time"):
                # Garantir duas folgas na semana e somente um colaborador full-time por final de semana
                escala_colaborador.append((dia.date(), None, None, True))
                folgas_restantes -= 1
            else:
                if total_horas + horas_por_dia <= horas_semanais:
                    escala_colaborador.append((dia.date(), "09:00", "17:00", False))
                    total_horas += horas_por_dia

        escala.extend([(data, inicio, fim, folga, id_colaborador) for data, inicio, fim, folga in escala_colaborador])

    # Inserir escala gerada no banco de dados
    cursor.executemany('''
        INSERT INTO Escala (data, horario_inicio, horario_fim, colaborador_id, folga)
        VALUES (?, ?, ?, ?, ?)
    ''', escala)
    conn.commit()
    conn.close()

# Rota para processar e gerar a escala automaticamente
@app.route('/gerar_escala', methods=['POST'])
def gerar_escala_automatica():
    try:
        gerar_escala()
        return jsonify({"message": "Escala gerada com sucesso."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Atualização para especificar caminho completo do requirements.txt
@app.route('/install_requirements', methods=['POST'])
def install_requirements():
    try:
        import subprocess
        subprocess.check_call(["pip", "install", "-r", "C:\\xampp\\htdocs\\escala-projeto\\requirements.txt"])
        return jsonify({"message": "Dependências instaladas com sucesso."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
