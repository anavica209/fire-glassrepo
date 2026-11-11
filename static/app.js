const screens = [...document.querySelectorAll("[data-screen]")];
const stepDots = [...document.querySelectorAll("[data-step-dot]")];
const categoryOptions = [...document.querySelectorAll("[data-category]")];
const shuffleButton = document.querySelector("#shuffle-button");
const revealButton = document.querySelector("#reveal-button");
const choiceRow = document.querySelector("#choice-row");
const selectionCount = document.querySelector("#selection-count");
const errorMessage = document.querySelector("#reading-error");
const interpretationCard = document.querySelector("#interpretation-card");
const readingProgress = document.querySelector("#reading-progress");
const actionFeedback = document.querySelector("#action-feedback");
const diaryDialog = document.querySelector("#diary-dialog");
const diaryList = document.querySelector("#diary-list");
const diaryKey = `fire-glass-reading-diary:${document.querySelector(".session-layout").dataset.userId}`;
const reading = {
  category: "amor",
  categoryFocus: "",
  question: "",
  cards: [],
  selected: new Set(),
  currentCard: 0,
};

const romanNumerals = ["I", "II", "III"];
let touchStartX = null;
let accessToken = null;
const sectionTrackingId =
  sessionStorage.getItem("fire-glass-analytics-session") || crypto.randomUUID();
sessionStorage.setItem("fire-glass-analytics-session", sectionTrackingId);
let activeTrackedSection = null;
let analyticsQueue = Promise.resolve();

function trackSection(section) {
  analyticsQueue = analyticsQueue
    .then(async () => {
      const response = await fetch("/api/analytics/section", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sectionTrackingId, section }),
        keepalive: true,
      });
      if (!response.ok) {
        console.error(`Analytics tracking failed with status ${response.status}.`);
      }
    })
    .catch((error) => {
      console.error("Could not send section analytics.", error);
    });
}

async function getAccessToken() {
  if (accessToken) return accessToken;

  const response = await fetch("/auth/session-token", { method: "POST" });
  if (response.status === 401) {
    window.location.assign("/login");
    throw new Error("Tu sesión expiró. Vuelve a iniciar sesión.");
  }
  if (!response.ok) {
    throw new Error("No se pudo validar tu sesión. Inténtalo de nuevo.");
  }

  const result = await response.json();
  accessToken = result.access_token;
  return accessToken;
}

async function authenticatedFetch(url, options) {
  let token = await getAccessToken();
  let response = await fetch(url, {
    ...options,
    headers: { ...options.headers, Authorization: `Bearer ${token}` },
  });

  if (response.status === 401) {
    accessToken = null;
    token = await getAccessToken();
    response = await fetch(url, {
      ...options,
      headers: { ...options.headers, Authorization: `Bearer ${token}` },
    });
  }
  if (response.status === 401) {
    window.location.assign("/login");
  }
  return response;
}

function getSavedReadings() {
  const savedReadings = JSON.parse(localStorage.getItem(diaryKey) || "[]");
  if (!Array.isArray(savedReadings)) {
    throw new Error("El diario guardado tiene un formato inesperado.");
  }
  return savedReadings;
}

function updateDiaryCount() {
  const count = document.querySelector("#diary-count");
  try {
    count.textContent = String(getSavedReadings().length);
    count.removeAttribute("title");
  } catch (error) {
    count.textContent = "!";
    count.title =
      error instanceof Error ? error.message : "No se pudo leer el diario.";
  }
}

function renderDiary() {
  const savedReadings = getSavedReadings();
  if (savedReadings.length === 0) {
    const empty = document.createElement("p");
    empty.className = "diary-empty";
    empty.textContent =
      "Aún no tienes lecturas guardadas. Cuando una lectura te acompañe, guárdala aquí.";
    diaryList.replaceChildren(empty);
    return;
  }

  diaryList.replaceChildren(
    ...savedReadings.map((savedReading) => {
      const entry = document.createElement("article");
      entry.className = "diary-entry";
      const heading = document.createElement("div");
      heading.className = "diary-entry-heading";
      const category = document.createElement("span");
      category.className = "diary-entry-category";
      category.textContent = savedReading.categoryLabel || savedReading.category || "Lectura";
      const date = document.createElement("time");
      const parsedDate = new Date(savedReading.date);
      date.textContent = Number.isNaN(parsedDate.getTime())
        ? "Fecha desconocida"
        : new Intl.DateTimeFormat("es", {
            dateStyle: "medium",
            timeStyle: "short",
          }).format(parsedDate);
      heading.append(category, date);
      entry.append(heading);

      if (savedReading.question) {
        const question = document.createElement("p");
        question.className = "diary-question";
        question.textContent = `“${savedReading.question}”`;
        entry.append(question);
      }
      if (savedReading.categoryFocus) {
        const focus = document.createElement("p");
        focus.className = "diary-focus";
        focus.textContent = savedReading.categoryFocus;
        entry.append(focus);
      }

      const cards = document.createElement("div");
      cards.className = "diary-cards";
      savedReading.cards.forEach((card) => {
        const item = document.createElement("section");
        item.className = "diary-card-entry";
        const title = document.createElement("h3");
        title.textContent = `${card.position} · ${card.name}`;
        const keywords = document.createElement("p");
        keywords.className = "diary-keywords";
        keywords.textContent = Array.isArray(card.keywords)
          ? card.keywords.join(" · ")
          : "";
        const interpretation = document.createElement("p");
        interpretation.className = "diary-interpretation";
        interpretation.textContent = card.interpretation || "";
        item.append(title, keywords, interpretation);
        cards.append(item);
      });
      entry.append(cards);
      return entry;
    }),
  );
}

