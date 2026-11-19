const fileInput = document.getElementById("audioFile");
const analyzeBtn = document.getElementById("analyzeBtn");
const fileMeta = document.getElementById("fileMeta");
const statusBox = document.getElementById("status");
const resultsBox = document.getElementById("results");
let selectedFile = null;

fileInput.addEventListener("change", () => {
  selectedFile = fileInput.files[0] || null;
  resultsBox.hidden = true;
  statusBox.textContent = "";
  analyzeBtn.disabled = !selectedFile;
  fileMeta.textContent = selectedFile
    ? `${selectedFile.name} · ${(selectedFile.size / 1024 / 1024).toFixed(2)} MB`
    : "WAV, FLAC, OGG or AIFF · Up to 25 MB · Maximum 120 seconds";
});

analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) return;
  const data = new FormData();
  data.append("audio", selectedFile);
  analyzeBtn.disabled = true;
  statusBox.textContent = "Analyzing audio… the first request may take a few minutes while the AI model loads.";
  resultsBox.hidden = true;
  try {
    const response = await fetch("/api/classify", { method: "POST", body: data });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Analysis failed.");
    resultsBox.innerHTML = "";
    const heading = document.createElement("h4");
    heading.textContent = "Top sound predictions";
    resultsBox.appendChild(heading);
    payload.results.forEach(item => {
      const row = document.createElement("div");
      row.className = "result-row";
      const left = document.createElement("div");
      const label = document.createElement("div");
      label.textContent = item.label;
      const bar = document.createElement("div");
      bar.className = "bar";
      const fill = document.createElement("i");
      fill.style.width = `${Math.min(100, item.confidence)}%`;
      bar.appendChild(fill);
      left.append(label, bar);
      const score = document.createElement("div");
      score.className = "confidence";
      score.textContent = `${item.confidence.toFixed(2)}%`;
      row.append(left, score);
      resultsBox.appendChild(row);
    });
    const note = document.createElement("p");
    note.className = "result-note";
    note.textContent = `${payload.model}. ${payload.note}`;
    resultsBox.appendChild(note);
    resultsBox.hidden = false;
    statusBox.textContent = payload.wildlife_related
      ? "Wildlife-related sound categories appear among the leading predictions."
      : "Analysis complete. No obvious wildlife category appeared in the leading predictions.";
  } catch (error) {
    statusBox.textContent = error.message;
  } finally {
    analyzeBtn.disabled = !selectedFile;
  }
});
