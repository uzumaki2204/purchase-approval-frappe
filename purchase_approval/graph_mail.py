"""Microsoft Graph delivery for Purchase Approval notifications only."""

import base64
import html
import json
import mimetypes
import re
import importlib.util
from pathlib import Path
from urllib.parse import quote

import frappe
from frappe.utils.password import get_decrypted_password, set_encrypted_password


_catalog = json.loads(Path(__file__).with_name("ui-translations.json").read_text(encoding="utf-8"))["messages"]
MAX_INLINE_ATTACHMENT = 3_000_000
SETTINGS_DOCTYPE = "PA Settings"
SECRET_FIELD = "graph_private_key"


def _message(key):
    return frappe.db.get_value("PA Translation", key, "text") or _catalog.get(key, key)


def _configuration():
    graph_enabled = frappe.db.get_single_value(SETTINGS_DOCTYPE, "graph_mail_enabled") in (True, 1, "1")
    private_key = get_decrypted_password(SETTINGS_DOCTYPE, SETTINGS_DOCTYPE, SECRET_FIELD, raise_exception=False)
    config = {
        "enabled": graph_enabled or frappe.conf.get("pa_graph_mail_enabled") in (True, 1),
        "tenant": str(frappe.db.get_single_value(SETTINGS_DOCTYPE, "graph_tenant_id") or frappe.conf.get("pa_graph_tenant_id") or "").strip().lower(),
        "client": str(frappe.db.get_single_value(SETTINGS_DOCTYPE, "graph_client_id") or frappe.conf.get("pa_graph_client_id") or "").strip().lower(),
        "sender": str(frappe.db.get_single_value(SETTINGS_DOCTYPE, "graph_sender_mailbox") or frappe.conf.get("pa_graph_sender_mailbox") or "").strip().lower(),
        "certificate": str(frappe.conf.get("pa_graph_certificate_path") or "").strip(),
        "private_key": private_key,
        "thumbprint": str(frappe.db.get_single_value(SETTINGS_DOCTYPE, "graph_certificate_thumbprint") or frappe.conf.get("pa_graph_certificate_thumbprint") or "").strip().upper(),
    }
    guid = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    config["configured"] = bool(re.fullmatch(guid, config["tenant"]) and
                                re.fullmatch(guid, config["client"]) and
                                config["sender"].count("@") == 1 and
                                re.fullmatch(r"[A-F0-9]{40}|[A-F0-9]{64}", config["thumbprint"]) and
                                (bool(config["private_key"]) or
                                 bool(config["certificate"] and Path(config["certificate"]).is_file())))
    return config


@frappe.whitelist(methods=["POST"])
def status():
    if not frappe.flags.get("in_safe_exec"):
        frappe.throw(_message("error.permission"), frappe.PermissionError)
    config = _configuration()
    from purchase_approval import outlook_action
    smtp_account = frappe.db.get_single_value(SETTINGS_DOCTYPE, "outgoing_email_account")
    if not smtp_account:
        smtp_account = frappe.db.get_value("Email Account", {"enable_outgoing": 1, "default_outgoing": 1}, "name")
    smtp_sender = frappe.db.get_value("Email Account", smtp_account, "email_id") if smtp_account else ""

    return {
        "provider": "graph" if config["enabled"] else "smtp",
        "tenant_id": config["tenant"],
        "client_id": config["client"],
        "sender_email": config["sender"],
        "smtp_sender_email": smtp_sender or "",
        "thumbprint": config["thumbprint"],
        "has_certificate": bool(config["private_key"] or config["certificate"] and Path(config["certificate"]).is_file()),
        "dependency_ready": importlib.util.find_spec("msal") is not None,
        "configured": config["configured"],
        "enabled": config["enabled"],
        "action_enabled": bool(outlook_action._configuration()),
    }


