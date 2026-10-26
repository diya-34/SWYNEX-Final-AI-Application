/**
 * SWYNEX Final AI Application - Student Announcement Intelligence System
 * Client-Side Application Logic (Vanilla JavaScript)
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  const announcementText = document.getElementById("announcementText");
  const charCounter = document.getElementById("charCounter");
  const sampleDropdown = document.getElementById("sampleDropdown");
  const btnLoadPreset = document.getElementById("btnLoadPreset");
  const analyzeForm = document.getElementById("analyzeForm");
  const btnAnalyze = document.getElementById("btnAnalyze");
  const btnClear = document.getElementById("btnClear");

  const validationAlert = document.getElementById("validationAlert");
  const warningAlert = document.getElementById("warningAlert");

  // KPI Elements
  const kpiCategory = document.getElementById("kpiCategory");
  const kpiConfidence = document.getElementById("kpiConfidence");
  const kpiPriority = document.getElementById("kpiPriority");
  const kpiScore = document.getElementById("kpiScore");
  const kpiDeadline = document.getElementById("kpiDeadline");
  const kpiDeadlineCount = document.getElementById("kpiDeadlineCount");
  const kpiDate = document.getElementById("kpiDate");
  const kpiDateCount = document.getElementById("kpiDateCount");
  const execTimeBadge = document.getElementById("execTimeBadge");

  // Insight Details Elements
  const probabilityBars = document.getElementById("probabilityBars");
  const methodExplanation = document.getElementById("methodExplanation");
  const priorityReasonBox = document.getElementById("priorityReasonBox");
  const priorityReasonTitle = document.getElementById("priorityReasonTitle");
  const priorityReasonText = document.getElementById("priorityReasonText");
  const priorityActionText = document.getElementById("priorityActionText");
  const urgencyFactorsList = document.getElementById("urgencyFactorsList");

  const extractedDates = document.getElementById("extractedDates");
  const extractedDeadlines = document.getElementById("extractedDeadlines");
  const extractedUrls = document.getElementById("extractedUrls");
  const extractedEmails = document.getElementById("extractedEmails");
  const extractedTags = document.getElementById("extractedTags");

  const summaryText = document.getElementById("summaryText");
  const sumOrigChars = document.getElementById("sumOrigChars");
  const sumNewChars = document.getElementById("sumNewChars");
  const sumRatio = document.getElementById("sumRatio");

  // Evaluation Elements
  const btnRunEval = document.getElementById("btnRunEval");
  const evalCatAcc = document.getElementById("evalCatAcc");
  const evalStdAcc = document.getElementById("evalStdAcc");
  const evalPrioAcc = document.getElementById("evalPrioAcc");
  const evalF1 = document.getElementById("evalF1");
  const evalTableBody = document.getElementById("evalTableBody");
  const demoCasesGrid = document.getElementById("demoCasesGrid");

  let sampleDataCache = null;

  // ---------------------------------------------------------------------------
  // 1. Tab Navigation
  // ---------------------------------------------------------------------------
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add("active");
      }

      // Auto load demo cases if opening demo tab
      if (targetId === "demo-tab" && demoCasesGrid.children.length === 0) {
        loadDemoCases();
      }
      // Auto load eval cases if opening eval tab
      if (targetId === "eval-tab" && evalTableBody.children.length <= 1) {
        loadEvaluationData();
      }
    });
  });

  // ---------------------------------------------------------------------------
  // 2. Character & Word Counter
  // ---------------------------------------------------------------------------
  function updateCounters() {
    const text = announcementText.value || "";
    const chars = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    charCounter.textContent = `${chars} chars | ${words} words`;
  }
  announcementText.addEventListener("input", updateCounters);
  updateCounters();

  // ---------------------------------------------------------------------------
  // 3. Preset Sample Loader
  // ---------------------------------------------------------------------------
  async function fetchSamples() {
    if (!sampleDataCache) {
      try {
        const res = await fetch("/api/samples");
        sampleDataCache = await res.json();
      } catch (e) {
        console.error("Failed to load sample announcements", e);
      }
    }
    return sampleDataCache;
  }

  btnLoadPreset.addEventListener("click", async () => {
    const samples = await fetchSamples();
    const key = sampleDropdown.value;
    if (samples && samples[key]) {
      announcementText.value = samples[key].text;
      updateCounters();
      triggerAnalysis();
    }
  });

  btnClear.addEventListener("click", () => {
    announcementText.value = "";
    updateCounters();
    validationAlert.style.display = "none";
    warningAlert.style.display = "none";
  });

  // ---------------------------------------------------------------------------
  // 4. Analysis Submission
  // ---------------------------------------------------------------------------
  analyzeForm.addEventListener("submit", (e) => {
    e.preventDefault();
    triggerAnalysis();
  });

  async function triggerAnalysis() {
    const text = announcementText.value;
    validationAlert.style.display = "none";
    warningAlert.style.display = "none";

    const btnText = btnAnalyze.querySelector(".btn-text");
    const spinner = btnAnalyze.querySelector(".spinner");
    btnText.textContent = "Analyzing...";
    btnAnalyze.disabled = true;

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
      });
      const data = await response.json();

      if (!data.success) {
        validationAlert.textContent = "❌ " + data.error;
        validationAlert.style.display = "block";
        execTimeBadge.textContent = "Error";
        execTimeBadge.className = "badge badge-match-no";
        return;
      }

      if (data.warning) {
        warningAlert.textContent = "⚠️ " + data.warning;
        warningAlert.style.display = "block";
      }

      renderResults(data);
    } catch (err) {
      validationAlert.textContent = "❌ Network or Server Error: " + err.message;
      validationAlert.style.display = "block";
    } finally {
      btnText.textContent = "🚀 Analyze Announcement";
      btnAnalyze.disabled = false;
    }
  }

  // ---------------------------------------------------------------------------
  // 5. Render Results to DOM
  // ---------------------------------------------------------------------------
  function renderResults(res) {
    const clf = res.classification;
    const prio = res.priority;
    const ext = res.extraction;
    const summ = res.summary;

    execTimeBadge.textContent = `${res.execution_time_ms} ms`;
    execTimeBadge.className = "badge badge-neutral";

    // KPI 1: Category
    const cat = clf.category;
    kpiCategory.innerHTML = `<span class="tag tag-${cat.toLowerCase()}">${cat}</span>`;
    kpiConfidence.innerHTML = `Confidence: <b>${(clf.confidence * 100).toFixed(1)}%</b>`;

    // KPI 2: Priority
    const pName = prio.priority;
    kpiPriority.innerHTML = `<span class="priority-pill priority-${pName.toLowerCase()}">${pName}</span>`;
    kpiScore.innerHTML = `Score: <b>${prio.score}/100</b>`;

    // KPI 3: Deadline
    if (ext.has_deadline && ext.deadlines.length > 0) {
      kpiDeadline.innerHTML = `<span class="deadline-highlight">${escapeHtml(ext.deadlines[0])}</span>`;
      kpiDeadlineCount.textContent = `${ext.deadlines.length} cutoff deadline(s)`;
    } else {
      kpiDeadline.innerHTML = `<span class="text-muted">None detected</span>`;
      kpiDeadlineCount.textContent = "No strict deadline";
    }

    // KPI 4: Date
    if (ext.has_date && ext.dates.length > 0) {
      kpiDate.innerHTML = escapeHtml(ext.dates[0]);
      kpiDateCount.textContent = `${ext.dates.length} date reference(s)`;
    } else {
      kpiDate.innerHTML = `<span class="text-muted">No date found</span>`;
      kpiDateCount.textContent = "Check official notices";
    }

    // Probability Bars
    probabilityBars.innerHTML = "";
    const probs = clf.probabilities || {};
    const sortedCats = Object.keys(probs).sort((a, b) => probs[b] - probs[a]);

    sortedCats.forEach(c => {
      const pVal = (probs[c] * 100).toFixed(1);
      const row = document.createElement("div");
      row.className = "prob-row";
      row.innerHTML = `
        <div class="prob-header">
          <span>${c}</span>
          <span>${pVal}%</span>
        </div>
        <div class="prob-track">
          <div class="prob-fill" style="width: ${pVal}%;"></div>
        </div>
      `;
      probabilityBars.appendChild(row);
    });

    // Method & Explanation
    methodExplanation.innerHTML = `
      <strong>Method:</strong> <code>${escapeHtml(clf.method)}</code><br>
      <strong>Justification:</strong> ${escapeHtml(clf.explanation)}
    `;

    // Priority Reason
    priorityReasonTitle.textContent = `${prio.priority} Priority (${prio.score}/100):`;
    priorityReasonText.textContent = prio.reason;
    priorityActionText.textContent = prio.recommended_action;

    urgencyFactorsList.innerHTML = "";
    if (prio.urgency_factors && prio.urgency_factors.length > 0) {
      prio.urgency_factors.forEach(f => {
        const li = document.createElement("li");
        li.textContent = f;
        urgencyFactorsList.appendChild(li);
      });
    }

    // Entities
    renderChips(extractedDates, ext.dates, "📅 ", "chip", ext.status_messages.dates);
    renderChips(extractedDeadlines, ext.deadlines, "⏰ ", "chip chip-deadline", "No strict deadline detected");

    // URLs
    extractedUrls.innerHTML = "";
    if (ext.urls && ext.urls.length > 0) {
      ext.urls.forEach(u => {
        const link = document.createElement("a");
        link.className = "chip chip-link";
        link.target = "_blank";
        link.href = u.startsWith("http") ? u : "https://" + u;
        link.textContent = "🔗 " + u;
        extractedUrls.appendChild(link);
      });
    } else {
      extractedUrls.innerHTML = `<span class="text-muted">${ext.status_messages.urls}</span>`;
    }

    // Emails
    extractedEmails.innerHTML = "";
    if (ext.emails && ext.emails.length > 0) {
      ext.emails.forEach(e => {
        const link = document.createElement("a");
        link.className = "chip chip-link";
        link.href = "mailto:" + e;
        link.textContent = "✉️ " + e;
        extractedEmails.appendChild(link);
      });
    } else {
      extractedEmails.innerHTML = `<span class="text-muted">${ext.status_messages.emails}</span>`;
    }

    // Action Tags
    renderChips(extractedTags, ext.keywords, "🏷️ ", "chip chip-tag", "No action tags detected");

    // Summary
    summaryText.textContent = `"${summ.summary}"`;
    sumOrigChars.textContent = `Original: ${summ.original_chars} chars`;
    sumNewChars.textContent = `Summary: ${summ.summary_chars} chars`;
    sumRatio.textContent = `Reduction: ${summ.compression_ratio}`;
  }

  function renderChips(container, items, icon, chipClass, emptyMsg) {
    container.innerHTML = "";
    if (items && items.length > 0) {
      items.forEach(it => {
        const sp = document.createElement("span");
        sp.className = chipClass;
        sp.textContent = icon + it;
        container.appendChild(sp);
      });
    } else {
      container.innerHTML = `<span class="text-muted">${escapeHtml(emptyMsg)}</span>`;
    }
  }

  // ---------------------------------------------------------------------------
  // 6. Demo & Test Cases Loader
  // ---------------------------------------------------------------------------
  async function loadDemoCases() {
    demoCasesGrid.innerHTML = "<p>Loading demo cases...</p>";
    try {
      const res = await fetch("/api/evaluate");
      const data = await res.json();
      if (!data.success) return;

      demoCasesGrid.innerHTML = "";
      data.cases.forEach(item => {
        const isEdge = item.is_edge_case;
        const card = document.createElement("div");
        card.className = "demo-card";
        card.innerHTML = `
          <div>
            <div class="demo-card-header">
              <span class="badge ${isEdge ? 'badge-match-no' : 'badge-primary'}">${item.id} • ${item.input_type.toUpperCase()}</span>
              <span class="tag tag-${item.expected_category.toLowerCase()}">${item.expected_category}</span>
            </div>
            <div class="demo-card-title">${escapeHtml(item.description)}</div>
            <div class="demo-card-text">${escapeHtml(item.summary_snippet || 'Empty')}</div>
            <div class="demo-card-meta">
              Expected Priority: <b>${item.expected_priority}</b> | Deadline: <b>${item.expected_deadline}</b>
            </div>
          </div>
          <button class="btn btn-outline btn-sm btn-test-case" style="width:100%; margin-top:0.5rem;">⚡ Load & Analyze This</button>
        `;

        const btnTest = card.querySelector(".btn-test-case");
        btnTest.addEventListener("click", () => {
          // Switch to analyzer tab and set text
          const analyzerTabBtn = document.getElementById("btn-tab-analyzer");
          analyzerTabBtn.click();
          announcementText.value = item.text || item.description;
          updateCounters();
          triggerAnalysis();
        });

        demoCasesGrid.appendChild(card);
      });
    } catch (e) {
      demoCasesGrid.innerHTML = "<p class='text-muted'>Failed to load demo cases.</p>";
    }
  }

  // ---------------------------------------------------------------------------
  // 7. Empirical Evaluation Loader
  // ---------------------------------------------------------------------------
  async function loadEvaluationData() {
    evalTableBody.innerHTML = "<tr><td colspan='8' style='text-align:center;'>Running live benchmark...</td></tr>";
    try {
      const res = await fetch("/api/evaluate");
      const data = await res.json();
      if (!data.success) {
        evalTableBody.innerHTML = `<tr><td colspan='8' style='color:red;'>Evaluation error: ${data.error}</td></tr>`;
        return;
      }

      evalCatAcc.textContent = `${data.category_accuracy}%`;
      evalStdAcc.textContent = `${data.standard_category_accuracy}%`;
      evalPrioAcc.textContent = `${data.priority_accuracy}%`;
      evalF1.textContent = `${data.weighted_f1}%`;

      evalTableBody.innerHTML = "";
      data.cases.forEach(c => {
        const row = document.createElement("tr");
        const catMatchBadge = c.category_match
          ? `<span class="badge-match-yes">YES</span>`
          : `<span class="badge-match-no">NO</span>`;
        const dlMatchBadge = c.deadline_match
          ? `<span class="badge-match-yes">YES</span>`
          : `<span class="badge-match-no">NO</span>`;

        row.innerHTML = `
          <td><strong>${c.id}</strong></td>
          <td>${escapeHtml(c.description)}</td>
          <td><span class="tag tag-${c.expected_category.toLowerCase()}">${c.expected_category}</span></td>
          <td><span class="tag tag-${c.predicted_category.toLowerCase()}">${c.predicted_category}</span></td>
          <td>${catMatchBadge}</td>
          <td>${c.expected_priority}</td>
          <td>${c.predicted_priority}</td>
          <td>${dlMatchBadge}</td>
        `;
        evalTableBody.appendChild(row);
      });
    } catch (err) {
      evalTableBody.innerHTML = `<tr><td colspan='8' style='color:red;'>Evaluation fetch failed: ${err.message}</td></tr>`;
    }
  }

  btnRunEval.addEventListener("click", () => {
    loadEvaluationData();
  });

  // Helper
  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Trigger initial analysis on page load
  triggerAnalysis();
});
