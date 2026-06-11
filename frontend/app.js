const state = {
    messages: [],
    documents: [],
    totalChunks: 0,
    topK: 5,
    selectedModel: localStorage.getItem("vietmind-model") || "qwen3:4b",
    availableModels: [],
    selectedFile: null,
    isAsking: false,
};

const els = {
    body: document.body,
    themeToggle: document.getElementById("themeToggle"),
    newChatBtn: document.getElementById("newChatBtn"),

    modelSelect: document.getElementById("modelSelect"),
    refreshModelsBtn: document.getElementById("refreshModelsBtn"),

    topKSlider: document.getElementById("topKSlider"),
    topKValue: document.getElementById("topKValue"),

    fileInput: document.getElementById("fileInput"),
    fileLabel: document.getElementById("fileLabel"),
    uploadBtn: document.getElementById("uploadBtn"),

    docCount: document.getElementById("docCount"),
    chunkCount: document.getElementById("chunkCount"),
    documentsList: document.getElementById("documentsList"),

    resetBtn: document.getElementById("resetBtn"),

    emptyState: document.getElementById("emptyState"),
    messages: document.getElementById("messages"),
    chatArea: document.getElementById("chatArea"),
    messageInput: document.getElementById("messageInput"),
    sendBtn: document.getElementById("sendBtn"),

    toast: document.getElementById("toast"),
};

function init() {
    initTheme();
    bindEvents();
    loadModels();
    loadDocuments();
    updateInputState();
}

function initTheme() {
    const savedTheme = localStorage.getItem("vietmind-theme") || "dark";

    els.body.dataset.theme = savedTheme;
    els.themeToggle.checked = savedTheme === "dark";
}

function bindEvents() {
    els.themeToggle.addEventListener("change", () => {
        const theme = els.themeToggle.checked ? "dark" : "light";
        els.body.dataset.theme = theme;
        localStorage.setItem("vietmind-theme", theme);
    });

    els.newChatBtn.addEventListener("click", () => {
        state.messages = [];
        renderMessages();
        updateEmptyState();
        showToast("Đã tạo cuộc trò chuyện mới.", "success");
    });

    els.modelSelect.addEventListener("change", () => {
        state.selectedModel = els.modelSelect.value;
        localStorage.setItem("vietmind-model", state.selectedModel);

        showToast(`Đã chọn model: ${state.selectedModel}`, "success");
    });

    els.refreshModelsBtn.addEventListener("click", () => {
        loadModels();
    });

    els.topKSlider.addEventListener("input", () => {
        state.topK = Number(els.topKSlider.value);
        els.topKValue.textContent = state.topK;
    });

    els.fileInput.addEventListener("change", () => {
        const file = els.fileInput.files[0];

        if (!file) {
            state.selectedFile = null;
            els.fileLabel.textContent = "Chọn PDF, TXT hoặc DOCX";
            els.uploadBtn.disabled = true;
            return;
        }

        state.selectedFile = file;
        els.fileLabel.textContent = file.name;
        els.uploadBtn.disabled = false;
    });

    els.uploadBtn.addEventListener("click", uploadSelectedFile);

    els.resetBtn.addEventListener("click", resetKnowledgeBase);

    els.sendBtn.addEventListener("click", () => {
        submitCurrentMessage();
    });

    els.messageInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submitCurrentMessage();
        }
    });

    els.messageInput.addEventListener("input", () => {
        autoResizeTextarea();
    });

    document.querySelectorAll(".prompt-card").forEach((button) => {
        button.addEventListener("click", () => {
            const question = button.dataset.question;
            ask(question);
        });
    });
}

function autoResizeTextarea() {
    els.messageInput.style.height = "auto";
    els.messageInput.style.height = `${els.messageInput.scrollHeight}px`;
}

function updateInputState() {
    const hasDocuments = state.documents.length > 0;

    els.messageInput.disabled = !hasDocuments;
    els.sendBtn.disabled = !hasDocuments;

    els.messageInput.placeholder = hasDocuments
        ? "Nhắn tin cho VietMind-RAG..."
        : "Upload và index tài liệu trước khi hỏi...";

    document.querySelectorAll(".prompt-card").forEach((button) => {
        button.disabled = !hasDocuments;
    });
}

