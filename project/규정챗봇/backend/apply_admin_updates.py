import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# 1. 앱 한글화 (apps.py)
APP_NAMES = {
    "accounts": "계정 관리",
    "audit": "감사 로그",
    "characters": "AI 캐릭터 관리",
    "chat": "챗봇 서비스",
    "documents": "규정 문서",
    "indexing": "조항 인덱싱",
    "llm": "LLM 관리",
    "orgs": "조직도 관리",
    "secretstore": "보안 키 관리",
}

for app, kor_name in APP_NAMES.items():
    apps_path = BASE_DIR / app / "apps.py"
    if apps_path.exists():
        with apps_path.open("r", encoding="utf-8") as f:
            content = f.read()
        if "verbose_name =" not in content:
            content = content.replace(f"name = '{app}'", f"name = '{app}'\n    verbose_name = '{kor_name}'")
            with apps_path.open("w", encoding="utf-8") as f:
                f.write(content)

# 2. Unfold 테마 적용 및 Inline 적용 (admin.py)
for root, dirs, files in os.walk(BASE_DIR):
    if "admin.py" in files and "migrations" not in root and "venv" not in root:
        admin_path = Path(root) / "admin.py"
        with admin_path.open("r", encoding="utf-8") as f:
            content = f.read()

        # unfold import 추가 및 admin.ModelAdmin 교체
        if "from unfold.admin import ModelAdmin" not in content:
            content = content.replace("from django.contrib import admin", "from django.contrib import admin\nfrom unfold.admin import ModelAdmin")

        content = content.replace("admin.ModelAdmin", "ModelAdmin")

        with admin_path.open("w", encoding="utf-8") as f:
            f.write(content)

# 3. 모델 한글화 및 옵션 추가 (models.py)
# 정규식을 써서 각 모델의 Meta 안에 verbose_name을 넣을 수도 있지만, 간단히 직접 교체하기엔 파일별로 너무 달라서
# 여기서는 필요한 파일만 특정해서 수정합니다.
