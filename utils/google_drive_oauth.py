import json
from io import BytesIO
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st
from requests_oauthlib import OAuth2Session
import requests


GOOGLE_AUTH_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_DRIVE_SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/drive.file",
]


def _secret_value(key, default=None):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def obtener_google_oauth_config():
    bloque = _secret_value("google_oauth", None)
    if bloque:
        bloque = dict(bloque)
        return {
            "client_id": bloque.get("client_id"),
            "client_secret": bloque.get("client_secret"),
            "redirect_uri": bloque.get("redirect_uri"),
        }

    return {
        "client_id": _secret_value("google_oauth_client_id"),
        "client_secret": _secret_value("google_oauth_client_secret"),
        "redirect_uri": _secret_value("google_oauth_redirect_uri"),
    }


def google_oauth_configurado():
    config = obtener_google_oauth_config()
    return bool(config.get("client_id") and config.get("client_secret") and config.get("redirect_uri"))


def _oauth_session(state=None, token=None):
    config = obtener_google_oauth_config()
    return OAuth2Session(
        client_id=config["client_id"],
        redirect_uri=config["redirect_uri"],
        scope=GOOGLE_DRIVE_SCOPES,
        state=state,
        token=token,
    )


def obtener_google_auth_url():
    if not google_oauth_configurado():
        return None

    oauth = _oauth_session()
    auth_url, state = oauth.authorization_url(
        GOOGLE_AUTH_BASE_URL,
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )
    st.session_state["google_drive_oauth_state"] = state
    return auth_url


def _fetch_userinfo(access_token):
    try:
        req = Request(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        with urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


def _query_param_value(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _intercambiar_code_por_token(code):
    config = obtener_google_oauth_config()
    payload = {
        "code": code,
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "redirect_uri": config["redirect_uri"],
        "grant_type": "authorization_code",
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=payload, timeout=20)
    data = response.json()
    if response.status_code >= 400 or "access_token" not in data:
        mensaje = data.get("error_description") or data.get("error") or f"HTTP {response.status_code}"
        raise ValueError(mensaje)
    return data


def procesar_google_oauth_callback():
    if not google_oauth_configurado():
        return None

    query_params = st.query_params
    code = _query_param_value(query_params.get("code"))
    state = _query_param_value(query_params.get("state"))
    error = _query_param_value(query_params.get("error"))

    if error:
        st.session_state["google_drive_oauth_error"] = error
        try:
            st.query_params.clear()
        except Exception:
            pass
        return False

    if not code:
        return None

    state_esperado = st.session_state.get("google_drive_oauth_state")
    if state_esperado and state != state_esperado:
        st.session_state["google_drive_oauth_error"] = "Estado OAuth inválido."
        try:
            st.query_params.clear()
        except Exception:
            pass
        return False

    try:
        token = _intercambiar_code_por_token(code)
    except Exception as e:
        st.session_state["google_drive_oauth_error"] = f"No se pudo completar la autenticación con Google: {e}"
        try:
            st.query_params.clear()
        except Exception:
            pass
        return False

    st.session_state["google_drive_oauth_token"] = token
    st.session_state["google_drive_oauth_userinfo"] = _fetch_userinfo(token.get("access_token"))
    st.session_state.pop("google_drive_oauth_error", None)

    try:
        st.query_params.clear()
    except Exception:
        pass
    return True


def google_drive_conectado():
    return bool(st.session_state.get("google_drive_oauth_token"))


def obtener_google_drive_usuario():
    return st.session_state.get("google_drive_oauth_userinfo")


def desconectar_google_drive():
    for key in [
        "google_drive_oauth_token",
        "google_drive_oauth_userinfo",
        "google_drive_oauth_state",
        "google_drive_oauth_error",
    ]:
        st.session_state.pop(key, None)


def subir_docx_con_oauth(docx_bytes, nombre_archivo, folder_id=None):
    token = st.session_state.get("google_drive_oauth_token")
    if not token:
        return {
            "ok": False,
            "configured": google_oauth_configurado(),
            "message": "Google Drive no está conectado con OAuth.",
        }

    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseUpload
    except Exception as e:
        return {
            "ok": False,
            "configured": True,
            "message": f"No se pudieron importar las librerías OAuth de Google: {e}",
        }

    config = obtener_google_oauth_config()
    creds = Credentials(
        token=token.get("access_token"),
        refresh_token=token.get("refresh_token"),
        token_uri=GOOGLE_TOKEN_URL,
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        scopes=GOOGLE_DRIVE_SCOPES,
    )

    try:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            st.session_state["google_drive_oauth_token"] = {
                **token,
                "access_token": creds.token,
            }

        service = build("drive", "v3", credentials=creds, cache_discovery=False)
        metadata = {"name": nombre_archivo}
        if folder_id:
            metadata["parents"] = [folder_id]

        media = MediaIoBaseUpload(
            BytesIO(docx_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            resumable=False,
        )

        archivo = service.files().create(
            body=metadata,
            media_body=media,
            fields="id,name,webViewLink",
            supportsAllDrives=True,
        ).execute()

        return {
            "ok": True,
            "configured": True,
            "file_id": archivo.get("id"),
            "name": archivo.get("name"),
            "webViewLink": archivo.get("webViewLink"),
        }
    except Exception as e:
        return {
            "ok": False,
            "configured": True,
            "message": f"No se pudo subir el archivo a Google Drive con OAuth: {e}",
        }
