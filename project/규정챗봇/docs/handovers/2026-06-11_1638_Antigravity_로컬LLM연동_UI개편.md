# [Antigravity] 로컬 LLM 고도화 및 데스크톱 앱 전면 UI 개편

**1. 작업 내용 (Content)**
- `backend/llm/providers.py`에 오프라인 최적화 모델인 `unsloth/gemma-4-E2B-it-qat-GGUF` (Q4_0) 모델 연동. 하드코딩된 파일명 대신 `models/` 디렉토리 내 `.gguf` 파일을 자동 감지하도록 로직 수정.
- `llama.cpp` + Django `runserver` `--noreload` 옵션을 사용하여 Mac Metal 가속 환경에서의 모델 로드 안정성 및 메모리 충돌(크래시) 문제 해결.
- `desktop/electron-demo/renderer/index.html` 및 `styles.css`를 수정하여 데스크톱 앱 실행 시 "공공기관 스타일" 전면 로그인 스크린이 등장하도록 UI/UX 전면 개편. 상단의 지저분한 로그인 상태 뱃지 완전 제거.
- 하드코딩된 부서/캐릭터 목록을 걷어내고, Django 백엔드(`/api/orgs/tree/`)에서 동적으로 데이터를 받아와 렌더링하도록 `renderer.js` 통합 완료. [🔄 새로고침] 기능 추가.
- `chat/services.py`에서 답변의 환각(Hallucination) 방지를 위해 너무 엄격했던 Citation(답변 근거) 문자열 일치 검증을 유연한 부분 일치 방식으로 완화. 추가로 프롬프트에 '답변 첫 문장에 규정명과 조항을 자연스럽게 명시하라'는 강력한 지시 추가.

**2. 완성도 (Completion)**
- 오프라인 단독 구동을 위한 백엔드 인프라(Django + Local LLM) 및 프론트엔드 연동(Electron + 동적 조직도/대화) 100% 구현 및 사용자 검증 완료.

**3. 발생한 에러 및 미해결 문제 (Errors & Issues)**
- 현재 진행을 가로막는 에러는 없음. (이전에 발생했던 llama.cpp 메모리 크래시 이슈는 Django 서버의 자동 재기동 옵션을 끄는 `--noreload`로 해결함)

**4. 원래 계획 대비 변경된 사항 (Changes & Workarounds)**
- 백엔드에 매번 바뀌는 모델명을 하드코딩하지 않고, `models` 폴더 내부의 `.gguf` 파일을 자동으로 스캔하여 가장 첫 번째 파일을 물고 올라가도록 로직을 유연하게 개선함. (현재 `gemma-4-E2B_q4_0-it.gguf` 모델이 단독으로 위치해 있음)

**5. 다음 작업자 추가 수행 사항 (Next Steps)**
- 다음 작업자인 **Codex**는 지금까지 구축된 백엔드(Django API + sqlite DB), 로컬 LLM 파일(`models/*.gguf`), 프론트엔드(Electron)를 모두 아울러서 **사용자 PC에 한 번에 배포할 수 있는 독립형 오프라인 데스크톱 앱 인스톨러(.dmg / .exe 등)** 제작을 시작해 주세요.
- `PyInstaller`를 통한 파이썬 내장 환경 구축 및 `electron-builder` 설정 등 오프라인 배포본 빌드 파이프라인(Packaging Pipeline) 설계가 핵심 목표입니다.
