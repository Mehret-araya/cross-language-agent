const form = document.querySelector("#analysis-form");
const analyzeButton = document.querySelector("#analyze-button");
const requestStatus = document.querySelector("#request-status");
const results = document.querySelector("#results");
const healthStatus = document.querySelector("#health-status");
const executeBilling = document.querySelector("#execute-billing");
const billingInputs = form.querySelectorAll(
  '[name="unit-price"], [name="quantity"]',
);

function syncBillingInputs() {
  for (const input of billingInputs) {
    input.disabled = !executeBilling.checked;
  }
}

function packageFromForm(formData, prefix) {
  const exports = formData
    .get(`${prefix}-exports`)
    .split(/[\n,]/)
    .map((name) => name.trim())
    .filter(Boolean);

  return {
    name: formData.get(`${prefix}-name`).trim(),
    language: formData.get(`${prefix}-language`).trim(),
    version: formData.get(`${prefix}-version`).trim(),
    runtime: formData.get(`${prefix}-runtime`).trim(),
    exports,
  };
}

function formatErrorDetail(detail) {
  if (typeof detail === "string") {
    return detail;
  }
  if (!Array.isArray(detail)) {
    return null;
  }

  const messages = detail.map((item) => {
    if (typeof item === "string") {
      return item;
    }
    if (!item || typeof item !== "object") {
      return "";
    }

    const message = typeof item.msg === "string"
      ? item.msg
      : "Invalid request.";
    const location = Array.isArray(item.loc)
      ? item.loc.filter((part) => part !== "body").join(".")
      : "";
    return location ? `${location}: ${message}` : message;
  }).filter(Boolean);

  return messages.length ? messages.join("; ") : null;
}

async function postJson(path, data) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  const payload = await response.json();

  if (!response.ok) {
    const detail = formatErrorDetail(payload.detail);
    throw new Error(detail || `Request failed (${response.status}).`);
  }
  return payload;
}

function createList(items) {
  const list = document.createElement("ul");
  for (const item of items) {
    const entry = document.createElement("li");
    entry.textContent = item;
    list.append(entry);
  }
  return list;
}

function createCard(title, content, wide = false) {
  const card = document.createElement("section");
  card.className = `result-card${wide ? " wide" : ""}`;
  const heading = document.createElement("div");
  heading.className = "result-title";
  heading.textContent = title;
  card.append(heading, content);
  return card;
}

function renderAnalysis(data) {
  results.replaceChildren();

  const analysisContent = document.createElement("div");
  const badge = document.createElement("span");
  badge.className = `badge${data.analysis.compatible ? "" : " review"}`;
  badge.textContent = data.analysis.compatible ? "Looks compatible" : "Needs review";
  const analysisHeading = document.createElement("div");
  analysisHeading.className = "result-title";
  analysisHeading.textContent = "Package analysis";
  analysisHeading.append(badge);
  const analysisCard = document.createElement("section");
  analysisCard.className = "result-card";
  analysisCard.append(analysisHeading);
  if (data.analysis.risks.length) {
    analysisCard.append(createList(data.analysis.risks));
  }
  if (data.analysis.evidence.length) {
    const evidence = document.createElement("p");
    evidence.textContent = data.analysis.evidence.join(" · ");
    analysisCard.append(evidence);
  }
  const nextStep = document.createElement("p");
  nextStep.textContent = `Next: ${data.analysis.recommended_next_step}`;
  analysisCard.append(nextStep);

  const strategyContent = document.createElement("div");
  const strategyName = document.createElement("p");
  strategyName.textContent = data.strategy.name;
  const strategyReason = document.createElement("p");
  strategyReason.textContent = data.strategy.reason;
  strategyContent.append(
    strategyName,
    strategyReason,
    createList(data.strategy.next_steps),
  );

  const planContent = document.createElement("div");
  const planSummary = document.createElement("p");
  planSummary.textContent =
    `${data.adapter_plan.source_package} → ${data.adapter_plan.target_package}`;
  planContent.append(
    planSummary,
    createList(data.adapter_plan.steps),
  );
  const requirementsTitle = document.createElement("p");
  requirementsTitle.textContent = "Test requirements";
  planContent.append(requirementsTitle, createList(data.adapter_plan.test_requirements));

  results.append(
    analysisCard,
    createCard("Recommended strategy", strategyContent),
    createCard("Adapter plan", planContent, true),
  );

  if (data.execution_example) {
    renderBillingResult(data.execution_example);
  }
  results.hidden = false;
}

function renderBillingResult(response) {
  const heading = document.createElement("div");
  heading.className = "result-title";
  heading.textContent = "Billing execution";
  const card = document.createElement("section");
  card.className = "result-card wide";
  card.append(heading);

  if (!response.ok) {
    const error = document.createElement("p");
    error.className = "billing-error";
    error.textContent = response.error || "Billing execution failed.";
    card.append(error);
  } else {
    const values = response.result;
    const summary = document.createElement("div");
    summary.className = "execution-result";
    for (const [label, value] of [
      ["Unit price", values.unit_price],
      ["Quantity", values.quantity],
      ["Total", values.total],
    ]) {
      const item = document.createElement("div");
      const itemLabel = document.createElement("span");
      itemLabel.textContent = label;
      const itemValue = document.createElement("strong");
      itemValue.textContent = value;
      item.append(itemLabel, itemValue);
      summary.append(item);
    }
    card.append(summary);
  }
  results.append(card);
}

async function checkHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) {
      throw new Error("API unavailable");
    }
    healthStatus.textContent = "API connected";
    healthStatus.dataset.state = "ok";
  } catch {
    healthStatus.textContent = "API unavailable";
    healthStatus.dataset.state = "error";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!form.reportValidity()) {
    return;
  }

  const formData = new FormData(form);
  const source = packageFromForm(formData, "source");
  const target = packageFromForm(formData, "target");
  requestStatus.textContent = "Analyzing packages…";
  requestStatus.dataset.state = "pending";
  results.hidden = true;
  results.replaceChildren();
  analyzeButton.disabled = true;

  try {
    const analysis = await postJson("/analyze-with-execution", {
      source,
      target,
    });
    renderAnalysis(analysis);
    requestStatus.textContent = "Analysis complete.";
    requestStatus.dataset.state = "ok";

    if (executeBilling.checked) {
      requestStatus.textContent = "Analysis complete. Running billing…";
      try {
        const billing = await postJson("/execute-billing-example", {
          unit_price: formData.get("unit-price").trim(),
          quantity: Number(formData.get("quantity")),
        });
        renderBillingResult(billing);
        requestStatus.textContent = "Analysis and billing complete.";
        requestStatus.dataset.state = "ok";
      } catch (error) {
        const card = document.createElement("section");
        card.className = "result-card wide";
        const heading = document.createElement("div");
        heading.className = "result-title";
        heading.textContent = "Billing execution";
        const message = document.createElement("p");
        message.className = "billing-error";
        message.textContent = error.message;
        card.append(heading, message);
        results.append(card);
        requestStatus.textContent = "Analysis complete; billing could not run.";
        requestStatus.dataset.state = "error";
      }
    }
  } catch (error) {
    requestStatus.textContent = error.message;
    requestStatus.dataset.state = "error";
  } finally {
    analyzeButton.disabled = false;
  }
});

executeBilling.addEventListener("change", syncBillingInputs);
syncBillingInputs();
checkHealth();
