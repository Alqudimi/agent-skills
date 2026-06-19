---
name: subagent-creator 
description: >
  Expert in designing, building, and orchestrating sub-agents for OpenCode (vibe coding tool).
  Covers: agent architecture, custom agent creation (JSON/Markdown), orchestration patterns
  (hierarchical, parallel, sequential, handoff), task tool usage, permission systems,
  model routing, context management, error handling, MCP integration, event-driven patterns,
  security sandboxing, token optimization, and production workflows.
  Triggers on: OpenCode agent creation, sub-agent design, multi-agent workflow,
  vibe coding agent setup, agent orchestration, custom agent configuration, agent permissions,
  agent testing, agent performance optimization, or any question about building agents in OpenCode.
  Keywords: opencode, subagent, sub-agent, agent, vibe code, vibe coding, orchestration,
  custom agent, agent team, multi-agent, task tool, agent pattern, agent workflow,
  agent configuration, agent permission, agent model, agent context, agent memory,
  agent security, agent testing, agent optimization, mcp, agent skill.
license: MIT
compatibility: opencode
metadata:
  author: Abdulaziz Alqudimi 
  version: "1.0.0"
  language: en/ar
  category: agent-development
  framework: opencode
---

# OpenCode Sub-Agent Expert

## When to Use This Skill

Activate this skill when the user needs to:
- Build or design custom agents (primary or sub-agent) in OpenCode
- Create multi-agent workflows or agent teams
- Configure agent permissions, models, or tools
- Optimize agent performance, context usage, or token costs
- Implement orchestration patterns (hierarchical, parallel, sequential, handoff)
- Set up MCP integration for external tools
- Debug, test, or validate agent behavior
- Design event-driven agent architectures
- Apply security sandboxing and least-privilege principles

## Core Principles

### 1. Agent Design Philosophy
- **Start simple, then specialize**: Begin with a generalist agent, then extract sub-agents for specific tasks
- **Least privilege**: Each agent gets ONLY the tools it needs (deny by default, allow explicitly)
- **Stateless by default**: Each sub-agent invocation is independent; pass all needed context in the task prompt
- **Model routing**: Use cheaper models (Haiku/Sonnet) for simple tasks, powerful models (Opus/Codex) for planning
- **Context isolation**: Each sub-agent gets a clean context window; results return to parent only

### 2. The 5-Layer Agent Architecture
```
Layer 1: User Interface (Primary Agent - Build/Plan)
Layer 2: Orchestrator (Coordinates sub-agents)
Layer 3: Specialist Sub-Agents (Code, Review, Research, Test)
Layer 4: Task Execution (Tools: read, edit, bash, MCP)
Layer 5: External Systems (APIs, DBs, Git, Cloud)
```

### 3. Key Metrics for Success
- **Token efficiency**: Sub-agent isolation reduces tokens by ~40% vs monolithic agents
- **Latency**: Parallel execution reduces time by 70-90% vs sequential
- **Accuracy**: Dedicated agents for specific tasks improve quality by 25-40%
- **Safety**: Permission gating prevents unauthorized actions

---

## Quick Reference: Agent Types

| Type | Mode | Visibility | Use Case | Example |
|------|------|------------|----------|---------|
| **Primary** | `mode: primary` | User-facing | Main interaction | `build`, `plan` |
| **Sub-agent** | `mode: subagent` | Hidden from user | Task delegation | `review`, `scout`, `test` |
| **Read-only** | `edit: deny`, `write: deny` | Hidden | Analysis, audit | `code-reviewer`, `security-auditor` |
| **Research** | `webfetch: allow`, `bash: deny` | Hidden | Information gathering | `researcher`, `docs-scout` |
| **Execution** | `edit: allow`, `bash: allow` | Hidden | Implementation | `coder`, `deployer` |

---

## Section 1: Creating Custom Agents

### 1.1 Markdown Method (Recommended)

Create files in `.opencode/agents/` or `~/.config/opencode/agents/`:

