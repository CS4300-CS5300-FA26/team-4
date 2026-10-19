const form = document.getElementById("watchlist-form");

if (form) {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const button = form.querySelector("button");
        const message = document.getElementById("watchlist-message");

        button.disabled = true;
        message.textContent = "Adding movie…";

        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: new FormData(form),
                credentials: "same-origin",
                headers: {
                    Accept: "application/json"
                }
            });

            if (response.redirected || response.status === 401) {
                message.textContent =
                    "Please log in again before adding this movie.";
                return;
            }

            if (response.status === 403) {
                message.textContent =
                    "Your request was rejected. Refresh the page and try again.";
                return;
            }

            const contentType =
                response.headers.get("content-type") || "";

            if (!contentType.includes("application/json")) {
                message.textContent =
                    "The server returned an unexpected response. Please try again.";
                return;
            }

            const data = await response.json();

            if (!response.ok) {
                message.textContent =
                    data.error || "Unable to add this movie. Please try again.";
                return;
            }

            message.textContent =
                data.message || "Movie added to your watchlist.";
        } catch (error) {
            message.textContent =
                "Unable to confirm whether the movie was added. Please try again.";
        } finally {
            button.disabled = false;
        }
    });
}
