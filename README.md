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

# 1. What is MCP?

**Model Context Protocol (MCP)** is an open protocol that standardizes how AI applications connect to external tools, data, and context.

It defines a common way for an AI application to discover and interact with capabilities exposed by an MCP server.

At a high level:

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

MCP separates the mechanism used to provide capabilities and context from the LLM itself.

The LLM can be from one provider while the MCP server can be implemented independently.

Official documentation:

https://modelcontextprotocol.io/

---

# 2. MCP Architecture: Host, Client and Server

Three terms are important to understand.

## Host

The **host** is the AI application that the user interacts with.

The host contains or manages the AI experience and can use one or more MCP clients.

Conceptually:

```text
Host / AI Application
        |
        +-- MCP Client
        |
        +-- LLM
```

## Client

The **MCP client** is the component responsible for communicating with an MCP server.

It manages the MCP connection, initialization, capability negotiation, discovery, and requests.

```text
Host
 |
MCP Client
 |
MCP Server
```

## Server

The **MCP server** exposes capabilities that an MCP client can discover and use.

These capabilities can include:

- Tools
- Resources
- Prompts

Therefore:

```text
Host
 |
MCP Client
 |
MCP Server
 |      |      |
Tools Resources Prompts
```

### Important distinction

The **LLM is not the MCP server**.

The LLM provides reasoning and decides what information or capability it needs.

The MCP client communicates with the MCP server and executes the requested MCP operations.

---

# 3. How MCP Communication Works

MCP communication follows a client-server model.

A simplified flow is:

```text
User
 |
 v
AI Application / Host
 |
 v
LLM
 |
 | decides a tool is required
 v
MCP Client
 |
 | MCP request
 v
MCP Server
 |
 | executes capability
 v
Tool Result
 |
 v
MCP Client
 |
 v
LLM
 |
 v
Final Answer
```

The LLM does not directly execute the Python function on the MCP server.

The LLM produces a tool request.

The MCP client receives that request and performs the MCP tool call.

---

# 4. MCP Lifecycle

Before the client can use MCP capabilities, the client and server establish an MCP session.

A simplified lifecycle is:

```text
1. Connect
     |
     v
2. Initialize
     |
     v
3. Capability Negotiation
     |
     v
4. Discover Capabilities
     |
     v
5. Call Tools / Read Resources / Get Prompts
     |
     v
6. Receive Results
     |
     v
7. Continue or End Session
```

## Initialize

The client starts the MCP session by sending an initialization request.

In this project:

```python
await session.initialize()
```

This establishes the protocol session and allows the client and server to negotiate supported capabilities.

## Discover

After initialization, the client can discover the capabilities exposed by the server.

For tools:

```python
response = await session.list_tools()
```

The client receives information such as:

- Tool name
- Tool description
- Input schema

## Call

Once a tool has been selected, the client calls it:

```python
result = await session.call_tool(
    tool_name,
    arguments,
)
```

## Result

The MCP server executes the tool and returns the result to the client.

The client can then provide that result to the LLM.

---

# 5. What is MCP Transport?

A **transport** is the communication mechanism used to carry MCP messages between the client and server.

Transport is different from MCP itself.

Think of it as:

```text
MCP
 |
 +-- Defines the protocol and message interaction
 |
 +-- Transport carries those messages
```

Common MCP transports include:

- stdio
- Streamable HTTP
- Legacy HTTP + SSE

The transport determines **how the client and server communicate**, while MCP defines **what they communicate and how the protocol works**.

---

# 6. What is stdio?

`stdio` stands for **standard input/output**.

In the stdio transport, the MCP client starts the MCP server as a local subprocess and communicates with it through:

```text
stdin  → messages to the server
stdout ← messages from the server
```

Conceptually:

```text
MCP Client Process
       |
       | stdin / stdout
       |
       v
MCP Server Process
```

In this project, the client starts the server using:

```python
server_params = StdioServerParameters(
    command="uv",
    args=[
        "run",
        "mcp",
        "run",
        "src/server/server.py",
    ],
)
```

Then:

```python
async with stdio_client(server_params) as (read, write):
```

creates the communication channel.

### Why use stdio here?

stdio is useful for:

- Local development
- Local MCP servers
- Command-line integrations
- Servers launched as child processes
- Simple demonstrations

