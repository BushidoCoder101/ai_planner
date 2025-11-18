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
        connectionError: document.getElementById('connection-error'),
        logTab: new bootstrap.Tab(document.getElementById('log-tab')),
        reportTab: new bootstrap.Tab(document.getElementById('report-tab')),
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
                li.innerHTML = `<span class="text-truncate me-2" data-goal="${idea.goal}" title="${idea.goal}">${idea.goal}</span>
                                <div class="use-button-wrapper">
                                    <button class="btn btn-sm btn-outline-primary flex-shrink-0" data-goal="${idea.goal}">Use</button>
                                </div>`;
                dom.previousIdeasList.appendChild(li);
            });
        } catch (error) {
            console.error('Error fetching ideas:', error);
            dom.previousIdeasList.innerHTML = '<li class="list-group-item bg-transparent text-danger small">Could not load ideas.</li>';
        }
    }

    function handleIdeaClick(e) {
        const target = e.target.closest('[data-goal]');
        if (!target) return;

        const goal = target.dataset.goal;
        dom.goalInput.value = goal;

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
        dom.startButton.addEventListener('click', handleExecute);

        // Initial render
        fetchAndRenderIdeas();
        setupSocketListeners();
        ui.reset();
    }

    init();
});