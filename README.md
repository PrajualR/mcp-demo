# MCP Demo

A practical demonstration of the **Model Context Protocol (MCP)** using Python, an MCP server, an MCP client, and an LLM.

The project demonstrates how an AI application can discover tools exposed by an MCP server, allow an LLM to select the appropriate tools, execute those tools through the MCP client, and use the returned information to answer a complex business question.

---

# Project Objective

This project demonstrates an enterprise-style project intelligence assistant.

The assistant is given a complex business question:

> Analyze all projects and identify which projects are currently At Risk or Delayed. For each affected project, identify the project owner, find unresolved High or Critical priority tickets, summarize the major risks, and determine which project requires the most immediate attention.

The LLM must determine which MCP tools are required to answer the question.

---

# Architecture

```text
                         User
                           |
                           | Complex business question
                           v
                    +-------------+
                    |     LLM     |
                    +-------------+
                           |
                           | Tool selection
                           v
                    +-------------+
                    | MCP Client  |
                    +-------------+
                           |
                           | MCP / stdio
                           v
                    +-------------+
                    | MCP Server  |
                    +-------------+
                       /    |    \
                      /     |     \
                     v      v      v
                Projects Employees Tickets
                     \      |      /
                      \     |     /
                       v    v    v
                       JSON Data
```

---


# Project Structure

```text
mcp-demo/
│
├── data/
│   ├── employees.json
│   ├── projects.json
│   └── tickets.json
│
├── src/
│   ├── client/
│   │   └── client.py
│   │
│   └── server/
│       └── server.py
│
├── tests/
│
├── .env
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

---


# MCP Server

The MCP server is implemented in:

```text
src/server/server.py
```

The server exposes five tools.

## Available Tools

### `list_projects`

Returns all projects with:

- Project ID
- Project name
- Description
- Status
- Completion percentage
- Owner ID

Example:

```text
list_projects()
```

---

### `get_project`

Retrieves detailed information about a specific project.

Example:

```text
get_project("P001")
```

---

### `get_employee`

Retrieves employee information using an employee ID.

Example:

```text
get_employee("E001")
```

---

### `list_project_tickets`

Returns all tickets associated with a project.

Example:

```text
list_project_tickets("P001")
```

---

### `search_tickets`

Searches tickets using optional filters:

- Project
- Priority
- Status

Example:

```text
search_tickets(
    project_id="P003",
    priority="Critical",
    status="Open"
)
```

---

## 1. What is MCP?

**Model Context Protocol (MCP)** is an open protocol that standardizes how AI applications connect to external tools, data, and context.

Instead of every AI application implementing a different integration mechanism for every external system, MCP provides a common interface between an AI application and the systems that provide capabilities or context.

Conceptually:

```text
AI Application
      |
      | MCP
      |
MCP Server
      |
      +-- Tools
      +-- Resources
      +-- Prompts
      |
External systems / data
```

Official documentation:

https://modelcontextprotocol.io/

---

# 2. Why MCP?

A common question is:

> Why do we need MCP? Why can't we just make normal API or function calls?

The short answer is:

**We can. MCP is not a replacement for APIs or normal function calls.**

For a small application, direct function calls may be simpler and completely appropriate.

The value of MCP becomes more apparent when an AI application needs to work with many different tools and external systems.

Without MCP, an AI application may need custom integration code for every system:

```text
AI Application
   |
   +-- Custom Salesforce integration
   |
   +-- Custom Jira integration
   |
   +-- Custom Database integration
   |
   +-- Custom GitHub integration
   |
   +-- Custom File integration
```

With MCP, those systems can expose standardized MCP interfaces:

```text
                    AI Application
                          |
                     MCP Client
                          |
              -------------------------
              |           |           |
          MCP Server   MCP Server   MCP Server
              |           |           |
           Jira        Database      GitHub
```

The AI application can interact with MCP servers through a standardized protocol instead of implementing a completely different integration mechanism for every MCP-enabled system.

---

# 3. MCP Does Not Replace APIs

MCP and APIs solve different problems.

An API answers:

> How can one software system communicate with another software system?

MCP answers:

> How can an AI application discover and interact with capabilities and context provided to it?

For example:

```text
Application
    |
    | REST API
    v
Jira
```

is completely valid.

An MCP server could internally use the Jira REST API:

```text
LLM
 |
MCP Client
 |
MCP Server
 |
Jira REST API
 |