```markdown
---
description: Reviews code for security vulnerabilities and best practices
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.1
permission:
  edit: deny
  write: deny
  bash: deny
  read: allow
  grep: allow
  glob: allow
  list: allow
  webfetch: allow
  websearch: allow
---
# Security Auditor

You are a security-focused code reviewer. Your ONLY job is to analyze code for vulnerabilities.

## Rules
- NEVER modify files (read-only)
- Focus on: SQL injection, XSS, CSRF, auth bypass, secrets leakage, insecure dependencies
- Report findings with: severity (Critical/High/Medium/Low), file path, line number, explanation, fix suggestion
- Use grep and glob to find relevant files
- Use websearch to check for known CVEs in dependencies

## Output Format
```json
{
  "findings": [
    {
      "severity": "Critical",
      "file": "src/auth.js",
      "line": 42,
      "issue": "Hardcoded API key",
      "explanation": "...",
      "fix": "Use environment variables via process.env"
    }
  ]
}
```
```

**File naming**: `security-auditor.md` → agent name becomes `security-auditor`

### 1.2 JSON Method (opencode.json)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "security-auditor": {
      "description": "Reviews code for security vulnerabilities",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "temperature": 0.1,
      "permission": {
        "edit": "deny",
        "write": "deny",
        "bash": "deny",
        "read": "allow",
        "grep": "allow",
        "glob": "allow",
        "webfetch": "allow",
        "websearch": "allow"
      }
    }
  }
}
```

### 1.3 Frontmatter Options Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | Yes | What this agent does (shown in tool descriptions) |
| `mode` | string | Yes | `primary` or `subagent` |
| `model` | string | No | Model ID (e.g., `anthropic/claude-sonnet-4-20250514`) |
| `temperature` | number | No | 0.0-1.0 (0.1 for deterministic, 0.8 for creative) |
| `permission` | object | No | Tool permissions (allow/ask/deny per tool) |
| `color` | string | No | UI color (hex, e.g., `#FF5733`) |
| `hidden` | boolean | No | Hide from user interface |
| `max_steps` | number | No | Max iterations before forcing text-only response |

### 1.4 Permission System Deep Dive

**Available permission keys**:
- `read`, `edit` (includes write, apply_patch), `glob`, `grep`, `list`
- `bash`, `task`, `external_directory`, `todowrite`, `webfetch`, `websearch`
- `lsp`, `skill`, `question`, `doom_loop`

**Permission values**:
- `"allow"` - No approval needed
- `"ask"` - Prompt user before execution
- `"deny"` - Completely disabled

**Pattern matching for bash**:
```yaml
permission:
  bash:
    "git status *": allow
    "git diff *": allow
    "git log *": allow
    "git *": ask        # All other git commands ask
    "rm -rf *": deny    # Never allow recursive delete
    "sudo *": deny      # Never allow sudo
    "*": ask            # Default: ask for everything else
```

**Important**: Last matching rule wins. Put specific rules first, wildcards last.

---

## Section 2: Orchestration Patterns

### 2.1 Pattern Selection Guide

```
User Request
    ↓
Is it a single task?
    ├─ Yes → Use single agent (Build/Plan)
    └─ No → How many sub-tasks?
            ├─ 2-5 independent → PARALLEL (Fan-out/Fan-in)
            ├─ Sequential pipeline → SEQUENTIAL CHAIN
            ├─ Complex with dependencies → HIERARCHICAL
            ├─ Dynamic handoff needed → HANDOFF
            └─ Collaborative discussion → GROUP CHAT
```

### 2.2 Parallel Execution (Fan-out/Fan-in)

**Use when**: Multiple independent tasks that can run simultaneously
**Example**: Code review + security audit + docs check on the same PR

```
Parent Agent
    ├── Task: @code-reviewer "Review src/auth.js"
    ├── Task: @security-auditor "Audit src/auth.js"
    ├── Task: @docs-checker "Check docs for auth changes"
    └── Task: @test-engineer "Verify test coverage"
         ↓
    Collect all results
         ↓
    Summarize to user
```

