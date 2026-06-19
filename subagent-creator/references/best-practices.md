# Advanced Best Practices & Optimization

## 1. Token Optimization Strategies

### 1.1 Context Size Reduction
- **File-level context**: Send specific files, not entire directories
- **Retrieval over stuffing**: Use grep/glob to find relevant files instead of loading everything
- **Scope prompts**: Focus on the task, not the whole repository
- **Bounded execution**: Set max_steps, retries, token budgets

### 1.2 Diffs Over Full Files
Request changes as diffs instead of rewritten files:
```
BAD:  "Rewrite the entire auth.js file"
GOOD: "Apply this diff to auth.js: @@ -45,7 +45,7 @@ ..."
```

### 1.3 Model Routing
Use cheaper models for simple tasks:
- **Haiku/3.5**: Title generation, simple grep, listing files
- **Sonnet**: Code review, implementation, testing
- **Opus**: Architecture design, complex refactoring, security audit

### 1.4 Caveman Skill
Use minimal prompts to reduce tokens by 65%:
```
BAD:  "Please analyze the following code and provide a detailed review..."
GOOD: "Review src/auth.js for bugs. Output JSON findings."
```

### 1.5 Conversation Chaining
Use `previous_response_id` to maintain continuity without reloading context:
```
Task 1: @researcher "Find OAuth2 libraries"
  ↓ (previous_response_id)
Task 2: @planner "Design using [library X from Task 1]"
  ↓ (previous_response_id)
Task 3: @coder "Implement [architecture from Task 2]"
```

### 1.6 Prompt Caching
Use `cache_control` to reduce costs by 90% on cached portions:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "[Large system prompt]",
      "cache_control": {"type": "ephemeral"}
    }
  ]
}
```

---

## 2. Security Best Practices

### 2.1 Permission Model
```yaml
# Start with ALL deny, then allow explicitly
permission:
  read: allow      # Usually safe
  edit: ask        # Destructive, needs approval
  write: ask       # Destructive, needs approval
  bash:
    "git status *": allow
    "git diff *": allow
    "git log *": allow
    "git *": ask
    "npm test": allow
    "npm run lint": allow
    "rm -rf *": deny      # NEVER allow
    "sudo *": deny         # NEVER allow
    "curl * | bash": deny  # NEVER allow
    "wget * | bash": deny  # NEVER allow
    "eval *": deny         # NEVER allow
    "exec *": deny         # NEVER allow
    "*": ask              # Default: ask
  webfetch: allow
  websearch: allow
```

### 2.2 Sub-Agent Isolation
Prevent sub-agents from accessing team messaging:
```yaml
# In sub-agent definition
permission:
  task:
    "*": deny  # Prevent creating more sub-agents
  # Or hide tools entirely
  tools: false
```

### 2.3 Secret Management
- NEVER hardcode secrets in prompts or agent definitions
- Use environment variables: `{env:API_KEY}`
- Use Key Vault for production
- Mask secrets in logs: `sk-...abcd`

### 2.4 Sandboxing for Production
```
Development: Process-level (OpenCode native)
Staging: Docker container
Production: MicroVM (Firecracker ~125ms, Kata ~200ms)
Multi-tenant: gVisor (syscall interception)
```

### 2.5 Audit Logging
Log every action:
```json
{
  "timestamp": "2026-06-05T10:30:00Z",
  "agent": "code-reviewer",
  "tool": "read",
  "target": "src/auth.js",
  "result": "success",
  "tokens_used": 1500
}
```

---

## 3. Performance Optimization

### 3.1 Parallel Execution
Launch independent sub-agents simultaneously:
```
Parent
  ├── Task: @reviewer (starts immediately)
  ├── Task: @tester (starts immediately)
  ├── Task: @security (starts immediately)
  └── Task: @docs (starts immediately)
       ↓
  Wait for all (max time = slowest agent)
```

### 3.2 Sequential Optimization
Minimize sequential chains:
```
BAD:  Research → Plan → Implement → Test → Review → Deploy (6 sequential)
GOOD: (Research + Plan) → Implement → (Test + Review) → Deploy (4 sequential)
      Parallel where possible
```

### 3.3 State Resets
Use Ralph Loop pattern for long sessions:
```
1. Complete task
2. Git commit
3. Reset conversation context
4. Start fresh with next task
```

### 3.4 Context Trimming
Compress context every 10-15 tool calls:
```
Before: 50K tokens (full conversation)
After:  5K tokens (summary + current task)
Savings: 90%
```

### 3.5 Tool Definition Compression
```
BAD:  {
  "name": "cpu_analyze",
  "description": "This tool analyzes CPU usage patterns...",
  "parameters": { ... }
}