It does not require the MCP server to expose a network port.

### Important

`stdio` is **not another MCP protocol**.

It is a transport used to carry MCP communication.

---

# 7. Other MCP Transports

## Streamable HTTP

**Streamable HTTP** is designed for MCP servers that are accessed over HTTP.

Conceptually:

```text
AI Application
      |
      | HTTP
      |
      v
MCP Server
```

This is appropriate when the MCP server is:

- Remote
- Deployed as a service
- Shared across applications
- Running independently of the client process

A client can connect to an MCP endpoint such as:

```text
https://example.com/mcp
```

Streamable HTTP is the current transport to consider for remote deployments.

## SSE

Earlier MCP implementations used **HTTP + Server-Sent Events (SSE)**.

It is now considered a legacy transport and is maintained mainly for compatibility with older MCP implementations.

For new remote deployments, Streamable HTTP is preferred.

### Transport comparison

| Transport | Typical Use |
|---|---|
| stdio | Local process / local development |
| Streamable HTTP | Remote or deployed MCP servers |
| SSE | Legacy compatibility |

---

# 8. Tools, Resources and Prompts

MCP defines different types of capabilities.

## Tools

Tools are callable capabilities.

They can perform operations such as:

```text
search_customer()
create_ticket()
query_database()
send_email()
```

Tools are generally used when the model needs to **perform an operation or request a computation/action**.

This project primarily demonstrates MCP tools.

## Resources

Resources expose data or context that can be read by the client.

For example:

```text
file://documents/customer-policy.pdf
```

or another URI identifying a piece of data.

Resources are generally read-oriented.

## Prompts

Prompts are reusable prompt templates exposed by an MCP server.

They can help standardize how users or applications invoke particular workflows.

### Simple distinction

```text
Tools
→ Do something

Resources
→ Provide data/context

Prompts
→ Provide reusable prompt templates
```

---

# 9. How the LLM and MCP Work Together

MCP itself does not decide which tool should be used.

The LLM is responsible for reasoning about the user's request and selecting an appropriate capability.

The application connects the two.

The flow is:

```text
User Question
      |
      v
LLM
      |
      | Tool request
      v
MCP Client
      |
      | MCP call
      v
MCP Server
      |
      v
Tool
      |
      v
Tool Result
      |
      v
MCP Client
      |
      v
LLM
      |
      v
Final Answer
```

The important separation is:

```text
LLM
→ Reasoning / tool selection

MCP Client
→ MCP communication

MCP Server
→ Capability implementation
```

---

# 10. MCP Tool Discovery

One of the important parts of MCP is **capability discovery**.

The client does not have to assume that the server provides a particular set of tools.

It can ask the server what tools are available.

Conceptually:

```text
Client
   |
   | tools/list
   v
Server
   |
   | Tool definitions
   v
Client
```

The returned tool information includes details such as:

```text
Tool name
Description
Input schema
```

The application can then provide these tool definitions to the LLM.

This allows the LLM to reason about the available capabilities.

---

# 11. MCP Tool Calling

After the LLM decides that a tool is required, the application performs the MCP tool call.

Conceptually:

```text
LLM
 |
 | "Call search_tickets with these arguments"
 v
MCP Client
 |
 | tools/call
 v
MCP Server
 |
 v
Tool Execution
 |
 v
Result
```

The result is then returned to the LLM as part of the conversation.

The LLM may decide that another tool is required.

This can produce a multi-step workflow:

```text
LLM
 |
 +-- Tool A
 |
 +-- Tool B
 |
 +-- Tool C
 |
 v
Final Answer
```

---

# 12. Why MCP?

A common question is:

> Why do we need MCP? Why can't we just make normal API or function calls?

The short answer is:

**We can. MCP is not a replacement for APIs or normal function calls.**

For a small, tightly controlled application, direct function calls may be simpler and more appropriate.

MCP becomes valuable when AI applications need standardized access to multiple capabilities and external systems.

Without a common protocol, applications may build custom integration logic for each system:

```text
AI Application
   |
   +-- Custom Jira integration
   |
   +-- Custom GitHub integration
   |
   +-- Custom Database integration
   |
   +-- Custom File integration
```

With MCP:

