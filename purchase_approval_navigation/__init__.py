# Backward-compatibility shim.
# Pilot/Bench đã đăng ký app này với tên "purchase_approval_navigation".
# Package thực tế hiện là "purchase_approval" (v2.0.0+).
# Module này đảm bảo `import purchase_approval_navigation` vẫn trả về
# __file__ hợp lệ (khác None) để Frappe bundler.py không crash.
from purchase_approval import *  # noqa: F401, F403
from purchase_approval import __version__  # noqa: F401

app_name = "purchase_approval_navigation"

__all__ = [name for name in dir() if not name.startswith("_")]
