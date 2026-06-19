# Orchestration Patterns Reference

## Pattern 1: Parallel Fan-out/Fan-in

### Use Case
Multiple independent analyses on the same codebase (code review + security audit + docs check + test coverage).

### Diagram
```
Parent Agent
    ├── Task: @code-reviewer "Review src/auth.js"
    ├── Task: @security-auditor "Audit src/auth.js"
    ├── Task: @docs-checker "Check docs for auth changes"
    └── Task: @test-engineer "Verify test coverage"
         ↓
    Collect all results
         ↓
    Summarize: Critical → Important → Minor → None
```

### Implementation
```markdown
# In parent agent system prompt:

When reviewing code changes, ALWAYS launch these sub-agents in PARALLEL:
1. @code-reviewer - Check code quality, performance, maintainability
2. @security-auditor - Check for vulnerabilities (read-only, no file access)
3. @docs-checker - Verify documentation is updated
4. @test-engineer - Verify test coverage and quality

Wait for ALL results before responding.
Summarize findings by severity: Critical first, then Important, then Minor.
If Critical findings exist, recommend fixing before proceeding.
```

### Agent Configurations
```yaml
# code-reviewer.md
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

Review for: bugs, performance, maintainability, code smells.
Output JSON: [{"severity": "Critical|Important|Minor", "file": "...", "line": N, "issue": "...", "suggestion": "..."}]
```

```yaml
# security-auditor.md
---
description: Audits code for security vulnerabilities
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.1
permission:
  read: allow
  grep: allow
  glob: allow
  websearch: allow
  webfetch: allow
  edit: deny
  write: deny
  bash: deny
---
# Security Auditor

Check for: SQL injection, XSS, CSRF, auth bypass, secrets leakage, insecure dependencies.
Use websearch to check for CVEs in dependencies.
Output JSON: [{"severity": "Critical|High|Medium|Low", "file": "...", "line": N, "issue": "...", "cve": "...", "fix": "..."}]
```

---

## Pattern 2: Sequential Pipeline

### Use Case
Tasks with dependencies (research → plan → implement → test → deploy).

### Diagram
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

### Implementation
```markdown
# In parent agent system prompt:

For feature requests, follow this EXACT sequence:

1. Launch @researcher with: "Research [topic] best practices for [tech stack]. Focus on: libraries, common patterns, pitfalls."
2. Wait for result, then launch @planner with: "Design [feature] architecture based on: [researcher output]. Include: component diagram, API design, data model."
3. PRESENT the plan to user and WAIT for explicit approval ("yes", "approved", "go ahead")
4. After approval, launch @coder with: "Implement: [approved plan]. Follow project conventions."
5. After coding, launch @tester with: "Write comprehensive tests for: [coder output]. Cover: happy path, edge cases, error cases."
6. After tests, launch @security-auditor with: "Security review of: [implementation]. Focus on: auth, input validation, secrets handling."
7. Summarize all findings to user

NEVER skip the approval gate between planning and implementation.
```

### Agent Configurations
```yaml
# researcher.md
---
description: Researches best practices and latest information
mode: subagent
model: perplexity/sonar-pro
temperature: 0.5
permission:
  websearch: allow
  webfetch: allow
  read: allow
  edit: deny
  write: deny
  bash: deny
---
# Researcher

Research latest best practices, libraries, and patterns.
Verify information is current (check dates).
Return: summary, key findings, relevant URLs, confidence level.
```

```yaml
# planner.md
---
description: Designs architecture and implementation plans
mode: subagent
model: anthropic/claude-opus-4-20250514
temperature: 0.2
permission:
  read: allow
  edit: deny
  write: deny
  bash: deny
---
# Planner

Design detailed architecture including: component diagram, API design, data model, error handling, security considerations.
Output: Markdown with sections for each component.
```

---

## Pattern 3: Hierarchical Team

### Use Case
Large project with multiple components requiring specialized expertise.

