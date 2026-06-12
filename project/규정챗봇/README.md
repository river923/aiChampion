# 기존 메신저 기반 AI직원을 통한 내부업무 안내서비스 

기존 메신저와 조직도 흐름 안에 AI 직원을 배치해, 내부 규정과 업무 매뉴얼을 근거 기반으로 안내하는 데스크탑 AI 챗봇입니다.

새로운 메신저를 하나 더 도입하는 대신, 사용자가 이미 익숙한 업무 환경 안에서 복무, 인사, 재무, 총무 등 업무별 AI 담당자에게 질문하고 답변 근거까지 확인할 수 있도록 설계했습니다.

---

## 1. 왜 만들었는가

조직 내부에 AI 기반 규정 안내 챗봇을 도입하려면 비용과 운영 부담이 큽니다.

외부 솔루션 도입 견적은 약 **3억 원에서 17억 원 수준**까지 제시될 수 있고, 단순히 챗봇만 구매하는 것이 아니라 별도의 메신저, 사용자 계정, IP/PW 관리 체계까지 함께 운영해야 하는 경우가 많습니다.

하지만 대부분의 조직에는 이미 업무용 메신저와 조직도가 존재합니다.

RegBot은 이 지점에서 출발했습니다.

> 새 시스템을 하나 더 사는 것이 아니라, 기존 메신저 안에 AI 직원을 배치해 더 세밀한 업무 안내를 제공하자.

---

## 2. 프로젝트 목적

RegBot의 목적은 기존 메신저를 활용해 조직도 상에 AI 직원을 만들고, 각 업무별 고유 규정과 매뉴얼을 상세히 안내하는 것입니다.

핵심 목표는 다음과 같습니다.

- 기존 메신저와 조직도 흐름을 활용한 AI 직원 배치
- 업무별 규정, 지침, 매뉴얼의 세밀한 안내
- 답변 근거 제공을 통한 신뢰성 확보
- 반복적인 규정 문의 대응 비용 절감
- 담당자별 안내 편차를 줄이는 내부 지식 표준화
- 외부 API와 로컬 LLM을 선택할 수 있는 유연한 운영 구조 확보

---

## 3. 서비스 개념

RegBot은 조직도 안에 실제 직원처럼 표시되는 AI 캐릭터를 통해 업무 문의를 처리합니다.

사용자는 복무, 인사, 재무, 총무, ESG, 전략기획 등 각 업무 영역별 AI 담당자를 선택해 자연어로 질문할 수 있습니다.

AI 담당자는 등록된 규정 문서와 매뉴얼을 기반으로 답변하고, 답변에 사용된 조항과 문서 근거를 함께 제공합니다.

```text
사용자
  ↓
기존 메신저 또는 데스크탑 앱
  ↓
조직도 기반 AI 직원 선택
  ↓
규정 문서 / 매뉴얼 / 조항 인덱스 검색
  ↓
외부 LLM API 또는 로컬 LLM
  ↓
근거 기반 답변 제공
```

---

## 4. 주요 기능

### 조직도 기반 AI 직원

- 부서와 팀 구조를 조직도 형태로 표시
- 각 업무 영역에 AI 담당자 배치
- 사용자는 실제 담당자를 찾듯 AI 직원을 선택

### 규정 기반 질의응답

- 내부 규정, 지침, 매뉴얼 문서를 기반으로 답변 생성
- 단순 검색 결과가 아니라 업무 상황에 맞춘 설명 제공
- 복잡한 규정도 사용자 질문 맥락에 맞게 안내

### 답변 근거 제공

- 답변에 사용된 규정 조항과 문서 근거 표시
- 표, 문단, 목록 등 문서 구조를 읽기 쉬운 형태로 표시
- 답변의 검토 가능성과 신뢰성 확보

### 데스크탑 앱 실행

- Electron 기반 데스크탑 앱 제공
- 앱 실행 시 Django 백엔드 서버 자동 기동
- 사용자는 명령어 없이 앱을 더블클릭해 실행 가능

