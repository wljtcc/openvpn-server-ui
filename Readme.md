## OpenVPN Server Manager

Frontend de administração para um servidor OpenVPN que permita listar usuários.
Foi usado o framework Flask (Python) para o backend e HTML/CSS/JavaScript para o frontend. 

Frontend básico que inclui:

    Backend Flask: Um serviço simples para listar os usuários conectados ao OpenVPN.
    Frontend: Uma interface web para exibir os usuários.
    O OpenVPN mantém informações sobre conexões ativas no arquivo openvpn-status.log. Este exemplo utiliza esse arquivo para listar os usuários conectados.

### Rodando a aplicação

#### 1. Certifique-se de que o Python e o Flask estão instalados:

```shell
  pip install flask
```

#### 2. Verifique o caminho do arquivo openvpn-status.log 

Geralmente em /run/openvpn-server/status-server.log
Altere o valor da variável OPENVPN_STATUS_FILE no código, caso necessário.
Inicie o servidor Flask:

```shell
  python app.py
```

#### 3. Acesse o frontend no navegador

```
http://127.0.0.1:5000/
```