async function loadModels() {
    els.modelSelect.disabled = true;
    els.modelSelect.innerHTML = `<option value="">Loading...</option>`;

    try {
        const response = await fetch("/models");

        if (!response.ok) {
            throw new Error(await response.text());
        }

        const data = await response.json();

        state.availableModels = data.models || [];

        if (state.availableModels.length === 0) {
            state.availableModels = [data.default_model || "qwen3:4b"];
        }

        if (!state.availableModels.includes(state.selectedModel)) {
            state.selectedModel = data.default_model || state.availableModels[0];
            localStorage.setItem("vietmind-model", state.selectedModel);
        }

        renderModelOptions();

        if (data.warning) {
            showToast("Không kết nối được Ollama. Đang dùng model mặc định.", "error");
        }
    } catch (error) {
        console.error(error);

        state.availableModels = [state.selectedModel || "qwen3:4b"];
        renderModelOptions();

        showToast("Không tải được danh sách model Ollama.", "error");
    } finally {
        els.modelSelect.disabled = false;
    }
}

function renderModelOptions() {
    els.modelSelect.innerHTML = state.availableModels
        .map((modelName) => {
            const selected = modelName === state.selectedModel ? "selected" : "";

            return `
                <option value="${escapeHTML(modelName)}" ${selected}>
                    ${escapeHTML(modelName)}
                </option>
            `;
        })
        .join("");
}

async function loadDocuments() {
    try {
        const response = await fetch("/documents");

        if (!response.ok) {
            throw new Error(await response.text());
        }

        const data = await response.json();

        state.documents = data.documents || [];
        state.totalChunks = data.total_chunks || 0;

        renderDocuments();
        updateInputState();
        updateEmptyState();
    } catch (error) {
        console.error(error);
        showToast("Không tải được Knowledge Base.", "error");
    }
}

function renderDocuments() {
    els.docCount.textContent = state.documents.length;
    els.chunkCount.textContent = state.totalChunks;

    if (state.documents.length === 0) {
        els.documentsList.innerHTML = `
            <div class="document-item">
                <div class="document-name">Chưa có tài liệu</div>
                <div class="document-meta">Upload file để bắt đầu.</div>
            </div>
        `;
        return;
    }

    els.documentsList.innerHTML = state.documents
        .map((doc) => {
            return `
                <div class="document-item">
                    <div class="document-name">${escapeHTML(doc.source)}</div>
                    <div class="document-meta">
                        ${doc.num_chunks} chunks · ${doc.num_pages} pages/sections
                    </div>
                    <button
                        class="delete-doc-btn"
                        data-source="${escapeHTML(doc.source)}"
                    >
                        Delete
                    </button>
                </div>
            `;
        })
        .join("");

    document.querySelectorAll(".delete-doc-btn").forEach((button) => {
        button.addEventListener("click", () => {
            const source = button.dataset.source;
            deleteDocument(source);
        });
    });
}

async function uploadSelectedFile() {
    if (!state.selectedFile) {
        showToast("Chưa chọn file.", "error");
        return;
    }

    const formData = new FormData();
    formData.append("file", state.selectedFile);

    els.uploadBtn.disabled = true;
    els.uploadBtn.textContent = "Indexing...";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        const data = await response.json();

        showToast(`Index thành công: ${data.num_chunks} chunks.`, "success");

        state.selectedFile = null;
        els.fileInput.value = "";
        els.fileLabel.textContent = "Chọn PDF, TXT hoặc DOCX";

        await loadDocuments();
    } catch (error) {
        console.error(error);
        showToast("Index thất bại. Kiểm tra backend hoặc định dạng file.", "error");
    } finally {
        els.uploadBtn.textContent = "Index document";
        els.uploadBtn.disabled = true;
    }
}

async function deleteDocument(source) {
    const ok = confirm(`Xóa tài liệu "${source}" khỏi Knowledge Base?`);

    if (!ok) return;

    try {
        const response = await fetch("/documents", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ source }),
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        showToast("Đã xóa tài liệu.", "success");
        await loadDocuments();
    } catch (error) {
        console.error(error);
        showToast("Không xóa được tài liệu.", "error");
    }
}

