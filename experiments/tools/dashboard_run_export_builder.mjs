import fs from "node:fs/promises";
import path from "node:path";
import { Workbook, SpreadsheetFile } from "/Users/aseesanwar/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const [, , inputPath, outputPath] = process.argv;

if (!inputPath || !outputPath) {
  console.error("Usage: node dashboard_run_export_builder.mjs <input.json> <output.xlsx>");
  process.exit(1);
}

const payload = JSON.parse(await fs.readFile(inputPath, "utf8"));
const runHistory = payload.run_history ?? [];
const workbook = Workbook.create();

function columnLabel(index) {
  let label = "";
  let current = index + 1;
  while (current > 0) {
    const remainder = (current - 1) % 26;
    label = String.fromCharCode(65 + remainder) + label;
    current = Math.floor((current - 1) / 26);
  }
  return label;
}

function normalizeValue(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "number" || typeof value === "string" || typeof value === "boolean") return value;
  return JSON.stringify(value);
}

function writeTable(sheetName, rows) {
  const sheet = workbook.worksheets.add(sheetName);
  if (!rows.length) {
    sheet.getRange("A1").values = [["No data"]];
    return;
  }

  const headers = [...new Set(rows.flatMap((row) => Object.keys(row)))];
  const matrix = [
    headers,
    ...rows.map((row) => headers.map((header) => normalizeValue(row[header]))),
  ];
  const endColumn = columnLabel(headers.length - 1);
  const endRow = matrix.length;
  sheet.getRange(`A1:${endColumn}${endRow}`).values = matrix;
  if (sheet.freezePanes?.freezeRows) {
    sheet.freezePanes.freezeRows = 1;
  }
}

const summaryRows = runHistory.map((run) => ({
  run_id: run.run_id,
  saved_at: run.saved_at,
  risk_profile: run.parameters.risk_profile,
  practice_runs: run.parameters.training_episodes,
  test_runs: run.parameters.evaluation_episodes,
  max_steps_per_run: run.parameters.episode_max_steps,
  starting_pattern_number: run.parameters.starting_pattern_number,
  training_success_rate: run.summary.training_success_rate,
  solved_bullying_percent: run.summary.evaluation_success_rate,
  average_overall_score: run.summary.average_overall_score,
  average_steps: run.summary.average_steps,
  final_exploration_rate: run.summary.final_exploration_rate,
  paper_success_rate: run.paper_reference["ISR (%)"] ?? "",
  paper_average_reward: run.paper_reference["AER"] ?? "",
}));

const actionRows = runHistory.flatMap((run) => {
  const total = Object.values(run.action_counts).reduce((sum, count) => sum + count, 0) || 1;
  return Object.entries(run.action_counts).map(([action, count]) => ({
    run_id: run.run_id,
    action,
    count,
    share_percent: Number(((count / total) * 100).toFixed(2)),
  }));
});

const outcomeRows = runHistory.flatMap((run) =>
  Object.entries(run.evaluation_outcomes).map(([outcome, count]) => ({
    run_id: run.run_id,
    outcome,
    count,
  })),
);

const trainingScoreRows = runHistory.flatMap((run) =>
  run.training_rewards.map((score, index) => ({
    run_id: run.run_id,
    practice_run_number: index + 1,
    overall_score: score,
  })),
);

const learningErrorRows = runHistory.flatMap((run) =>
  run.training_losses.map((error, index) => ({
    run_id: run.run_id,
    learning_update: index + 1,
    prediction_error: error,
  })),
);

const sampleEpisodeRows = runHistory.flatMap((run) =>
  run.sample_episode.map((step) => ({
    run_id: run.run_id,
    step: step.step,
    action: step.action,
    action_label: step.action_label,
    reward: step.reward,
    aggression_active: step.aggression_active,
    victim_emotion: step.victim_emotion,
    bully_emotion: step.bully_emotion,
    teacher_alerted: step.teacher_alerted,
    resolved: step.resolved,
    observer_pos: step.observer_pos,
    bully_pos: step.bully_pos,
    victim_pos: step.victim_pos,
    teacher_pos: step.teacher_pos,
  })),
);

const notesRows = [
  {
    note: "This workbook was exported from the Algorithm 1 Streamlit dashboard.",
    details: "Each row in the summary sheet is one dashboard run.",
  },
  {
    note: "Practice runs",
    details: "These are the learning runs used to train the observer.",
  },
  {
    note: "Test runs",
    details: "These are the later runs used to measure how the observer performed after learning.",
  },
];

writeTable("Run Summary", summaryRows);
writeTable("Action Usage", actionRows);
writeTable("Run Outcomes", outcomeRows);
writeTable("Training Scores", trainingScoreRows);
writeTable("Learning Error", learningErrorRows);
writeTable("Sample Episode", sampleEpisodeRows);
writeTable("Notes", notesRows);

await fs.mkdir(path.dirname(outputPath), { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(outputPath);