### 로컬 패키징 구조

- Django 백엔드 서버 포함
- SQLite 기반 배포용 DB 포함
- macOS DMG 패키징 지원
- Windows NSIS / Portable 패키징 구조 지원

---

## 5. AI 모델 운영 전략

RegBot은 운영 환경에 따라 사용할 LLM을 선택할 수 있도록 설계했습니다.

인터넷 사용이 가능한 환경에서는 백엔드에서 외부 LLM API를 선택해 사용할 수 있습니다. 현재 구조는 Google Gemini API와 OpenRouter 연동을 고려해 개발되었으며, 운영 정책에 따라 모델 제공자를 전환할 수 있습니다.

반대로 인터넷 연결이 제한되거나 외부 API 사용이 어려운 환경에서는 로컬 LLM을 사용할 수 있도록 설계했습니다. 현재는 **로컬 Gemma 4 12B 모델** 적용을 기준으로 구성해, 인터넷이 없는 상황에서도 최소한의 규정 안내가 가능하도록 했습니다.

이 구조의 핵심은 특정 AI 모델에 종속되지 않는 것입니다.

- 외부 API 기반 고성능 LLM 사용 가능
- 백엔드에서 모델 제공자 선택 가능
- Gemini / OpenRouter 연동 구조
- 로컬 Gemma 4 12B 적용 구조
- 인터넷이 없는 환경에서도 최소 안내 가능
- 조직 보안 정책에 따른 폐쇄망 운영 가능성 확보

---

## 6. 기대 효과

### 비용 절감

고가의 외부 AI 챗봇 솔루션과 별도 메신저 도입 비용을 줄일 수 있습니다.

### 운영 단순화

새로운 계정 체계나 별도 로그인 시스템을 추가하지 않고, 기존 조직도와 메신저 흐름을 활용합니다.

### 업무 응답 품질 향상

사용자가 규정 문서를 직접 찾아보지 않아도 AI 담당자가 업무 맥락에 맞게 안내합니다.

### 지식 표준화

담당자마다 다르게 안내되던 규정 해석을 근거 중심으로 표준화할 수 있습니다.

### 내부 확장성

복무, 인사, 재무, 총무 등 일부 업무에서 시작해 다른 부서와 업무 영역으로 확장할 수 있습니다.

---

## 7. 기술 스택

| 영역 | 기술 |
| --- | --- |
| Desktop | Electron |
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Django, Django REST Framework |
| Database | SQLite |
| LLM API | Google Gemini API, OpenRouter |
| Local LLM | Gemma 4 12B 적용 구조 |
| Packaging | PyInstaller, Electron Builder |
| macOS 배포 | DMG |
| Windows 배포 | NSIS, Portable 구조 |

---

## 8. 시스템 구조

