# 규정챗봇 RegBot

사내 규정, 지침, 매뉴얼 문서를 근거로 답변하는 데스크탑 AI 챗봇입니다. Electron 데스크탑앱 안에 Django 백엔드 실행파일과 배포용 SQLite DB를 함께 넣어, 사용자는 앱을 더블클릭해 실행할 수 있습니다.

## 현재 배포 상태

- macOS Apple Silicon용 DMG 생성 완료
  - `desktop/electron-demo/dist/RegBot-0.1.0-arm64.dmg`
- 앱 실행 방식
  - `RegBot.app` 실행
  - 앱이 임의의 로컬 포트에서 번들 Django 서버 자동 실행
  - 최초 실행 시 번들 seed DB를 사용자 데이터 폴더로 복사
- Windows용 설치파일
  - Electron 빌드 설정은 준비되어 있음
  - 단, Windows용 Python 백엔드 실행파일(`backend.exe`)은 Windows 환경에서 별도 PyInstaller 빌드가 필요함

## 포함/제외 기준

패키지에 포함:

- Electron 데스크탑 UI
- PyInstaller로 만든 Django 백엔드 실행파일
- 배포용 SQLite DB
  - 조직도, AI 캐릭터, 규정 문서 메타데이터, 조항 인덱스, 파싱 본문 포함

패키지와 GitHub에서 제외:

- `.env`, API 키, 암호화된 SecretCredential
- 감사 로그, 세션
- 원본문서 HWP/HWPX/PDF
- 로컬 GGUF 모델 파일
- 개발용 DB 원본, 캐시, 빌드 중간 산출물

배포용 DB는 원본 `backend/db.sqlite3`를 복사한 뒤 `secretstore_secretcredential`, `audit_queryauditlog`, `django_session`을 비워 만든 것입니다.

## 프로젝트 구조

```text
규정챗봇/
├── backend/                       # Django 백엔드
│   ├── config/                    # 설정/URL
│   ├── chat/                      # 질의 처리, 근거 검증, 응답 파싱
│   ├── documents/                 # 문서 업로드/파싱
│   ├── indexing/                  # 조항 인덱스
│   ├── llm/                       # LLM 공급자 어댑터
│   ├── orgs/                      # 조직도/담당자
│   ├── secretstore/               # API 키 암호화 저장
│   ├── backend.spec               # PyInstaller 설정
│   └── run_server.py              # 패키징 백엔드 진입점
├── desktop/electron-demo/
│   ├── main.js                    # Electron 메인 프로세스
│   ├── runtime-data.js            # 번들 seed DB 초기 복사
│   ├── renderer/                  # 데스크탑 UI
│   └── package.json               # Electron Builder 설정
├── docs/                          # 설계/인수인계 문서
├── requirements.txt
└── pytest.ini
```

## macOS 사용 방법

1. `desktop/electron-demo/dist/RegBot-0.1.0-arm64.dmg`를 엽니다.
2. `RegBot.app`을 실행합니다.
3. 최초 실행 시 macOS 보안 경고가 나오면 `시스템 설정 > 개인정보 보호 및 보안`에서 실행을 허용합니다.
4. 앱이 백그라운드에서 Django 서버를 자동 실행합니다.

개발자 인증서로 서명/공증한 앱이 아니므로 공개 배포 시 Gatekeeper 경고가 발생할 수 있습니다. 현재 산출물은 내부 테스트용 ad-hoc 서명 앱입니다.

## macOS 패키징 절차

