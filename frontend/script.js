// script.js
document.addEventListener('DOMContentLoaded', () => {
    // --- 1. State and Constants ---
    const API_URL = 'http://localhost:5000/api/missions';
    const IDEAS_URL = 'http://localhost:5000/api/ideas';
    const SOCKET_URL = 'http://localhost:5000';

    const appState = {
        isSidebarOpen: false,
        isExecuting: false,
        completedNodes: new Set(), // Track all completed nodes for visualization
        socket: null, // To hold the socket instance
        status: 'IDLE', // IDLE, CONNECTING, RUNNING, COMPLETED, FAILED
    };

    // --- 2. DOM Element Cache ---
    const dom = {
        body: document.body,
        sidebar: document.getElementById('sidebar'),
        sidebarToggle: document.getElementById('sidebar-toggle'),
        sidebarClose: document.getElementById('sidebar-close'),
        goalInput: document.getElementById('goal-input'),
        startButton: document.getElementById('start-button'),
        statusIndicator: document.getElementById('status-indicator'),
        logContainer: document.getElementById('log-container'),
        logPlaceholder: document.getElementById('log-placeholder'),
        finalReport: document.getElementById('final-report'),
        previousIdeasList: document.getElementById('previous-ideas-list'),
        activeMissionsList: document.getElementById('active-missions-list'),
        refreshMissionsBtn: document.getElementById('refresh-missions-btn'),
        addIdeaForm: document.getElementById('add-idea-form'),
        newIdeaInput: document.getElementById('new-idea-input'),
        connectionError: document.getElementById('connection-error'),
        logTab: new bootstrap.Tab(document.getElementById('log-tab')),
        reportTab: new bootstrap.Tab(document.getElementById('report-tab')),
        editIdeaModal: new bootstrap.Modal(document.getElementById('edit-idea-modal')),
        editIdeaId: document.getElementById('edit-idea-id'),
        editIdeaInput: document.getElementById('edit-idea-input'),
        saveIdeaBtn: document.getElementById('save-idea-btn'),
    };

    const graph = {
        nodes: document.querySelectorAll('.graph-node'),
        connectors: document.querySelectorAll('.connector'),
    };

    const templates = {
        emptyReport: `
            <div class="empty-state">
                <i class="bi bi-file-earmark-text"></i>
                <span>The final report will appear here.</span>
            </div>`,
        emptyLog: `
            <div class="empty-state" id="log-placeholder">
                <i class="bi bi-terminal"></i>
                <span>Execution logs will appear here...</span>
            </div>`,
    };

    // --- 3. UI Update Functions ---
    const ui = {
        toggleSidebar(isOpen) {
            appState.isSidebarOpen = isOpen;
            dom.sidebar.classList.toggle('is-open', isOpen);
            dom.sidebar.classList.toggle('is-closed', !isOpen);
        },
        setExecuting(isExecuting) {
            appState.isExecuting = isExecuting;
            dom.startButton.disabled = isExecuting;
            dom.goalInput.disabled = isExecuting;
        },
        updateStatus(status, color, connected) {
            appState.status = status;
            const icons = {
                IDLE: 'bi-broadcast', CONNECTING: 'bi-plug', RUNNING: 'bi-gear-wide-connected',
                COMPLETED: 'bi-check-circle', FAILED: 'bi-exclamation-triangle-fill'
            };
            const pulseClass = (status === 'RUNNING' || status === 'CONNECTING') ? 'animate-pulse' : '';
            const dotClass = connected ? 'connected' : '';

            dom.statusIndicator.innerHTML = `
                <span class="status-badge text-bg-${color} ${pulseClass}">
                    <span class="connection-dot ${dotClass}"></span>
                    <i class="bi ${icons[status] || 'bi-question-circle'} me-1"></i>${status}
                </span>`;
        },
        logMessage(message) {
            if (dom.logPlaceholder) {
                dom.logPlaceholder.remove();
                dom.logPlaceholder = null; // Ensure it's only removed once
            }

            const msgEl = document.createElement('div');
            msgEl.className = 'log-message';
            msgEl.innerHTML = `<div class="log-content">${message}</div>`;
            dom.logContainer.appendChild(msgEl);
            dom.logContainer.scrollTop = dom.logContainer.scrollHeight;
        },
        updateGraph(nodeName) {
            // Map nodes to their preceding connectors
            const connectorMap = {
                create_plan: '1',
                execute_step: '2',
                synthesize_report: '3',
            };

            // Add the current node to the set of completed nodes
            appState.completedNodes.add(nodeName);

            // Reset all visual states
            graph.nodes.forEach(n => n.classList.remove('active', 'loading'));
            graph.connectors.forEach(c => c.classList.remove('active'));

            // Activate all completed nodes and their preceding connectors
            appState.completedNodes.forEach(completedNode => {
                document.querySelector(`[data-node="${completedNode}"]`)?.classList.add('active');
                const connectorId = connectorMap[completedNode];
                if (connectorId) {
                    document.querySelector(`[data-connector="${connectorId}"]`)?.classList.add('active');
                }
            });

            // Set the current node to a 'loading' state
            const activeNode = document.querySelector(`[data-node="${nodeName}"]`);
            if (activeNode) activeNode.classList.add('loading');
        },
        reset() {
            dom.logContainer.innerHTML = templates.emptyLog;
            dom.logPlaceholder = document.getElementById('log-placeholder'); // Re-cache
            dom.finalReport.innerHTML = templates.emptyReport;
            this.setExecuting(false);
            appState.completedNodes.clear();
            this.updateStatus('IDLE', 'secondary', false);
            dom.connectionError.classList.add('d-none');
            graph.nodes.forEach(n => n.classList.remove('active', 'loading'));
            graph.connectors.forEach(c => c.classList.remove('active'));
            dom.logTab.show();
            this.toggleSidebar(true); // Start with sidebar open by default
        }
    };

    // --- 4. Data & Event Handling ---
    async function fetchAndRenderMissions() {
        try {
            const response = await fetch(API_URL);
            if (!response.ok) throw new Error('Failed to fetch missions.');
            const missions = await response.json();

            dom.activeMissionsList.innerHTML = ''; // Clear loading message
            if (missions.length === 0) {
                dom.activeMissionsList.innerHTML = '<li class="list-group-item bg-transparent text-muted small">No active missions.</li>';
                return;
            }

            missions.forEach(mission => {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center bg-transparent border-secondary';
                li.innerHTML = `
                    <div class="text-truncate me-2">
                        <span class="d-block text-truncate" title="${mission.goal}">${mission.goal}</span>
                        <small class="text-muted">${mission.status}</small>
                    </div>
                    <button class="btn btn-sm btn-outline-danger flex-shrink-0 delete-mission-btn" data-mission-id="${mission.id}" title="Delete Mission">
                        <i class="bi bi-trash"></i>
                    </button>`;
                dom.activeMissionsList.appendChild(li);
            });
        } catch (error) {
            console.error('Error fetching missions:', error);
            dom.activeMissionsList.innerHTML = '<li class="list-group-item bg-transparent text-danger small">Could not load missions.</li>';
        }
    }

    async function handleDeleteMission(e) {
        const deleteBtn = e.target.closest('.delete-mission-btn');
        if (!deleteBtn) return;

        const missionId = deleteBtn.dataset.missionId;
        if (!confirm(`Are you sure you want to delete mission ${missionId}?`)) return;

        try {
            const response = await fetch(`${API_URL}/${missionId}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Failed to delete mission.');
            // Refresh the list to show the mission has been removed
            await fetchAndRenderMissions();
        } catch (error) {
            console.error('Error deleting mission:', error);
            alert('Could not delete the mission. Please check the console for details.');
        }
    }

    async function handleAddIdea(e) {
        e.preventDefault();
        const goal = dom.newIdeaInput.value.trim();
        if (!goal) return;

        try {
            const response = await fetch(IDEAS_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ goal })
            });
            if (!response.ok) throw new Error('Failed to add idea.');
            dom.newIdeaInput.value = ''; // Clear input
            await fetchAndRenderIdeas(); // Refresh list
        } catch (error) {
            console.error('Error adding idea:', error);
            alert('Could not add the new idea.');
        }
    }

    async function handleSaveIdea() {
        const id = dom.editIdeaId.value;
        const goal = dom.editIdeaInput.value.trim();
        if (!id || !goal) return;

        try {
            const response = await fetch(`${IDEAS_URL}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ goal })
            });
            if (!response.ok) throw new Error('Failed to update idea.');
            dom.editIdeaModal.hide();
            await fetchAndRenderIdeas();
        } catch (error) {
            console.error('Error updating idea:', error);
            alert('Could not update the idea.');
        }
    }

    async function fetchAndRenderIdeas() {
        try {
            const response = await fetch(IDEAS_URL);
            if (!response.ok) throw new Error('Failed to fetch ideas.');
            const ideas = await response.json();

            dom.previousIdeasList.innerHTML = ''; // Clear loading message
            if (ideas.length === 0) {
                dom.previousIdeasList.innerHTML = '<li class="list-group-item bg-transparent text-muted small">No previous ideas found.</li>';
                return;
            }

            ideas.forEach(idea => {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center bg-transparent border-secondary';
                li.innerHTML = `
                    <span class="text-truncate me-2 use-idea-btn" data-goal="${idea.goal}" title="${idea.goal}">${idea.goal}</span>
                    <div class="use-button-wrapper btn-group">
                        <button class="btn btn-sm btn-outline-secondary edit-idea-btn" data-id="${idea.id}" data-goal="${idea.goal}" title="Edit">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-idea-btn" data-id="${idea.id}" title="Delete">
                            <i class="bi bi-trash"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-primary use-idea-btn" data-goal="${idea.goal}" title="Use">Use</button>
                    </div>
                `;
                dom.previousIdeasList.appendChild(li);
            });
        } catch (error) {
            console.error('Error fetching ideas:', error);
            dom.previousIdeasList.innerHTML = '<li class="list-group-item bg-transparent text-danger small">Could not load ideas.</li>';
        }
    }

    function handleIdeaClick(e) {
        const useBtn = e.target.closest('.use-idea-btn');
        const editBtn = e.target.closest('.edit-idea-btn');
        const deleteBtn = e.target.closest('.delete-idea-btn');

        if (editBtn) {
            dom.editIdeaId.value = editBtn.dataset.id;
            dom.editIdeaInput.value = editBtn.dataset.goal;
            dom.editIdeaModal.show();
            return;
        }

        if (deleteBtn) {
            const ideaId = deleteBtn.dataset.id;
            if (confirm('Are you sure you want to delete this idea?')) {
                fetch(`${IDEAS_URL}/${ideaId}`, { method: 'DELETE' })
                    .then(res => res.ok ? fetchAndRenderIdeas() : Promise.reject('Failed to delete'))
                    .catch(err => {
                        console.error('Error deleting idea:', err);
                        alert('Could not delete the idea.');
                    });
            }
            return;
        }

        if (!useBtn) return;

        // "Copied!" feedback
        const buttonWrapper = target.closest('li').querySelector('.use-button-wrapper');
        if (buttonWrapper) {
            const feedbackEl = document.createElement('div');
            feedbackEl.className = 'copy-feedback';
            feedbackEl.textContent = 'Copied!';
            buttonWrapper.appendChild(feedbackEl);
            setTimeout(() => feedbackEl.classList.add('show'), 10); // Show
            setTimeout(() => feedbackEl.classList.remove('show'), 1500); // Hide
            setTimeout(() => feedbackEl.remove(), 2000); // Cleanup
        }

        // Professional touch: flash the textarea to confirm selection
        dom.goalInput.classList.add('goal-flash');
        setTimeout(() => {
            dom.goalInput.classList.remove('goal-flash');
        }, 500);
    }

    async function handleExecute() {
        const goal = dom.goalInput.value.trim();
        if (!goal) {
            alert('Goal cannot be empty.');
            return;
        }

        ui.reset();
        ui.setExecuting(true);
        ui.updateStatus('CONNECTING', 'primary', true);

        // Auto-close sidebar on mobile
        if (window.innerWidth < 992) {
            ui.toggleSidebar(false);
        }

        try {
            // Use fetch to start the mission
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ goal })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const missionData = await response.json();
            console.log('Mission started:', missionData);
            // Refresh the active missions list to include the new one
            await fetchAndRenderMissions();
            // The backend will now send updates via WebSocket

        } catch (error) {
            console.error('Execution failed:', error);
            ui.logMessage(`<strong>Error starting mission:</strong> ${error.message}`);
            ui.updateStatus('FAILED', 'danger', false);
            dom.connectionError.classList.remove('d-none');
            ui.setExecuting(false);
        }
    }

    function setupSocketListeners() {
        appState.socket = io(SOCKET_URL);

        appState.socket.on('connect', () => {
            console.log('Socket.IO connected!');
            ui.updateStatus(appState.isExecuting ? 'RUNNING' : 'IDLE', 'secondary', true);
            dom.connectionError.classList.add('d-none');
        });

        appState.socket.on('disconnect', () => {
            console.warn('Socket.IO disconnected.');
            ui.updateStatus('FAILED', 'danger', false);
            if (appState.isExecuting) {
                dom.connectionError.classList.remove('d-none');
            }
        });

        appState.socket.on('connect_error', (error) => {
            console.error('Socket.IO connection error:', error);
            ui.updateStatus('FAILED', 'danger', false);
            dom.connectionError.classList.remove('d-none');
        });

        appState.socket.on('log', (data) => {
            console.log('Log received:', data.message);
            // Check if the log message includes a plan to be formatted
            if (data.plan && Array.isArray(data.plan)) {
                const planHtml = data.plan.map(step => `<li>${step}</li>`).join('');
                const formattedMessage = `
                    ${data.message}
                    <ul class="log-plan-list">${planHtml}</ul>
                `;
                ui.logMessage(formattedMessage);
            } else {
                ui.logMessage(data.message);
            }
        });

        appState.socket.on('status_update', (data) => {
            console.log('Status update:', data);
            ui.updateGraph(data.node);
            ui.updateStatus(data.status, 'info', true);

            if (data.status === 'COMPLETED' || data.status === 'FAILED') {
                ui.setExecuting(false);
                graph.nodes.forEach(n => n.classList.remove('loading'));
                ui.updateStatus(data.status, data.status === 'COMPLETED' ? 'success' : 'danger', true);
                // Refresh the list to show the final status
                fetchAndRenderMissions();
            }
        });

        appState.socket.on('final_report', (data) => {
            // Use the 'marked' library (included in ai_planner.html) to parse the report.
            // This converts Markdown into rich HTML.
            if (window.marked) {
                dom.finalReport.innerHTML = window.marked.parse(data.report);
            } else {
                dom.finalReport.innerHTML = `<p>${data.report.replace(/\n/g, '<br>')}</p>`;
            }
            dom.reportTab.show();
        });

        // If server requests a reload (e.g. backend restarted), reload the page
        appState.socket.on('reload', () => {
            console.log('Server requested reload — reloading page');
            // Force reload from server
            window.location.reload(true);
        });
    }

    // --- 5. Initial Setup ---
    function init() {
        // Sidebar toggles
        dom.sidebarToggle.addEventListener('click', () => ui.toggleSidebar(true));
        dom.sidebarClose.addEventListener('click', () => ui.toggleSidebar(false));

        // Main action
        dom.previousIdeasList.addEventListener('click', handleIdeaClick);
        dom.activeMissionsList.addEventListener('click', handleDeleteMission);
        dom.refreshMissionsBtn.addEventListener('click', fetchAndRenderMissions);
        dom.addIdeaForm.addEventListener('submit', handleAddIdea);
        dom.saveIdeaBtn.addEventListener('click', handleSaveIdea);
        dom.startButton.addEventListener('click', handleExecute);

        // Initial render
        fetchAndRenderIdeas();
        setupSocketListeners();
        fetchAndRenderMissions();
        ui.reset();
    }

    init();
});