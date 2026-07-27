import { execFileSync } from "node:child_process";

import { selectReadyIssues } from "./ready-issues.mjs";

function executeGhJson(args, cwd) {
  return JSON.parse(
    execFileSync("gh", args, {
      cwd,
      encoding: "utf8",
      maxBuffer: 64 * 1024 * 1024,
    })
  );
}

function loadNativeParents(issueNumbers, cwd, gh) {
  if (issueNumbers.length === 0) return new Map();

  const { nameWithOwner } = gh(
    ["repo", "view", "--json", "nameWithOwner"],
    cwd
  );
  const [owner, name] = nameWithOwner.split("/");
  const parents = new Map();
  for (let offset = 0; offset < issueNumbers.length; offset += 50) {
    const batch = issueNumbers.slice(offset, offset + 50);
    const fields = batch
      .map(
        (number) =>
          `i${number}: issue(number: ${number}) { parent { number labels(first: 20) { nodes { name } } } }`
      )
      .join("\n");
    const query = `query($owner: String!, $name: String!) { repository(owner: $owner, name: $name) { ${fields} } }`;
    const response = gh(
      [
        "api",
        "graphql",
        "-f",
        `query=${query}`,
        "-F",
        `owner=${owner}`,
        "-F",
        `name=${name}`,
      ],
      cwd
    );
    const repository = response.data?.repository ?? {};

    for (const number of batch) {
      const parent = repository[`i${number}`]?.parent;
      parents.set(
        number,
        parent
          ? {
              number: parent.number,
              labels: parent.labels.nodes,
            }
          : null
      );
    }
  }

  return parents;
}

export function loadReadyFrontier(cwd, gh = executeGhJson) {
  const candidates = gh(
    [
      "issue",
      "list",
      "--state",
      "open",
      "--label",
      "ready-for-agent",
      "--limit",
      "1000",
      "--json",
      "number,title,body,labels,assignees,state,comments",
    ],
    cwd
  );
  const knownIssues = gh(
    [
      "issue",
      "list",
      "--state",
      "all",
      "--limit",
      "1000",
      "--json",
      "number,state",
    ],
    cwd
  );
  const parents = loadNativeParents(
    candidates.map((issue) => Number(issue.number)),
    cwd,
    gh
  );
  const children = candidates.map((issue) => ({
    ...issue,
    parent: parents.get(Number(issue.number)),
  }));

  return selectReadyIssues(children, knownIssues);
}