```bash
cd project/규정챗봇

# 1. 테스트
.venv/bin/python -m pytest

# 2. 배포용 seed DB 생성
rm -rf desktop/electron-demo/build-resources/seed
mkdir -p desktop/electron-demo/build-resources/seed
cp backend/db.sqlite3 desktop/electron-demo/build-resources/seed/db.sqlite3
.venv/bin/python - <<'PY'
import sqlite3
conn = sqlite3.connect("desktop/electron-demo/build-resources/seed/db.sqlite3")
cur = conn.cursor()
for table in ["secretstore_secretcredential", "audit_queryauditlog", "django_session"]:
    cur.execute(f"DELETE FROM {table}")
conn.commit()
conn.execute("VACUUM")
conn.close()
PY

# 3. 백엔드 실행파일 생성
rm -rf backend/build backend/dist
cd backend
../.venv/bin/python -m PyInstaller backend.spec
cd ..

# 4. Electron macOS 패키지 생성
cd desktop/electron-demo
npm run dist:mac

# 5. 내부 테스트용 ad-hoc 서명
codesign --force --deep --sign - dist/mac-arm64/RegBot.app
codesign --verify --deep --strict --verbose=2 dist/mac-arm64/RegBot.app
```

## Windows 패키징 절차

Windows 설치파일은 Windows PC 또는 Windows CI에서 생성해야 합니다.

```powershell
cd project\규정챗봇

# Python 가상환경 준비 후 의존성 설치
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt

# seed DB 생성 후 비밀/로그 테이블 정리
mkdir desktop\electron-demo\build-resources\seed
copy backend\db.sqlite3 desktop\electron-demo\build-resources\seed\db.sqlite3
.\.venv\Scripts\python -c "import sqlite3; conn=sqlite3.connect('desktop/electron-demo/build-resources/seed/db.sqlite3'); cur=conn.cursor(); [cur.execute(f'DELETE FROM {table}') for table in ['secretstore_secretcredential','audit_queryauditlog','django_session']]; conn.commit(); conn.execute('VACUUM'); conn.close()"

# Windows 백엔드 실행파일 생성
cd backend
..\.venv\Scripts\python -m PyInstaller backend.spec
cd ..

# Windows Electron 설치파일 생성
cd desktop\electron-demo
npm install
npm run dist:win
```

Windows 패키지는 `backend/dist/backend/backend.exe`가 포함되어야 더블클릭 실행 시 서버가 자동 실행됩니다.

## 개발 실행

패키징 전 개발 모드는 백엔드와 Electron을 따로 실행합니다.

```bash
cd project/규정챗봇
.venv/bin/python backend/manage.py runserver 127.0.0.1:8000 --noreload
```

다른 터미널:

```bash
cd project/규정챗봇/desktop/electron-demo
npm start
```

## API

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/auth/csrf/` | CSRF 토큰 발급 |
| POST | `/api/auth/login/` | 로그인 |
| GET | `/api/auth/status/` | 로그인 상태 확인 |
| GET | `/api/orgs/tree/` | 조직도와 캐릭터 목록 |
| POST | `/api/chat/ask/` | 규정 질문 |

## LLM 키 등록

배포용 DB에는 LLM 키가 포함되지 않습니다. 앱 실행 후 관리자 화면에서 키를 등록하거나 개발 환경에서 아래 명령을 사용합니다.

```bash
export GEMINI_API_KEY="실제_키"
python backend/manage.py setup_llm_key --model gemini-3.5-flash
```

API 키를 명령행 인자로 넘기지 마세요.

## 검증

이번 macOS 패키징에서 확인한 항목:

- `node --check` 통과
- `pytest` 8개 통과
- PyInstaller 백엔드 `check` 통과
- `RegBot.app` ad-hoc 코드서명 검증 통과
- 패키징 앱 실행 시 번들 백엔드 자동 실행 확인
- `/api/auth/status/`, `/api/auth/csrf/`, `/api/orgs/tree/` 200 응답 확인

## GitHub 업로드 주의

GitHub에 올리지 않는 항목:

- `backend/db.sqlite3`
- `desktop/electron-demo/build-resources/seed/db.sqlite3`
- `desktop/electron-demo/dist/`
- `backend/dist/`, `backend/build/`
- `backend/models/*.gguf`
- `data/raw/*`
- `media/`
- `.env`, `.env.*`

릴리스 파일은 Git 저장소에 커밋하지 말고 GitHub Release 자산으로 업로드합니다.
