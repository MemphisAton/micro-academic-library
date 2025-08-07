document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("arxiv-form");
    const limitInput = document.getElementById("limit");
    const categoryInput = document.getElementById("category");

    // Restore last used value from localStorage
    const lastLimit = localStorage.getItem("lastLimit");
    if (lastLimit) limitInput.value = lastLimit;

    // Timestamp when the page was loaded
    const pageLoadedAt = new Date().toISOString();

    // Handle form submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const limit = limitInput.value;
        const category = categoryInput.value;

        // Save last value
        localStorage.setItem("lastLimit", limit);

        showPopup(`Loading ${limit} publications. Estimated time: ${limit * 5} seconds.`);

        try {
            const response = await fetch(`/publications/bulk/arxiv/?limit=${limit}&category=${encodeURIComponent(category)}`, {
                method: "POST"
            });

            if (!response.ok) {
                const data = await response.json();
                const errorMessage = data?.error || "An error occurred while starting the download.";
                showPopup(errorMessage, true); // red background
                return;
            }

        } catch (err) {
            console.error(err);
            showPopup("An unexpected error occurred.", true);
        }
    });

    // Poll the server every 10 seconds for new publications
    setInterval(async () => {
        try {
            const response = await fetch(`/publications/updated-since?after=${encodeURIComponent(pageLoadedAt)}`);
            const data = await response.json();

            if (data.updated) {
                console.log(`New publications detected (${data.new_count}). Reloading...`);
                location.reload();
            }
        } catch (err) {
            console.warn("Error while polling for updates:", err);
        }
    }, 10000);
});


// ===================================
// 🔔 Popup Notification
// ===================================

let currentPopup = null;

function showPopup(message, isError = false) {
    // Remove existing popup
    if (currentPopup) {
        currentPopup.remove();
        currentPopup = null;
    }

    const popup = document.createElement("div");
    popup.innerText = message;

    Object.assign(popup.style, {
        position: "fixed",
        bottom: "20px",
        right: "20px",
        backgroundColor: isError ? "#8B0000" : "rgba(0, 0, 0, 0.8)",
        color: "#fff",
        padding: "12px 16px",
        borderRadius: "8px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
        zIndex: "9999",
        fontSize: "14px",
        transition: "opacity 0.3s ease",
        cursor: "pointer",
        opacity: "0"
    });

    document.body.appendChild(popup);
    currentPopup = popup;

    const closePopup = () => {
        popup.style.opacity = "0";
        setTimeout(() => {
            popup.remove();
            if (currentPopup === popup) {
                currentPopup = null;
            }
        }, 300);
        document.removeEventListener("click", closePopup);
    };

    setTimeout(() => {
        popup.style.opacity = "1";
    }, 10);

    setTimeout(closePopup, 5000);
    document.addEventListener("click", closePopup);
}