GOOD: cpu_analyze(json) - Analyze CPU usage patterns
```

---

## 4. Error Handling Patterns

### 4.1 Exponential Backoff
```python
delay = (2 ** attempt) + random.uniform(0, 0.5)
# Attempt 1: 2.0-2.5s
# Attempt 2: 4.0-4.5s
# Attempt 3: 6.0-6.5s
```

### 4.2 Dead Letter Queue (DLQ)
For failed events after max retries:
```json
{
  "dead_letter_queue": [
    {
      "event": "deploy.production",
      "failure_reason": "Connection timeout",
      "retry_count": 3,
      "timestamp": "2026-06-05T10:30:00Z",
      "payload": "..."
    }
  ]
}
```

### 4.3 Circuit Breaker States
```
CLOSED: Normal operation
  ↓ (3 failures)
OPEN: Block requests, return degraded response
  ↓ (5 minutes)
HALF-OPEN: Allow 1 test request
  ↓ (success)
CLOSED: Resume normal operation
```

### 4.4 Validation Loops
```
1. Do the work
2. Run validation (script, checklist, or self-check)
3. If validation fails:
   - Review error message
   - Fix issues
   - Run validation again
4. Only proceed when validation passes
```

---

## 5. Multi-Agent Team Setup

### 5.1 Recommended Team Structure
```
@project-manager (Opus - planning & coordination)
    ├── @backend-lead (Sonnet - implementation)
    │       ├── @api-designer (Sonnet - API design)
    │       ├── @db-architect (Sonnet - data models)
    │       └── @security-engineer (Sonnet - security)
    ├── @frontend-lead (Sonnet - implementation)
    │       ├── @ui-designer (Haiku - UI/UX)
    │       ├── @react-dev (Sonnet - components)
    │       └── @a11y-checker (Haiku - accessibility)
    └── @devops-lead (Sonnet - infrastructure)
            ├── @ci-cd-engineer (Sonnet - pipelines)
            ├── @infra-architect (Opus - architecture)
            └── @monitoring-setup (Haiku - observability)
```

### 5.2 Communication Protocol
```json
{
  "message": {
    "from": "@backend-lead",
    "to": "@frontend-lead",
    "type": "api_contract",
    "payload": {
      "endpoint": "/api/v1/users",
      "method": "POST",
      "request": {"email": "string", "password": "string"},
      "response": {"id": "string", "token": "string"},
      "errors": [400, 401, 409]
    }
  }
}
```

### 5.3 Handoff Checklist
When handing off between agents:
- [ ] Full context provided (requirements, constraints, previous decisions)
- [ ] Current state documented (what's done, what's pending)
- [ ] Known issues listed
- [ ] Next steps clearly defined
- [ ] Acceptance criteria specified

---

## 6. Testing & Validation

### 6.1 Agent Testing Levels

| Level | Scope | Method | Frequency |
|-------|-------|--------|-----------|
| **Unit** | Single decision | Mock inputs, verify outputs | Every change |
| **Integration** | Agent + tools | Real tool calls, verify results | Daily |
| **End-to-end** | Full workflow | Simulate user request | Weekly |
| **Multi-turn** | Context preservation | Long conversation | Weekly |

### 6.2 Test Cases for Agents
```json
{
  "test_cases": [
    {
      "name": "Code reviewer finds SQL injection",
      "input": "src/auth.js with raw query",
      "expected_output": "Critical finding: SQL injection",
      "agent": "@security-auditor"
    },
    {
      "name": "Test engineer writes edge case tests",
      "input": "Function with boundary conditions",
      "expected_output": "Tests for min, max, empty, null",
      "agent": "@test-engineer"
    }
  ]
}
```

### 6.3 Observability Metrics
```python
@dataclass
class AgentMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    tool_calls: dict = field(default_factory=dict)
    average_response_time: float = 0.0
    token_usage: int = 0
    cost_per_request: float = 0.0
    
    def get_success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