```text
규정챗봇/
├── backend/                       # Django 백엔드
│   ├── chat/                      # 질의 처리, 근거 검증, 응답 파싱
│   ├── documents/                 # 문서 업로드/파싱
│   ├── indexing/                  # 조항 인덱스
│   ├── llm/                       # LLM 공급자 선택/연동
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

---

## 9. 현재 구현 상태

현재 버전에서는 다음 기능이 구현되어 있습니다.

- 조직도 기반 AI 담당자 표시
- AI 캐릭터 선택
- 규정 기반 질문 입력
- 외부 LLM API 선택 구조
- 로컬 Gemma 4 12B 적용 구조
- 답변 생성 및 응답 파싱
- 답변 근거 표시
- HTML 표 형태 근거 렌더링
- macOS 데스크탑 앱 패키징
- 앱 실행 시 백엔드 서버 자동 실행
- 배포용 DB 포함 구조

---

## 10. 보안 및 배포 정책

RegBot은 내부 규정과 업무 데이터를 다루는 서비스이므로, GitHub와 배포 패키지에 포함되는 데이터를 분리합니다.

GitHub에는 다음 항목을 포함하지 않습니다.

- 실제 API Key
- `.env`
- 원본 DB
- 사용자 세션
- 감사 로그
- 원본문서 HWP/HWPX/PDF
- 대용량 LLM 모델 파일
- 로컬 빌드 산출물

패키지에 포함되는 배포용 DB는 원본 DB를 복사한 뒤 다음 테이블을 비워 만든 seed DB입니다.

- `secretstore_secretcredential`
- `audit_queryauditlog`
- `django_session`

API Key와 운영 환경 설정은 `.env` 또는 관리자 화면을 통해 별도로 관리합니다.

---

## 11. 실행 방식

### macOS

macOS에서는 DMG 파일을 실행해 앱을 설치할 수 있습니다.

```text
desktop/electron-demo/dist/RegBot-0.1.0-arm64.dmg
```

앱을 실행하면 내부적으로 Django 백엔드 서버가 자동 실행되고, 사용자는 데스크탑 앱 화면에서 바로 규정챗봇을 사용할 수 있습니다.

현재 산출물은 내부 테스트용 ad-hoc 서명 앱이므로, 최초 실행 시 macOS Gatekeeper 경고가 표시될 수 있습니다.

### Windows

Windows 패키징 구조도 준비되어 있습니다.

단, Windows용 백엔드 실행파일(`backend.exe`)은 Windows 환경에서 PyInstaller로 별도 빌드해야 합니다.

---

## 12. 개발 실행

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

---

## 13. macOS 패키징 절차

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

---

## 14. Windows 패키징 절차

Windows 설치파일은 Windows PC 또는 Windows CI에서 생성해야 합니다.

```powershell
cd project\규정챗봇

py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt

mkdir desktop\electron-demo\build-resources\seed
copy backend\db.sqlite3 desktop\electron-demo\build-resources\seed\db.sqlite3
.\.venv\Scripts\python -c "import sqlite3; conn=sqlite3.connect('desktop/electron-demo/build-resources/seed/db.sqlite3'); cur=conn.cursor(); [cur.execute(f'DELETE FROM {table}') for table in ['secretstore_secretcredential','audit_queryauditlog','django_session']]; conn.commit(); conn.execute('VACUUM'); conn.close()"

cd backend
..\.venv\Scripts\python -m PyInstaller backend.spec
cd ..

cd desktop\electron-demo
npm install
npm run dist:win
```

Windows 패키지는 `backend/dist/backend/backend.exe`가 포함되어야 더블클릭 실행 시 서버가 자동 실행됩니다.

---

## 15. 검증 결과

현재 macOS 패키징 과정에서 확인한 항목은 다음과 같습니다.

- `node --check` 통과
- `pytest` 8개 통과
- PyInstaller 백엔드 `check` 통과
- `RegBot.app` ad-hoc 코드서명 검증 통과
- 패키징 앱 실행 시 번들 백엔드 자동 실행 확인
- `/api/auth/status/`, `/api/auth/csrf/`, `/api/orgs/tree/` 200 응답 확인

---

## 16. 향후 확장 방향

- 실제 메신저 연동
- 사내 인증 시스템 연동
- 부서별 AI 담당자 자동 생성
- 문서 업로드 및 자동 인덱싱
- 답변 품질 평가 기능
- 사용자 질문 로그 기반 규정 개선 리포트
- 관리자 페이지 고도화
- Windows 설치 파일 완성
- 운영 환경 배포 자동화

---

## 17. 결론

RegBot은 고가의 외부 AI 챗봇 솔루션을 바로 도입하기보다, 기존 조직도와 메신저 환경을 활용해 내부 업무 지식을 AI 직원 형태로 제공하는 현실적인 대안입니다.

핵심은 새로운 업무 도구를 하나 더 추가하는 것이 아니라, 사용자가 이미 익숙한 업무 흐름 안에 AI를 자연스럽게 배치하는 것입니다.

이를 통해 비용은 줄이고, 규정 안내의 정확성과 접근성은 높이며, 조직 내부 지식 활용 방식을 단계적으로 개선할 수 있습니다.
