import os
import subprocess
from flask import Flask, jsonify, render_template, request, send_file

app = Flask(__name__)

# Configurações do OpenVPN
OPENVPN_STATUS_FILE = "/run/openvpn-server/status-server.log"
USER_CONFIG_FOLDER = "/opt/openvpn/ovpn/"  # Diretório onde os arquivos de configuração dos usuários estão
OVPN_TEMPLATE = "/etc/openvpn/client-template.ovpn"  # Modelo para criação de novos usuários


# Função para listar usuários conectados
def get_connected_users():
    if not os.path.exists(OPENVPN_STATUS_FILE):
        return {"error": "Arquivo de status do OpenVPN não encontrado."}

    users = []
    with open(OPENVPN_STATUS_FILE, "r") as file:
        lines = file.readlines()
        parsing = False

        for line in lines:
            if "Common Name,Real Address" in line:
                parsing = True
                continue

            if parsing:
                if line.strip() == "":
                    break
                parts = line.split(",")
                if len(parts) >= 5:
                    users.append({
                        "common_name": parts[0].strip(),
                        "real_address": parts[1].strip(),
                        "bytes_received": parts[2].strip(),
                        "bytes_sent": parts[3].strip(),
                        "connected_since": parts[4].strip()
                    })

    return users


# Função para listar usuários cadastrados
def get_registered_users():
    if not os.path.exists(USER_CONFIG_FOLDER):
        return {"error": "Diretório de configurações de usuários não encontrado."}

    users = []
    for filename in os.listdir(USER_CONFIG_FOLDER):
        if filename.endswith(".ovpn"):
            users.append(filename.replace(".ovpn", ""))
    return users


# Rota para listar usuários conectados
@app.route("/api/connected-users", methods=["GET"])
def list_connected_users():
    users = get_connected_users()
    return jsonify(users)


# Rota para listar usuários cadastrados
@app.route("/api/registered-users", methods=["GET"])
def list_registered_users():
    users = get_registered_users()
    return jsonify(users)


# Rota para download do arquivo de configuração
@app.route("/api/users/<username>/download", methods=["GET"])
def download_user_config(username):
    user_config_path = os.path.join(USER_CONFIG_FOLDER, f"{username}.ovpn")
    if not os.path.exists(user_config_path):
        return jsonify({"error": "Configuração do usuário não encontrada."}), 404

    return send_file(user_config_path, as_attachment=True)


# Rota para o frontend
@app.route("/")
def index():
    return render_template("index2.html")


if __name__ == "__main__":
    app.run(debug=True,
            port=5000,
            host='0.0.0.0')