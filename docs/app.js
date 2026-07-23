const MAP_POSITIONS = {
  AK: [1, 1],
  ME: [1, 13],
  WA: [2, 2],
  MT: [2, 4],
  ND: [2, 5],
  MN: [2, 6],
  WI: [2, 7],
  MI: [2, 8],
  VT: [2, 11],
  NH: [2, 12],
  OR: [3, 2],
  ID: [3, 3],
  WY: [3, 4],
  SD: [3, 5],
  IA: [3, 6],
  IL: [3, 7],
  IN: [3, 8],
  OH: [3, 9],
  PA: [3, 10],
  NY: [3, 11],
  MA: [3, 12],
  RI: [3, 13],
  CA: [4, 2],
  NV: [4, 3],
  UT: [4, 4],
  CO: [4, 5],
  NE: [4, 6],
  MO: [4, 7],
  KY: [4, 8],
  WV: [4, 9],
  VA: [4, 10],
  MD: [4, 11],
  NJ: [4, 12],
  CT: [4, 13],
  AZ: [5, 3],
  NM: [5, 4],
  KS: [5, 6],
  AR: [5, 7],
  TN: [5, 8],
  NC: [5, 10],
  SC: [5, 11],
  DE: [5, 12],
  DC: [5, 13],
  HI: [6, 2],
  OK: [6, 6],
  LA: [6, 7],
  MS: [6, 8],
  AL: [6, 9],
  GA: [6, 10],
  TX: [7, 5],
  FL: [7, 11],
};

const QUALITY_SORT = {
  exact: 1,
  state: 2,
  federal: 3,
};

const state = {
  data: null,
  activeFilter: "all",
  searchTerm: "",
  selectedCode: "CO",
  sortKey: "name",
  sortDirection: "asc",
};

const elements = {
  tileMap: document.querySelector("#tile-map"),
  detail: document.querySelector("#state-detail"),
  tableBody: document.querySelector("#state-table-body"),
  stateSearch: document.querySelector("#state-search"),
  visibleCount: document.querySelector("#visible-state-count"),
  downloadFiltered: document.querySelector("#download-filtered"),
  downloadGrid: document.querySelector("#download-grid"),
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function safeUrl(value) {
  try {
    const parsed = new URL(value);
    return ["http:", "https:"].includes(parsed.protocol) ? parsed.href : "";
  } catch {
    return "";
  }
}

function formatNumber(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "Not available";
  }
  return Number(value).toFixed(digits).replace(/\.0$/, "");
}