```text
                    AI Application
                          |
                     MCP Client
                          |
              -------------------------
              |           |           |
          MCP Server   MCP Server   MCP Server
              |           |           |
            Jira       Database      GitHub
```

The integration boundary becomes standardized.

---

# 13. MCP vs Direct Function Calls

Direct function calling is a valid approach.

For example:

```text
Application
    |
    +-- get_customer()
    +-- search_orders()
    +-- calculate_price()
```

The functions are directly implemented and controlled by the application.

With MCP:

```text
Application
    |
MCP Client
    |
MCP Server
    |
    +-- get_customer()
    +-- search_orders()
    +-- calculate_price()
```

The capabilities are exposed through the MCP protocol.

### Key difference

Direct function calls:

- Tightly coupled to the application
- Simple for small systems
- No additional protocol layer required

MCP:

- Standardized client-server interface
- Capabilities can be exposed independently
- Easier to reuse MCP servers across compatible AI applications
- Supports capability discovery
- Separates the capability provider from the consuming application

### Important conclusion

MCP is **not automatically better** than direct function calls.

The right choice depends on the architecture and requirements.

---

# 14. MCP vs REST API

REST and MCP solve different problems.

REST is primarily an API style for communication between software systems.

```text
Application
    |
    | HTTP request
    v
REST API
    |
    v
Service
```

MCP is a protocol designed for AI applications to interact with capabilities and context.

```text
AI Application
    |
MCP Client
    |
MCP Server
    |
Service / Database / API
```

An MCP server can internally call a REST API.

For example:

```text
LLM
 |
MCP Client
 |
MCP Server
 |
REST API
 |
External System
```

Therefore, MCP does not replace REST.

It can provide an AI-oriented interface over existing services and APIs.

---

# 15. MCP vs RAG

MCP and RAG solve different problems.

## RAG

RAG focuses on retrieving relevant information and providing it to the LLM.

```text
Documents
   |
Embedding / Retrieval
   |
Relevant Context
   |
LLM
```

The primary purpose is information retrieval and grounding.

## MCP

MCP provides a standardized protocol through which an AI application can access capabilities and context.

```text
AI Application
      |
   MCP Client
      |
   MCP Server
      |
 +----+----+
 |    |    |
Tool Data API
```

An MCP server could expose a retrieval tool.

For example:

```text
search_documents()
```

That tool could internally use a vector database.

However:

**MCP is not RAG.**

RAG is a retrieval architecture.

MCP is an integration protocol.

They can be used together.

---

# 16. MCP vs LangChain Tools

LangChain can provide tools to an agent within a LangChain application.

For example:

```text
LangChain Agent
     |
     +-- Tool A
     +-- Tool B
     +-- Tool C
```

MCP standardizes communication between AI applications and external capability providers.

They can also work together:

```text
LangChain Agent
      |
  MCP Client
      |
  MCP Server
      |
    Tools
```

Therefore, MCP and LangChain tools are not direct replacements for each other.

LangChain is an application/agent framework.

MCP is a protocol for connecting applications to external capabilities and context.

---

# 17. MCP and Agents

An agent typically involves a loop such as:

```text
LLM
 |
 | Decide
 v
Tool Selection
 |
 v
Tool Execution
 |
 v
Observation / Result
 |
 v
Further Reasoning
 |
 +-----> Another Tool
 |
 v
Final Answer
```

MCP does not create the agent.

Instead, MCP can provide the tools that an agent uses.

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

Therefore:

**Agent = reasoning/orchestration approach**

**MCP = standardized capability integration protocol**

They can be used together.

---

# 18. Security Considerations

MCP does not automatically make an application secure.

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

A server exposing a capability should have only the permissions required for that capability.

For example, a read-only tool should not automatically have permission to modify the underlying system.

Security becomes especially important when MCP servers expose tools capable of performing external side effects.

---

# 19. Error Handling

A production implementation should handle:

- MCP connection failures
- Invalid tool arguments
- Tool execution failures
- LLM failures
- API timeouts
- Authentication failures
- Malformed tool responses
- Network failures
- Unavailable MCP servers

The client should not blindly trust every tool result.

Tool results and errors should be validated before being passed into subsequent processing.

The current project is a learning/demo implementation, so error handling is intentionally lightweight.

---

# 20. Why Tool Descriptions and Schemas Matter

MCP tool definitions contain information such as:

