class TaskManager {
    constructor() {
        this.tasks = [];
        this.BACKEND_URL = 'http://127.0.0.1:8000'; 
        this.initializeEventListeners();
        this.updateTaskCount();
    }

    initializeEventListeners() {
        document.getElementById('taskForm').addEventListener('submit', (e) => this.handleAddTask(e));
        document.getElementById('analyzeBtn').addEventListener('click', () => this.analyzeTasks());
        document.getElementById('suggestBtn').addEventListener('click', () => this.getSuggestions());
        document.getElementById('loadJson').addEventListener('click', () => this.loadFromJson());
        document.getElementById('clearTasks').addEventListener('click', () => this.clearTasks());
    }

    handleAddTask(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        
        const task = {
            id: formData.get('id').trim(),
            title: formData.get('title').trim(),
            due_date: formData.get('due_date') || null,
            estimated_hours: formData.get('estimated_hours') ? parseFloat(formData.get('estimated_hours')) : null,
            importance: formData.get('importance') ? parseInt(formData.get('importance')) : null,
            dependencies: formData.get('dependencies') 
                ? formData.get('dependencies').split(',').map(d => d.trim()).filter(d => d)
                : []
        };

        if (!task.id || !task.title) {
            this.showError('Task ID and Title are required');
            return;
        }

        if (this.tasks.some(t => t.id === task.id)) {
            this.showError('Task ID must be unique');
            return;
        }

        this.tasks.push(task);
        event.target.reset();
        this.renderTaskList();
        this.updateTaskCount();
    }

    loadFromJson() {
        const jsonInput = document.getElementById('jsonInput').value.trim();
        if (!jsonInput) return;

        try {
            const parsedTasks = JSON.parse(jsonInput);
            if (!Array.isArray(parsedTasks)) {
                throw new Error('Input must be a JSON array');
            }

            parsedTasks.forEach(task => {
                if (!this.tasks.some(t => t.id === task.id)) {
                    this.tasks.push(task);
                }
            });

            this.renderTaskList();
            this.updateTaskCount();
            document.getElementById('jsonInput').value = '';
        } catch (error) {
            this.showError('Invalid JSON format: ' + error.message);
        }
    }

    clearTasks() {
        this.tasks = [];
        this.renderTaskList();
        this.updateTaskCount();
    }

    async analyzeTasks() {
        if (this.tasks.length === 0) {
            this.showError('No tasks to analyze');
            return;
        }

        this.showLoading();
        const strategy = document.getElementById('strategy').value;

        try {
            const response = await fetch(`${this.BACKEND_URL}/api/tasks/analyze/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tasks: this.tasks, strategy})
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Analysis failed');
            }

            this.displayAnalysisResults(data);
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.hideLoading();
        }
    }

    async getSuggestions() {
        if (this.tasks.length === 0) {
            this.showError('No tasks to analyze');
            return;
        }

        this.showLoading();
        const strategy = document.getElementById('strategy').value;

        try {
            const tasksJson = encodeURIComponent(JSON.stringify(this.tasks));
            const response = await fetch(`${this.BACKEND_URL}/api/tasks/suggest/?tasks=${tasksJson}&strategy=${strategy}`);

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Suggestion failed');
            }

            this.displaySuggestions(data);
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.hideLoading();
        }
    }

    displayAnalysisResults(data) {
        this.hideAllResults();
        
        document.getElementById('currentStrategy').textContent = data.strategy;
        const resultsContainer = document.getElementById('tasksResults');
        
        resultsContainer.innerHTML = data.tasks.map(task => {
            const priorityClass = task.priority_score >= 75 ? 'high' : 
                                task.priority_score >= 40 ? 'medium' : 'low';
            
            return `
                <div class="priority-task ${priorityClass}">
                    <div class="task-score">${task.priority_score}/100</div>
                    <h4>${task.title}</h4>
                    <div class="task-explanation">${task.explanation}</div>
                    <div class="task-details">
                        <small>ID: ${task.id} | Due: ${task.due_date || 'No date'} | 
                        Hours: ${task.estimated_hours ?? 'N/A'} | Importance: ${task.importance ?? 'N/A'}</small>
                    </div>
                </div>
            `;
        }).join('');
        
        document.getElementById('analysisResults').classList.remove('hidden');
    }

    displaySuggestions(data) {
        this.hideAllResults();
        
        document.getElementById('suggestionStrategy').textContent = data.strategy;
        const suggestionsContainer = document.getElementById('suggestionsList');
        
        suggestionsContainer.innerHTML = data.recommendations.map(rec => {
            const task = rec.task;
            return `
                <div class="recommendation-item rank-${rec.rank}">
                    <div class="task-score">#${rec.rank} - Score: ${task.priority_score}/100</div>
                    <h4>${task.title}</h4>
                    <div class="task-explanation">${rec.explanation}</div>
                    <div class="task-reasoning">${rec.reasoning}</div>
                    <div class="task-details">
                        <small>ID: ${task.id} | Due: ${task.due_date || 'No date'} | 
                        Hours: ${task.estimated_hours ?? 'N/A'} | Importance: ${task.importance ?? 'N/A'}</small>
                    </div>
                </div>
            `;
        }).join('');
        
        document.getElementById('suggestionsResults').classList.remove('hidden');
    }

    renderTaskList() {
        const tasksList = document.getElementById('tasksList');
        tasksList.innerHTML = this.tasks.map(task => `
            <div class="task-item">
                <span>${task.id}: ${task.title}</span>
                <button class="remove-task" data-task-id="${task.id}">Remove</button>
            </div>
        `).join('');
         tasksList.querySelectorAll('.remove-task').forEach(button => {
            button.addEventListener('click', (e) => {
                const taskId = e.target.getAttribute('data-task-id');
                this.removeTask(taskId);
            });
        });
    }

    

    removeTask(taskId) {
        this.tasks = this.tasks.filter(task => task.id !== taskId);
        this.renderTaskList();
        this.updateTaskCount();
    }

    updateTaskCount() {
        document.getElementById('taskCount').textContent = this.tasks.length;
    }

    showLoading() {
        this.hideAllResults();
        document.getElementById('loading').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }

    showError(message) {
        const errorDiv = document.getElementById('error');
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
        setTimeout(() => errorDiv.classList.add('hidden'), 5000);
    }

    hideAllResults() {
        document.getElementById('analysisResults').classList.add('hidden');
        document.getElementById('suggestionsResults').classList.add('hidden');
        document.getElementById('error').classList.add('hidden');
    }
}

const taskManager = new TaskManager();