document.querySelector("#open-diary").addEventListener("click", () => {
  try {
    renderDiary();
  } catch (error) {
    const message = document.createElement("p");
    message.className = "diary-error";
    message.textContent =
      error instanceof Error ? error.message : "No se pudo abrir el diario.";
    diaryList.replaceChildren(message);
  }
  diaryDialog.showModal();
});
document.querySelector("#close-diary").addEventListener("click", () => {
  diaryDialog.close();
});

document.querySelector("#download-reading").addEventListener("click", async (event) => {
  const downloadButton = event.currentTarget;
  downloadButton.disabled = true;
  downloadButton.textContent = "Preparando tus imágenes…";
  actionFeedback.textContent = "";
  try {
    const response = await authenticatedFetch("/api/reading/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category: reading.category,
        cards: reading.cards.map(({ position, name }) => ({ position, name })),
      }),
    });
    if (!response.ok) {
      const result = await response.json();
      throw new Error(
        typeof result.detail === "string"
          ? result.detail
          : "No se pudo preparar la descarga de la lectura.",
      );
    }

    const downloadUrl = URL.createObjectURL(await response.blob());
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = "lectura-fire-glass.zip";
    document.body.append(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);
    actionFeedback.textContent = "Descarga iniciada: incluye una imagen por cada carta.";
  } catch (error) {
    actionFeedback.textContent =
      error instanceof TypeError
        ? "No pudimos conectar con Fire glass. Comprueba que el servidor siga activo."
        : error instanceof Error
          ? error.message
          : "No se pudo descargar la lectura.";
  } finally {
    downloadButton.disabled = false;
    downloadButton.innerHTML = 'Descargar mis cartas <span aria-hidden="true">↓</span>';
  }
});

function showScreen(screenNumber) {
  const section = screenNumber < screens.length ? screenNumber + 1 : null;
  if (section !== activeTrackedSection) {
    activeTrackedSection = section;
    trackSection(section);
  }
  screens.forEach((screen) => {
    const active = Number(screen.dataset.screen) === screenNumber;
    screen.hidden = !active;
    screen.classList.toggle("is-active", active);
  });
  stepDots.forEach((dot) => {
    const active = Number(dot.dataset.stepDot) === screenNumber;
    dot.classList.toggle("is-current", active);
    dot.classList.toggle("is-complete", Number(dot.dataset.stepDot) < screenNumber);
    if (active) dot.setAttribute("aria-current", "step");
    else dot.removeAttribute("aria-current");
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden") {
    trackSection(null);
  } else {
    trackSection(activeTrackedSection);
  }
});
window.addEventListener("pagehide", () => trackSection(null));

document.querySelectorAll(".flow-next, .flow-back").forEach((button) => {
  button.addEventListener("click", () => {
    showScreen(Number(button.dataset.go));
  });
});

categoryOptions.forEach((option) => {
  option.addEventListener("click", () => {
    reading.category = option.dataset.category;
    categoryOptions.forEach((item) => {
      const selected = item === option;
      item.classList.toggle("is-selected", selected);
      item.setAttribute("aria-pressed", String(selected));
    });
  });
});

function updateSelection() {
  const count = reading.selected.size;
  selectionCount.textContent =
    count === 3
      ? "Las tres cartas te esperan. Cuando estés listo, descubre su mensaje."
      : `Has elegido ${count} de 3 cartas. Toca otra para continuar.`;
  revealButton.disabled = count !== 3;
}

