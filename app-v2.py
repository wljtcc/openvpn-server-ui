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


# Rota para listar usuários conectados
@app.route("/api/users", methods=["GET"])
def list_users():
    users = get_connected_users()
    return jsonify(users)


# Rota para criar um novo usuário
@app.route("/api/users", methods=["POST"])
def create_user():
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "Nome de usuário é obrigatório."}), 400

    user_config_path = os.path.join(USER_CONFIG_FOLDER, f"{username}.ovpn")
    if os.path.exists(user_config_path):
        return jsonify({"error": "Usuário já existe."}), 400

    with open(OVPN_TEMPLATE, "r") as template:
        config = template.read().replace("{{username}}", username)

    with open(user_config_path, "w") as config_file:
        config_file.write(config)

    return jsonify({"success": f"Usuário {username} criado com sucesso."})


# Rota para deletar um usuário
@app.route("/api/users/<username>", methods=["DELETE"])
def delete_user(username):
    user_config_path = os.path.join(USER_CONFIG_FOLDER, f"{username}.ovpn")
    if not os.path.exists(user_config_path):
        return jsonify({"error": "Usuário não encontrado."}), 404

    os.remove(user_config_path)
    return jsonify({"success": f"Usuário {username} deletado com sucesso."})


# Rota para desconectar um usuário
@app.route("/api/users/<username>/disconnect", methods=["POST"])
def disconnect_user(username):
    result = subprocess.run(
        ["sudo", "openvpn", "--management", "127.0.0.1", "7505", "kill", username],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode != 0:
        return jsonify({"error": f"Erro ao desconectar o usuário {username}."}), 400

    return jsonify({"success": f"Usuário {username} desconectado com sucesso."})


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