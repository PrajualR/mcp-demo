import asyncio
import json
import os

from dotenv import load_dotenv
from groq import Groq

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")


MODEL = "openai/gpt-oss-120b"
TEMPERATURE = 0.2

groq = Groq(api_key=GROQ_API_KEY)


server_params = StdioServerParameters(
    command="uv",
    args=[
        "run",
        "mcp",
        "run",
        "src/server/server.py",
    ],
)


def convert_mcp_tools_to_groq(mcp_tools):
    tools = []

    for tool in mcp_tools:
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.input_schema,
                },
            }
        )

    return tools


def extract_mcp_result(result):
    output = []

    for content in result.content:
        if hasattr(content, "text"):
            output.append(content.text)
        else:
            output.append(str(content))

    return "\n".join(output)


async def main():

    print("=" * 60)
    print("MCP + GROQ DEMO")
    print("=" * 60)

    print("\nConnecting to MCP server...")

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            # Initialize MCP session
            await session.initialize()

            print("Connected to MCP server.")

            # Discover tools exposed by the MCP server
            response = await session.list_tools()
            mcp_tools = response.tools

            print("\nMCP tools discovered:")

            for tool in mcp_tools:
                print(f"  - {tool.name}")

            # Convert MCP tool schemas to Groq tool format
            groq_tools = convert_mcp_tools_to_groq(mcp_tools)

            user_question = """
Analyze all projects and identify which projects are
currently At Risk or Delayed.

For each affected project:

1. Identify the project owner.
2. Find unresolved High or Critical priority tickets.
3. Summarize the major risks.

Finally, determine which project requires the most
immediate attention and explain why.
"""

            print("\n")
            print("=" * 60)
            print("USER QUESTION")
            print("=" * 60)

            print(user_question)

            messages = [
                {
                    "role": "system",
                    "content": """
You are an enterprise project intelligence assistant.

You have access to project, employee and ticket information
through MCP tools.

Use the available tools whenever you need information.

Do not invent project, employee or ticket information.

For complex questions, perform all necessary tool calls
before producing the final answer.

Analyze the information returned by the tools and provide
a clear explanation of your reasoning.
"""
                },
                {
                    "role": "user",
                    "content": user_question
                }
            ]

            while True:

                print("\nCalling Groq...")

                response = groq.chat.completions.create(
                    model=MODEL,
                    temperature=TEMPERATURE,
                    messages=messages,
                    tools=groq_tools,
                    tool_choice="auto",
                )

                assistant_message = response.choices[0].message

                if not assistant_message.tool_calls:

                    print("\n")
                    print("=" * 60)
                    print("FINAL ANSWER")
                    print("=" * 60)

                    print(assistant_message.content)

                    break

                messages.append(assistant_message)

                # Execute the MCP tools selected by the LLM
                for tool_call in assistant_message.tool_calls:

                    tool_name = tool_call.function.name
                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                    print("\n")
                    print("-" * 60)
                    print("LLM REQUESTED MCP TOOL")
                    print("-" * 60)

                    print(f"Tool      : {tool_name}")
                    print(f"Arguments : {arguments}")

                    result = await session.call_tool(
                        tool_name,
                        arguments,
                    )

                    result_text = extract_mcp_result(result)

                    print("\nMCP RESULT:")
                    print(result_text)

                    # Return the MCP result to the LLM
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_text,
                        }
                    )


if __name__ == "__main__":
    asyncio.run(main())