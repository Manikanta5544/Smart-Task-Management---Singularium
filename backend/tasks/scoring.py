from datetime import datetime, date
from typing import List, Dict, Tuple
import math
from collections import defaultdict

STRATEGIES = {
    "smart_balance": {"urgency": 0.35, "importance": 0.35, "effort": 0.15, "dependency": 0.15},
    "fastest_wins": {"urgency": 0.10, "importance": 0.20, "effort": 0.60, "dependency": 0.10},
    "high_impact": {"urgency": 0.15, "importance": 0.60, "effort": 0.05, "dependency": 0.20},
    "deadline_driven": {"urgency": 0.60, "importance": 0.20, "effort": 0.10, "dependency": 0.10},
}

def detect_circular_dependencies(tasks: List[Dict]) -> Tuple[bool, List]:
    graph = {task['id']: set(task.get('dependencies', [])) for task in tasks}
    visited = set()
    recursion_stack = set()
    cycles = []

    def dfs(node, path):
        if node in recursion_stack:
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return
        if node in visited:
            return
        
        visited.add(node)
        recursion_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor in graph:
                dfs(neighbor, path + [node])
        
        recursion_stack.remove(node)
    
    for node in graph:
        if node not in visited:
            dfs(node, [])
    
    return len(cycles) > 0, cycles

def calculate_task_score(task: Dict, weights: Dict, blocking_counts: Dict, max_blockers: int) -> Dict:
    today = date.today()
    
    due_date = task.get('due_date')
    importance = max(1, min(10, task.get('importance', 5)))
    estimated_hours = max(0.5, task.get('estimated_hours', 4))
    
    urgency_score = 0.1
    urgency_details = ""
    
    if due_date:
        try:
            due = datetime.strptime(due_date, '%Y-%m-%d').date()
            days_diff = (due - today).days
            
            if days_diff < 0:
                urgency_score = min(1.5, 1.0 + (abs(days_diff) / 7.0) * 0.3)
                urgency_details = f"Overdue by {abs(days_diff)} days"
            else:
                urgency_score = 1.0 / (1.0 + (days_diff / 7.0))
                urgency_details = f"Due in {days_diff} days"
        except:
            urgency_details = "Invalid date"
    
    importance_score = (importance / 10.0) ** 0.9
    effort_score = 1.0 / (1.0 + math.log(estimated_hours + 1))
    
    blocking_count = blocking_counts.get(task['id'], 0)
    dependency_score = math.log(1 + (blocking_count / max(1, max_blockers)) * 5) / math.log(6)
    
    weighted_score = (
        urgency_score * weights['urgency'] +
        importance_score * weights['importance'] +
        effort_score * weights['effort'] +
        dependency_score * weights['dependency']
    )
    
    priority_score = min(100, max(0, round(weighted_score * 100, 2)))
    
    explanation_parts = []
    if urgency_details:
        explanation_parts.append(urgency_details)
    explanation_parts.append(f"Importance: {importance}/10")
    explanation_parts.append(f"Effort: {estimated_hours}h")
    if blocking_count > 0:
        explanation_parts.append(f"Blocks {blocking_count} tasks")
    
    return {
        'priority_score': priority_score,
        'explanation': ' | '.join(explanation_parts),
        'urgency_score': round(urgency_score, 3),
        'importance_score': round(importance_score, 3),
        'effort_score': round(effort_score, 3),
        'dependency_score': round(dependency_score, 3)
    }

def analyze_tasks(tasks: List[Dict], strategy: str = "smart_balance") -> List[Dict]:
    if not tasks:
        return []
    
    if strategy not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy}. Available: {list(STRATEGIES.keys())}")
    
    valid_tasks = []
    for task in tasks:
        if not task.get('id'):
            continue  
        if not task.get('title'):
            task['title'] = f"Untitled Task {task['id']}"
        valid_tasks.append(task)
    
    if not valid_tasks:
        return []
    
    weights = STRATEGIES.get(strategy, STRATEGIES["smart_balance"])
    
    blocking_counts = defaultdict(int)
    for task in tasks:
        for dep_id in task.get('dependencies', []):
            blocking_counts[dep_id] += 1
    
    max_blockers = max(blocking_counts.values()) if blocking_counts else 1
    
    scored_tasks = []
    for task in tasks:
        score_data = calculate_task_score(task, weights, blocking_counts, max_blockers)
        scored_task = {**task, **score_data}
        scored_tasks.append(scored_task)
    
    scored_tasks.sort(key=lambda x: (-x['priority_score'], x.get('due_date', '9999-12-31')))
    return scored_tasks

def get_top_recommendations(tasks: List[Dict], strategy: str = "smart_balance", limit: int = 3) -> List[Dict]:
    analyzed_tasks = analyze_tasks(tasks, strategy)
    
    recommendations = []
    for i, task in enumerate(analyzed_tasks[:limit], 1):
        reasoning = generate_recommendation_reasoning(task, i)
        recommendations.append({
            'rank': i,
            'task': {
                'id': task['id'],
                'title': task['title'],
                'priority_score': task['priority_score'],
                'due_date': task.get('due_date'),
                'estimated_hours': task.get('estimated_hours'),
                'importance': task.get('importance')
            },
            'explanation': task['explanation'],
            'reasoning': reasoning
        })
    
    return {
        'recommendations': recommendations,
        'strategy_used': strategy,
        'total_tasks_analyzed': len(analyzed_tasks),
        'timestamp': datetime.now().isoformat()
    }

def generate_recommendation_reasoning(task: Dict, rank: int) -> str:


    factors = []
    
    if task['urgency_score'] > 0.8:
        factors.append("High urgency")
    elif task['urgency_score'] > 0.6:
        factors.append("Approaching deadline")
    
    if task['importance_score'] > 0.8:
        factors.append("Critical importance")
    elif task['importance_score'] > 0.6:
        factors.append("High impact")
    
    if task['effort_score'] > 0.7:
        factors.append("Quick win")
    
    if task['dependency_score'] > 0.5:
        factors.append("Blocks other work")
    
    if not factors:
        factors.append("Well-balanced")
    
    return f"Rank #{rank} - Score: {task['priority_score']}/100. Key factors: {', '.join(factors)}"

def validate_task_data(task: Dict) -> Tuple[bool, str]:
    if not task.get('id'):
        return False, "Task missing 'id'"
    if not task.get('title'):
        return False, "Task missing 'title'"
    return True, "Valid"