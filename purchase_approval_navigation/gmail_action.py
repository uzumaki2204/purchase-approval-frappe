"""Gmail ConfirmAction bridge for the existing Purchase Approval Server Script."""

import hashlib
import ipaddress
import json
import secrets
from pathlib import Path
from urllib.parse import urlencode, urlsplit, urlunsplit

import frappe
from frappe.utils import add_to_date, get_datetime, now_datetime


CALLBACK_PATH = "/api/method/purchase_approval_navigation.gmail_action.confirm"
TOKEN_DOCTYPE = "PA Gmail Approval Token"
GMAIL_AUTHORIZED_PARTY = "gmail@system.gserviceaccount.com"
GMAIL_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/1.0 (KHTML, like Gecko; Gmail Actions)"
_catalog = json.loads(Path(__file__).with_name("ui-translations.json").read_text(encoding="utf-8"))["messages"]


def _message(key):
    return frappe.db.get_value("PA Translation", key, "text") or _catalog.get(key, key)


def _configuration():
    if frappe.conf.get("pa_gmail_actions_enabled") not in (True, 1):
        return None
    url = str(frappe.conf.get("pa_gmail_callback_url") or "").strip()
    sender = str(frappe.conf.get("pa_gmail_registered_sender") or "").strip().lower()
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
    if sender.count("@") != 1 or not sender.split("@", 1)[1]:
        return None
    return {"url": url, "sender": sender, "audience": "https://" + sender.split("@", 1)[1]}


def _sender_email():
    account = frappe.db.get_single_value("PA Settings", "outgoing_email_account")
    if account:
        return str(frappe.db.get_value("Email Account", account, "email_id") or "").lower()
    defaults = frappe.get_all("Email Account", filters={"enable_outgoing": 1, "default_outgoing": 1}, fields=["email_id"], limit_page_length=2)
    return str(defaults[0].email_id or "").lower() if len(defaults) == 1 else ""


@frappe.whitelist(allow_guest=True, methods=["POST"])
def issue_action(outbox_name):
    """Only the notification Server Script may obtain a raw one-time token."""
    if not frappe.flags.get("in_safe_exec"):
        frappe.throw(_message("gmail.unauthorized"), frappe.PermissionError)
    config = _configuration()
    if not config or _sender_email() != config["sender"]:
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

    # A retry can create a new mail. Revoke the token from every older attempt.
    for row in frappe.get_all(TOKEN_DOCTYPE, filters={"outbox": outbox.name, "consumed_at": ["is", "not set"]}, fields=["name"]):
        frappe.db.set_value(TOKEN_DOCTYPE, row.name, "consumed_at", frappe.utils.now())
    raw = secrets.token_urlsafe(32)
    digest = hashlib.sha256(raw.encode("ascii")).hexdigest()
    frappe.get_doc({
        "doctype": TOKEN_DOCTYPE,
        "token_hash": digest,
        "outbox": outbox.name,
        "request": request.name,
        "instance": instance.name,
        "step_order": outbox.step_order,
        "recipient": outbox.recipient,
        "expected_revision": request.revision,
        "expected_modified": str(request.modified),
        "expires_at": add_to_date(now_datetime(), days=7, as_string=True),
    }).insert(ignore_permissions=True)
    parts = urlsplit(config["url"])
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode({"token": raw}), ""))


@frappe.whitelist(allow_guest=True, methods=["POST"])
def verified_actor():
    """Expose the callback's checked actor to the nested Server Script only."""
    if frappe.request.path != CALLBACK_PATH or not frappe.flags.get("in_safe_exec"):
        frappe.throw(_message("gmail.unauthorized"), frappe.PermissionError)
    user = frappe.flags.get("pa_gmail_approval_actor")
    if not user:
        frappe.throw(_message("gmail.unauthorized"), frappe.PermissionError)
    return user


def _verify_google(config):
    header = frappe.get_request_header("X-PA-Gmail-Authorization", "")
    if not header.startswith("Bearer ") or frappe.get_request_header("User-Agent", "") != GMAIL_USER_AGENT:
        return False
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import id_token

        claims = id_token.verify_oauth2_token(header[7:], Request(), config["audience"])
        return claims.get("azp") == GMAIL_AUTHORIZED_PARTY
    except Exception:
        return False


def _reject(key, status=400):
    frappe.local.response.http_status_code = status
    return {"status": "rejected", "message": _message(key)}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def confirm(token=None, confirmed=None):
    """Accept Google's POST, then run the same locked approval command as Desk."""
    config = _configuration()
    if not config:
        return _reject("gmail.unavailable", 503)
    if not _verify_google(config):
        return _reject("gmail.unauthorized", 401)
    if confirmed != "Approved" or not isinstance(token, str) or len(token) > 128 or not token:
        return _reject("gmail.invalid", 400)
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    rows = frappe.db.sql("select name from `tabPA Gmail Approval Token` where token_hash=%s for update", (digest,), as_dict=True)
    if not rows:
        return _reject("gmail.invalid", 401)
    action = frappe.get_doc(TOKEN_DOCTYPE, rows[0].name)
    if action.consumed_at:
        return {"status": "already_processed", "message": _message("gmail.already_processed")}
    if get_datetime(action.expires_at) <= now_datetime():
        return _reject("gmail.expired", 400)
    request = frappe.get_doc("PA Purchase Request", action.request)
    if (request.status != "Pending Approval" or request.current_instance != action.instance or
            int(request.revision or 0) != int(action.expected_revision or 0) or
            str(request.modified) != str(action.expected_modified)):
        return _reject("gmail.stale", 400)

    from frappe.utils.safe_exec import run_script

    frappe.flags.pa_gmail_approval_actor = action.recipient
    try:
        run_script("pa_approval_action", payload=json.dumps({
            "name": action.request,
            "expected_modified": action.expected_modified,
            "expected_revision": action.expected_revision,
            "action": "Approve",
        }))
    finally:
        frappe.flags.pop("pa_gmail_approval_actor", None)

    action.consumed_at = frappe.utils.now()
    action.save(ignore_permissions=True)
    frappe.response.pop("message", None)
    return {"status": "approved", "message": _message("gmail.approved")}
