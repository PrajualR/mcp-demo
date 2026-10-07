import json
from pathlib import Path

from mcp.server import MCPServer

mcp = MCPServer("Enterprise Project Intelligence")

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

def load_json(filename: str):
    """Load JSON data from the data directory."""

    file_path = DATA_DIR / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)



@mcp.tool()
def list_projects() -> list:
    """
    Get all projects with their current status,
    completion percentage, and project owner.
    """

    projects = load_json("projects.json")

    return [
        {
            "project_id": project["project_id"],
            "name": project["name"],
            "description": project["description"],
            "status": project["status"],
            "completion_percentage": project["completion_percentage"],
            "owner_id": project["owner_id"],
        }
        for project in projects
    ]


@mcp.tool()
def get_project(project_id: str) -> dict:
    """
    Get detailed information about a specific project
    using its project ID.
    """

    projects = load_json("projects.json")

    for project in projects:
        if project["project_id"] == project_id:
            return project

    return {
        "error": f"Project {project_id} not found"
    }


@mcp.tool()
def get_employee(employee_id: str) -> dict:
    """
    Get employee details using the employee ID.
    """

    employees = load_json("employees.json")

    for employee in employees:
        if employee["employee_id"] == employee_id:
            return employee

    return {
        "error": f"Employee {employee_id} not found"
    }


@mcp.tool()
def list_project_tickets(project_id: str) -> list:
    """
    Get all tickets associated with a specific project.
    """

    tickets = load_json("tickets.json")

    return [
        ticket
        for ticket in tickets
        if ticket["project_id"] == project_id
    ]


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

    tickets = load_json("tickets.json")

    results = tickets

    if project_id:
        results = [
            ticket
            for ticket in results
            if ticket["project_id"] == project_id
        ]

    if priority:
        results = [
            ticket
            for ticket in results
            if ticket["priority"].lower() == priority.lower()
        ]

    if status:
        results = [
            ticket
            for ticket in results
            if ticket["status"].lower() == status.lower()
        ]

    return results


if __name__ == "__main__":
    mcp.run()