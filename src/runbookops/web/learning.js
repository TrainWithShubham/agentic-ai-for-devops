// Friendly labels sit beside the real events; they never replace API authorization or validation.
export const toolNames = {
  get_service_health: "Check checkout",
  get_recent_logs: "Read error logs",
  get_recent_deployments: "Check the last change",
  search_runbooks: "Search company notes",
  prepare_change: "Suggest a fix",
};
export const eventNames = {
  incident_created: "Task opened",
  node_started: "Step started",
  node_completed: "Step finished",
  mcp_connected: "Tools connected",
  model_request: "Asking the AI",
  model: "AI replied",
  tool: "Tool finished",
  tool_error: "Tool could not finish",
  proposal_prepared: "Fix suggested",
  investigation_finished: "Checks finished",
  approval_denied: "Approval blocked",
  approval_decision: "Human decision saved",
  change_applied: "Fix applied",
  verification: "Result checked",
  investigation_cancelled: "Task stopped",
};
export function explainError(value) {
  const text = String(value || "");
  if (/429|quota|rate.limit|throttl/i.test(text))
    return [
      "The AI service is busy or has reached its limit.",
      "Wait a little, then press Run again. Your instructor can check the account limit.",
    ];
  if (/timed?\s*out|timeout/i.test(text))
    return [
      "The AI took too long to reply.",
      "Press Run to try a new task. If it keeps happening, ask your instructor to check the model.",
    ];
  if (
    /401|access token|token.*expired|token.*invalid|connect again|bearer access/i.test(
      text,
    )
  )
    return [
      "Your sign-in needs to be refreshed.",
      "Open the shield icon at the top and connect again.",
    ];
  if (
    /AccessDeniedException|not authorized to perform.*bedrock|aws.*access/i.test(
      text,
    )
  )
    return [
      "The app cannot access this AWS model.",
      "Ask your instructor to check Bedrock permissions and model access.",
    ];
  if (
    /403|lacks.*permission|not.*authorized|cannot approve|access.denied/i.test(
      text,
    )
  )
    return [
      "This account cannot do that step.",
      "For approval, switch to Jethalal. He is the approver in this practice app.",
    ];
  if (/expir|revision|hash|409|conflict/i.test(text))
    return [
      "This suggested fix is out of date.",
      "Start a new task and review the new suggestion before approving it.",
    ];
  if (/budget|step limit|call limit/i.test(text))
    return [
      "The AI reached the allowed number of steps.",
      "Try a shorter task, such as: Why is checkout not working?",
    ];
  if (/key|credential|model access/i.test(text))
    return [
      "The AI connection needs to be set up.",
      "Ask your instructor to check the provider key or AWS access.",
    ];
  if (/network|connect|fetch|provider|502|503|unavailable/i.test(text))
    return [
      "We could not reach the AI service.",
      "Check the connection and try again. Your instructor can check the service if this continues.",
    ];
  if (/stopped|cancelled|abort/i.test(text))
    return [
      "You stopped this task.",
      "Press Run when you are ready to start a new one.",
    ];
  return [
    "This step could not finish.",
    "Open Technical details below, or ask your instructor for help.",
  ];
}
