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


# Função para listar usuários cadastrados com paginação
def get_registered_users(page, per_page):
    if not os.path.exists(USER_CONFIG_FOLDER):
        return {"error": "Diretório de configurações de usuários não encontrado."}

    all_users = [f.replace(".ovpn", "") for f in os.listdir(USER_CONFIG_FOLDER) if f.endswith(".ovpn")]
    total_users = len(all_users)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_users = all_users[start:end]

    return {
        "users": paginated_users,
        "total": total_users,
        "page": page,
        "per_page": per_page
    }


# Rota para listar usuários conectados
@app.route("/api/connected-users", methods=["GET"])
def list_connected_users():
    users = get_connected_users()
    return jsonify(users)


# Rota para listar usuários cadastrados com paginação
@app.route("/api/registered-users", methods=["GET"])
def list_registered_users():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        return jsonify({"error": "Parâmetros de paginação inválidos."}), 400

    users = get_registered_users(page, per_page)
    return jsonify(users)


# Rota para download do arquivo de configuração
@app.route("/api/users/<username>/download", methods=["GET"])
def download_user_config(username):
    user_config_path = os.path.join(USER_CONFIG_FOLDER, f"{username}.ovpn")
    if not os.path.exists(user_config_path):
        return jsonify({"error": "Configuração do usuário não encontrada."}), 404

    return send_file(user_config_path, as_attachment=True)


# Rota para excluir o arquivo de configuração de um usuário
@app.route("/api/users/<username>/delete", methods=["DELETE"])
def delete_user_config(username):
    user_config_path = os.path.join(USER_CONFIG_FOLDER, f"{username}.ovpn")
    if not os.path.exists(user_config_path):
        return jsonify({"error": "Configuração do usuário não encontrada."}), 404

    os.remove(user_config_path)
    return jsonify({"success": f"Configuração do usuário {username} excluída com sucesso."})


# Rota para o frontend
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True,
            port=5000,
            host='0.0.0.0')