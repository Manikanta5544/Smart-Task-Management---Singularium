# Smart Task Analyzer
Intelligent Prioritization System for Complex Task Workflows

![Project Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)


Smart Task Analyzer is a full-stack application that intelligently evaluates and prioritizes tasks using urgency, importance, effort, and dependency networks. The backend is powered by Django, while the frontend is built using pure HTML, CSS, and JavaScript for a lightweight and responsive user experience.

This project was developed for the Singularium Internship Assignment 2025, focusing on scoring algorithms, backend API design, critical thinking, and test coverage.

# Setup Instructions
## Backend Setup
```bash
cd backend
pip install -r requirements.txt
python manage.py runserver 
```

Backend runs at:
```bash
http://127.0.0.1:8000
```

## Frontend Setup

No build tools are required.
Simply open:
```bash
frontend/index.html
```
in any modern browser.

# Algorithm Explanation 

The Smart Task Analyzer utilizes a weighted, multi-factor scoring algorithm designed to evaluate tasks across four fundamental dimensions: urgency, importance, effort, and dependency influence. These dimensions were chosen because they represent the most common real-world factors that affect task prioritization in personal workflows, engineering teams, and project management systems.

Urgency is computed using the difference between the current date and a task’s due date. If a task is overdue, it receives a substantial urgency boost, indicating its immediate importance. Tasks due soon maintain high urgency, calculated using an inverse decay function that gradually reduces urgency for further deadlines. Tasks with invalid or missing dates are handled safely and assigned a neutral urgency value. This ensures robustness even when user input is inconsistent.

Importance reflects the criticality of a task, ranging between 1 and 10. Instead of using this value directly, the algorithm applies a normalization factor by raising it to the power of 0.9. This prevents extremely high importance values from overshadowing all other factors, while still preserving their influence.

Effort is represented as estimated hours and is intentionally inverted using a logarithmic function. Smaller effort values produce higher normalized scores, encouraging “quick wins.” This technique prevents tasks requiring large effort from unfairly dominating the priority list while still factoring them into the calculation.

Dependency Influence models how many other tasks depend on a given task. Tasks that unblock more downstream work receive higher dependency scores. A logarithmic scale is applied to maintain diminishing returns, ensuring a task with five dependents is proportionally more important than one with two—but not disproportionately so.

These components are combined through weighted scoring strategies. The project supports four strategies: Smart Balance, Fastest Wins, High Impact, and Deadline Driven. Each strategy assigns different weights to the four dimensions, allowing the system to adapt to various work environments. For example, “Fastest Wins” favors low-effort tasks, while “Deadline Driven” heavily emphasizes urgency.

To produce meaningful output, tasks are sorted by final score and then by nearest due date as a tie-breaker. Tasks with missing fields are gracefully supported, and all operations employ defensive programming to avoid runtime errors. The system also features cycle detection to prevent circular dependencies from corrupting the evaluation process.

Overall, the algorithm balances flexibility, robustness, and interpretability while providing actionable recommendations for users.

# Design Decisions
1. Pure JavaScript Frontend

  Chosen to keep the project lightweight, dependency-free, and easy to evaluate. No frameworks required.

2. Defensive Backend Architecture

  All numeric fields (importance, estimated_hours) tolerate None, strings, or invalid formats through safe conversion and fallback defaults.

3. Logarithmic Modeling

  Effort and dependency influence use logarithmic scales for natural diminishing effects and realistic priority distribution.

4. Strategy-Based Scoring

  Implementing multiple strategies avoids a “one-size-fits-all” approach and supports broader task management styles.

5. Simplicity Over Abstraction

Function-based views in Django were chosen for readability and clarity instead of more abstract ViewSets or class-based models.

# Time Breakdown
Component	Time Spent
Architecture and analysis ~ 2 hours
Backend Development	~2 hours
Frontend Development	~1 hour
Testing & Edge-Case Coverage	~20–30 minutes
Documentation & Polishing	~15 minutes

# Bonus Challenges Attempted
The assignment provides optional bonus prompts. The following were addressed:

## Comprehensive unit test suite covering:

  1. Missing fields
  2. None values
  3. Invalid dates
  4. Circular dependencies
  5. Strategy variation
 
## Dependency Graph Visualization 

  ### A complete graph-based representation of task dependencies was built, including:
    1. Directed graph structure showing task flows
    2. Node grouping (critical, leaf, root, independent, normal)
    3. Automatic detection & highlighting of circular dependencies
    4. Click-to-highlight corresponding task in list
    5. Export as PNG
    6. Toggle physics, auto-fit, and dynamic layout
    7. Visually accurate representation of each task’s blocking impact 

## Recommendation limits

Other bonus ideas (ML model, visualizations) are documented but not implemented due to time constraints.

# Future Improvements

  - Integrate a machine learning model to adjust task priority weights over time based on user behavior.

  - Overhaul UI/UX with a more modern, responsive, and animated interface.

  - Add API caching, rate limiting, and OAuth authentication for improved security and scalability.

  - Introduce persistent storage for saving and managing long-term task lists.

  - Add visualizations such as dependency graphs or task timelines.

  - Provide import/export features for task configuration.

# Project Structure
```bash
backend/
│── tasks/
│   ├── scoring.py
│   ├── tests.py
│   └── urls.py
│   ├── views.py
│── taskmanager/
│   └── settings.py
│   └── urls.py
│── manage.py
frontend/
│── index.html
│── script.js
│── styles.css
README.md
```



