// Helper functions
function truncateText(text, maxLength = 25) {
    return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
}

function disableButtons(disabled) {
    const buttons = document.querySelectorAll("#documentList button");
    buttons.forEach(button => {
        button.disabled = disabled;
        button.innerHTML = disabled ? '<i class="fas fa-spinner fa-spin"></i>' : '<i class="fas fa-plus"></i>';
    });
}

// Chat-related functions
const chatBox = document.getElementById("chatBox");
const chatContent = document.getElementById("chatContent");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");

function formatTextWithLineBreaks(text) {
    return text.replace(/\n/g, "<br>");
}

async function sendMessage() {
    const question = userInput.value.trim();
    if (!question) return;

    chatContent.innerHTML += `<div class="d-flex justify-content-end"><div class="message message-user"><strong>You:</strong> ${formatTextWithLineBreaks(
        question
    )}</div></div>`;
    userInput.value = "";

    chatBox.scrollTop = chatBox.scrollHeight;

    userInput.disabled = true;
    sendButton.disabled = true;

    const contextOption = document.querySelector(
        'input[name="contextOption"]:checked'
    ).value;
    const endpoint =
        contextOption === "all" ? "/query/query_single/" : "/query/query_split/";

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question }),
        });
        const data = await response.json();

        const result = formatTextWithLineBreaks(
            data.result || "No response available"
        );
        chatContent.innerHTML += `<div class="d-flex justify-content-start"><div class="message message-model"><strong>Model:</strong> ${result}</div></div>`;

        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (error) {
        console.error("Error sending message:", error);
        chatContent.innerHTML += `<div class="d-flex justify-content-start"><div class="message message-model"><strong>Error:</strong> Could not retrieve answer.</div></div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    } finally {
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
    }
}

sendButton.addEventListener("click", sendMessage);

userInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

// Model loading and updating functions for navbar
const currentModelElement = document.getElementById("currentModel");
const modelsList = document.getElementById("modelsList");

async function fetchCurrentModel() {
    try {
        const response = await fetch("/query/get_current_model/");
        const data = await response.json();
        currentModelElement.textContent = data.current_model || "Select Model";
    } catch (error) {
        console.error("Error fetching current model:", error);
        currentModelElement.textContent = "Error loading model";
    }
}

async function fetchModels() {
    try {
        const response = await fetch("/query/check_available_models/");
        const data = await response.json();

        if (data.models && data.models.length > 0) {
            data.models.forEach((model) => {
                const listItem = document.createElement("li");
                const link = document.createElement("a");
                link.className = "dropdown-item";
                link.href = "#";
                link.textContent = model;
                link.addEventListener("click", async () => {
                    await updateModel(model);
                });

                listItem.appendChild(link);
                modelsList.appendChild(listItem);
            });
        } else {
            modelsList.innerHTML = `<li><a class="dropdown-item" href="#">No models available</a></li>`;
        }
    } catch (error) {
        console.error("Error loading models:", error);
        modelsList.innerHTML = `<li><a class="dropdown-item" href="#">Error loading models</a></li>`;
    }
}

async function updateModel(modelName) {
    try {
        const response = await fetch("/query/update_llm/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ llm_name: modelName }),
        });
        const data = await response.json();

        if (data.status === "success") {
            currentModelElement.textContent = data.current_model;
        } else {
            console.error("Failed to update model:", data);
            alert("Error updating model");
        }
    } catch (error) {
        console.error("Error updating model:", error);
        alert("Error updating model");
    }
}

// Document and vectorstore fetching and updating functions
async function fetchDocuments() {
    try {
        const response = await fetch("/documents/list_documents/");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const documentListElement = document.getElementById("documentList");
        documentListElement.innerHTML = "";

        const vectorstores = await fetchVectorstoreNames();

        if (data.documents && data.documents.length > 0) {
            data.documents.slice(0, 5).forEach((docName) => {
                const div = document.createElement("div");
                div.className = "d-flex justify-content-between align-items-center mb-2";

                const icon = document.createElement("i");
                icon.className = "fas fa-file-pdf text-danger me-2";

                const nameLabel = document.createElement("span");
                nameLabel.textContent = truncateText(docName);
                nameLabel.style.fontSize = "0.8em";

                const button = document.createElement("button");
                button.className = "btn btn-sm rounded-circle";
                button.style.width = "30px";
                button.style.height = "30px";
                button.innerHTML = '<i class="fas fa-plus"></i>';

                const vectorstoreName = docName.replace(".pdf", "");
                button.classList.add(vectorstores.includes(vectorstoreName) ? "btn-success" : "btn-danger");

                button.onclick = () => collectData(docName);

                div.appendChild(icon);
                div.appendChild(nameLabel);
                div.appendChild(button);
                documentListElement.appendChild(div);
            });
        } else {
            documentListElement.innerHTML = "<p>No documents available</p>";
        }
    } catch (error) {
        console.error("Error fetching documents:", error);
        document.getElementById("documentList").innerHTML = "<p>Error loading documents</p>";
    }
}

async function fetchVectorstoreNames() {
    try {
        const response = await fetch("/vectorstore/list_vectorstores/");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data.vectorstores || [];
    } catch (error) {
        console.error("Error fetching vectorstore names:", error);
        return [];
    }
}

async function fetchVectorstores() {
    try {
        const response = await fetch("/vectorstore/list_vectorstores/");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const vectorstoreListElement = document.getElementById("vectorstoreList");
        vectorstoreListElement.innerHTML = "";

        if (data.vectorstores && data.vectorstores.length > 0) {
            data.vectorstores.forEach((vectorstore) => {
                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.id = `vectorstore_${vectorstore}`;
                checkbox.value = vectorstore;
                checkbox.className = "form-check-input";

                const label = document.createElement("label");
                label.htmlFor = `vectorstore_${vectorstore}`;
                label.className = "form-check-label";
                label.textContent = truncateText(vectorstore);
                label.style.fontSize = "0.8em";

                const div = document.createElement("div");
                div.className = "form-check mb-2";
                div.appendChild(checkbox);
                div.appendChild(label);

                vectorstoreListElement.appendChild(div);

                checkbox.addEventListener("change", updateRetriever);
            });

            await fetchCurrentRetrievers();
        } else {
            vectorstoreListElement.innerHTML = "<p>No vectorstores available</p>";
        }
    } catch (error) {
        console.error("Error fetching vectorstores:", error);
        document.getElementById("vectorstoreList").innerHTML = "<p>Error loading vectorstores</p>";
    }
}

async function fetchCurrentRetrievers() {
    try {
        const response = await fetch("/query/get_current_retrievers/");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const currentRetrievers = data.retrievers || [];

        currentRetrievers.forEach(retriever => {
            const checkbox = document.getElementById(`vectorstore_${retriever}`);
            if (checkbox) {
                checkbox.checked = true;
            }
        });
    } catch (error) {
        console.error("Error fetching current retrievers:", error);
    }
}

async function updateRetriever() {
    const selectedVectorstores = Array.from(document.querySelectorAll("#vectorstoreList input[type=checkbox]:checked"))
        .map((checkbox) => checkbox.value);

    try {
        const response = await fetch("/query/update_retriever/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ vectorstores: selectedVectorstores })
        });

        const data = await response.json();
        if (data.status === "success") {
            console.log("Retriever updated successfully:", data.current_retrievers);
        } else {
            console.error("Failed to update retriever");
        }
    } catch (error) {
        console.error("Error updating retriever:", error);
    }
}

async function collectData(filename) {
    disableButtons(true);
    try {
        const response = await fetch(`/vectorstore/save_vectorstore/?filename=${encodeURIComponent(filename)}`, {
            method: "POST",
        });

        const data = await response.json();
        if (data.status === "success") {
            alert(`Data collected successfully for ${filename}`);

            fetchDocuments();
            fetchVectorstores();
        } else {
            alert(`Failed to collect data for ${filename}`);
        }
    } catch (error) {
        console.error("Error collecting data:", error);
        alert("An error occurred while collecting data.");
    } finally {
        disableButtons(false);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    fetchDocuments();
    fetchVectorstores();
    fetchCurrentModel();
    fetchModels();
});
