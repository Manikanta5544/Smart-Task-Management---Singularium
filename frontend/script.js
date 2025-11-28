class TaskManager {
    constructor() {
        this.tasks = [];
        this.BACKEND_URL = 'http://127.0.0.1:8000'; 
        this.network = null;
        this.graphData = null;
        this.physicsEnabled = true;
        this.initializeEventListeners();
        this.updateTaskCount();
    }

    initializeEventListeners() {
        document.getElementById('taskForm').addEventListener('submit', (e) => this.handleAddTask(e));
        document.getElementById('analyzeBtn').addEventListener('click', () => this.analyzeTasks());
        document.getElementById('suggestBtn').addEventListener('click', () => this.getSuggestions());
        document.getElementById('loadJson').addEventListener('click', () => this.loadFromJson());
        document.getElementById('clearTasks').addEventListener('click', () => this.clearTasks());
        document.getElementById('showGraphBtn').addEventListener('click', () => this.showDependencyGraph());
        document.getElementById('fitGraphBtn').addEventListener('click', () => this.fitGraph());
        document.getElementById('exportGraphBtn').addEventListener('click', () => this.exportGraph());
        document.getElementById('togglePhysicsBtn').addEventListener('click', () => this.togglePhysics());
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
    async showDependencyGraph() {
    if (this.tasks.length === 0) {
        this.showError("No tasks to visualize");
        return;
    }

    this.showLoading();

    try {
        const tasksJson = encodeURIComponent(JSON.stringify(this.tasks));

        const response = await fetch(`${this.BACKEND_URL}/api/tasks/dependency-graph/?tasks=${tasksJson}`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status} - ${response.statusText}`);
        }

        const data = await response.json();

        const graphContainer = document.getElementById("graphContainer");
        if (!graphContainer) throw new Error("graphContainer missing in HTML");

        graphContainer.classList.remove("hidden");

        setTimeout(() => {
            this.renderDependencyGraph(data.graph);
            this.displayGraphAnalysis(data.graph.analysis);
        }, 50);

    } catch (err) {
        this.showError("Failed to load dependency graph: " + err.message);
    } finally {
        this.hideLoading();
    }
}


    renderDependencyGraph(graphData) {
        const graphContainer = document.getElementById('graphContainer');
        const graphNetwork = document.getElementById('graphNetwork');
        
        if (!graphContainer || !graphNetwork) return;

        graphContainer.classList.remove('hidden');

        if (this.network) {
            this.network.destroy();
        }

        const isDarkMode = document.body.classList.contains('dark');

        const nodes = new vis.DataSet(graphData.nodes.map(node => ({
            id: node.id,
            label: node.label.length > 22 ? node.label.substring(0, 22) + '...' : node.label,
            group: node.group,
            value: node.value,
            title: node.title,
            shape: 'dot',
            size: 18 + (node.value * 1.6),
            
            font: {
                size: 15,
                color: isDarkMode ? "#f1f5f9" : "#1f2937",
                face: "Inter",
                bold: false,
                strokeWidth: 1.2,
                strokeColor: isDarkMode ? "rgba(0,0,0,0.55)" : "rgba(255,255,255,0.55)"
            },

            color: this.getNodeColor(node.group),
            borderWidth: 2,
            shadow: {
                enabled: true,
                color: isDarkMode ? "rgba(0,0,0,0.35)" : "rgba(0,0,0,0.15)",
                size: 12,
                x: 0,
                y: 3
            }
        })));


        const edges = new vis.DataSet(graphData.edges.map(edge => ({
            from: edge.from,
            to: edge.to,
            arrows: 'to',
            color: {
                color: isDarkMode ? "rgba(140,180,255,0.75)" : "rgba(37,99,235,0.70)",
                highlight: isDarkMode ? "#90b4ff" : "#2563eb",
                hover: isDarkMode ? "#90b4ff" : "#2563eb"
            },
            width: 2,
            smooth: {
                enabled: true,
                type: "continuous"
            },
            shadow: {
                enabled: true,
                color: isDarkMode ? "rgba(0,0,0,0.4)" : "rgba(0,0,0,0.15)",
                size: 8,
                x: 0,
                y: 2
            }
        })));




        const container = graphNetwork;
        const data = { nodes, edges };
        
       const options = {
            layout: { improvedLayout: true },

            physics: {
                enabled: this.physicsEnabled,
                stabilization: { iterations: 120 }
            },

            interaction: {
                dragNodes: true,
                dragView: true,
                zoomView: true
            },

            groups: {
                critical: {
                    color: { background: "#ff6b6b", border: "#d84747" },
                    font: { color: "#ffffff", size: 16, bold: true }
                },
                root: {
                    color: { background: "#4ade80", border: "#2f9e57" },
                    font: { color: "#ffffff", size: 15 }
                },
                leaf: {
                    color: { background: "#60a5fa", border: "#3b82f6" },
                    font: { color: "#ffffff", size: 15 }
                },
                independent: {
                    color: { background: "#a8b1bd", border: "#8d959f" },
                    font: { color: "#ffffff", size: 14 }
                },
                normal: {
                    color: { background: "#fbbf24", border: "#d97706" },
                    font: { color: "#ffffff", size: 15 }
                }
            },

            nodes: {
                shadow: {
                    enabled: true,
                    size: 12,
                    x: 1,
                    y: 2
                }
            },

            edges: {
                smooth: { enabled: true, type: "continuous" },
                color: { color: "#6ea8fe" },
                width: 2,
                shadow: true
            }
        };


        this.network = new vis.Network(container, data, options);

        this.network.on('click', (params) => {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                this.highlightTaskInList(nodeId);
            }
        });

        this.network.on('stabilizationIterationsDone', () => {
            this.fitGraph();
        });
    }

    getNodeColor(group) {
        const colors = {
            critical: { background: '#e74c3c', border: '#c0392b' },
            root: { background: '#27ae60', border: '#219a52' },
            leaf: { background: '#3498db', border: '#2980b9' },
            independent: { background: '#95a5a6', border: '#7f8c8d' },
            normal: { background: '#f39c12', border: '#d68910' }
        };
        return colors[group] || colors.normal;
    }

    displayGraphAnalysis(analysis) {
        const analysisContainer = document.getElementById('graphAnalysis');
        if (!analysisContainer) return;

        let analysisHTML = `
            <h4>Dependency Analysis</h4>
            <div class="analysis-item">
                <strong>Total Tasks:</strong> ${analysis.total_tasks}
            </div>
            <div class="analysis-item">
                <strong>Total Dependencies:</strong> ${analysis.total_dependencies}
            </div>
        `;

        if (analysis.circular_dependencies.length > 0) {
            analysisHTML += `
                <div class="circular-warning">
                    <strong> Circular Dependencies Detected!</strong>
                    <div>${analysis.circular_dependencies.map(cycle => cycle.join(' → ')).join('<br>')}</div>
                </div>
            `;
        }

        if (analysis.critical_tasks.length > 0) {
            analysisHTML += `
                <div class="analysis-item">
                    <strong>Critical Tasks (Block ≥ 3 others):</strong> ${analysis.critical_tasks.join(', ')}
                </div>
            `;
        }

        if (analysis.root_tasks.length > 0) {
            analysisHTML += `
                <div class="analysis-item">
                    <strong>Root Tasks (No dependencies):</strong> ${analysis.root_tasks.join(', ')}
                </div>
            `;
        }

        analysisContainer.innerHTML = analysisHTML;
    }

    highlightTaskInList(taskId) {
        const taskItems = document.querySelectorAll('.task-item');
        taskItems.forEach(item => {
            if (item.querySelector('span').textContent.startsWith(taskId + ":")) {
                item.style.backgroundColor = '#fff3cd';
                item.style.border = '2px solid #ffc107';
                setTimeout(() => {
                    item.style.backgroundColor = '';
                    item.style.border = '';
                }, 2000);
            }
        });
    }

    fitGraph() {
    if (this.network && this.network.fit) {
        try {
            this.network.fit({ animation: true });
        } catch (e) {
            console.warn("Graph fit skipped:", e);
        }
    }
}

    exportGraph() {
        if (this.network) {
            const canvas = document.querySelector('#graphNetwork canvas');
            if (canvas) {
                const link = document.createElement('a');
                link.download = 'dependency-graph.png';
                link.href = canvas.toDataURL();
                link.click();
            }
        }
    }

    togglePhysics() {
        this.physicsEnabled = !this.physicsEnabled;
        if (this.network) {
            this.network.setOptions({ physics: { enabled: this.physicsEnabled } });
        }
        
        const togglePhysicsBtn = document.getElementById('togglePhysicsBtn');
        if (togglePhysicsBtn) {
            togglePhysicsBtn.textContent = this.physicsEnabled ? 'Disable Physics' : 'Enable Physics';
        }
    }
}

const taskManager = new TaskManager();