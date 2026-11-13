const byId = id => document.getElementById(id);
const make = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
};
byId("search").addEventListener("submit", async event => {
  event.preventDefault();
  const query = byId("query").value.trim();
  if (!query) return;
  const button = event.currentTarget.querySelector("button");
  button.disabled = true;
  byId("state").textContent = "Checking the pinned source…";
  byId("result").hidden = true;
  try {
    const response = await fetch("/api/ask", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question: query})
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error);
    const answered = result.status === "answered";
    byId("badge").textContent = answered ? "Cited answer" : "Feature not found";
    byId("badge").dataset.status = result.status;
    byId("commit").textContent = "Snapshot " + result.snapshot_commit.slice(0, 10);
    byId("answer").replaceChildren(...result.answer.split("\n\n").map(text => make("p", text)));
    byId("scope").textContent = result.limitations.join(" ") + (answered ? " Evidence rating: " + result.confidence_score : "");
    const sources = byId("sources");
    sources.replaceChildren();
    if (result.citations.length) {
      sources.append(make("h3", "Source citations"));
      for (const citation of result.citations) {
        const card = make("details");
        const location = citation.start_line === citation.end_line
          ? String(citation.start_line) : citation.start_line + "–" + citation.end_line;
        card.append(make("summary", citation.id + "  ·  " + citation.file_path + ":" + location));
        const code = make("pre", undefined, "snippet");
        citation.code_snippet.split("\n").forEach((line, index) => {
          const row = make("span", undefined, "highlight");
          row.append(make("span", String(citation.start_line + index), "line"), document.createTextNode(line));
          code.append(row, document.createTextNode("\n"));
        });
        card.append(code);
        sources.append(card);
      }
    }
    byId("result").hidden = false;
    byId("state").textContent = "";
  } catch (error) {
    byId("state").textContent = error.message || "Could not load the answer.";
  } finally {
    button.disabled = false;
  }
});
