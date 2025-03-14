from flask import Flask, jsonify, request, send_file
import os

app = Flask(__name__)

# Directory where OpenVPN configuration files are stored
OPENVPN_CONFIG_DIR = "/opt/openvpn/ovpn/s"

# Mocked data for demonstration purposes
MOCK_USERS = [
    {"username": "user1", "ipAddress": "192.168.1.10"},
    {"username": "user2", "ipAddress": "192.168.1.11"},
    {"username": "user3", "ipAddress": "192.168.1.12"},
    {"username": "user4", "ipAddress": "192.168.1.13"},
    {"username": "user5", "ipAddress": "192.168.1.14"},
    {"username": "user6", "ipAddress": "192.168.1.15"},
    {"username": "user7", "ipAddress": "192.168.1.16"},
    {"username": "user8", "ipAddress": "192.168.1.17"},
]

@app.route("/users", methods=["GET"])
def list_users():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 5))

    start = (page - 1) * limit
    end = start + limit

    users = MOCK_USERS[start:end]
    total_pages = (len(MOCK_USERS) + limit - 1) // limit

    return jsonify({"users": users, "totalPages": total_pages})

@app.route("/users/<username>/download", methods=["GET"])
def download_config(username):
    config_path = os.path.join(OPENVPN_CONFIG_DIR, f"{username}.ovpn")
    if not os.path.exists(config_path):
        return jsonify({"error": "Configuration file not found"}), 404

    return send_file(config_path, as_attachment=True)

@app.route("/users/<username>", methods=["DELETE"])
def delete_config(username):
    config_path = os.path.join(OPENVPN_CONFIG_DIR, f"{username}.ovpn")
    if os.path.exists(config_path):
        os.remove(config_path)
        return jsonify({"message": "Configuration deleted successfully"}), 200
    return jsonify({"error": "Configuration file not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)