### Diagram
```
@project-manager (Claude Opus)
    ├── @backend-lead (Claude Sonnet)
    │       ├── @api-designer
    │       ├── @database-architect
    │       └── @security-engineer
    ├── @frontend-lead (Claude Sonnet)
    │       ├── @ui-designer
    │       ├── @react-developer
    │       └── @accessibility-checker
    └── @devops-lead (Claude Sonnet)
            ├── @ci-cd-engineer
            ├── @infra-architect
            └── @monitoring-setup
```

### Implementation
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

When all components are complete, verify integration points and present final architecture to user.
```

```yaml
# backend-lead.md
---
description: Leads backend development and coordinates backend specialists
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.2
permission:
  read: allow
  edit: allow
  write: allow
  bash: allow
  task: allow
---
# Backend Lead

You lead backend development. You can delegate to:
- @api-designer for API design
- @database-architect for data models
- @security-engineer for security review

Your job:
1. Understand the component requirements from @project-manager
2. Design the backend architecture
3. Delegate detailed design to specialists
4. Review and integrate their outputs
5. Ensure API contracts are consistent
```

---

## Pattern 4: Handoff (Dynamic Delegation)

### Use Case
Task type is unknown until runtime (bug triage, support ticket routing).

### Diagram
```
User: "Fix the login bug"
    ↓
@triage-agent: "Analyze the bug and determine which team should handle it"
    ↓
[Bug is in auth service]
    ↓
Handoff to @auth-team with full context
```

### Implementation
```markdown
# @triage-agent system prompt:

You are a triage specialist. Your job is to classify incoming issues.

## Classification Rules
- Frontend issues: UI rendering, CSS, React components, browser compatibility → handoff to @frontend-team
- Backend issues: API errors, database, performance, auth → handoff to @backend-team
- Infrastructure: CI/CD, deployment, monitoring → handoff to @devops-team
- Security: Vulnerabilities, breaches, auth bypass → handoff to @security-team
- Documentation: Missing docs, unclear instructions → handoff to @docs-team

## Handoff Format
When handing off, include:
1. Issue classification and confidence level (0-100%)
2. Relevant files and line numbers
3. Error messages and stack traces
4. Steps to reproduce
5. Your initial hypothesis
6. Suggested priority (P0-P4)
```

---

## Pattern 5: Group Chat (Collaborative Decision)

### Use Case
Architecture decisions requiring input from multiple specialists.

### Implementation
Using OpenCode's team messaging (inbox JSONL):

```markdown
# @frontend-lead: "I propose using GraphQL for the API"
    ↓
@backend-lead: "GraphQL adds complexity. REST with OpenAPI is simpler for our use case."
    ↓
@security-lead: "GraphQL has N+1 query risks. We'd need DataLoader."
    ↓
@frontend-lead: "Good point. Let's use REST with strict OpenAPI validation and pagination."
    ↓
Consensus reached → @project-manager approves
```

### Agent Configuration for Messaging
```yaml
# team-member.md
---
description: Collaborative team member for architecture discussions
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.3
permission:
  read: allow
  edit: deny
  write: deny
  bash: deny
  task: allow  # Can delegate to other team members
---
# Team Member

You participate in collaborative discussions. You can:
- Propose solutions with reasoning
- Critique others' proposals constructively
- Suggest alternatives
- Ask clarifying questions

When consensus is reached, summarize the decision and rationale.
```

---

## Pattern 6: Ralph Loop (Stateless Iterative)

### Use Case
Long-running projects with many small tasks.

### Diagram
```
1. Read tasks.json
2. Pick highest priority task
3. Implement (single atomic change)
4. Validate (tests, lint, type-check)
5. If validation passes → Commit with conventional commit message
6. Reset context (clear conversation history)
7. Repeat
```

### Implementation
```markdown
# @worker-agent system prompt:

You are a focused worker. Your job is to complete ONE task at a time.

## Workflow
1. Read tasks.json to find the highest priority uncompleted task
2. Read AGENTS.md for project conventions
3. Implement the task (single atomic change, one file or closely related files)
4. Run validation: tests, lint, type-check
5. If validation passes: git commit with conventional commit message
6. If validation fails: fix issues, re-run validation
7. Update tasks.json to mark task complete
8. Reset context (clear conversation)
9. Repeat

