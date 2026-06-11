const citationModal = document.querySelector("#citation-modal");
const modalTitle = document.querySelector("#modal-title");
const modalBody = document.querySelector("#modal-body-content");
const modalCloseBtn = document.querySelector("#modal-close-btn");
const citationList = document.querySelector("#citations");

const allowedTags = new Set([
  "b",
  "br",
  "em",
  "i",
  "li",
  "ol",
  "p",
  "strong",
  "table",
  "tbody",
  "td",
  "tfoot",
  "th",
  "thead",
  "tr",
  "ul"
]);

function renderCitations(items) {
  citationList.replaceChildren();
  if (items.length === 0) {
    citationList.append(createEmptyCitationItem());
    return;
  }
  for (const citation of items) {
    citationList.append(createCitationItem(citation));
  }
}

function createEmptyCitationItem() {
  const item = document.createElement("li");
  item.textContent = "표시할 근거가 없습니다.";
  return item;
}

function createCitationItem(citation) {
  const item = document.createElement("li");
  if (citation !== null && typeof citation === "object") {
    item.textContent = String(citation.title || "근거 조항");
    item.addEventListener("click", () => {
      showCitationModal(citation.title, citation.body);
    });
    return item;
  }
  item.textContent = String(citation);
  return item;
}

function showCitationModal(title, bodyText) {
  modalTitle.textContent = String(title || "근거 조항");
  modalBody.replaceChildren(renderEvidenceBody(bodyText));
  citationModal.style.display = "flex";
}

function renderEvidenceBody(bodyText) {
  const text = String(bodyText || "").trim();
  if (!text) {
    const empty = document.createElement("p");
    empty.className = "evidence-empty";
    empty.textContent = "표시할 근거 본문이 없습니다.";
    return empty;
  }
  if (/<[a-z][\s\S]*>/i.test(text)) {
    return renderSanitizedHtml(text);
  }
  return renderPlainText(text);
}

function renderPlainText(text) {
  const fragment = document.createDocumentFragment();
  for (const block of text.split(/\n{2,}/)) {
    const paragraph = document.createElement("p");
    paragraph.className = "evidence-paragraph";
    paragraph.textContent = block.trim();
    fragment.append(paragraph);
  }
  return fragment;
}

function renderSanitizedHtml(text) {
  const parser = new DOMParser();
  const parsed = parser.parseFromString(`<div>${text}</div>`, "text/html");
  const source = parsed.body.firstElementChild;
  const fragment = document.createDocumentFragment();
  for (const node of source.childNodes) {
    const safeNode = sanitizeNode(node);
    if (safeNode !== null) {
      fragment.append(safeNode);
    }
  }
  if (fragment.childNodes.length === 0) {
    return renderPlainText(text);
  }
  return fragment;
}

function sanitizeNode(node) {
  if (node.nodeType === Node.TEXT_NODE) {
    return document.createTextNode(node.textContent || "");
  }
  if (node.nodeType !== Node.ELEMENT_NODE) {
    return null;
  }
  const tagName = node.tagName.toLowerCase();
  if (!allowedTags.has(tagName)) {
    return document.createTextNode(node.textContent || "");
  }
  const safeElement = document.createElement(tagName);
  copySafeTableAttributes(node, safeElement);
  if (tagName === "table") {
    safeElement.className = "evidence-table";
  }
  for (const child of node.childNodes) {
    const safeChild = sanitizeNode(child);
    if (safeChild !== null) {
      safeElement.append(safeChild);
    }
  }
  return safeElement;
}

function copySafeTableAttributes(source, target) {
  if (!["td", "th"].includes(target.tagName.toLowerCase())) {
    return;
  }
  copyPositiveIntegerAttribute(source, target, "rowspan", "rowSpan");
  copyPositiveIntegerAttribute(source, target, "colspan", "colSpan");
}

function copyPositiveIntegerAttribute(source, target, sourceName, targetName) {
  const rawValue = source.getAttribute(sourceName);
  const parsedValue = Number.parseInt(rawValue || "", 10);
  if (Number.isInteger(parsedValue) && parsedValue > 1 && parsedValue <= 50) {
    target[targetName] = parsedValue;
  }
}

function hideCitationModal() {
  citationModal.style.display = "none";
}

modalCloseBtn.addEventListener("click", hideCitationModal);

window.addEventListener("click", (event) => {
  if (event.target === citationModal) {
    hideCitationModal();
  }
});

window.regbotCitations = {
  render: renderCitations
};