```

---

## 7. Cost Optimization

### 7.1 Cost Per 1M Tokens (2026 Approximate)
| Model | Input | Output |
|-------|-------|--------|
| Claude 3.5 Haiku | $0.25 | $1.25 |
| Claude 4 Sonnet | $3.00 | $15.00 |
| Claude 4.5 Opus | $15.00 | $75.00 |
| GPT-4o-mini | $0.15 | $0.60 |
| GPT-5.1 | $2.50 | $10.00 |

### 7.2 Cost Reduction Strategy
- Use Haiku for 80% of tasks (simple queries, listing, grep)
- Use Sonnet for 15% of tasks (implementation, review, testing)
- Use Opus for 5% of tasks (architecture, complex reasoning)
- **Expected savings**: 70-80% vs using Opus for everything

### 7.3 Token Budgeting
```json
{
  "budget": {
    "daily_limit": 1000000,
    "per_task_limit": 100000,
    "alert_threshold": 80,
    "emergency_threshold": 95
  }
}
```

---

## 8. Memory & Persistence

### 8.1 Hindsight Plugin
```bash
# Install
npm install @vectorize-io/opencode-hindsight

# Config
{
  "plugin": ["@vectorize-io/opencode-hindsight"]
}
```

Features:
- `retain`: Store important facts
- `recall`: Retrieve relevant facts
- `reflect`: Summarize and synthesize

### 8.2 opencode-agent-memory Plugin
```bash
# Install
npm install opencode-agent-memory

# Usage
- Editable memory blocks on disk (markdown files)
- Global blocks: ~/.config/opencode/memory/
- Project blocks: .opencode/memory/
```

### 8.3 Manual Memory Management
```markdown
# AGENTS.md - Project conventions

## Memory
- Store decisions in decisions.md
- Store architecture in architecture.md
- Store progress in progress.md
- Read these files at the start of each session
```

---

## 9. Migration & Upgrade

### 9.1 From Legacy Tools Config
```json
// OLD (deprecated)
{
  "tools": {
    "write": true,
    "bash": true
  }
}

// NEW (permission-based)
{
  "permission": {
    "edit": "allow",
    "bash": "allow"
  }
}
```

### 9.2 From Cursor Rules
```markdown
# OLD: .cursorrules
Always use TypeScript strict mode.
Prefer functional patterns.

# NEW: AGENTS.md
## TypeScript
- Use strict mode
- Prefer functional patterns

## Commands
- `npm run build` - Build project
- `npm test` - Run tests
```

### 9.3 From Claude Code
```markdown
# Claude Code: CLAUDE.md
# OpenCode: AGENTS.md (same format, different location)

# Additional: OpenCode supports:
- Custom agents in .opencode/agents/
- Permission system
- Model routing
- MCP integration
```

---

## 10. Anti-Patterns to Avoid

### 10.1 Monolithic Agent
```
BAD: One agent does everything (research, plan, implement, test, review)
GOOD: Specialized agents for each phase
```

### 10.2 Over-Permission
```
BAD: All agents have edit + bash + write access
GOOD: Read-only for reviewers, limited bash for specific commands
```

### 10.3 Context Stuffing
```
BAD: Loading entire repository into context
GOOD: File-level context with grep/glob for relevance
```

### 10.4 Ignoring Failures
```
BAD: Continuing after sub-agent failure
GOOD: Circuit breaker + retry with backoff + validation
```

### 10.5 No Validation
```
BAD: Accepting sub-agent output without verification
GOOD: Post-execution validation + checkpoint before major operations
```

### 10.6 Temperature Mismatch
```
BAD: Using temperature 0.8 for coding tasks
GOOD: Temperature 0.1-0.2 for deterministic tasks, 0.5-0.8 for creative
```

### 10.7 Missing Approval Gates
```
BAD: Auto-executing destructive operations
GOOD: Human approval for: database migrations, production deploys, secret changes
```

---

## 11. Production Checklist

Before deploying agents to production:

- [ ] Permissions are minimal (least privilege)
- [ ] System prompt is < 9000 characters
- [ ] Output format is specified and tested
- [ ] Error handling covers: timeout, failure, invalid input
- [ ] Model selection matches task complexity
- [ ] Temperature is appropriate (0.1-0.2 for coding)
- [ ] Sub-agents cannot access team messaging (if applicable)
- [ ] Git snapshot is enabled for rollback
- [ ] Tests exist for the agent's core logic
- [ ] Audit logging is configured
- [ ] Rate limiting is enabled
- [ ] Circuit breakers are configured
- [ ] DLQ is set up for failed events
- [ ] Monitoring and alerting are active
- [ ] Rollback procedure is documented
- [ ] Secrets are not hardcoded
- [ ] Sandboxing is configured for production
- [ ] Cost budgets are set
- [ ] Team has been trained on agent usage
- [ ] Documentation is up to date