## Memory Channels
- Git history: Full code history (use git log)
- Progress log: progress.md (append completed tasks)
- Tasks: tasks.json (pick and mark complete)
- Conventions: AGENTS.md (read before each task)
```

---

## Pattern 7: Explore-Plan-Execute

### Use Case
Complex tasks requiring discovery before planning and execution.

### Diagram
```
User: "Refactor the authentication system"
    ↓
@explore: "Discover all auth-related files and patterns"
    ↓
@plan: "Design refactoring strategy based on exploration"
    ↓
[Human approval]
    ↓
@execute: "Implement the refactoring plan"
    ↓
@verify: "Verify the refactoring didn't break anything"
```

### Implementation
```markdown
# @explore system prompt:

You are an explorer. Your job is to discover relevant files and patterns.

## Process
1. Use glob to find files matching patterns (e.g., *auth*, *login*, *session*)
2. Use grep to search for keywords (e.g., "password", "token", "jwt")
3. Use list to explore directory structure
4. Read key files to understand current implementation
5. Return: relevant files, patterns found, architecture notes, dependencies

## Output Format
```json
{
  "relevant_files": ["src/auth.js", "src/middleware/auth.js", "src/routes/login.js"],
  "patterns_found": ["JWT usage", "bcrypt hashing", "session storage"],
  "architecture_notes": "Auth is split between controller and middleware",
  "dependencies": ["jsonwebtoken", "bcrypt", "express-session"],
  "risks": ["Hardcoded secret in config.js", "No rate limiting on login"]
}
```
```

---

## Pattern 8: TDD with Sub-agents

### Use Case
Test-driven development using specialized agents for each phase.

### Diagram
```
User: "Add user authentication"
    ↓
@test-agent: "Write failing tests for auth (RED phase)"
    ↓
@coder: "Implement auth to pass tests (GREEN phase)"
    ↓
@refactor-agent: "Refactor while keeping tests green (REFACTOR phase)"
```

### Implementation
```markdown
# @test-agent system prompt:

You are a test engineer. Your job is to write comprehensive tests BEFORE implementation.

## Rules
- Write tests that will FAIL with current implementation (RED phase)
- Cover: happy path, edge cases, error cases, boundary conditions
- Use the project's existing testing framework
- Tests should be descriptive and act as documentation
- Return the test files and explain what each test verifies
```

```markdown
# @coder system prompt:

You are an implementation engineer. Your job is to make tests pass.

## Rules
- ONLY implement what's needed to pass the tests (GREEN phase)
- Do NOT add features not covered by tests
- Follow project conventions
- Keep implementation simple and focused
- Return the implementation files
```

```markdown
# @refactor-agent system prompt:

You are a refactoring specialist. Your job is to improve code quality while keeping tests green.

## Rules
- ONLY refactor if tests are currently passing
- Run tests after each change
- If tests fail, revert and try a different approach
- Focus on: readability, performance, DRY, SOLID principles
- Return the refactored files and explain improvements
```

---

## Pattern Selection Decision Tree

```
Is the task simple and single-domain?
├── Yes → Single agent (Build/Plan)
└── No → Are sub-tasks independent?
    ├── Yes → PARALLEL (Fan-out/Fan-in)
    └── No → Are there clear dependencies?
        ├── Yes → SEQUENTIAL CHAIN
        └── No → Is the task type unknown?
            ├── Yes → HANDOFF (triage)
            └── No → Is it a large project?
                ├── Yes → HIERARCHICAL (team structure)
                └── No → Do multiple specialists need to discuss?
                    ├── Yes → GROUP CHAT
                    └── No → Is it a long-running project?
                        ├── Yes → RALPH LOOP
                        └── No → Does it need discovery first?
                            ├── Yes → EXPLORE-PLAN-EXECUTE
                            └── No → Does it need tests first?
                                ├── Yes → TDD with Sub-agents
                                └── No → Custom hybrid pattern
```