function formatDate(dateString) {
  const parsed = new Date(`${dateString}T12:00:00`);
  if (Number.isNaN(parsed.getTime())) {
    return dateString;
  }
  return new Intl.DateTimeFormat("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(parsed);
}

function percentOf(part, total) {
  return total ? Math.round((part / total) * 100) : 0;
}

function isVisible(item) {
  const matchesFilter =
    state.activeFilter === "all" || item.quality === state.activeFilter;
  const searchable = `${item.name} ${item.code} ${item.assessment}`.toLowerCase();
  return matchesFilter && searchable.includes(state.searchTerm);
}

function getVisibleStates() {
  return state.data.states.filter(isVisible);
}

function selectFallbackState(visibleStates) {
  if (!visibleStates.length) {
    return;
  }
  if (!visibleStates.some((item) => item.code === state.selectedCode)) {
    state.selectedCode = visibleStates[0].code;
  }
}

function updateSummary() {
  const { counts } = state.data;
  const stateShare = percentOf(counts.statePublished, counts.jurisdictions);

  document.querySelector("#build-date").textContent = formatDate(state.data.buildDate);
  document.querySelector("#state-published-count").textContent = counts.statePublished;
  document.querySelector("#state-published-share").textContent = `${stateShare}%`;
  document.querySelector("#exact-count").textContent = counts.exact;
  document.querySelector("#state-reference-count").textContent = counts.state;
  document.querySelector("#federal-count").textContent = counts.federal;
  document.querySelector("#coverage-share-label").textContent = `${stateShare}% covered`;

  document.querySelector("#all-filter-count").textContent = counts.jurisdictions;
  document.querySelector("#exact-filter-count").textContent = counts.exact;
  document.querySelector("#state-filter-count").textContent = counts.state;
  document.querySelector("#federal-filter-count").textContent = counts.federal;

  document.querySelector("#coverage-exact-bar").style.width =
    `${percentOf(counts.exact, counts.jurisdictions)}%`;
  document.querySelector("#coverage-state-bar").style.width =
    `${percentOf(counts.state, counts.jurisdictions)}%`;
  document.querySelector("#coverage-federal-bar").style.width =
    `${percentOf(counts.federal, counts.jurisdictions)}%`;
}

function renderMap() {
  const visibleStates = getVisibleStates();
  selectFallbackState(visibleStates);
  const visibleCodes = new Set(visibleStates.map((item) => item.code));

  elements.tileMap.replaceChildren(
    ...state.data.states.map((item) => {
      const [row, column] = MAP_POSITIONS[item.code];
      const button = document.createElement("button");
      button.type = "button";
      button.className = [
        "state-tile",
        item.quality,
        item.code === state.selectedCode ? "selected" : "",
        visibleCodes.has(item.code) ? "" : "filtered-out",
      ]
        .filter(Boolean)
        .join(" ");
      button.style.gridRow = row;
      button.style.gridColumn = column;
      button.textContent = item.code;
      button.setAttribute(
        "aria-label",
        `${item.name}: ${item.qualityLabel}. Select to view details.`
      );
      button.setAttribute("aria-pressed", String(item.code === state.selectedCode));
      button.tabIndex = visibleCodes.has(item.code) ? 0 : -1;
      button.addEventListener("click", () => {
        state.selectedCode = item.code;
        renderExplorer();
      });
      return button;
    })
  );

  elements.visibleCount.textContent = `${visibleStates.length} shown`;
}

function renderBins(item) {
  if (!item.bins.length) {
    return `
      <p class="detail-note">
        A detailed performance-level split is not available in the source used for this state.
      </p>
    `;
  }

  return `
    <p class="detail-section-label">Published performance view</p>
    <div class="bin-list">
      ${item.bins
        .map(
          (bin) => `
            <div class="bin-row ${bin.isBelowBasicAnalog ? "is-analog" : ""}">
              <span class="bin-label" title="${escapeHtml(bin.label)}">${escapeHtml(bin.label)}</span>
              <span class="bin-track" aria-hidden="true">
                <span class="bin-fill" style="width: ${Math.min(Number(bin.value), 100)}%"></span>
              </span>
              <span class="bin-value">${formatNumber(bin.value)}%</span>
            </div>
          `
        )
        .join("")}
    </div>
  `;
}

function resultDescriptor(item) {
  if (item.quality === "exact") {
    return "Lowest state performance tier";
  }
  if (item.quality === "state") {
    return "State-published not-proficient analog";
  }
  return "Federal not-proficient proxy";
}

function renderDetail() {
  const item = state.data.states.find((candidate) => candidate.code === state.selectedCode);
  if (!item) {
    elements.detail.innerHTML = '<p class="detail-loading">Select a state to see details.</p>';
    return;
  }

  const sourcePageUrl = safeUrl(item.sourcePageUrl);
  const sourceUrl = safeUrl(item.sourceUrl);
  const showSecondSource = sourceUrl && sourceUrl !== sourcePageUrl;
  const nationalNaep = state.data.nationalNaepValue;
  const naepContext =
    item.naepValue === null || item.naepValue === undefined
      ? ""
      : `
        <div class="naep-context">
          <strong>${formatNumber(item.naepValue)}%</strong>
          <span>
            2024 NAEP Grade 4 Reading below Basic for ${escapeHtml(item.name)}.
            National public benchmark: ${formatNumber(nationalNaep)}%.
          </span>
        </div>
      `;

  elements.detail.innerHTML = `
    <div class="detail-topline">
      <p class="detail-code">${escapeHtml(item.code)} / UNITED STATES</p>
      <span class="quality-badge ${escapeHtml(item.quality)}">${escapeHtml(item.qualityShortLabel)}</span>
    </div>
    <h3>${escapeHtml(item.name)}</h3>
    <p class="detail-meta">${escapeHtml(item.assessment)} · ${escapeHtml(item.schoolYear)} · Grade 3 ELA</p>

    <div class="detail-result">
      <p class="detail-result-value">${formatNumber(item.analogValue)}<span>%</span></p>
      <p class="detail-result-label">
        <strong>${escapeHtml(resultDescriptor(item))}</strong>
        ${escapeHtml(item.analogLabel)}
      </p>
    </div>

    ${renderBins(item)}
    ${naepContext}

    <p class="detail-section-label">Source note</p>
    <p class="detail-note">${escapeHtml(item.sourceNotes)}</p>
    <div class="detail-links">
      ${
        sourcePageUrl
          ? `<a href="${escapeHtml(sourcePageUrl)}" target="_blank" rel="noopener noreferrer">Official source ↗</a>`
          : ""
      }
      ${
        showSecondSource
          ? `<a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">Source file ↗</a>`
          : ""
      }
    </div>
  `;
}

function compareStates(left, right) {
  const direction = state.sortDirection === "asc" ? 1 : -1;
  const key = state.sortKey;
  let leftValue = left[key];
  let rightValue = right[key];

  if (key === "quality") {
    leftValue = QUALITY_SORT[left.quality];
    rightValue = QUALITY_SORT[right.quality];
  }
  if (key === "analogValue") {
    leftValue = Number(leftValue ?? -1);
    rightValue = Number(rightValue ?? -1);
  }
  if (typeof leftValue === "string") {
    return leftValue.localeCompare(String(rightValue)) * direction;
  }
  return (leftValue - rightValue) * direction;
}

function renderTable() {
  const items = getVisibleStates().sort(compareStates);
  if (!items.length) {
    elements.tableBody.innerHTML = `
      <tr><td colspan="7" class="empty-row">No jurisdictions match this filter.</td></tr>
    `;
    return;
  }

  elements.tableBody.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td class="state-name-cell">
            <strong>${escapeHtml(item.name)}</strong>
            <span>${escapeHtml(item.code)}</span>
          </td>
          <td>
            <span class="table-quality ${escapeHtml(item.quality)}">${escapeHtml(item.qualityShortLabel)}</span>
          </td>
          <td class="assessment-cell">
            ${escapeHtml(item.assessment)}
            <span>Grade 3 ELA</span>
          </td>
          <td>${escapeHtml(item.schoolYear)}</td>
          <td>${escapeHtml(item.analogLabel)}</td>
          <td class="numeric result-cell">${formatNumber(item.analogValue)}%</td>
          <td>
            <button
              class="row-open-button"
              type="button"
              data-state-code="${escapeHtml(item.code)}"
              aria-label="Open ${escapeHtml(item.name)} details"
            >→</button>
          </td>
        </tr>
      `
    )
    .join("");

  elements.tableBody.querySelectorAll("[data-state-code]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedCode = button.dataset.stateCode;
      renderExplorer();
      elements.detail.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });
}

