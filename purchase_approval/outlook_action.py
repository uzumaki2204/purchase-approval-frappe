"""Outlook Actionable Message bridge for the existing approval command."""

import hashlib
import ipaddress
import json
import re
import secrets
from pathlib import Path
from urllib.parse import urlsplit

import frappe
from frappe.utils import add_to_date, get_datetime, now_datetime


CALLBACK_PATH = "/api/method/purchase_approval.outlook_action.confirm"
TOKEN_DOCTYPE = "PA Outlook Approval Token"
ACTION_CLIENT_ID = "48af08dc-f6d2-435f-b2a7-069abd99c086"
_catalog = json.loads(Path(__file__).with_name("ui-translations.json").read_text(encoding="utf-8"))["messages"]


def _message(key):
    return frappe.db.get_value("PA Translation", key, "text") or _catalog.get(key, key)


def _configuration():
    from purchase_approval import graph_mail
    graph = graph_mail._configuration()
    if frappe.conf.get("pa_outlook_actions_enabled") not in (True, 1) or not graph["enabled"]:
        return None
    url = str(frappe.conf.get("pa_outlook_callback_url") or "").strip()
    sender = str(frappe.conf.get("pa_outlook_registered_sender") or "").strip().lower()
    originator = str(frappe.conf.get("pa_outlook_originator") or "").strip()
    tenant = str(frappe.conf.get("pa_outlook_tenant_id") or "").strip().lower()
    audience = str(frappe.conf.get("pa_outlook_app_id_uri") or "").strip()
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path != CALLBACK_PATH:
        return None
    if not parsed.hostname or parsed.hostname == "localhost" or parsed.hostname.endswith(".local"):
        return None
    try:
        ipaddress.ip_address(parsed.hostname)
        return None
    except ValueError:
        pass
    guid = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    if not re.fullmatch(guid, originator.lower()) or not re.fullmatch(guid, tenant):
        return None
    if sender.count("@") != 1 or not audience.startswith("api://"):
        return None
    if sender != graph["sender"]:
        return None
    return {"url": url, "sender": sender, "originator": originator, "tenant": tenant, "audience": audience}


@frappe.whitelist(methods=["POST"])
def issue_action(outbox_name):
    """Return card data only to the notification Server Script."""
    if not frappe.flags.get("in_safe_exec"):
        frappe.throw(_message("outlook.unauthorized"), frappe.PermissionError)
    config = _configuration()
    if not config:
        return None
    outbox = frappe.get_doc("PA Notification Outbox", outbox_name)
    if outbox.status != "Pending":
        return None
    request = frappe.get_doc("PA Purchase Request", outbox.request)
    instance = frappe.get_doc("PA Approval Instance", outbox.instance)
    if (request.status != "Pending Approval" or request.current_instance != instance.name or
            instance.status != "Pending" or int(request.revision or 0) != int(instance.revision or 0) or
            int(instance.current_sequence or 0) != int(outbox.step_order or 0) or
            not any(row.user == outbox.recipient and row.status == "Pending" and
                    int(row.step_order or 0) == int(outbox.step_order or 0) for row in instance.assignees)):
        return None
    # Revoke prior attempts; only token hashes are retained in the database.
    rows = frappe.get_all(TOKEN_DOCTYPE, filters={"outbox": outbox.name, "consumed_at": ["is", "not set"]},
                          fields=["name"])
    for row in rows:
        frappe.db.set_value(TOKEN_DOCTYPE, row.name, "consumed_at", frappe.utils.now())
    raw = secrets.token_urlsafe(32)
    frappe.get_doc({
        "doctype": TOKEN_DOCTYPE,
        "token_hash": hashlib.sha256(raw.encode("ascii")).hexdigest(),
        "outbox": outbox.name,
        "request": request.name,
        "instance": instance.name,
        "step_order": outbox.step_order,
        "recipient": outbox.recipient,
        "expected_revision": request.revision,
        "expected_modified": str(request.modified),
        "expires_at": add_to_date(now_datetime(), days=7, as_string=True),
    }).insert(ignore_permissions=True)
    return {"url": config["url"], "token": raw, "originator": config["originator"]}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def verified_actor():
    if frappe.request.path != CALLBACK_PATH or not frappe.flags.get("in_safe_exec"):
        frappe.throw(_message("outlook.unauthorized"), frappe.PermissionError)
    user = frappe.flags.get("pa_outlook_approval_actor")
    if not user:
        frappe.throw(_message("outlook.unauthorized"), frappe.PermissionError)
    return user


