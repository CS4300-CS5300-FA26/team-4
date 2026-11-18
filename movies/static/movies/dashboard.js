(() => {
    const profile = document.querySelector("#profile");
    const recommendations = document.querySelector("#recommendations");

    if (!profile || !recommendations) {
        return;
    }

    async function readResponse(response) {
        if (response.status === 401 || response.redirected) {
            throw new Error("Please log in again to view your dashboard.");
        }

        const contentType = response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {
            throw new Error(
                "Unable to load this section. Refresh the page and try again."
            );
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Unable to load this section. Please try again."
            );
        }

        return data;
    }

    function sectionLoader(section, url, render, clear) {
        let controller;

        const status = section.querySelector(".dashboard-status");
        const retry = section.querySelector(".dashboard-retry");

        const load = async () => {
            if (controller) {
                controller.abort();
            }

            controller = new AbortController();
            const current = controller;

            clear();
            status.textContent = "Loading…";
            retry.hidden = true;
            section.setAttribute("aria-busy", "true");

            try {
                const response = await fetch(url, {
                    credentials: "same-origin",
                    headers: {
                        Accept: "application/json",
                    },
                    signal: current.signal,
                });

                const data = await readResponse(response);

                if (current.signal.aborted) {
                    return;
                }

                status.textContent = "";
                render(data, status);
            } catch (error) {
                if (current.signal.aborted) {
                    return;
                }

                status.textContent =
                    error.message || "Unable to load this section. Please try again.";

                retry.hidden = false;
            } finally {
                if (controller === current) {
                    section.removeAttribute("aria-busy");
                }
            }
        };

        retry.addEventListener("click", load);

        return load;
    }

        const statsContent = profile.querySelector(".stats-content");
    const chart = profile.querySelector(".genre-chart");

    const loadStats = sectionLoader(
        profile,
        profile.dataset.statsUrl,
        (data) => {
            profile.querySelectorAll("[data-stat]").forEach((element) => {
                element.textContent = data[element.dataset.stat];
            });

            statsContent.hidden = false;

            const summary = profile.querySelector(".genre-summary");

            if (data.genre_counts.length) {
                summary.textContent = `Your top genre is ${data.top_genre}.`;
            } else if (data.total_watched) {
                summary.textContent =
                    "Genre information is unavailable for your watched movies. Try again later.";
            } else {
                summary.textContent =
                    "Mark movies as watched to see your favorite genres here.";
            }

            data.genre_counts.forEach(({ genre, count }, index) => {
                const row = document.createElement("li");
                const label = document.createElement("label");
                const meter = document.createElement("meter");

                meter.id = `genre-${index}`;
                meter.min = 0;
                meter.max = Math.max(data.total_watched, count, 1);
                meter.value = count;

                label.htmlFor = meter.id;
                label.textContent =
                    `${genre} · ${count} ${count === 1 ? "movie" : "movies"}`;

                row.append(label, meter);
                chart.append(row);
            });
        },
        () => {
            statsContent.hidden = true;
            chart.replaceChildren();
        }
    );

        const grid = recommendations.querySelector(".recommendation-grid");

    const loadRecommendations = sectionLoader(
        recommendations,
        recommendations.dataset.recommendationsUrl,
        (data, status) => {
            if (!data.movies.length) {
                status.textContent = data.has_history
                    ? "No new suggestions right now. Try rating more watched movies."
                    : "Mark a movie as watched and give it a rating to get personalized suggestions.";

                return;
            }

            data.movies.forEach((movie) => {
                const card = document
                    .querySelector("#recommendation-card")
                    .content.cloneNode(true);

                const link = card.querySelector(".recommendation-title");

                link.href = movie.detail_url;
                link.textContent = movie.title;

                card.querySelector(".year").textContent =
                    movie.release_year || "";

                card.querySelector("form").action = movie.add_url;

                if (movie.poster_url) {
                    const image = document.createElement("img");

                    image.className = "movie-thumbnail";
                    image.src = movie.poster_url;
                    image.alt = `Poster for ${movie.title}`;
                    image.loading = "lazy";

                    image.addEventListener("error", () => {
                        const placeholder = document.createElement("div");

                        placeholder.className =
                            "movie-thumbnail poster-placeholder";

                        placeholder.textContent = "Poster unavailable";

                        image.replaceWith(placeholder);
                    }, { once: true });

                    card.querySelector(".poster-placeholder")
                        .replaceWith(image);
                }

                grid.append(card);
            });
        },
        () => {
            grid.replaceChildren();
        }
    );

        grid.addEventListener("submit", async (event) => {
        const form = event.target.closest(".recommendation-add-form");

        if (!form) {
            return;
        }

        event.preventDefault();

        const button = form.querySelector("button");
        const message = form.querySelector(".watchlist-message");

        if (button.disabled) {
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
                    Accept: "application/json",
                },
            });

            await readResponse(response);

            window.location.reload();
        } catch (error) {
            message.textContent =
                error.message || "Unable to add this movie. Please try again.";

            button.disabled = false;
        }
    });

        document.addEventListener("watchlist:changed", () => {
        loadStats();
        loadRecommendations();
    });

    loadStats();
    loadRecommendations();
})();