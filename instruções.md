# Manual de Migração do Remanexo para Mobile (Expo + Flask API)

Você já possui:

* backend funcional em Flask
* banco/modelagem pronta
* regras de negócio funcionando
* autenticação
* ORM com polimorfismo

Agora o objetivo é:

```txt id="1vr79m"
Frontend HTML/Jinja
        ↓
Frontend Expo React Native
```

mantendo:

* Flask
* SQLite
* SQLAlchemy
* toda lógica financeira

---

# ARQUITETURA FINAL

## Backend

```txt id="6bjc94"
Flask API REST
```

Responsável por:

* autenticação
* regras financeiras
* banco
* cálculos
* categorização
* parcelamentos

---

## Frontend

```txt id="nvh8ha"
Expo Router + React Native
```

Responsável por:

* interface
* navegação
* formulários
* armazenamento local do token

---

# ETAPA 1 — ORGANIZAR O BACKEND

# Objetivo

Separar:

* rotas HTML antigas
* rotas API novas

---

# Estrutura recomendada

## Modifique para:

```txt id="c4r5pw"
backend/
│
├── app.py
├── database.py
│
├── routes/
│   ├── web/
│   │    ├── dashboard.py
│   │    └── ...
│   │
│   └── api/
│        ├── auth.py
│        ├── dashboard.py
│        ├── transacoes.py
│        ├── metas.py
│        └── ...
```

---

# O que fazer AGORA

## Crie:

```txt id="1mgccz"
backend/routes/api/
```

---

# ETAPA 2 — CRIAR LOGIN API

# Arquivo

```txt id="h4m9zj"
backend/routes/api/auth.py
```

---

# Código inicial

```python id="nmu3jq"
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from backend.database import UsuarioModel

bp = Blueprint('api_auth', __name__)

@bp.route('/api/login', methods=['POST'])
def login():

    data = request.get_json()

    email = data.get('email')
    senha = data.get('senha')

    usuario = UsuarioModel.query.filter_by(email=email).first()

    if not usuario:
        return jsonify({
            "erro": "Usuário não encontrado"
        }), 401

    if not check_password_hash(usuario.senha_hash, senha):
        return jsonify({
            "erro": "Senha inválida"
        }), 401

    return jsonify({
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email
        }
    })
```

---

# ETAPA 3 — REGISTRAR BLUEPRINT

# Arquivo

```txt id="r3kq1q"
backend/app.py
```

---

# Adicione

```python id="saxdy0"
from backend.routes.api.auth import bp as auth_api_bp

app.register_blueprint(auth_api_bp)
```

---

# ETAPA 4 — TESTAR API

Execute:

```bash id="2fyvwb"
python run.py
```

---

# Teste no navegador

## POST

```txt id="f9jvop"
http://localhost:5000/api/login
```

Use:

* Insomnia
* Postman
* Thunder Client

Body:

```json id="x8f18w"
{
  "email": "demo@remanexo.com",
  "senha": "123456"
}
```

---

# ETAPA 5 — CONECTAR EXPO AO FLASK

# Arquivo

```txt id="7tzw5f"
app/(auth)/login.js
```

---

# Substitua o handleLogin

```jsx id="z19xfi"
async function handleLogin() {

  try {

    const response = await fetch(
      "http://SEU_IP:5000/api/login",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          email,
          senha,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      Alert.alert("Erro", data.erro);
      return;
    }

    console.log(data);

  } catch (err) {
    Alert.alert("Erro", "Falha ao conectar");
  }
}
```

---

# IMPORTANTE

## NÃO use localhost

No celular/emulador:

```txt id="jlwmms"
localhost != seu computador
```

Use seu IP local.

---

# Descobrir IP

Linux:

```bash id="0d9e2m"
ip a
```

Procure:

```txt id="k53m5m"
192.168.x.x
```

---

# Exemplo

```js id="9b7w0j"
http://192.168.0.15:5000/api/login
```

---

# ETAPA 6 — HABILITAR CORS

# Instale

```bash id="o4x5pr"
pip install flask-cors
```

---

# Arquivo

```txt id="4flv7u"
backend/app.py
```

---

# Adicione

```python id="w0xhj1"
from flask_cors import CORS

CORS(app)
```

---

# ETAPA 7 — SALVAR LOGIN

# Instale

```bash id="am0knr"
npx expo install @react-native-async-storage/async-storage
```

---

# Salve usuário/token

## login.js

```jsx id="u2lq2n"
import AsyncStorage from "@react-native-async-storage/async-storage";
```

---

## Depois do login

```jsx id="3v2hry"
await AsyncStorage.setItem(
  "usuario",
  JSON.stringify(data.usuario)
);

router.replace("/(app)/home");
```

---

# ETAPA 8 — CRIAR BOOTSTRAP

# Arquivo

```txt id="yqgby7"
app/index.js
```

---

# Código

```jsx id="w6q0ln"
import { useEffect } from "react";
import { router } from "expo-router";
import AsyncStorage from "@react-native-async-storage/async-storage";

export default function Index() {

  useEffect(() => {

    async function verificar() {

      const usuario = await AsyncStorage.getItem("usuario");

      if (usuario) {
        router.replace("/(app)/home");
      } else {
        router.replace("/(auth)/login");
      }
    }

    verificar();

  }, []);

  return null;
}
```

---

# ETAPA 9 — CRIAR DASHBOARD API

# Arquivo

```txt id="qylvho"
backend/routes/api/dashboard.py
```

---

# Código

```python id="prg51k"
from flask import Blueprint, jsonify

bp = Blueprint('api_dashboard', __name__)

@bp.route('/api/dashboard')
def dashboard():

    return jsonify({
        "saldo": 5000,
        "receitas": 8000,
        "despesas": 3000
    })
```

---

# ETAPA 10 — CONSUMIR DASHBOARD

# Arquivo

```txt id="vqvaxm"
app/(app)/home.js
```

---

# Fluxo

```jsx id="i1d9t5"
useEffect(() => {
  carregarDashboard();
}, []);
```

---

# Buscar dados

```jsx id="t1t9ye"
const response = await fetch(
  "http://IP:5000/api/dashboard"
);

const data = await response.json();
```

---

# ETAPA 11 — MIGRAR FUNCIONALIDADE POR FUNCIONALIDADE

Ordem ideal:

---

## 1. Login

---

## 2. Dashboard

---

## 3. Transações

---

## 4. Metas

---

## 5. Parcelamentos

---

## 6. Nexo/Open Finance

---

## 7. Categorias

---

# REGRA MAIS IMPORTANTE

# O FLASK CONTINUA SENDO O CÉREBRO

O app mobile:

* NÃO calcula saldo
* NÃO processa parcelamentos
* NÃO categoriza
* NÃO implementa regra financeira

Tudo continua no backend.

---

# O QUE VOCÊ VAI EDITAR MAIS

## Backend

```txt id="xhl8xw"
backend/routes/api/*
backend/app.py
```

---

## Frontend

```txt id="86r0x0"
app/*
```

---

# O QUE VOCÊ NÃO DEVE MEXER MUITO

## database.py

Sua modelagem já está excelente.

---

# Resultado final

Você terá:

```txt id="5wt95x"
Expo Mobile App
       ↓
Flask API
       ↓
SQLite
```

com:

* autenticação
* Open Finance
* dashboard
* transações
* metas
* parcelamentos

todos funcionando no mobile.