- Tool name
- Description
- Input schema

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

The description explains the purpose of the tool.

The input schema tells the client/model what arguments the tool accepts.

This information is important when an LLM is deciding which tool to use.

Poorly designed tools can make tool selection less reliable.

Good MCP tool design should therefore include:

- Clear tool names
- Accurate descriptions
- Well-defined input schemas
- Appropriate boundaries
- Minimal required permissions

---

# 21. MCP Inspector

MCP Inspector is a development and testing tool for MCP servers.

It allows developers to:

- Connect to an MCP server
- Discover available tools
- Inspect tool descriptions
- Inspect input schemas
- Manually call tools
- Inspect returned results

Run:

```bash
uv run mcp dev src/server/server.py
```

This provides a convenient way to verify the MCP server independently of the LLM.

---

# 22. Important MCP Concepts at a Glance

| Concept | Purpose |
|---|---|
| Host | AI application that provides the user-facing experience |
| Client | Connects the host/application to an MCP server |
| Server | Provides tools, resources, prompts and other capabilities |
| Tool | Callable capability |
| Resource | Readable data/context |
| Prompt | Reusable prompt template |
| Transport | Carries MCP messages between client and server |
| stdio | Local process-based transport |
| Streamable HTTP | Remote/deployed transport |
| SSE | Legacy HTTP transport |
| Discovery | Client learns what capabilities are available |
| Initialization | Establishes the MCP session and negotiates capabilities |
| Tool call | Client requests execution of a tool |
| LLM | Reasons about the user request and can select tools |

---

# 23. Manager Q&A

## Q1. What problem does MCP solve?

MCP provides a standardized way for AI applications to discover and interact with external tools, data, and context.

It reduces the need for every AI application to implement a separate integration pattern for every external capability.

---

## Q2. Why can't we just call APIs directly?

We can.

Direct API calls are appropriate for many applications.

MCP becomes useful when an AI application needs a standardized way to discover and use multiple capabilities, especially when those capabilities may be shared across different AI applications.

MCP can also sit on top of existing APIs rather than replacing them.

---

## Q3. What is the main advantage of MCP?

The main advantage is **standardized AI-to-capability integration**.

The AI application does not need to define a completely different integration mechanism for every MCP-enabled capability.

---

## Q4. What exactly does MCP standardize?

MCP standardizes the interaction between an MCP client and MCP server, including concepts such as:

- Session lifecycle
- Capability negotiation
- Tool discovery
- Tool invocation
- Resource access
- Prompt retrieval
- Message exchange

The underlying business logic remains the responsibility of the server.

---

## Q5. Is MCP an API?

MCP is a protocol rather than a business API.

An MCP server can expose tools that internally call REST APIs, databases, SDKs, or other services.

---

## Q6. Is MCP an alternative to REST?

No.

REST is commonly used for service-to-service communication.

MCP provides a standardized interface for AI applications to interact with tools and context.

They can work together.

---

## Q7. What is the difference between MCP and function calling?

Function calling allows an LLM to request that an application execute a defined function.

MCP defines a standardized client-server protocol for discovering and interacting with capabilities.

Function calling can therefore be used **with** MCP.

A common architecture is:

```text
LLM
 |
 | tool call
 v
Application
 |
 | MCP
 v
MCP Server
 |
 v
Tool
```

---

## Q8. Who decides which MCP tool to call?

The LLM typically decides which tool is appropriate based on:

- User request
- Tool name
- Tool description
- Input schema
- Conversation context

The application then performs the MCP call.

The MCP server executes the actual capability.

---

## Q9. Does MCP itself contain an LLM?

No.

MCP is a protocol.

The LLM is a separate component of the AI application.

---

## Q10. Does the LLM communicate directly with the MCP server?

Typically, the application/host uses an MCP client to communicate with the MCP server.

```text
LLM
 |
Host / AI Application
 |
MCP Client
 |
MCP Server
```

The client handles the MCP protocol communication.

---

## Q11. What is the difference between a host and a client?

The **host** is the AI application.

The **client** is the MCP component within that application that maintains the connection to an MCP server.

A host can use MCP clients to connect to one or more servers.

---

## Q12. What is a transport in MCP?

A transport is the mechanism used to carry MCP messages between the client and server.

Examples include:

- stdio
- Streamable HTTP
- legacy SSE