async function resetKnowledgeBase() {
    const ok = confirm(
        "Bạn chắc chắn muốn xóa toàn bộ Knowledge Base? Thao tác này không thể hoàn tác."
    );

    if (!ok) return;

    try {
        const response = await fetch("/reset", {
            method: "DELETE",
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        state.messages = [];
        renderMessages();

        showToast("Đã reset Knowledge Base.", "success");
        await loadDocuments();
    } catch (error) {
        console.error(error);
        showToast("Reset thất bại.", "error");
    }
}

function submitCurrentMessage() {
    const question = els.messageInput.value.trim();

    if (!question || state.isAsking) return;

    els.messageInput.value = "";
    autoResizeTextarea();

    ask(question);
}

async function ask(question) {
    if (state.documents.length === 0) {
        showToast("Hãy upload và index tài liệu trước.", "error");
        return;
    }

    addMessage({
        role: "user",
        content: question,
    });

    const typingId = addTypingMessage();

    state.isAsking = true;
    els.sendBtn.disabled = true;

    const start = performance.now();

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                question,
                top_k: state.topK,
                model: state.selectedModel,
            }),
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        const data = await response.json();
        const elapsed = (performance.now() - start) / 1000;

        removeMessageById(typingId);

        addMessage({
            role: "assistant",
            content: data.answer || "Không có câu trả lời.",
            sources: data.sources || [],
            elapsed,
            model: data.model || state.selectedModel,
        });
    } catch (error) {
        console.error(error);

        removeMessageById(typingId);

        addMessage({
            role: "assistant",
            content: "Đã xảy ra lỗi khi gọi backend hoặc LLM. Hãy kiểm tra FastAPI và Ollama.",
            sources: [],
        });
    } finally {
        state.isAsking = false;
        els.sendBtn.disabled = false;
    }
}

function addMessage(message) {
    state.messages.push({
        id: crypto.randomUUID(),
        sources: [],
        ...message,
    });

    renderMessages();
    updateEmptyState();
    scrollToBottom();
}

function addTypingMessage() {
    const id = crypto.randomUUID();

    state.messages.push({
        id,
        role: "assistant",
        content: "__typing__",
        sources: [],
    });

    renderMessages();
    updateEmptyState();
    scrollToBottom();

    return id;
}

function removeMessageById(id) {
    state.messages = state.messages.filter((message) => message.id !== id);
    renderMessages();
    updateEmptyState();
}

function renderMessages() {
    els.messages.innerHTML = state.messages
        .map((message) => renderMessage(message))
        .join("");
}

function renderMessage(message) {
    const roleClass = message.role === "user" ? "user" : "assistant";
    const avatar = message.role === "user" ? "U" : "AI";

    if (message.content === "__typing__") {
        return `
            <div class="message-row assistant">
                <div class="message-group">
                    <div class="avatar assistant">AI</div>
                    <div>
                        <div class="bubble assistant">
                            <div class="typing">
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    const modelMeta = message.model
        ? ` · Model: ${escapeHTML(message.model)}`
        : "";

    const meta = message.elapsed
        ? `<div class="message-meta">⏱️ ${message.elapsed.toFixed(2)}s${modelMeta}</div>`
        : "";

    const sourcesHTML =
        message.role === "assistant" && message.sources && message.sources.length > 0
            ? renderSources(message.sources)
            : "";

    return `
        <div class="message-row ${roleClass}">
            <div class="message-group">
                <div class="avatar ${roleClass}">${avatar}</div>
                <div>
                    <div class="bubble ${roleClass}">
                        ${renderMarkdownLite(message.content)}
                    </div>
                    ${meta}
                    ${sourcesHTML}
                </div>
            </div>
        </div>
    `;
}

function renderSources(sources) {
    const items = sources
        .map((source) => {
            const distance =
                typeof source.distance === "number"
                    ? source.distance.toFixed(4)
                    : "N/A";

            return `
                <div class="source-item">
                    <div class="source-title">
                        [Nguồn ${escapeHTML(String(source.ref_id ?? ""))}]
                        ${escapeHTML(String(source.source ?? ""))}
                    </div>
                    <div class="source-meta">
                        Trang: ${escapeHTML(String(source.page ?? ""))}
                        · Distance: ${distance}
                    </div>
                    <div class="source-text">
                        ${escapeHTML(String(source.text ?? ""))}
                    </div>
                </div>
            `;
        })
        .join("");

    return `
        <details class="sources-box">
            <summary>🔎 Xem nguồn truy xuất</summary>
            ${items}
        </details>
    `;
}

function updateEmptyState() {
    els.emptyState.style.display = state.messages.length === 0 ? "block" : "none";
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        els.chatArea.scrollTop = els.chatArea.scrollHeight;
    });
}

function renderMarkdownLite(text) {
    let safe = escapeHTML(String(text));

    safe = safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    safe = safe.replace(
        /\[(Nguồn\s*\d+)\]/g,
        "<span class='source-ref'>[$1]</span>"
    );

    safe = safe.replace(/\n---\n/g, "<br><hr><br>");
    safe = safe.replace(/\n/g, "<br>");

    return safe;
}

function escapeHTML(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function showToast(message, type = "success") {
    els.toast.textContent = message;
    els.toast.className = `toast show ${type}`;

    setTimeout(() => {
        els.toast.className = "toast";
    }, 2600);
}

init();