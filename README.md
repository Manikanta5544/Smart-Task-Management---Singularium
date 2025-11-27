##!SECTION --- Test cases for testing this:
[
  {
    "id": "critical_overdue",
    "title": "Fix production server crash",
    "due_date": "2024-11-20",
    "estimated_hours": 8,
    "importance": 10,
    "dependencies": ["monitoring_setup", "backup_system"]
  },
  {
    "id": "quick_win",
    "title": "Update README documentation",
    "due_date": null,
    "estimated_hours": 1,
    "importance": 4,
    "dependencies": []
  },
  {
    "id": "high_impact_blocker",
    "title": "Design new architecture",
    "due_date": "2025-12-15",
    "estimated_hours": 20,
    "importance": 9,
    "dependencies": []
  },
  {
    "id": "urgent_medium_importance",
    "title": "Prepare client demo",
    "due_date": "2025-11-28",
    "estimated_hours": 6,
    "importance": 7,
    "dependencies": ["critical_overdue"]
  },
  {
    "id": "low_priority_far_deadline",
    "title": "Research new technologies",
    "due_date": "2026-01-30",
    "estimated_hours": 15,
    "importance": 5,
    "dependencies": ["high_impact_blocker"]
  },
  {
    "id": "medium_effort_high_value",
    "title": "Implement user authentication",
    "due_date": "2025-12-10",
    "estimated_hours": 12,
    "importance": 8,
    "dependencies": []
  },
  {
    "id": "minimal_task",
    "title": "Test task with minimal data",
    "due_date": null,
    "estimated_hours": null,
    "importance": null,
    "dependencies": []
  },
  {
    "id": "dependency_chain_start",
    "title": "Setup development environment",
    "due_date": "2025-12-01",
    "estimated_hours": 4,
    "importance": 6,
    "dependencies": []
  },
  {
    "id": "multiple_dependencies",
    "title": "Deploy to staging",
    "due_date": "2025-12-05",
    "estimated_hours": 3,
    "importance": 7,
    "dependencies": ["medium_effort_high_value", "dependency_chain_start"]
  },
  {
    "id": "week_deadline",
    "title": "Complete sprint review",
    "due_date": "2025-12-04",
    "estimated_hours": 2,
    "importance": 6,
    "dependencies": ["multiple_dependencies"]
  },
  {
    "id": "extremely_overdue",
    "title": "Q3 financial report",
    "due_date": "2024-09-30",
    "estimated_hours": 10,
    "importance": 8,
    "dependencies": []
  },
  {
    "id": "zero_effort_task",
    "title": "Quick email response",
    "due_date": "2025-11-28",
    "estimated_hours": 0.5,
    "importance": 3,
    "dependencies": []
  },
  {
    "id": "maximum_importance",
    "title": "Security vulnerability patch",
    "due_date": "2025-11-27",
    "estimated_hours": 6,
    "importance": 10,
    "dependencies": []
  },
  {
    "id": "complex_dependency_web",
    "title": "Launch final product",
    "due_date": "2025-12-20",
    "estimated_hours": 40,
    "importance": 10,
    "dependencies": ["critical_overdue", "high_impact_blocker", "medium_effort_high_value", "multiple_dependencies"]
  },
  {
    "id": "no_due_date_high_importance",
    "title": "Long-term strategic planning",
    "due_date": null,
    "estimated_hours": 25,
    "importance": 9,
    "dependencies": []
  }
]