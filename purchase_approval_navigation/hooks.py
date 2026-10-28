# Backward-compatibility shim for Frappe hooks.
# Bench/Pilot nhận diện app qua app_name trong hooks.py.
# Giữ nguyên app_name = "purchase_approval_navigation" để Pilot
# không cần thay đổi cấu hình bench, đồng thời tất cả logic thực tế
# vẫn chạy từ purchase_approval.
from purchase_approval.hooks import *  # noqa: F401, F403

app_name = "purchase_approval_navigation"
