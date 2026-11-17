// Support the movie-detail form and each search-result form.
document.querySelectorAll(
    "#watchlist-form, .watchlist-add-form"
).forEach((form) => {
    const button = form.querySelector('button[type="submit"]');

    const message = form.querySelector(
        "#watchlist-message, .watchlist-message"
    );

    const wrapper = form.querySelector(
        "#watchlist-button-wrapper, .watchlist-button-wrapper"
    );

    let isSaved = button.disabled;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (isSaved || button.disabled) {
            return;
        }

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

            const loginUrl = new URL(
                form.dataset.loginUrl,
                window.location.href
            );

            const finalUrl = new URL(response.url);

            const redirectedToLogin =
                response.redirected &&
                finalUrl.origin === loginUrl.origin &&
                finalUrl.pathname === loginUrl.pathname;

            if (response.status === 401 || redirectedToLogin) {
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

            isSaved = true;
            button.textContent = "Added to Watchlist";

            button.setAttribute(
                "aria-label",
                "Added to Watchlist — already saved"
            );

            if (wrapper) {
                wrapper.title = "Already saved to your watchlist";
            }

            message.textContent =
                data.message || "Movie added to your watchlist.";

        } catch (error) {
            message.textContent =
                "Unable to confirm whether the movie was added. Please try again.";

        } finally {
            button.disabled = isSaved;
        }
    });
});