function renderExplorer() {
  renderMap();
  renderDetail();
  renderTable();
}

function renderDownloads() {
  elements.downloadGrid.innerHTML = state.data.downloads
    .map(
      (download) => `
        <a class="download-card" href="${escapeHtml(download.file)}" download>
          <span class="download-type">CSV dataset</span>
          <h3>${escapeHtml(download.label)}</h3>
          <p>${escapeHtml(download.description)}</p>
          <span class="download-arrow" aria-hidden="true">↓</span>
        </a>
      `
    )
    .join("");
}

function setFilter(nextFilter) {
  state.activeFilter = nextFilter;
  document.querySelectorAll("[data-filter]").forEach((button) => {
    const isActive = button.dataset.filter === nextFilter;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });
  renderExplorer();
}

function csvCell(value) {
  const text = String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

function downloadFilteredCsv() {
  const items = getVisibleStates().sort((left, right) => left.name.localeCompare(right.name));
  const rows = [
    [
      "state",
      "state_name",
      "data_quality",
      "assessment",
      "school_year",
      "reported_measure",
      "result_pct",
      "official_source",
    ],
    ...items.map((item) => [
      item.code,
      item.name,
      item.qualityLabel,
      item.assessment,
      item.schoolYear,
      item.analogLabel,
      item.analogValue,
      item.sourcePageUrl,
    ]),
  ];
  const csv = rows.map((row) => row.map(csvCell).join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `state-assessment-${state.activeFilter}-results.csv`;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
}

function bindEvents() {
  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => setFilter(button.dataset.filter));
  });

  elements.stateSearch.addEventListener("input", (event) => {
    state.searchTerm = event.target.value.trim().toLowerCase();
    renderExplorer();
  });

  document.querySelectorAll("[data-sort]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextKey = button.dataset.sort;
      if (state.sortKey === nextKey) {
        state.sortDirection = state.sortDirection === "asc" ? "desc" : "asc";
      } else {
        state.sortKey = nextKey;
        state.sortDirection = nextKey === "analogValue" ? "desc" : "asc";
      }
      renderTable();
    });
  });

  elements.downloadFiltered.addEventListener("click", downloadFilteredCsv);
}

function renderError(error) {
  const message = escapeHtml(error instanceof Error ? error.message : String(error));
  elements.detail.innerHTML = `
    <p class="detail-loading">The dashboard data could not be loaded.</p>
    <p class="detail-note">${message}</p>
  `;
  elements.tableBody.innerHTML = `
    <tr><td colspan="7" class="empty-row">Dashboard data unavailable.</td></tr>
  `;
  elements.downloadGrid.innerHTML =
    '<p class="download-loading">Download links are temporarily unavailable.</p>';
}

async function initialize() {
  try {
    const response = await fetch("data/dashboard.json");
    if (!response.ok) {
      throw new Error(`Dashboard data request failed with status ${response.status}.`);
    }
    state.data = await response.json();
    updateSummary();
    renderExplorer();
    renderDownloads();
    bindEvents();
  } catch (error) {
    renderError(error);
  }
}

initialize();