function renderChoices() {
  choiceRow.replaceChildren(
    ...reading.cards.map((card, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "choice-card";
      button.setAttribute("aria-label", `Elegir carta ${index + 1}, ${card.position}`);
      button.setAttribute("aria-pressed", "false");
      const indexLabel = document.createElement("span");
      indexLabel.className = "choice-index";
      indexLabel.textContent = romanNumerals[index];
      const symbol = document.createElement("span");
      symbol.className = "choice-symbol";
      symbol.textContent = "✳";
      const position = document.createElement("span");
      position.className = "choice-position";
      position.textContent = card.position;
      const status = document.createElement("span");
      status.className = "choice-status";
      status.textContent = "Toca para elegir";
      button.append(indexLabel, symbol, position, status);
      button.addEventListener("click", () => {
        if (reading.selected.has(index)) {
          reading.selected.delete(index);
          button.classList.remove("is-picked");
          button.setAttribute("aria-pressed", "false");
          status.textContent = "Toca para elegir";
        } else {
          reading.selected.add(index);
          button.classList.add("is-picked");
          button.setAttribute("aria-pressed", "true");
          status.textContent = "Elegida ✳";
        }
        updateSelection();
      });
      return button;
    }),
  );
}

shuffleButton.addEventListener("click", async () => {
  shuffleButton.disabled = true;
  shuffleButton.classList.add("is-loading");
  errorMessage.hidden = true;
  document.querySelector("#shuffle-instruction").textContent =
    "Respira y mantén tu pregunta en mente mientras el mazo encuentra su lugar.";
  document.querySelector("#shuffle-deck").classList.add("is-shuffling");

  try {
    const response = await authenticatedFetch("/api/reading", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category: reading.category,
        question: document.querySelector("#reading-question").value.trim(),
      }),
    });
    if (response.status === 401) {
      window.location.assign("/login");
      return;
    }
    if (!response.ok) {
      throw new Error("No pudimos mezclar el mazo. Inténtalo de nuevo.");
    }

    const result = await response.json();
    reading.category = result.category;
    reading.categoryFocus = result.category_focus;
    reading.question = result.question;
    reading.cards = result.cards;
    reading.selected.clear();
    renderChoices();
    document.querySelector("#shuffle-deck").hidden = true;
    choiceRow.hidden = false;
    shuffleButton.hidden = true;
    revealButton.hidden = false;
    document.querySelector("#shuffle-instruction").textContent =
      "Desliza la intuición: toca las cartas que quieras elegir.";
    updateSelection();
  } catch (error) {
    errorMessage.textContent =
      error instanceof TypeError
        ? "No pudimos conectar con Fire glass. Comprueba que Uvicorn siga ejecutándose en esta dirección y vuelve a intentarlo."
        : error instanceof Error
          ? error.message
          : "Ocurrió un error inesperado.";
    errorMessage.hidden = false;
    document.querySelector("#shuffle-instruction").textContent =
      "Tu lectura está lista cuando tú lo estés.";
  } finally {
    shuffleButton.disabled = false;
    shuffleButton.classList.remove("is-loading");
    document.querySelector("#shuffle-deck").classList.remove("is-shuffling");
  }
});

function renderCard() {
  const card = reading.cards[reading.currentCard];
  if (!card) return;

  interpretationCard.classList.remove("card-flipping");
  void interpretationCard.offsetWidth;
  interpretationCard.classList.add("card-flipping");
  document.querySelector("#interpretation-index").textContent =
    romanNumerals[reading.currentCard];
  document.querySelector("#interpretation-position").textContent =
    card.position.toUpperCase();
  document.querySelector("#interpretation-name").textContent = card.name;
  document.querySelector("#position-heading").textContent =
    `${card.position} · ${card.position_label}`;
  document.querySelector("#meaning-title").textContent = card.name;
  document.querySelector("#interpretation-text").textContent =
    card.interpretation;
  document.querySelector("#category-focus").textContent =
    reading.categoryFocus;
  document.querySelector("#keyword-list").replaceChildren(
    ...card.keywords.map((keyword) => {
      const tag = document.createElement("span");
      tag.className = "keyword-tag";
      tag.textContent = keyword;
      return tag;
    }),
  );

  readingProgress.replaceChildren(
    ...reading.cards.map((_, index) => {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.className = `progress-dot${index === reading.currentCard ? " is-active" : ""}`;
      dot.setAttribute("aria-label", `Ver carta ${index + 1}: ${reading.cards[index].position}`);
      dot.setAttribute("aria-current", index === reading.currentCard ? "step" : "false");
      dot.addEventListener("click", () => {
        reading.currentCard = index;
        renderCard();
      });
      return dot;
    }),
  );

  const atStart = reading.currentCard === 0;
  const atEnd = reading.currentCard === reading.cards.length - 1;
  document.querySelector("#previous-card").disabled = atStart;
  document.querySelector("#next-card").disabled = atEnd;
  document.querySelector("#reading-next").hidden = atEnd;
  document.querySelector("#reading-finish").hidden = !atEnd;
}

