export function selectReadyIssues(issues) {
  return issues.filter((issue) => {
    if (issue.state && issue.state.toUpperCase() !== "OPEN") return false;
    if ((issue.assignees ?? []).length > 0) return false;

    const labels = new Set(
      (issue.labels ?? []).map((label) =>
        typeof label === "string" ? label : label.name
      )
    );

    return (
      labels.has("ready-for-agent") &&
      !labels.has("ready-for-human") &&
      !labels.has("needs-info") &&
      !labels.has("needs-triage") &&
      !labels.has("wayfinder:grilling") &&
      !labels.has("wayfinder:prototype")
    );
  });
}

export function boundedPositiveInteger(value, fallback, maximum, name) {
  const parsed = Number.parseInt(value ?? String(fallback), 10);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > maximum) {
    throw new Error(`${name} must be an integer between 1 and ${maximum}`);
  }
  return parsed;
}
