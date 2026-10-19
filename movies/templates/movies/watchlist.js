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
                credentials: "same-origin"
            });

            const data = await response.json();

            message.textContent = data.message || data.error
                || "Unable to add this movie.";
        } catch (error) {
            message.textContent = "Something went wrong. Please try again.";
        } finally {
            button.disabled = false;
        }
    });
}