def _verify_microsoft(config):
    header = frappe.get_request_header("X-PA-Outlook-Authorization", "")
    if not header.startswith("Bearer "):
        return None
    try:
        import jwt

        issuer = "https://login.microsoftonline.com/" + config["tenant"] + "/v2.0"
        jwks = jwt.PyJWKClient("https://login.microsoftonline.com/" + config["tenant"] + "/discovery/v2.0/keys")
        signed = header[7:]
        claims = jwt.decode(signed, jwks.get_signing_key_from_jwt(signed).key,
                            algorithms=["RS256"], audience=config["audience"], issuer=issuer,
                            options={"require": ["exp", "nbf", "iat", "tid", "azp"]})
        if claims.get("tid", "").lower() != config["tenant"] or claims.get("azp", "").lower() != ACTION_CLIENT_ID:
            return None
        return claims
    except Exception:
        return None


def _reject(key, status=400):
    frappe.local.response.http_status_code = status
    message = _message(key)
    frappe.local.response_headers["CARD-ACTION-STATUS"] = _message("outlook.header_error")
    return {"status": "rejected", "message": message}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def confirm(token=None, action=None):
    config = _configuration()
    if not config:
        return _reject("outlook.unavailable", 503)
    claims = _verify_microsoft(config)
    if not claims:
        return _reject("outlook.unauthorized", 401)
    if action != "Approve" or not isinstance(token, str) or not 32 <= len(token) <= 128:
        return _reject("outlook.invalid", 400)
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    rows = frappe.db.sql("select name from `tabPA Outlook Approval Token` where token_hash=%s for update", (digest,), as_dict=True)
    if not rows:
        return _reject("outlook.invalid", 401)
    approval = frappe.get_doc(TOKEN_DOCTYPE, rows[0].name)
    if approval.consumed_at:
        return {"status": "already_processed", "message": _message("outlook.already_processed")}
    if get_datetime(approval.expires_at) <= now_datetime():
        return _reject("outlook.expired", 400)
    approver_email = str(frappe.db.get_value("User", approval.recipient, "email") or approval.recipient).lower()
    identity = str(claims.get("preferred_username") or claims.get("upn") or claims.get("email") or "").lower()
    if identity != approver_email or not identity:
        return _reject("outlook.unauthorized", 403)
    request = frappe.get_doc("PA Purchase Request", approval.request)
    instance = frappe.get_doc("PA Approval Instance", approval.instance)
    if (request.status != "Pending Approval" or request.current_instance != approval.instance or
            int(request.revision or 0) != int(approval.expected_revision or 0) or
            str(request.modified) != str(approval.expected_modified) or instance.status != "Pending" or
            int(instance.current_sequence or 0) != int(approval.step_order or 0)):
        return _reject("outlook.stale", 400)

    from frappe.utils.safe_exec import run_script

    frappe.flags.pa_outlook_approval_actor = approval.recipient
    try:
        run_script("pa_approval_action", payload=json.dumps({
            "name": approval.request,
            "expected_modified": approval.expected_modified,
            "expected_revision": approval.expected_revision,
            "action": "Approve",
        }))
    finally:
        frappe.flags.pop("pa_outlook_approval_actor", None)
    approval.consumed_at = frappe.utils.now()
    approval.save(ignore_permissions=True)
    frappe.response.pop("message", None)
    return {"status": "approved", "message": _message("outlook.approved")}