Jira
```

Therefore:

**MCP can sit on top of existing APIs.**

It does not require replacing the underlying API.

---

# 21. When MCP Becomes Valuable

MCP becomes more useful when:

- Multiple AI applications need the same tools.
- Tools belong to different systems.
- Tool discovery is important.
- Standardized integration is desired.
- The organization has many AI applications.
- External capabilities need to be exposed consistently.
- The same MCP server should be usable by different MCP-compatible hosts.

---

# 22. MCP vs REST API

REST API:

```text
Application
    |
    | HTTP request
    v
Service
```

MCP:

```text
AI Application
    |
    | MCP
    v
MCP Server
    |
    v
Service / Database / API
```

REST is primarily an application/service communication mechanism.

MCP is designed around providing AI applications standardized access to tools and context.

An MCP server can itself call REST APIs.

---

# 23. MCP vs RAG

MCP and RAG solve different problems.

### RAG

RAG focuses on:

```text
Documents
   |
Embedding / Retrieval
   |
Relevant Context
   |
LLM
```

Its primary purpose is retrieving relevant information for the model.

### MCP

MCP provides standardized access to capabilities and context:

```text
LLM Application
      |
   MCP Client
      |
   MCP Server
      |
 +----+----+
 |    |    |
Tool Data API
```

MCP can therefore provide a tool that performs retrieval, but MCP itself is not a RAG technique.

---

# 24. MCP vs LangChain Tools

LangChain can provide tools to an agent within a LangChain application.

For example:

```text
LangChain Agent
     |
     +-- Tool A
     +-- Tool B
     +-- Tool C
```

MCP standardizes the communication between AI applications and external capability providers.

They can also work together.

For example:

```text
LangChain Agent
      |
  MCP Client
      |
  MCP Server
      |
    Tools
```

Therefore MCP and LangChain are not necessarily competitors.

---

# 25. MCP and Agents

An agent generally involves:

```text
LLM
 +
Tool selection
 +
Execution
 +
Observation
 +
Further reasoning
```

MCP provides a standardized way for the agent/application to access external capabilities.

Therefore:

```text
Agent
  |
  +-- MCP Client
          |
          +-- MCP Server
                  |
                  +-- Tool
                  +-- Tool
                  +-- Tool
```

MCP is the integration protocol, not the agent itself.

---

# 26. MCP Host, Client and Server

These terms are easy to confuse.

### Host

The host is the AI application that the user interacts with.

Examples can include an AI coding application or another AI-enabled application.

### Client

The MCP client manages the connection between the host/application and an MCP server.

### Server

The MCP server exposes capabilities such as tools, resources, and prompts.

In this project:

```text
Our Python application
        |
        +-- MCP Client
                |
                v
        Our MCP Server
```

The Groq LLM is the model being used by the application; it is not the MCP server.

---

# 27. Tools, Resources and Prompts

MCP supports different primitives.

## Tools

Tools represent callable capabilities.

Examples:

```text
search_customer()
create_ticket()
query_database()
```

The current project primarily demonstrates tools.

## Resources

Resources represent data that an MCP client can read.

They are useful when the server exposes context/data identified by URIs.

## Prompts

Prompts are reusable prompt templates exposed by an MCP server.

The current project does not implement resources or prompts because they are not required for the core project-intelligence use case.

---

# 28. Security Considerations

MCP does not automatically make a system secure.

A production MCP implementation should consider:

- Authentication
- Authorization
- Least-privilege access
- Input validation
- Tool permissions
- Secret management
- Audit logging
- Rate limiting
- Sensitive data handling
- Tool execution boundaries

For example, a read-only project analysis server should not automatically have permission to modify project records.

A useful principle is:

> Give an MCP server only the permissions required for the capabilities it exposes.

---

# 29. Error Handling

A production implementation should also handle:

- MCP connection failures
- Invalid tool arguments
- Tool execution failures
- LLM failures
- API timeouts
- Authentication failures
- Malformed tool responses
- Network failures

The current project is a learning/demo implementation, so error handling is intentionally lightweight.

---

# 30. Why the Tool Descriptions Matter

The tool docstrings in `server.py` are important.

For example:

```python
@mcp.tool()
def search_tickets(
    project_id: str | None = None,
    priority: str | None = None,
    status: str | None = None,
) -> list:
    """
    Search tickets using optional filters for project,
    priority, and status.
    """
