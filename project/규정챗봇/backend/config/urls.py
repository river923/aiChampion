from django.contrib import admin
from django.urls import path

from chat.views import ask_question, csrf_token, get_org_tree, login_api, login_status

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/csrf/", csrf_token, name="csrf-token"),
    path("api/auth/login/", login_api, name="login-api"),
    path("api/auth/status/", login_status, name="login-status"),
    path("api/orgs/tree/", get_org_tree, name="get-org-tree"),
    path("api/chat/ask/", ask_question, name="ask-question"),
]
