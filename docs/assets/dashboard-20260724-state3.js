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
  activeView: "state",
  activeFilter: "all",
  searchTerm: "",
  selectedCode: "CO",
  sortKey: "name",
  sortDirection: "asc",
  naepFilter: "all",
  naepSearchTerm: "",
  naepSelectedCode: "CO",
  naepSortKey: "name",
  naepSortDirection: "asc",
};

const elements = {
  dashboardTabs: [...document.querySelectorAll("[data-dashboard-view]")],
  stateView: document.querySelector("#state-view"),
  naepView: document.querySelector("#naep-view"),
  stateNav: document.querySelector("#state-nav"),
  naepNav: document.querySelector("#naep-nav"),
  tileMap: document.querySelector("#tile-map"),
  detail: document.querySelector("#state-detail"),
  tableBody: document.querySelector("#state-table-body"),
  stateSearch: document.querySelector("#state-search"),
  visibleCount: document.querySelector("#visible-state-count"),
  downloadFiltered: document.querySelector("#download-filtered"),
  naepTileMap: document.querySelector("#naep-tile-map"),
  naepDetail: document.querySelector("#naep-detail"),
  naepTableBody: document.querySelector("#naep-table-body"),
  naepSearch: document.querySelector("#naep-search"),
  naepVisibleCount: document.querySelector("#naep-visible-state-count"),
  downloadNaepFiltered: document.querySelector("#download-naep-filtered"),
  downloadGrid: document.querySelector("#download-grid"),
  footerScope: document.querySelector("#footer-scope"),
  backToTop: document.querySelector("#back-to-top"),
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
  const number = Number(value);
  const factor = 10 ** digits;
  const rounded =
    Math.sign(number) * (Math.round((Math.abs(number) + Number.EPSILON) * factor) / factor);
  return rounded.toFixed(digits).replace(/\.0$/, "");
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

function formatSignedNumber(value, digits = 1) {
  const number = Number(value);
  if (Number.isNaN(number)) {
    return "Not available";
  }
  if (Math.abs(number) < 0.05) {
    return "0";
  }
  const prefix = number > 0 ? "+" : "";
  return `${prefix}${formatNumber(number, digits)}`;
}

function naepDifference(item) {
  return Number(item.naepValue) - Number(state.data.naep.nationalValue);
}

function naepFilterKey(item) {
  const difference = naepDifference(item);
  if (difference < -2) {
    return "lower";
  }
  if (difference > 2) {
    return "higher";
  }
  return "near";
}

function naepBand(value) {
  const number = Number(value);
  if (number < 35) {
    return "level-1";
  }
  if (number < 40) {
    return "level-2";
  }
  if (number < 45) {
    return "level-3";
  }
  if (number < 50) {
    return "level-4";
  }
  return "level-5";
}

function naepComparison(item) {
  const difference = naepDifference(item);
  if (Math.abs(difference) <= 2) {
    return {
      key: "near",
      label: "Near the U.S. benchmark",
      detail: `${formatSignedNumber(difference)} percentage points from the U.S.`,
    };
  }
  if (difference < 0) {
    return {
      key: "lower",
      label: "Lower share Below Basic",
      detail: `${formatNumber(Math.abs(difference))} percentage points below the U.S.`,
    };
  }
  return {
    key: "higher",
    label: "Higher share Below Basic",
    detail: `${formatNumber(difference)} percentage points above the U.S.`,
  };
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

function isNaepVisible(item) {
  if (item.naepValue === null || item.naepValue === undefined) {
    return false;
  }
  const matchesFilter =
    state.naepFilter === "all" || naepFilterKey(item) === state.naepFilter;
  const searchable = `${item.name} ${item.code}`.toLowerCase();
  return matchesFilter && searchable.includes(state.naepSearchTerm);
}

function getVisibleNaepStates() {
  return state.data.states.filter(isNaepVisible);
}

function selectFallbackState(visibleStates) {
  if (!visibleStates.length) {
    return;
  }
  if (!visibleStates.some((item) => item.code === state.selectedCode)) {
    state.selectedCode = visibleStates[0].code;
  }
}

function selectFallbackNaepState(visibleStates) {
  if (!visibleStates.length) {
    return;
  }
  if (!visibleStates.some((item) => item.code === state.naepSelectedCode)) {
    state.naepSelectedCode = visibleStates[0].code;
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
  document.querySelector("#federal-state-list").textContent = state.data.states
    .filter((item) => item.quality === "federal")
    .map((item) => item.name)
    .sort((a, b) => a.localeCompare(b))
    .join(" · ") || "None";
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

function updateNaepSummary() {
  const national = Number(state.data.naep.nationalValue);
  const statesWithNaep = state.data.states.filter(
    (item) => item.naepValue !== null && item.naepValue !== undefined
  );
  const filterCounts = {
    lower: statesWithNaep.filter((item) => naepFilterKey(item) === "lower").length,
    near: statesWithNaep.filter((item) => naepFilterKey(item) === "near").length,
    higher: statesWithNaep.filter((item) => naepFilterKey(item) === "higher").length,
  };

  document.querySelector("#naep-national-value").textContent = formatNumber(national);
  document.querySelector("#naep-jurisdiction-count").textContent = statesWithNaep.length;
  document.querySelector("#naep-below-national-count").textContent =
    statesWithNaep.filter((item) => Number(item.naepValue) < national).length;
  document.querySelector("#naep-above-national-count").textContent =
    statesWithNaep.filter((item) => Number(item.naepValue) > national).length;
  document.querySelector("#naep-all-filter-count").textContent = statesWithNaep.length;
  document.querySelector("#naep-lower-filter-count").textContent = filterCounts.lower;
  document.querySelector("#naep-near-filter-count").textContent = filterCounts.near;
  document.querySelector("#naep-higher-filter-count").textContent = filterCounts.higher;

  const officialSource = safeUrl(state.data.naep.sourcePageUrl);
  const officialSourceLink = document.querySelector("#naep-official-source");
  if (officialSource) {
    officialSourceLink.href = officialSource;
  }
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

function renderNaepMap() {
  const visibleStates = getVisibleNaepStates();
  selectFallbackNaepState(visibleStates);
  const visibleCodes = new Set(visibleStates.map((item) => item.code));

  elements.naepTileMap.replaceChildren(
    ...state.data.states.map((item) => {
      const [row, column] = MAP_POSITIONS[item.code];
      const button = document.createElement("button");
      const comparison = naepComparison(item);
      button.type = "button";
      button.className = [
        "state-tile",
        "naep-tile",
        naepBand(item.naepValue),
        item.code === state.naepSelectedCode ? "selected" : "",
        visibleCodes.has(item.code) ? "" : "filtered-out",
      ]
        .filter(Boolean)
        .join(" ");
      button.style.gridRow = row;
      button.style.gridColumn = column;
      button.textContent = item.code;
      button.title = `${item.name}: ${formatNumber(item.naepValue)}% Below Basic`;
      button.setAttribute(
        "aria-label",
        `${item.name}: ${formatNumber(item.naepValue)} percent Below Basic. ${comparison.detail} Select to view details.`
      );
      button.setAttribute("aria-pressed", String(item.code === state.naepSelectedCode));
      button.tabIndex = visibleCodes.has(item.code) ? 0 : -1;
      button.addEventListener("click", () => {
        state.naepSelectedCode = item.code;
        renderNaepExplorer();
      });
      return button;
    })
  );

  elements.naepVisibleCount.textContent = `${visibleStates.length} shown`;
}

function renderNaepDetail() {
  const item = state.data.states.find(
    (candidate) => candidate.code === state.naepSelectedCode
  );
  if (!item || item.naepValue === null || item.naepValue === undefined) {
    elements.naepDetail.innerHTML =
      '<p class="detail-loading">Select a jurisdiction to see NAEP details.</p>';
    return;
  }

  const national = Number(state.data.naep.nationalValue);
  const nationalBelowProficient = Number(
    state.data.naep.nationalBelowProficientValue
  );
  const comparison = naepComparison(item);
  const sourcePageUrl = safeUrl(state.data.naep.sourcePageUrl);

  elements.naepDetail.innerHTML = `
    <div class="detail-topline">
      <p class="detail-code">${escapeHtml(item.code)} / UNITED STATES</p>
      <span class="quality-badge naep">2024 NAEP</span>
    </div>
    <h3>${escapeHtml(item.name)}</h3>
    <p class="detail-meta">Grade 4 Reading · Public schools · Full achievement-level distribution</p>

    <div class="naep-key-metrics">
      <article class="naep-key-metric primary">
        <p>${formatNumber(item.naepValue)}<span>%</span></p>
        <div>
          <strong>Below NAEP Basic</strong>
          <span>U.S. public: ${formatNumber(national)}%</span>
        </div>
      </article>
      <article class="naep-key-metric">
        <p>${formatNumber(item.naepBelowProficientValue)}<span>%</span></p>
        <div>
          <strong>Below NAEP Proficient</strong>
          <span>Below Basic + Basic · U.S.: ${formatNumber(nationalBelowProficient)}%</span>
        </div>
      </article>
    </div>

    <p class="detail-section-label">Achievement-level breakdown</p>
    <div class="bin-list naep-level-list">
      ${item.naepLevels
        .map(
          (level) => `
            <div class="bin-row">
              <span class="bin-label" title="${escapeHtml(level.label)}">${escapeHtml(level.label)}</span>
              <span class="bin-track" aria-hidden="true">
                <span
                  class="bin-fill naep-level-fill ${escapeHtml(level.id)}"
                  style="width: ${Math.min(Number(level.value), 100)}%"
                ></span>
              </span>
              <span class="bin-value">${formatNumber(level.value)}%</span>
            </div>
          `
        )
        .join("")}
    </div>

    <div class="naep-comparison ${escapeHtml(comparison.key)}">
      <span class="naep-comparison-mark" aria-hidden="true"></span>
      <div>
        <strong>${escapeHtml(comparison.label)}</strong>
        <span>${escapeHtml(comparison.detail)}</span>
      </div>
    </div>

    <p class="detail-section-label">State and national comparison</p>
    <div class="naep-bar-list">
      <div class="naep-bar-row">
        <span>${escapeHtml(item.name)}</span>
        <span class="naep-bar-track" aria-hidden="true">
          <span class="naep-bar-fill state-value" style="width: ${Math.min(Number(item.naepValue), 100)}%"></span>
        </span>
        <strong>${formatNumber(item.naepValue)}%</strong>
      </div>
      <div class="naep-bar-row">
        <span>National public</span>
        <span class="naep-bar-track" aria-hidden="true">
          <span class="naep-bar-fill national-value" style="width: ${Math.min(national, 100)}%"></span>
        </span>
        <strong>${formatNumber(national)}%</strong>
      </div>
    </div>

    <p class="detail-section-label">Interpretation note</p>
    <p class="detail-note naep-detail-note">
      NAEP Proficient is not equivalent to a state’s grade-level proficiency standard.
      These are descriptive percentages from a representative sample; the dashboard does
      not test whether differences from the national result are statistically significant.
    </p>
    <div class="detail-links">
      ${
        sourcePageUrl
          ? `<a href="${escapeHtml(sourcePageUrl)}" target="_blank" rel="noopener noreferrer">Official NAEP source ↗</a>`
          : ""
      }
      <a href="${escapeHtml(state.data.naep.downloadFile)}" download>Download NAEP CSV ↓</a>
    </div>
  `;
}

function compareNaepStates(left, right) {
  const direction = state.naepSortDirection === "asc" ? 1 : -1;
  const key = state.naepSortKey;
  let leftValue = key === "naepDifference" ? naepDifference(left) : left[key];
  let rightValue = key === "naepDifference" ? naepDifference(right) : right[key];

  if (
    key === "naepValue" ||
    key === "naepBelowProficientValue" ||
    key === "naepDifference"
  ) {
    leftValue = Number(leftValue);
    rightValue = Number(rightValue);
  }
  if (typeof leftValue === "string") {
    return leftValue.localeCompare(String(rightValue)) * direction;
  }
  return (leftValue - rightValue) * direction;
}

function renderNaepTable() {
  const items = getVisibleNaepStates().sort(compareNaepStates);
  if (!items.length) {
    elements.naepTableBody.innerHTML = `
      <tr><td colspan="7" class="empty-row">No jurisdictions match this filter.</td></tr>
    `;
    return;
  }

  elements.naepTableBody.innerHTML = items
    .map((item) => {
      const difference = naepDifference(item);
      const comparison = naepComparison(item);
      return `
        <tr>
          <td class="state-name-cell">
            <strong>${escapeHtml(item.name)}</strong>
            <span>${escapeHtml(item.code)}</span>
          </td>
          <td class="numeric result-cell">${formatNumber(item.naepValue)}%</td>
          <td class="numeric result-cell">${formatNumber(item.naepBelowProficientValue)}%</td>
          <td class="numeric naep-difference ${escapeHtml(comparison.key)}">
            ${formatSignedNumber(difference)} pts
          </td>
          <td>
            <span class="naep-table-comparison ${escapeHtml(comparison.key)}">${escapeHtml(comparison.label)}</span>
          </td>
          <td class="assessment-cell">
            NAEP
            <span>2024 · Grade 4 Reading</span>
          </td>
          <td>
            <button
              class="row-open-button"
              type="button"
              data-naep-state-code="${escapeHtml(item.code)}"
              aria-label="Open ${escapeHtml(item.name)} NAEP details"
            >→</button>
          </td>
        </tr>
      `;
    })
    .join("");

  elements.naepTableBody.querySelectorAll("[data-naep-state-code]").forEach((button) => {
    button.addEventListener("click", () => {
      state.naepSelectedCode = button.dataset.naepStateCode;
      renderNaepExplorer();
      elements.naepDetail.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });
}

function renderNaepExplorer() {
  renderNaepMap();
  renderNaepDetail();
  renderNaepTable();
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

function setNaepFilter(nextFilter) {
  state.naepFilter = nextFilter;
  document.querySelectorAll("[data-naep-filter]").forEach((button) => {
    const isActive = button.dataset.naepFilter === nextFilter;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });
  renderNaepExplorer();
}

function viewFromLocation() {
  const params = new URLSearchParams(window.location.search);
  if (params.get("view") === "naep" || window.location.hash.startsWith("#naep")) {
    return "naep";
  }
  return "state";
}

function setDashboardView(nextView, updateUrl = true) {
  const nextIsNaep = nextView === "naep";
  state.activeView = nextIsNaep ? "naep" : "state";
  elements.stateView.hidden = nextIsNaep;
  elements.naepView.hidden = !nextIsNaep;
  elements.stateNav.hidden = nextIsNaep;
  elements.naepNav.hidden = !nextIsNaep;

  elements.dashboardTabs.forEach((tab) => {
    const isActive = tab.dataset.dashboardView === state.activeView;
    tab.classList.toggle("active", isActive);
    tab.setAttribute("aria-selected", String(isActive));
    tab.tabIndex = isActive ? 0 : -1;
  });

  document.title = nextIsNaep
    ? "NAEP Grade 4 Reading | State Assessment Data Monitor"
    : "State Assessment Data Monitor";
  elements.footerScope.textContent = nextIsNaep
    ? "50 states + DC · 2024 NAEP Grade 4 Reading · Achievement-level results"
    : "50 states + DC · Grade 3 ELA · Source quality shown throughout";
  elements.backToTop.href = nextIsNaep ? "#naep-top" : "#top";
  if (updateUrl) {
    const url = new URL(window.location.href);
    url.hash = "";
    if (nextIsNaep) {
      url.searchParams.set("view", "naep");
    } else {
      url.searchParams.delete("view");
    }
    window.history.replaceState(null, "", `${url.pathname}${url.search}`);
    document.querySelector(".dashboard-tabs").scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }
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

function downloadFilteredNaepCsv() {
  const national = Number(state.data.naep.nationalValue);
  const nationalBelowProficient = Number(
    state.data.naep.nationalBelowProficientValue
  );
  const nationalLevels = Object.fromEntries(
    state.data.naep.nationalLevels.map((level) => [level.id, level.value])
  );
  const items = getVisibleNaepStates().sort((left, right) =>
    left.name.localeCompare(right.name)
  );
  const rows = [
    [
      "state",
      "state_name",
      "year",
      "grade",
      "subject",
      "state_below_basic_pct",
      "state_basic_pct",
      "state_proficient_pct",
      "state_advanced_pct",
      "state_below_proficient_pct",
      "national_public_below_basic_pct",
      "national_public_basic_pct",
      "national_public_proficient_pct",
      "national_public_advanced_pct",
      "national_public_below_proficient_pct",
      "below_basic_difference_from_national_percentage_points",
      "comparison",
      "official_source",
    ],
    ...items.map((item) => {
      const levels = Object.fromEntries(
        item.naepLevels.map((level) => [level.id, level.value])
      );
      return [
        item.code,
        item.name,
        state.data.naep.year,
        state.data.naep.grade,
        state.data.naep.subject,
        levels.below_basic,
        levels.basic,
        levels.proficient,
        levels.advanced,
        item.naepBelowProficientValue,
        nationalLevels.below_basic,
        nationalLevels.basic,
        nationalLevels.proficient,
        nationalLevels.advanced,
        nationalBelowProficient,
        Number(naepDifference(item).toFixed(2)),
        naepComparison(item).label,
        state.data.naep.sourcePageUrl,
      ];
    }),
  ];
  const csv = rows.map((row) => row.map(csvCell).join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `naep-2024-grade4-reading-${state.naepFilter}-results.csv`;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
}

function bindEvents() {
  elements.dashboardTabs.forEach((tab, index) => {
    tab.addEventListener("click", () => {
      setDashboardView(tab.dataset.dashboardView);
    });
    tab.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) {
        return;
      }
      event.preventDefault();
      let nextIndex = index;
      if (event.key === "ArrowLeft") {
        nextIndex = (index - 1 + elements.dashboardTabs.length) % elements.dashboardTabs.length;
      } else if (event.key === "ArrowRight") {
        nextIndex = (index + 1) % elements.dashboardTabs.length;
      } else if (event.key === "Home") {
        nextIndex = 0;
      } else if (event.key === "End") {
        nextIndex = elements.dashboardTabs.length - 1;
      }
      const nextTab = elements.dashboardTabs[nextIndex];
      nextTab.focus();
      setDashboardView(nextTab.dataset.dashboardView);
    });
  });

  document.querySelector(".brand").addEventListener("click", (event) => {
    event.preventDefault();
    setDashboardView("state");
  });

  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => setFilter(button.dataset.filter));
  });

  document.querySelectorAll("[data-naep-filter]").forEach((button) => {
    button.addEventListener("click", () => setNaepFilter(button.dataset.naepFilter));
  });

  elements.stateSearch.addEventListener("input", (event) => {
    state.searchTerm = event.target.value.trim().toLowerCase();
    renderExplorer();
  });

  elements.naepSearch.addEventListener("input", (event) => {
    state.naepSearchTerm = event.target.value.trim().toLowerCase();
    renderNaepExplorer();
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

  document.querySelectorAll("[data-naep-sort]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextKey = button.dataset.naepSort;
      if (state.naepSortKey === nextKey) {
        state.naepSortDirection = state.naepSortDirection === "asc" ? "desc" : "asc";
      } else {
        state.naepSortKey = nextKey;
        state.naepSortDirection = nextKey === "name" ? "asc" : "desc";
      }
      renderNaepTable();
    });
  });

  elements.downloadFiltered.addEventListener("click", downloadFilteredCsv);
  elements.downloadNaepFiltered.addEventListener("click", downloadFilteredNaepCsv);

  window.addEventListener("hashchange", () => {
    const nextView = viewFromLocation();
    if (nextView !== state.activeView) {
      setDashboardView(nextView, false);
    }
  });
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
  elements.naepDetail.innerHTML = `
    <p class="detail-loading">The NAEP data could not be loaded.</p>
    <p class="detail-note">${message}</p>
  `;
  elements.naepTableBody.innerHTML = `
    <tr><td colspan="7" class="empty-row">NAEP data unavailable.</td></tr>
  `;
  elements.downloadGrid.innerHTML =
    '<p class="download-loading">Download links are temporarily unavailable.</p>';
}

async function initialize() {
  try {
    const response = await fetch("data/dashboard-20260724-state3.json");
    if (!response.ok) {
      throw new Error(`Dashboard data request failed with status ${response.status}.`);
    }
    state.data = await response.json();
    if (
      !state.data.naep ||
      state.data.naep.jurisdictions !== 51 ||
      state.data.naep.nationalLevels?.length !== 4 ||
      state.data.naep.nationalBelowProficientValue === null ||
      state.data.naep.nationalBelowProficientValue === undefined ||
      state.data.states.some(
        (item) =>
          item.naepValue === null ||
          item.naepValue === undefined ||
          item.naepBelowProficientValue === null ||
          item.naepBelowProficientValue === undefined ||
          item.naepLevels?.length !== 4
      )
    ) {
      throw new Error("The NAEP data bundle is incomplete.");
    }
    updateSummary();
    updateNaepSummary();
    renderExplorer();
    renderNaepExplorer();
    renderDownloads();
    bindEvents();
    const initialView = viewFromLocation();
    setDashboardView(initialView, false);
  } catch (error) {
    renderError(error);
  }
}

initialize();
