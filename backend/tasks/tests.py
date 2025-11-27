from django.test import TestCase
from datetime import date, timedelta
from .scoring import analyze_tasks, detect_circular_dependencies, get_top_recommendations

class TaskScoringTest(TestCase):
    def setUp(self):
        self.sample_tasks = [
            {
                "id": "task1",
                "title": "Urgent important task",
                "due_date": (date.today() + timedelta(days=1)).isoformat(),
                "estimated_hours": 2,
                "importance": 9,
                "dependencies": []
            },
            {
                "id": "task2",
                "title": "Low priority task", 
                "due_date": (date.today() + timedelta(days=30)).isoformat(),
                "estimated_hours": 8,
                "importance": 3,
                "dependencies": ["task1"]
            },
            {
                "id": "task3",
                "title": "Quick win task",
                "due_date": None,
                "estimated_hours": 1,
                "importance": 6,
                "dependencies": []
            }
        ]

    def test_analyze_tasks_returns_prioritized_list(self):
        result = analyze_tasks(self.sample_tasks)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["id"], "task1")
        self.assertGreater(result[0]["priority_score"], result[1]["priority_score"])

    def test_circular_dependency_detection(self):
        circular_tasks = [
            {"id": "a", "dependencies": ["b"]},
            {"id": "b", "dependencies": ["a"]}
        ]
        has_cycle, cycles = detect_circular_dependencies(circular_tasks)
        self.assertTrue(has_cycle)
        self.assertEqual(len(cycles), 1)

    def test_no_circular_dependencies(self):
        has_cycle, cycles = detect_circular_dependencies(self.sample_tasks)
        self.assertFalse(has_cycle)
        self.assertEqual(len(cycles), 0)

    def test_get_top_recommendations(self):
        result = get_top_recommendations(self.sample_tasks, limit=2)
        if isinstance(result, dict):
            recommendations =result['recommendations']
        else:
            recommendations = result    
        self.assertEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0]["rank"], 1)
        self.assertIn("reasoning", recommendations[0])

    def test_different_strategies(self):
        fast_wins = analyze_tasks(self.sample_tasks, "fastest_wins")
        high_impact = analyze_tasks(self.sample_tasks, "high_impact")
        
        self.assertNotEqual(fast_wins[0]["id"], high_impact[0]["id"])

    def test_task_with_missing_fields(self):
        incomplete_task = [{"id": "test", "title": "Test task"}]
        result = analyze_tasks(incomplete_task)
        self.assertEqual(len(result), 1)
        self.assertIn("priority_score", result[0])