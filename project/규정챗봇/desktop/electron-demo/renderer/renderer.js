const messages = document.querySelector("#messages");
const citations = document.querySelector("#citations");
const form = document.querySelector("#question-form");
const loginForm = document.querySelector("#login-form");
const input = document.querySelector("#question-input");
const usernameInput = document.querySelector("#username-input");
const passwordInput = document.querySelector("#password-input");
const loginErrorMsg = document.querySelector("#login-error-msg");

const refreshOrgBtn = document.querySelector("#refresh-org-btn");
const orgTreeContainer = document.querySelector("#org-tree-container");
const characterListContainer = document.querySelector("#character-list-container");
const chatHeaderTitle = document.querySelector(".chat-header h1");
const chatHeaderDesc = document.querySelector(".chat-header p");

let characterId = null;
let backendBaseUrl = "http://127.0.0.1:8000";
let csrfToken = "";

initialize();

async function initialize() {
  if (window.regbot) {
    backendBaseUrl = await window.regbot.backendBaseUrl();
  }

  await refreshLoginState();
  await loadOrgTree();

  refreshOrgBtn.addEventListener("click", async () => {
    await loadOrgTree();
  });

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const response = await loginUser(usernameInput.value.trim(), passwordInput.value);
    if (response.authenticated) {
      csrfToken = response.csrfToken || csrfToken;
      document.body.className = "state-logged-in";
      loginErrorMsg.textContent = "";
      return;
    }
    loginErrorMsg.textContent = response.error || "로그인에 실패했습니다.";
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const question = input.value.trim();
    if (!question) {
      return;
    }
    appendMessage("user", question);
    input.value = "";

    if (!characterId) {
        appendMessage("bot", "먼저 조직도에서 대화할 AI 캐릭터를 선택해 주세요.");
        return;
    }

    const response = await askQuestion(question);
    appendMessage("bot", response.answer || response.error_message || "응답을 표시할 수 없습니다.");
    window.regbotCitations.render(response.citations || []);
  });
}

async function refreshLoginState() {
  try {
    csrfToken = await fetchCsrfToken();
    const response = await requestApi({ path: "/api/auth/status/" });
    const payload = response.data;
    if (payload.authenticated) {
      document.body.className = "state-logged-in";
    } else {
      document.body.className = "state-logged-out";
    }
  } catch (error) {
    document.body.className = "state-logged-out";
    loginErrorMsg.textContent = "백엔드 연결 실패: 서버 상태를 확인해 주세요.";
  }
}

async function loadOrgTree() {
  try {
    const response = await requestApi({ path: "/api/orgs/tree/" });
    if (response.ok && response.data && response.data.tree) {
      renderOrgTree(response.data.tree);
    }
  } catch (error) {
    console.error("Failed to load org tree:", error);
  }
}

function renderOrgTree(treeData) {
  orgTreeContainer.replaceChildren();
  characterListContainer.replaceChildren();

  // 트리 렌더링
  for (const node of treeData) {
    const el = document.createElement("div");
    // 버튼인지 단순 라벨인지
    if (node.characters && node.characters.length > 0) {
      el.className = `org-node depth-${node.level}`;
      const btn = document.createElement("button");
      btn.textContent = node.name;
      btn.style.width = "100%";
      btn.style.textAlign = "left";
      btn.style.background = "none";
      btn.style.border = "none";
      btn.style.cursor = "pointer";
      btn.style.color = "var(--text-primary)";
      btn.addEventListener("click", () => renderCharacters(node));
      el.appendChild(btn);
    } else {
      el.className = `org-node depth-${node.level}`;
      el.textContent = node.name;
    }
    orgTreeContainer.append(el);
  }
}

function renderCharacters(node) {
  characterListContainer.replaceChildren();
  // 부서 클릭 시 소속된 캐릭터들을 보여줌
  for (const char of node.characters) {
    const card = document.createElement("div");
    card.className = "character-card";
    if (char.id === characterId) {
      card.classList.add("active");
    }
    card.style.cursor = "pointer";

    const avatar = document.createElement("div");
    avatar.className = "character-avatar";
    avatar.innerHTML = `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bot"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>`;

    const info = document.createElement("div");
    const nameEl = document.createElement("div");
    nameEl.innerHTML = `<strong>${char.name}</strong> <span class="ai-badge">AI</span>`;
    nameEl.style.display = "flex";
    nameEl.style.alignItems = "center";
    nameEl.style.gap = "6px";

    const descEl = document.createElement("p");
    descEl.textContent = char.description || `${node.name} 규정 담당 AI`;

    info.appendChild(nameEl);
    info.appendChild(descEl);

    card.appendChild(avatar);
    card.appendChild(info);

    card.addEventListener("click", () => selectCharacter(char, node));
    characterListContainer.appendChild(card);
  }
}

function selectCharacter(char, node) {
  characterId = char.id;
  chatHeaderTitle.textContent = char.name;
  chatHeaderDesc.textContent = char.description || `${node.name} 규정 담당 AI`;

  // 입력창 활성화 및 안내문구 동적 변경
  input.disabled = false;
  if (char.duty_keywords) {
    // 콤마나 띄어쓰기로 구분된 키워드 중 첫 번째 키워드를 추출하여 예시로 표시
    const firstKeyword = char.duty_keywords.split(/[, ]+/).filter(Boolean)[0] || "관련 규정";
    input.placeholder = `예: ${firstKeyword} 기준을 알려줘`;
  } else {
    input.placeholder = `예: ${char.name} 관련 규정을 알려줘`;
  }

  // UI 갱신을 위해 캐릭터 리스트 리렌더링
  renderCharacters(node);

  // 채팅창 초기화
  messages.replaceChildren();
  window.regbotCitations.render([]);

  appendMessage("bot", `안녕하세요, ${node.name} 소속 ${char.name}입니다. 질문을 입력해 주세요.`);
}

async function fetchCsrfToken() {
  const response = await requestApi({ path: "/api/auth/csrf/" });
  return response.data.csrfToken || "";
}

async function loginUser(username, password) {
  try {
    const response = await requestApi({
      path: "/api/auth/login/",
      method: "POST",
      csrfToken,
      body: { username, password }
    });
    return response.data;
  } catch (error) {
    return { error: "Django 백엔드에 연결할 수 없습니다." };
  }
}

async function askQuestion(question) {
  try {
    const response = await requestApi({
      path: "/api/chat/ask/",
      method: "POST",
      csrfToken,
      body: { character_id: characterId, question }
    });
    if (response.redirected || response.status === 403 || response.status === 302) {
      return { answer: "로그인이 필요합니다. Django 관리자 페이지에서 로그인한 뒤 다시 시도해 주세요." };
    }
    return response.data;
  } catch (error) {
    return { answer: "Django 백엔드에 연결할 수 없습니다. 서버 실행 상태를 확인해 주세요." };
  }
}

async function requestApi(request) {
  if (window.regbot?.apiRequest) {
    return window.regbot.apiRequest(request);
  }
  const response = await fetch(`${backendBaseUrl}${request.path}`, {
    method: request.method || "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": request.csrfToken || ""
    },
    body: request.body === undefined ? undefined : JSON.stringify(request.body)
  });
  return {
    ok: response.ok,
    status: response.status,
    redirected: response.redirected,
    data: await response.json()
  };
}

function appendMessage(kind, text) {
  const article = document.createElement("article");
  article.className = `message ${kind}`;
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  article.append(paragraph);
  messages.append(article);
  messages.scrollTop = messages.scrollHeight;
}