```

The description helps the client/model understand what the tool does and what inputs it accepts.

Therefore MCP tool design is not only about writing executable code.

Good tool names, descriptions, and schemas are important for reliable model-driven tool selection.

---

## Q1. What problem does MCP solve?

MCP provides a standardized protocol for AI applications to discover and interact with external tools and context.

---

## Q2. Why not just call APIs directly?

Direct API calls are perfectly valid.

MCP is useful when an AI application needs standardized, reusable access to many capabilities and systems.

MCP can also sit on top of existing APIs rather than replacing them.

---

## Q3. Is MCP an alternative to REST?

Not exactly.

REST is an API communication style.

MCP is an AI-oriented protocol for exposing and consuming capabilities and context.

An MCP server can internally call REST APIs.

---

## Q4. Is MCP an agent framework?

No.

MCP provides the integration protocol.

An agent can use MCP to access tools.

---

## Q5. Is MCP RAG?

No.

RAG is a retrieval architecture.

MCP is a protocol for connecting AI applications with tools and context providers.

An MCP server could expose a retrieval capability, but MCP itself is not RAG.

---

## Q6. Does MCP replace function calling?

No.

Function calling and MCP can work together.

In this project, the LLM's tool-calling capability is used to decide which MCP tool should be invoked.

---

## Q7. What happens when a new MCP tool is added?

The MCP client can discover the new tool through tool listing.

The application does not necessarily need a new hardcoded integration for every tool.

The model receives the tool name, description, and input schema and can potentially select it when appropriate.

---

## Q8. Does the LLM communicate directly with the MCP server?

In this architecture, no.

The application contains the MCP client.

Conceptually:

```text
LLM
 |
AI Application
 |
MCP Client
 |
MCP Server
```

The MCP client handles the protocol communication.

---

## Q9. Who decides which tool to call?

The LLM decides which available tool is appropriate based on the user's question and the tool descriptions/schema.

The application then executes the requested MCP tool through the MCP client.

---

## Q10. Can one MCP server have many tools?

Yes.

This project demonstrates five tools in one MCP server.

A production MCP server could expose many capabilities, depending on its purpose.

---

## Q11. Can multiple MCP servers be used?

Yes.

An AI application can connect to multiple MCP servers.

For example:

```text
AI Application
      |
      +-- MCP Server: Jira
      |
      +-- MCP Server: GitHub
      |
      +-- MCP Server: Database
      |
      +-- MCP Server: Internal APIs
```

This is one of the areas where the standardized protocol becomes particularly useful.

---

## Q12. What is the role of MCP Inspector?

Inspector is a development/testing tool for interacting with an MCP server.

It allows developers to inspect available capabilities and manually test tools before connecting a complete AI application.

---

## Q13. What happens if the LLM chooses the wrong tool?

The application should validate tool calls and handle failures.

In production systems, tool descriptions, schemas, authorization, validation, and guardrails should all be designed carefully.

---

## Q14. Can MCP access databases?

Yes.

An MCP tool can query a database and return the relevant result.

The MCP server becomes the controlled interface between the AI application and the database.

---

## Q15. Can MCP modify data?

Yes, technically.

A tool can perform actions such as:

```text
create_ticket()
update_customer()
send_email()
delete_record()
```

However, write operations require appropriate authorization and safeguards.

---

## Q16. Is MCP only for Anthropic models?

No.

MCP is a protocol.

The LLM provider and MCP server are separate concepts.

An application can use different model providers while communicating with MCP servers.

---

## Q17. What happens if the MCP server is unavailable?

The MCP client will not be able to execute the requested capability.

A production application should handle connection failures, timeouts, and retries appropriately.

---

## Q18. Why are we using stdio here?

This project uses stdio because it is simple for a local development/demo environment.

The client launches the MCP server as a subprocess and communicates with it through standard input/output.

For deployed systems, other transports such as Streamable HTTP can be appropriate.

---

## Q19. Why don't we implement every MCP feature?

Because the goal of the project is to demonstrate the core MCP workflow.

The project focuses on tools because the business scenario is an action/query-oriented project intelligence use case.

Adding resources and prompts would not necessarily improve this particular demonstration.

---

## Q20. What is the biggest benefit of MCP?

The biggest benefit is **standardization of AI-to-capability integration**.

Instead of every AI application implementing a unique integration mechanism for every external capability, MCP provides a common protocol for discovering and interacting with MCP-enabled servers.

---