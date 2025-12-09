// Safe JSON parser
async function safeJson(response) {
    try {
        const text = await response.text();
        return text ? JSON.parse(text) : {};
    } catch (err) {
        return {};
    }
}

// Toast message popup
function showToast(msg, type = "success") {
    const toast = document.createElement("div");
    toast.className = "toast " + type;
    toast.innerText = msg;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 2500);
}

// Redirect helper
function go(url) {
    window.location.href = url;
}