@frappe.whitelist(methods=["POST"])
def save_settings(data):
    if not frappe.flags.get("in_safe_exec") or frappe.session.user != "Administrator" and "PA Super Admin" not in frappe.get_roles(frappe.session.user):
        frappe.throw(_message("error.permission"), frappe.PermissionError)
    if isinstance(data, str):
        data = json.loads(data)
    if not isinstance(data, dict):
        frappe.throw(_message("error.required"))
    tenant = str(data.get("tenant_id") or "").strip().lower()
    client = str(data.get("client_id") or "").strip().lower()
    sender = str(data.get("sender_email") or "").strip().lower()
    thumbprint = str(data.get("thumbprint") or "").strip().replace(":", "").upper()
    private_key = data.get("private_key")
    enabled = data.get("enabled") is True
    guid = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    if not re.fullmatch(guid, tenant) or not re.fullmatch(guid, client):
        frappe.throw(_message("error.graph_ids"))
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", sender):
        frappe.throw(_message("error.mail_email"))
    if not re.fullmatch(r"[A-F0-9]{40}|[A-F0-9]{64}", thumbprint):
        frappe.throw(_message("error.graph_thumbprint"))
    if private_key is not None:
        if not frappe.request.is_secure:
            frappe.throw(_message("error.graph_https"))
        if not isinstance(private_key, str) or len(private_key) > 65536 or "-----BEGIN " not in private_key or "PRIVATE KEY-----" not in private_key:
            frappe.throw(_message("error.graph_private_key"))
        try:
            from cryptography.hazmat.primitives.serialization import load_pem_private_key
            load_pem_private_key(private_key.encode("utf-8"), password=None)
        except Exception:
            frappe.throw(_message("error.graph_private_key"))
    has_key = bool(private_key or get_decrypted_password(SETTINGS_DOCTYPE, SETTINGS_DOCTYPE, SECRET_FIELD, raise_exception=False))
    if enabled and (not has_key or importlib.util.find_spec("msal") is None or not frappe.request.is_secure):
        frappe.throw(_message("error.graph_activation"))
    settings = frappe.get_doc(SETTINGS_DOCTYPE)
    settings.graph_tenant_id = tenant
    settings.graph_client_id = client
    settings.graph_sender_mailbox = sender
    settings.graph_certificate_thumbprint = thumbprint
    settings.graph_mail_enabled = int(enabled)
    frappe.flags.pa_graph_config_write = True
    try:
        settings.save(ignore_permissions=True)
    finally:
        frappe.flags.pop("pa_graph_config_write", None)
    if private_key:
        set_encrypted_password(SETTINGS_DOCTYPE, SETTINGS_DOCTYPE, private_key, fieldname=SECRET_FIELD)
    return status()


def _access_token(config):
    import msal

    credential = {
        "thumbprint": config["thumbprint"],
        "private_key": config["private_key"] or Path(config["certificate"]).read_text(encoding="utf-8"),
    }
    client = msal.ConfidentialClientApplication(
        config["client"],
        authority="https://login.microsoftonline.com/" + config["tenant"],
        client_credential=credential,
    )
    result = client.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if not result.get("access_token"):
        frappe.throw(_message("error.graph_auth"))
    return result["access_token"]


def _attachment(name, content, content_type, inline=False, content_id=None):
    return {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": name,
        "contentType": content_type,
        "contentBytes": base64.b64encode(content).decode("ascii"),
        "isInline": inline,
        **({"contentId": content_id} if content_id else {}),
    }


@frappe.whitelist(methods=["POST"])
def send_approval(recipient, subject, message, pdf_name, pdf_bytes, inline_images=None):
    if not frappe.flags.get("in_safe_exec"):
        frappe.throw(_message("error.permission"), frappe.PermissionError)
    config = _configuration()
    if not config["enabled"] or not config["configured"]:
        frappe.throw(_message("error.graph_configuration"))
    if not isinstance(pdf_bytes, bytes) or len(pdf_bytes) >= MAX_INLINE_ATTACHMENT:
        frappe.throw(_message("error.graph_attachment_large"))
    if not isinstance(recipient, str) or recipient.count("@") != 1:
        frappe.throw(_message("error.mail_email"))
    attachments = [_attachment(pdf_name, pdf_bytes, "application/pdf")]
    for index, picture in enumerate(inline_images or []):
        content = picture.get("filecontent")
        name = str(picture.get("filename") or "")
        if not isinstance(content, bytes) or not name or len(content) >= MAX_INLINE_ATTACHMENT:
            continue
        content_id = "pa-inline-" + str(index) + "@purchase-approval"
        message = message.replace('embed="' + html.escape(name, quote=True) + '"',
                                  'src="cid:' + content_id + '"')
        attachments.append(_attachment(name, content, mimetypes.guess_type(name)[0] or "application/octet-stream", True, content_id))
    import requests

    payload = {"message": {
        "subject": subject,
        "body": {"contentType": "HTML", "content": message},
        "toRecipients": [{"emailAddress": {"address": recipient}}],
        "attachments": attachments,
    }, "saveToSentItems": True}
    response = requests.post(
        "https://graph.microsoft.com/v1.0/users/" + quote(config["sender"], safe="") + "/sendMail",
        headers={"Authorization": "Bearer " + _access_token(config), "Content-Type": "application/json"},
        json=payload, timeout=30,
    )
    if response.status_code != 202:
        frappe.throw(_message("error.graph_send"))
    return {"accepted": True}