**Implementation**:
```markdown
# In parent agent system prompt:

When reviewing a pull request, ALWAYS launch these 4 sub-agents in parallel:
1. @code-reviewer - Check code quality and best practices
2. @security-auditor - Check for vulnerabilities (read-only)
3. @docs-checker - Verify documentation is updated
4. @test-engineer - Verify test coverage

Wait for ALL results before responding to the user.
Summarize findings by severity: Critical → Important → Minor → None.
```

### 2.3 Sequential Chain (Pipeline)

**Use when**: Tasks have dependencies (output of A is input to B)
**Example**: Research → Plan → Implement → Test → Deploy

```
User: "Add OAuth2 authentication"
    ↓
@researcher: "Find best OAuth2 libraries for this stack"
    ↓
@planner: "Design OAuth2 integration architecture"
    ↓
[Human approval gate]
    ↓
@coder: "Implement the OAuth2 flow"
    ↓
@tester: "Write tests for OAuth2 implementation"
    ↓
@security-auditor: "Final security review"
    ↓
@deployer: "Deploy to staging"
```

**Implementation**:
```markdown
# In parent agent system prompt:

For feature requests, follow this EXACT sequence:
1. Launch @researcher with: "Research OAuth2 best practices for [stack]"
2. Wait for result, then launch @planner with: "Design OAuth2 architecture based on: [researcher output]"
3. Present plan to user and WAIT for approval
4. After approval, launch @coder with: "Implement: [approved plan]"
5. After coding, launch @tester with: "Write tests for: [coder output]"
6. After tests, launch @security-auditor with: "Security review of: [implementation]"
7. Summarize all findings to user
```

### 2.4 Hierarchical (Tree Structure)

**Use when**: Complex project with multiple components and sub-components
**Example**: Building a full-stack application

```
@project-manager (Opus/Claude)
    ├── @backend-lead (Sonnet)
    │       ├── @api-designer
    │       ├── @database-architect
    │       └── @security-engineer
    ├── @frontend-lead (Sonnet)
    │       ├── @ui-designer
    │       ├── @react-developer
    │       └── @accessibility-checker
    └── @devops-lead (Sonnet)
            ├── @ci-cd-engineer
            ├── @infra-architect
            └── @monitoring-setup
```

**Implementation**:
```markdown
# @project-manager system prompt:

You are a project manager. You do NOT write code.
Your job is to:
1. Break down the project into components
2. Delegate each component to the appropriate team lead
3. Review and integrate their outputs
4. Ensure consistency across components

For each component, create a detailed task description including:
- Requirements and constraints
- Interface contracts (API signatures, data formats)
- Dependencies on other components
- Acceptance criteria
```

### 2.5 Handoff (Dynamic Delegation)

**Use when**: The task type is unknown until runtime
**Example**: User asks "Fix the bug" - need to determine if it's frontend, backend, or infra

```
User: "Fix the login bug"
    ↓
@triage-agent: "Analyze the bug and determine which team should handle it"
    ↓
[Bug is in auth service]
    ↓
Handoff to @auth-team with full context
```

**Implementation**:
```markdown
# @triage-agent system prompt:

You are a triage specialist. Your job is to classify incoming issues.

## Classification Rules
- Frontend issues: UI rendering, CSS, React components, browser compatibility → handoff to @frontend-team
- Backend issues: API errors, database, performance, auth → handoff to @backend-team
- Infrastructure: CI/CD, deployment, monitoring → handoff to @devops-team
- Security: Vulnerabilities, breaches, auth bypass → handoff to @security-team

## Handoff Format
When handing off, include:
1. Issue classification and confidence level
2. Relevant files and line numbers
3. Error messages and stack traces
4. Steps to reproduce
5. Your initial hypothesis
```

### 2.6 Group Chat (Collaborative)

**Use when**: Multiple agents need to discuss and reach consensus
**Example**: Architecture decision requiring input from frontend, backend, and security

**Implementation**:
```markdown
# Use OpenCode's team messaging (inbox JSONL):

@frontend-lead: "I propose using GraphQL for the API"
    ↓
@backend-lead: "GraphQL adds complexity. REST with OpenAPI is simpler."
    ↓
@security-lead: "GraphQL has N+1 query risks. Need DataLoader."
    ↓
@frontend-lead: "Good point. Let's use REST with strict OpenAPI validation."
    ↓
Consensus reached → @project-manager approves
```

