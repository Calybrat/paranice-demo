"""
Corre este script UNA VEZ para generar config.yaml.
  python3 auth_setup.py

Edita USUARIOS para agregar contactos de Paranice.
"""
import os, yaml
import streamlit_authenticator as stauth

# ── USUARIOS ──────────────────────────────────────────────────────────────────
USUARIOS = [
    {"username": "nicolas",       "name": "Nicolás Gort", "email": "nicolasgort@gmail.com", "password": "Admin2026"},
    {"username": "paranice_demo", "name": "Paranice Demo","email": "",                      "password": "Paranice2026"},
    # Agrega más aquí:
    # {"username": "fundador", "name": "Fundador Paranice", "email": "contacto@paranice.co", "password": "MiClave123"},
]
# ─────────────────────────────────────────────────────────────────────────────

credentials = {"usernames": {}}
for u in USUARIOS:
    credentials["usernames"][u["username"]] = {
        "name":     u["name"],
        "email":    u["email"],
        "password": stauth.Hasher.hash(u["password"]),
    }

config = {
    "credentials": credentials,
    "cookie": {
        "name":        "calybrat_paranice",
        "key":         os.urandom(32).hex(),
        "expiry_days": 7,
    },
}

with open("config.yaml", "w", encoding="utf-8") as f:
    yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

print("\n✅  config.yaml generado.\n")
print("Usuarios:")
for u in USUARIOS:
    print(f"  {u['username']:20s} → {u['password']}")
print()