revealButton.addEventListener("click", () => {
  if (reading.selected.size !== 3) return;
  reading.currentCard = 0;
  const saveButton = document.querySelector("#save-reading");
  saveButton.disabled = false;
  saveButton.innerHTML = 'Guardar en mi diario <span aria-hidden="true">↗</span>';
  const selectedCategory = categoryOptions.find(
    (option) => option.dataset.category === reading.category,
  );
  document.querySelector("#reading-category").textContent = selectedCategory
    ? `· ${selectedCategory.querySelector("strong").textContent}`
    : "";
  const questionDisplay = document.querySelector("#reading-question-display");
  questionDisplay.hidden = !reading.question;
  questionDisplay.textContent = reading.question ? `“${reading.question}”` : "";
  document.querySelector("#reading-title").innerHTML =
    "Una carta a la vez.<br />Un espacio para <em>escuchar.</em>";
  renderCard();
  showScreen(3);
});

function moveCard(direction) {
  const next = reading.currentCard + direction;
  if (next < 0 || next >= reading.cards.length) return;
  reading.currentCard = next;
  renderCard();
}

document.querySelector("#previous-card").addEventListener("click", () => moveCard(-1));
document.querySelector("#next-card").addEventListener("click", () => moveCard(1));
document.querySelector("#reading-next").addEventListener("click", () => moveCard(1));
document.querySelector("#reading-finish").addEventListener("click", () => {
  const summary = document.querySelector("#closing-summary");
  summary.replaceChildren(
    ...reading.cards.map((card) => {
      const item = document.createElement("span");
      item.textContent = card.name;
      return item;
    }),
  );
  actionFeedback.textContent = "";
  showScreen(4);
});

const interpretationLayout = document.querySelector("#interpretation-layout");
interpretationLayout.addEventListener("pointerdown", (event) => {
  touchStartX = event.clientX;
});
interpretationLayout.addEventListener("pointerup", (event) => {
  if (touchStartX === null) return;
  const delta = event.clientX - touchStartX;
  touchStartX = null;
  if (Math.abs(delta) > 45) moveCard(delta < 0 ? 1 : -1);
});
interpretationLayout.addEventListener("pointercancel", () => {
  touchStartX = null;
});
document.addEventListener("keydown", (event) => {
  if (Number(document.querySelector(".flow-screen.is-active")?.dataset.screen) !== 3) return;
  if (event.key === "ArrowRight") moveCard(1);
  if (event.key === "ArrowLeft") moveCard(-1);
});

document.querySelector("#save-reading").addEventListener("click", () => {
  try {
    const savedReadings = getSavedReadings();
    savedReadings.unshift({
      date: new Date().toISOString(),
      category: reading.category,
      categoryFocus: reading.categoryFocus,
      categoryLabel:
        categoryOptions.find((option) => option.dataset.category === reading.category)
          ?.querySelector("strong")
          .textContent ?? reading.category,
      question: reading.question,
      cards: reading.cards.map((card) => ({
        name: card.name,
        position: card.position,
        keywords: card.keywords,
        interpretation: card.interpretation,
      })),
    });
    localStorage.setItem(diaryKey, JSON.stringify(savedReadings.slice(0, 100)));
    document.querySelector("#save-reading").disabled = true;
    document.querySelector("#save-reading").textContent = "Guardada en mi diario ✓";
    updateDiaryCount();
    actionFeedback.textContent =
      "Lectura guardada en este dispositivo. Puedes volver a ella desde el diario.";
  } catch (error) {
    actionFeedback.textContent =
      error instanceof Error
        ? `No se pudo guardar la lectura: ${error.message}`
        : "No se pudo guardar la lectura en este dispositivo.";
  }
});

document.querySelector("#finish-session").addEventListener("click", () => {
  reading.cards = [];
  reading.selected.clear();
  reading.currentCard = 0;
  reading.question = "";
  reading.categoryFocus = "";
  document.querySelector("#reading-question").value = "";
  document.querySelector("#shuffle-deck").hidden = false;
  choiceRow.hidden = true;
  choiceRow.replaceChildren();
  shuffleButton.hidden = false;
  revealButton.hidden = true;
  revealButton.disabled = true;
  selectionCount.textContent = "Tres cartas esperan por ti.";
  document.querySelector("#shuffle-instruction").textContent =
    "Mantén tu pregunta en mente y mezcla el mazo.";
  errorMessage.hidden = true;
  updateDiaryCount();
  showScreen(0);
});

showScreen(0);
