export function parseBlockingIssueNumbers(body) {
  const firstLine = String(body ?? "")
    .split("\n")
    .find((line) => line.trim().length > 0);
  const match = /^Blocked by:\s*(.+)$/i.exec(firstLine ?? "");

  if (!match) return { valid: false, issueNumbers: [] };

  const value = match[1].trim();
  if (/^none$/i.test(value)) return { valid: true, issueNumbers: [] };

  const references = value.split(",").map((reference) => reference.trim());
  if (references.length === 0) return { valid: false, issueNumbers: [] };

  const issueNumbers = [];
  for (const reference of references) {
    const referenceMatch = /^#([1-9]\d*)$/.exec(reference);
    if (!referenceMatch) return { valid: false, issueNumbers: [] };
    issueNumbers.push(Number.parseInt(referenceMatch[1], 10));
  }

  if (new Set(issueNumbers).size !== issueNumbers.length) {
    return { valid: false, issueNumbers: [] };
  }

  return { valid: true, issueNumbers };
}

const WAYFINDER_DECISION_LABELS = new Set([
  "wayfinder:research",
  "wayfinder:prototype",
  "wayfinder:grilling",
  "wayfinder:task",
]);

export function selectReadyIssues(issues, knownIssues = issues) {
  const statesByNumber = new Map(
    knownIssues.map((issue) => [Number(issue.number), issue.state])
  );

  return issues
    .filter((issue) => {
      if (issue.state && issue.state.toUpperCase() !== "OPEN") return false;
      if ((issue.assignees ?? []).length > 0) return false;

      const labels = new Set(
        (issue.labels ?? []).map((label) =>
          typeof label === "string" ? label : label.name
        )
      );
      const isWayfinderDecision = [...labels].some((label) =>
        WAYFINDER_DECISION_LABELS.has(label)
      );
      const parentLabels = new Set(
        (issue.parent?.labels ?? []).map((label) =>
          typeof label === "string" ? label : label.name
        )
      );
      const isWayfinderChild =
        Number.isInteger(Number(issue.parent?.number)) &&
        parentLabels.has("wayfinder:map");

      const blocking = parseBlockingIssueNumbers(issue.body);
      const hasOpenOrUnknownBlocker = blocking.issueNumbers.some((number) => {
        const state = statesByNumber.get(number);
        return !state || state.toUpperCase() !== "CLOSED";
      });

      return (
        labels.has("ready-for-agent") &&
        isWayfinderDecision &&
        isWayfinderChild &&
        !labels.has("ready-for-human") &&
        !labels.has("needs-info") &&
        !labels.has("needs-triage") &&
        !labels.has("wayfinder:grilling") &&
        !labels.has("wayfinder:prototype") &&
        blocking.valid &&
        !hasOpenOrUnknownBlocker
      );
    })
    .sort((left, right) => Number(left.number) - Number(right.number));
}

export function boundedPositiveInteger(value, fallback, maximum, name) {
  const parsed = Number.parseInt(value ?? String(fallback), 10);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > maximum) {
    throw new Error(`${name} must be an integer between 1 and ${maximum}`);
  }
  return parsed;
}