The transport does not define the business capability. It only provides the communication channel.

---

## Q13. Why are we using stdio?

stdio is convenient for local MCP servers.

The client starts the server as a subprocess and communicates with it through standard input and output.

It is simple and does not require a network endpoint.

---

## Q14. Is stdio the only MCP transport?

No.

For current MCP implementations, the main transports to know are:

- **stdio** for local process-based integrations
- **Streamable HTTP** for remote/deployed servers
- **SSE** for compatibility with older implementations

Streamable HTTP is the preferred approach for new remote deployments.

---

## Q15. Can an MCP server be remote?

Yes.

A remote MCP server can be exposed through Streamable HTTP.

The architecture can then look like:

```text
AI Application
      |
MCP Client
      |
HTTP
      |
MCP Server
      |
External Systems
```

---

## Q16. What happens during MCP initialization?

The client and server establish the MCP session and negotiate the protocol capabilities they support.

Only after the session is initialized should normal MCP operations proceed.

---

## Q17. How does the client know what tools are available?

The client uses MCP tool discovery.

Conceptually:

```text
Client
  |
  | tools/list
  v
Server
  |
  | Tool definitions
  v
Client
```

The definitions include information such as names, descriptions, and input schemas.

---

## Q18. Can one MCP server expose multiple tools?

Yes.

A server can expose multiple related capabilities.

The number and type of tools depend on what the server is designed to provide.

---

## Q19. Can an application connect to multiple MCP servers?

Yes.

For example:

```text
AI Application
      |
      +-- MCP Server → Jira
      |
      +-- MCP Server → GitHub
      |
      +-- MCP Server → Database
      |
      +-- MCP Server → Internal APIs
```

This is one of the useful architectural benefits of having a standardized protocol.

---

## Q20. What are Tools, Resources and Prompts?

A simple distinction is:

```text
Tools
→ Callable capabilities

Resources
→ Readable data/context

Prompts
→ Reusable prompt templates
```

They serve different purposes within MCP.

---

## Q21. Is MCP RAG?

No.

RAG is a retrieval architecture used to retrieve relevant information for an LLM.

MCP is a protocol for connecting AI applications with capabilities and context providers.

They can be combined.

---

## Q22. Is MCP an agent framework?

No.

An agent is an application pattern involving reasoning, tool selection, execution, observation, and further reasoning.

MCP can provide the tools that an agent uses.

---

## Q23. Is MCP the same as LangChain tools?

No.

LangChain provides application and agent abstractions, including tools.

MCP provides a standardized protocol for connecting AI applications to external capabilities.

A LangChain agent can use MCP tools through an MCP client.

---

## Q24. Can MCP access databases?

Yes.

An MCP server can expose database operations through tools or resources.

The server can control what queries or operations are allowed.

---

## Q25. Can MCP modify external systems?

Yes.

An MCP tool can perform write operations or other side effects.

For example:

```text
create_ticket()
update_customer()
send_email()
```

However, write-capable tools require appropriate authorization and safeguards.

---

## Q26. Is MCP only for a particular LLM provider?

No.

MCP is independent of the LLM provider.

The AI application can use different model providers while using MCP to connect to MCP servers.

---

## Q27. What happens if the MCP server is unavailable?

The client cannot execute capabilities provided by that server.

A production application should handle:

- Connection failures
- Timeouts
- Retries where appropriate
- Tool errors
- User-facing failure messages

---

## Q28. What happens if the LLM selects the wrong tool?

The application should not assume that every model-generated tool call is correct.

Production systems should use:

- Clear tool descriptions
- Strong input schemas
- Argument validation
- Authorization
- Error handling
- Guardrails where necessary

The MCP server should also enforce its own validation and permissions.

---

## Q29. Why not create one large tool instead of many small tools?

Smaller, well-defined tools are generally easier for both applications and models to understand and reuse.

A large tool can become difficult to describe, validate, secure, and maintain.

Tool boundaries should reflect meaningful capabilities.

---

## Q30. Is MCP always the right choice?

No.

MCP may not be necessary when:

- The application is small.
- There are only a few tightly coupled functions.
- The tools are used by only one application.
- Direct function calls are simpler.
- There is no need for standardized capability discovery or reuse.

The architecture should determine whether MCP adds value.

---