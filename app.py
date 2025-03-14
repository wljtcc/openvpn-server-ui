from flask import Flask, jsonify, render_template
import os

app = Flask(__name__)

# Caminho para o arquivo de status do OpenVPN
OPENVPN_STATUS_FILE = "/run/openvpn-server/status-server.log"

def parse_openvpn_status():
    """Lê e analisa o arquivo de status do OpenVPN."""
    if not os.path.exists(OPENVPN_STATUS_FILE):
        return {"error": "Arquivo de status do OpenVPN não encontrado"}

    users = []
    with open(OPENVPN_STATUS_FILE, 'r') as file:
        lines = file.readlines()
        parsing = False

        for line in lines:
            # Identifica a seção CONNECTED CLIENTS
            if "Common Name,Real Address" in line:
                parsing = True
                continue

            if parsing:
                if line.strip() == "":
                    break  # Fim da seção
                parts = line.split(',')
                if len(parts) >= 5:
                    users.append({
                        "common_name": parts[0].strip(),
                        "real_address": parts[1].strip(),
                        "bytes_received": parts[2].strip(),
                        "bytes_sent": parts[3].strip(),
                        "connected_since": parts[4].strip()
                    })

    return users

@app.route("/api/users", methods=["GET"])
def get_users():
    """Rota para retornar a lista de usuários conectados."""
    users = parse_openvpn_status()
    return jsonify(users)

@app.route("/")
def index():
    """Rota para o frontend."""
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True,
            port=5000,
            host='0.0.0.0')