---

## Section 3: The Task Tool (Core Mechanism)

### 3.1 How Task Tool Works

The Task tool is the ONLY way to invoke sub-agents in OpenCode:

```
Parent Agent
    ↓
Task Tool: "Launch @code-reviewer to review src/auth.js"
    ↓
Session.create() → New session with isolated context
    ↓
Sub-agent executes with its own system prompt + tools
    ↓
Result returns as text to parent agent ONLY (hidden from user)
    ↓
Parent agent decides next action
```

### 3.2 Task Tool Best Practices

**DO**:
- ✅ Launch multiple sub-agents in parallel for independent tasks
- ✅ Provide ALL necessary context in the task description
- ✅ Specify the expected output format (JSON, markdown, etc.)
- ✅ Use for: code review, research, testing, documentation, security audit
- ✅ Trust sub-agent outputs (they're designed for specific tasks)

**DON'T**:
- ❌ Don't try to send follow-up messages to a running sub-agent (stateless)
- ❌ Don't use sub-agents for trivial tasks (overhead > benefit)
- ❌ Don't pass sensitive data unnecessarily
- ❌ Don't chain too many sequential sub-agents (latency adds up)

### 3.3 Task Description Template

```markdown
## Task Description Template

For [AGENT_NAME], task: [CLEAR DESCRIPTION]

Context:
- Project: [project name and tech stack]
- Files: [relevant file paths]
- Goal: [what needs to be achieved]
- Constraints: [limitations, must not break X, must follow Y pattern]
- Output format: [JSON/markdown/specific structure]
- Previous work: [if continuing from another agent's output]

Example:
"@security-auditor, task: Audit the authentication flow in src/auth/ 
for SQL injection and XSS vulnerabilities. 
Focus on: login.js, register.js, middleware/auth.js. 
Output: JSON array of findings with severity, file, line, issue, fix."
```

### 3.4 Parallel vs Sequential Decision Matrix

| Scenario | Pattern | Why |
|----------|---------|-----|
| Code review + Security audit + Docs check | Parallel | Independent analyses |
| Research → Plan → Implement | Sequential | Output of each step is input to next |
| Multiple file edits in same component | Sequential | Avoid conflicts |
| Cross-component changes | Parallel (per component) | Independent components |
| Testing after implementation | Sequential | Must implement first |
| Lint + Type check + Unit test | Parallel | Independent validations |

---

## Section 4: Model Routing & Temperature

### 4.1 Model Selection Guide

| Task Type | Recommended Model | Temperature | Reason |
|-----------|-------------------|-------------|--------|
| **Architecture/Planning** | Opus / Claude 4.5 | 0.2-0.3 | Complex reasoning, system design |
| **Code Implementation** | Sonnet / Claude 4 | 0.1-0.2 | Balanced speed and quality |
| **Code Review** | Sonnet / Claude 4 | 0.1 | Consistent, thorough analysis |
| **Testing** | Haiku / Claude 3.5 | 0.1 | Fast, good enough for tests |
| **Research/Web** | Perplexity Sonar | 0.5-0.8 | Creative search, broad exploration |
| **Documentation** | Haiku / Sonnet | 0.3 | Clear, concise writing |
| **Security Audit** | Opus / Sonnet | 0.1 | Thorough, no hallucinations |
| **Simple Refactoring** | Haiku | 0.1 | Fast, low cost |

### 4.2 Temperature Guidelines

- **0.0-0.2**: Deterministic tasks (coding, testing, security, review)
- **0.3-0.5**: Balanced tasks (planning, documentation, debugging)
- **0.6-0.8**: Creative tasks (research, brainstorming, exploration)
- **0.9-1.0**: Highly creative tasks (rarely needed in coding)

**Rule**: Lower temperature = more consistent, higher = more creative. For coding, ALWAYS prefer 0.1-0.2.

### 4.3 Cost Optimization

```
Cost per 1M tokens (approximate, 2026):
- Claude 3.5 Haiku: $0.25 / $1.25
- Claude 4 Sonnet: $3 / $15
- Claude 4.5 Opus: $15 / $75
- GPT-4o-mini: $0.15 / $0.60
- GPT-5.1: $2.50 / $10

Strategy: Use Haiku for 80% of tasks, Sonnet for 15%, Opus for 5% (planning only)
```

---

## Section 5: Context Management

### 5.1 Context Isolation

Each sub-agent gets:
- **Clean context window** (no parent conversation history)
- **Task string only** as user message
- **Own system prompt** (from agent definition)
- **Own tools** (filtered by permissions)

**Parent context is NOT copied to child** (except in fork mode for prompt cache sharing).

### 5.2 Context Optimization Strategies

1. **File-level context**: Send specific files, not entire directories
2. **Retrieval over stuffing**: Use grep/glob to find relevant files instead of loading everything
3. **Scope prompts**: Focus on the task, not the whole repository
4. **Bounded execution**: Set max_steps, retries, token budgets
5. **Diffs over full files**: Request changes as diffs, not rewritten files
6. **Caveman skill**: Use minimal prompts to reduce tokens by 65%

### 5.3 Prompt Cache Sharing (Fork Mode)

```
Normal mode:
  Parent context: 50K tokens
  Sub-agent context: 0 tokens (fresh start)
  Total: 50K + 50K = 100K

Fork mode:
  Parent context: 50K tokens (cached)
  Sub-agent context: 50K tokens (shares cache)
  Total: 50K + ~5K = 55K (90% savings on cached portion)
```

Use fork mode when sub-agents need the same project context as the parent.

### 5.4 Conversation Chaining

Use `previous_response_id` to maintain continuity across related tasks without reloading context:

```
Task 1: @researcher "Find OAuth2 libraries"
  ↓ (previous_response_id)
Task 2: @planner "Design architecture using [library X from Task 1]"
  ↓ (previous_response_id)
Task 3: @coder "Implement [architecture from Task 2]"
```

---

## Section 6: Error Handling & Resilience

### 6.1 Retry Strategy

```python
# Exponential backoff with jitter
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = (2 ** attempt) + random.uniform(0, 0.5)  # 2s, 4s, 6s + jitter
            time.sleep(delay)
```

### 6.2 Timeout Configuration

| Task Type | Timeout | Reason |
|-----------|---------|--------|
| Simple query | 30s | Fast lookup, grep, list |
| Code analysis | 120s | Reading multiple files |
| Complex refactoring | 300s | Multi-file changes |
| Test suite | 600s | Full test execution |
| Research | 300s | Web search + synthesis |

### 6.3 Circuit Breakers

```
Agent A fails 3 times in a row
    ↓
Circuit breaker opens
    ↓
Instead of calling Agent A, use degraded mode:
  - Simplified task description
  - Alternative agent (Agent B)
  - Direct parent execution with warnings
    ↓
After 5 minutes, try Agent A again (half-open)
```

### 6.4 Post-Execution Validation

After EVERY sub-agent execution, validate:
1. **Output format**: Does it match the expected structure?
2. **Completeness**: Are all requested items present?
3. **Accuracy**: Cross-check key facts with grep/read
4. **No duplicates**: Ensure no redundant findings
5. **Reasonable scope**: Results should match task size

### 6.5 Silent Failure Detection

Silent failures are the MOST dangerous:
- Agent thinks it succeeded but output is wrong
- **Solution**: Checkpoint before major operations + validation after
- **Example**: Before refactoring, save git snapshot. After refactoring, run tests. If tests fail, restore snapshot.

---

## Section 7: Security & Sandboxing

### 7.1 OpenCode Permission Model (UX Layer)

**WARNING**: OpenCode's permission system is a UX feature, NOT a real sandbox. For true isolation, use containers.

### 7.2 Sandboxing Options

| Level | Tool | Boot Time | Use Case |
|-------|------|-----------|----------|
| **Process** | Subprocess | Instant | Basic isolation |
| **Container** | Docker | ~1s | Standard isolation |
| **MicroVM** | Firecracker | ~125ms | Hardware-level isolation |
| **MicroVM** | Kata Containers | ~200ms | Hardware-level + K8s |
| **Syscall** | gVisor | ~500ms | Multi-tenant SaaS |

### 7.3 Security Best Practices

1. **Least privilege**: Start with ALL deny, allow only what's needed
2. **Approval gates**: Set `ask` for destructive operations (bash, edit, write)
3. **Secret isolation**: Use Key Vault, never hardcode secrets in prompts
4. **Network isolation**: Block outbound except explicit allowlist
5. **Audit logging**: Log every action with timestamp, agent, tool, result
6. **Read-only agents**: For review/audit tasks, explicitly disable edit/write/bash
7. **Sub-agent isolation**: Prevent sub-agents from accessing team messaging (security audit commit 2ad270dc4)

### 7.4 Dangerous Commands to Always Deny

```yaml
permission:
  bash:
    "rm -rf *": deny
    "sudo *": deny
    "curl * | bash": deny
    "wget * | bash": deny
    "eval *": deny
    "exec *": deny
    "* > /dev/null": deny  # Silent output hiding
    "* &": deny            # Background processes
```

---

## Section 8: MCP Integration

### 8.1 MCP Architecture

```
OpenCode (Client) ←→ MCP Server (stdio/HTTP)
    ↓
Tool Discovery (automatic)
    ↓
LLM decides to use Tool
    ↓
Client executes on Server
    ↓
Result returns to LLM
```

### 8.2 MCP Server Types

| Type | Connection | Use Case | Example |
|------|------------|----------|---------|
| **Local** | `npx` on machine | Local tools, development | File system, git |
| **Remote** | URL in cloud | SaaS integrations | Jira, Slack, GitHub |
| **Public** | No credentials | Open data sources | Weather, news |

### 8.3 Adding MCP Servers

```bash
# Via CLI
opencode mcp add <server-name>

# Via opencode.json
{
  "mcp": {
    "servers": {
      "github": {
        "type": "remote",
        "url": "https://mcp-github.com/sse",
        "auth": "oauth"
      }
    }
  }
}
```

### 8.4 MCP Permissions

```json
{
  "permission": {
    "mcp": {
      "github_*": "ask",
      "jira_*": "allow",
      "slack_*": "deny"
    }
  }
}
```

### 8.5 Composio Integration

For 1000+ app integrations:
```bash
opencode mcp add composio
# Provides: GitHub, Jira, Slack, Figma, Notion, etc.
```

---

## Section 9: Event-Driven Patterns

### 9.1 Publisher-Subscriber

```
@ci-agent publishes: "Build completed, tests passed"
    ↓
@deploy-agent subscribes → "Deploy to staging"
@notify-agent subscribes → "Send Slack notification"
@docs-agent subscribes → "Update changelog"
```

### 9.2 Event Sourcing

Store all events as immutable log:
```json
{
  "events": [
    {"id": 1, "type": "task.created", "agent": "user", "timestamp": "..."},
    {"id": 2, "type": "agent.assigned", "agent": "project-manager", "timestamp": "..."},
    {"id": 3, "type": "code.reviewed", "agent": "code-reviewer", "timestamp": "..."}
  ]
}
```

Benefits: Full audit trail, replay capability, state reconstruction.

### 9.3 Event Streaming

For high-throughput scenarios:
- **Kafka**: >1M events/sec, distributed
- **Pulsar**: Multi-tenancy, geo-replication
- **AWS EventBridge**: Serverless, managed

### 9.4 Event Choreography

No central coordinator. Agents react to events independently:
```
Event: "PR opened"
    → @reviewer: "Review code"
    → @ci: "Run tests"
    → @security: "Scan dependencies"
    → @docs: "Check docs updated"

All agents work in parallel, no orchestrator needed.
```

---

## Section 10: Production Workflows

### 10.1 The Ralph Loop Pattern

For long-running projects:
```
1. Pick task from tasks.json
2. Implement (single atomic change)
3. Validate (tests, lint, type-check)
4. Commit (if validation passes)
5. Reset context (clear conversation)
6. Repeat
```

**Memory channels**:
- Git history: Full code history
- Progress log: `progress.md` with completed tasks
- Tasks: `tasks.json` with pending tasks
- Agent knowledge: `AGENTS.md` with project conventions

### 10.2 Plan-Validate-Execute

For destructive operations:
```
1. Plan: Create intermediate artifact (field_values.json)
2. Validate: Check against source of truth (form_fields.json)
3. Execute: Only if validation passes
4. Rollback: Git snapshot if execution fails
```

### 10.3 TDD with Sub-agents

```
User: "Add user authentication"
    ↓
@test-agent: "Write failing tests for auth"
    ↓
[RED phase]
    ↓
@coder: "Implement auth to pass tests"
    ↓
[GREEN phase]
    ↓
@refactor-agent: "Refactor while keeping tests green"
    ↓
[REFACTOR phase]
```

### 10.4 Continuous Review

Auto-trigger review after every task:
```
@coder completes task
    ↓
Auto-launch @reviewer (read-only)
    ↓
Feedback categorized: Critical / Important / Minor
    ↓
@coder addresses Critical before proceeding
```

---

## Section 11: Testing & Validation

### 11.1 Testing Levels

| Level | What | How | Frequency |
|-------|------|-----|-----------|
| **Unit** | Single agent decision | Mock inputs, verify outputs | Every change |
| **Integration** | Agent + tools | Real tool calls, verify results | Daily |
| **End-to-end** | Full workflow | Simulate user request, verify outcome | Weekly |
| **Multi-turn** | Context preservation | Long conversation, verify consistency | Weekly |

### 11.2 Validation Checklists

**Before deploying an agent**:
- [ ] Permissions are minimal (least privilege)
- [ ] System prompt is < 9000 characters
- [ ] Output format is specified and tested
- [ ] Error handling covers: timeout, failure, invalid input
- [ ] Model selection matches task complexity
- [ ] Temperature is appropriate (0.1-0.2 for coding)
- [ ] Sub-agents cannot access team messaging (if applicable)
- [ ] Git snapshot is enabled for rollback
- [ ] Tests exist for the agent's core logic

### 11.3 Observability

Use LangSmith, TrueFoundry AI Gateway, or custom metrics:
```python
@dataclass
class AgentMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    tool_calls: dict = field(default_factory=dict)
    average_response_time: float = 0.0
    token_usage: int = 0
```

---

## Section 12: Advanced Patterns

### 12.1 Dedicated @reviewer Teammate

```markdown
---
description: Auto-triggers on every task completion for code review
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.1
permission:
  read: allow
  grep: allow
  glob: allow
  edit: deny
  write: deny
  bash: deny
---
# Auto-Reviewer

You are an automated code reviewer. You are triggered after EVERY task completion.

## Rules
- NEVER modify code (read-only)
- Review for: bugs, security, performance, maintainability, tests
- Categorize findings: Critical (block merge), Important (should fix), Minor (nice to have)
- If Critical findings exist, recommend fixing before proceeding
```

### 12.2 Context Scout Pattern

```markdown
---
description: Discovers relevant files and patterns before other agents work
mode: subagent
model: anthropic/claude-haiku-4-20250514
temperature: 0.1
permission:
  read: allow
  grep: allow
  glob: allow
  list: allow
  edit: deny
  write: deny
  bash: deny
---
# Context Scout

Your job is to discover relevant files BEFORE other agents start working.

## Process
1. Use glob to find files matching patterns
2. Use grep to search for keywords
3. Use list to explore directory structure
4. Return: relevant file paths, key patterns found, architectural notes

## Output Format
```json
{
  "relevant_files": ["src/auth.js", "src/middleware/auth.js"],
  "patterns_found": ["JWT usage", "bcrypt hashing"],
  "architecture_notes": "Auth is split between controller and middleware"
}
```
```

### 12.3 External Scout Pattern

```markdown
---
description: Fetches latest documentation and best practices from the web
mode: subagent
model: perplexity/sonar-pro
temperature: 0.5
permission:
  webfetch: allow
  websearch: allow
  read: deny
  edit: deny
  write: deny
  bash: deny
---
# External Scout

Your job is to fetch the LATEST information from the web.

## Rules
- Use websearch for broad queries
- Use webfetch for specific URLs
- Verify information is current (check dates)
- Return: summary, key findings, relevant URLs, confidence level
- NEVER modify local files
```

### 12.4 Skill Composition

Combine multiple skills for complex workflows:
```
User request
    ↓
Load skill: opencode-subagent-expert (this skill)
Load skill: systematic-debugging (for error handling)
Load skill: brainstorming (for design phase)
    ↓
Execute workflow using combined knowledge
```

---

## Section 13: Troubleshooting

### 13.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Agent not found | Wrong file name or location | Check `.opencode/agents/` or `~/.config/opencode/agents/` |
| Skill not loading | Missing frontmatter or wrong name | Verify `SKILL.md` is uppercase, name matches directory |
| Permission denied | Global config overrides project | Check precedence: Project > Global |
| Sub-agent not returning | Timeout or crash | Check logs, increase timeout, simplify task |
| Context overflow | Too much history | Use state resets, context trimming, or sub-agents |
| High token usage | Loading full directories | Use file-level context, grep for relevance |
| Agent loops forever | No max_steps set | Add `max_steps: 10` to agent config |

### 13.2 Debugging Checklist

1. Check agent file syntax (valid YAML frontmatter)
2. Verify permissions (use `opencode run "test"` to validate config)
3. Check model availability (`opencode models`)
4. Review logs for error messages
5. Test agent in isolation with simple task
6. Verify tool permissions (try `read` first, then add others)
7. Check if sub-agent can access required files

---

## Reference Resources

For detailed examples, templates, and patterns, load the reference files:

| File | When to Use |
|------|------------|
| `references/patterns.md` | Need orchestration pattern examples |
| `references/examples.md` | Need complete agent configuration examples |
| `references/templates.md` | Need ready-to-use agent templates |
| `references/best-practices.md` | Need advanced best practices and optimization |

---

## Quick Start: Your First Agent Team

### Step 1: Create the directory structure
```bash
mkdir -p .opencode/agents
```

### Step 2: Create a code reviewer
Create `.opencode/agents/code-reviewer.md`:
```markdown
---
description: Reviews code for quality and best practices
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.1
permission:
  read: allow
  grep: allow
  glob: allow
  edit: deny
  write: deny
  bash: deny
---
# Code Reviewer

Review code for: bugs, performance, maintainability, security.
Output: JSON with findings categorized by severity.
```

### Step 3: Create a test engineer
Create `.opencode/agents/test-engineer.md`:
```markdown
---
description: Writes comprehensive tests for code changes
mode: subagent
model: anthropic/claude-haiku-4-20250514
temperature: 0.1
permission:
  read: allow
  edit: allow
  write: allow
  bash: allow
---
# Test Engineer

Write tests covering: happy path, edge cases, error cases.
Use the existing testing framework in the project.
```

### Step 4: Use in your primary agent
In your primary agent's system prompt or AGENTS.md:
```markdown
When implementing features, ALWAYS:
1. Launch @code-reviewer and @test-engineer in parallel
2. Wait for both results
3. Address Critical findings from reviewer
4. Ensure tests pass before marking complete
```

### Step 5: Test
```bash
opencode run "Implement user authentication"
```

---

## Appendix: OpenCode vs Alternatives

| Feature | OpenCode | Claude Code | Cursor |
|---------|----------|-------------|--------|
| **Cost** | Free (BYOK $5-50/mo) | $20-200/mo | $20-40/mo |
| **Models** | 75+ (any provider) | Anthropic only | Limited |
| **Open Source** | Yes (MIT) | No | No |
| **Sub-agents** | Native (Task tool) | Native | Limited |
| **MCP** | Full support | Full support | Partial |
| **Best For** | Flexibility, budget, multi-model | Complex reasoning | IDE-native |
| **Token Usage** | Efficient | 5.5x fewer than Cursor | High |
| **Learning Curve** | Medium | Low | Lowest |

---

*This skill is designed to make you an expert in OpenCode sub-agent development. For questions not covered here, refer to the official documentation at https://opencode.ai/docs/*
