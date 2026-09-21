/**
 * Ayurvidya · Sanskrit Shloka Analysis Frontend Application
 * Sushruta Samhita · Nidana Sthana · Vatavyadhi Nidana
 * Pure Vanilla JavaScript Client
 */

(function () {
    'use strict';

    // Application State
    let allShlokas = [];
    let activeShlokaId = null;
    let activeStepNumber = 1;
    let currentDetail = null;
    let currentViewMode = 'tabs'; // 'tabs' or 'accordion'

    // DOM Elements
    const elements = {
        // Header
        systemStatusBadge: document.getElementById('systemStatusBadge'),
        statusLabel: document.getElementById('statusLabel'),
        btnOpenSearch: document.getElementById('btnOpenSearch'),

        // Sidebar
        shlokaSelect: document.getElementById('shlokaSelect'),
        shlokaCardsList: document.getElementById('shlokaCardsList'),
        chkForceRefresh: document.getElementById('chkForceRefresh'),
        btnClearCache: document.getElementById('btnClearCache'),
        provCollection: document.getElementById('provCollection'),
        provChunkCount: document.getElementById('provChunkCount'),
        provLLM: document.getElementById('provLLM'),

        // Hero Card
        badgeChapter: document.getElementById('badgeChapter'),
        badgeVerse: document.getElementById('badgeVerse'),
        badgeSource: document.getElementById('badgeSource'),
        badgeCacheStatus: document.getElementById('badgeCacheStatus'),
        shlokaPagesCitation: document.getElementById('shlokaPagesCitation'),
        shlokaDevanagari: document.getElementById('shlokaDevanagari'),
        shlokaTranslit: document.getElementById('shlokaTranslit'),
        shlokaEnglishTopic: document.getElementById('shlokaEnglishTopic'),

        // Actions & Progress & Meta Chips
        btnRunAnalysis: document.getElementById('btnRunAnalysis'),
        execTimeValue: document.getElementById('execTimeValue'),
        chipShlokaNum: document.getElementById('chipShlokaNum'),
        chipLLMVal: document.getElementById('chipLLMVal'),
        chipProvVal: document.getElementById('chipProvVal'),
        progressContainer: document.getElementById('progressContainer'),
        progressBarFill: document.getElementById('progressBarFill'),
        progressStatusText: document.getElementById('progressStatusText'),

        // Analysis Tabs & Step Panel
        tabsNavBar: document.getElementById('tabsNavBar'),
        tabButtons: document.querySelectorAll('.tab-button'),
        btnViewTabs: document.getElementById('btnViewTabs'),
        btnViewAccordion: document.getElementById('btnViewAccordion'),
        tabContentPanel: document.getElementById('tabContentPanel'),
        stepNumberTag: document.getElementById('stepNumberTag'),
        stepNameSanskrit: document.getElementById('stepNameSanskrit'),
        stepNameEnglish: document.getElementById('stepNameEnglish'),
        stepDescription: document.getElementById('stepDescription'),
        emptyStepNotice: document.getElementById('emptyStepNotice'),
        stepTextOutput: document.getElementById('stepTextOutput'),
        contextExpander: document.getElementById('contextExpander'),
        contextCountBadge: document.getElementById('contextCountBadge'),
        contextCardsContainer: document.getElementById('contextCardsContainer'),

        // Accordion (All 7 Steps View)
        accordionContainer: document.getElementById('accordionContainer'),
        accordionList: document.getElementById('accordionList'),
        btnExpandAll: document.getElementById('btnExpandAll'),
        btnCollapseAll: document.getElementById('btnCollapseAll'),

        // Chatbot
        chatScopeBadge: document.getElementById('chatScopeBadge'),
        chatSubtitle: document.getElementById('chatSubtitle'),
        chatMessagesContainer: document.getElementById('chatMessagesContainer'),
        chatInputForm: document.getElementById('chatInputForm'),
        chatInputText: document.getElementById('chatInputText'),
        btnChatSend: document.getElementById('btnChatSend'),

        // Search Modal
        searchModal: document.getElementById('searchModal'),
        modalSearchInput: document.getElementById('modalSearchInput'),
        btnCloseSearch: document.getElementById('btnCloseSearch'),
        modalSearchResults: document.getElementById('modalSearchResults'),
    };

    // =========================================================================
    // Initialization & Lifecycle
    // =========================================================================
    async function initApp() {
        bindEvents();
        await fetchSystemStatus();
        await loadShlokaList();
    }

    function bindEvents() {
        // Dropdown selection
        elements.shlokaSelect.addEventListener('change', (e) => {
            selectShloka(e.target.value);
        });

        // Run Analysis action
        elements.btnRunAnalysis.addEventListener('click', handleRunAnalysis);

        // Clear Cache action
        elements.btnClearCache.addEventListener('click', handleClearCache);

        // Tab selection
        elements.tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const step = parseInt(btn.getAttribute('data-step'), 10);
                setActiveStep(step);
            });
        });

        // View Mode Toggle (Tabs vs Accordion)
        if (elements.btnViewTabs) {
            elements.btnViewTabs.addEventListener('click', () => setViewMode('tabs'));
        }
        if (elements.btnViewAccordion) {
            elements.btnViewAccordion.addEventListener('click', () => setViewMode('accordion'));
        }

        // Accordion Expand/Collapse All
        if (elements.btnExpandAll) {
            elements.btnExpandAll.addEventListener('click', expandAllAccordion);
        }
        if (elements.btnCollapseAll) {
            elements.btnCollapseAll.addEventListener('click', collapseAllAccordion);
        }

        // Chat form submit
        elements.chatInputForm.addEventListener('submit', handleChatSubmit);

        // Search modal open/close
        elements.btnOpenSearch.addEventListener('click', openSearchModal);
        elements.btnCloseSearch.addEventListener('click', closeSearchModal);
        elements.searchModal.addEventListener('click', (e) => {
            if (e.target === elements.searchModal) closeSearchModal();
        });

        // Global hotkey: '/' to open search, Escape to close
        document.addEventListener('keydown', (e) => {
            if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
                e.preventDefault();
                openSearchModal();
            } else if (e.key === 'Escape' && elements.searchModal.style.display !== 'none') {
                closeSearchModal();
            }
        });

        // Search input on enter
        elements.modalSearchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                executeModalSearch(elements.modalSearchInput.value.trim());
            }
        });
    }

    // =========================================================================
    // API Requests
    // =========================================================================

    async function fetchSystemStatus() {
        try {
            const res = await fetch('/api/status');
            if (!res.ok) throw new Error('Status endpoint unavailable');
            const data = await res.json();

            elements.statusLabel.textContent = `ChromaDB Ready (${data.indexed_chunks} Chunks)`;
            elements.provCollection.textContent = data.chroma_collection;
            elements.provChunkCount.textContent = `${data.indexed_chunks} passages`;
            const providerName = data.llm_provider ? data.llm_provider.charAt(0).toUpperCase() + data.llm_provider.slice(1) : 'Unknown';
            elements.provLLM.textContent = `${providerName} (${data.llm_model})`;
            if (elements.chipLLMVal) {
                elements.chipLLMVal.textContent = `${providerName} (${data.llm_model})`;
            }
        } catch (err) {
            console.error('Failed to fetch system status:', err);
            elements.statusLabel.textContent = 'Offline / Error';
            elements.statusLabel.style.color = '#ef4444';
        }
    }

    async function loadShlokaList() {
        try {
            const res = await fetch('/api/shlokas');
            if (!res.ok) throw new Error('Failed to fetch shlokas list');
            allShlokas = await res.json();

            renderSidebarShlokaList(allShlokas);

            if (allShlokas.length > 0) {
                selectShloka(allShlokas[0].id, false);
            }
        } catch (err) {
            console.error('Error loading shlokas:', err);
        }
    }

    async function selectShloka(shlokaId, notifyChat = true) {
        if (!shlokaId) return;
        activeShlokaId = shlokaId;

        // Sync dropdown & sidebar cards
        elements.shlokaSelect.value = shlokaId;
        const allCards = elements.shlokaCardsList.querySelectorAll('.shloka-nav-card');
        allCards.forEach(card => {
            if (card.dataset.id === shlokaId) {
                card.classList.add('active');
                card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            } else {
                card.classList.remove('active');
            }
        });

        // Fetch detail
        try {
            const res = await fetch(`/api/shlokas/${shlokaId}`);
            if (!res.ok) throw new Error('Failed to get shloka detail');
            currentDetail = await res.json();

            const verseLabel = currentDetail.shloka.shloka_number_display || currentDetail.shloka.shloka_number;
            renderShlokaHero(currentDetail.shloka, currentDetail.is_cached);

            if (currentDetail.is_cached) {
                updateAnalysisMetadata(
                    verseLabel,
                    '<0.05s (SQLite Cache)',
                    'Gemini 2.5 Flash',
                    'Cached'
                );
            } else {
                updateAnalysisMetadata(
                    '—',
                    '—',
                    'Gemini 2.5 Flash',
                    'Not Analyzed'
                );
            }

            if (currentViewMode === 'accordion') {
                renderAccordion();
            } else {
                renderStepPanel();
            }

            if (notifyChat) {
                appendSystemNotification(`📍 Switched active context to Śloka ${verseLabel}`);
            }
        } catch (err) {
            console.error('Error fetching shloka details:', err);
        }
    }

    // =========================================================================
    // UI Renderers & View Modes
    // =========================================================================

    function updateAnalysisMetadata(verseNum, execTime, provider, status) {
        if (elements.chipShlokaNum) elements.chipShlokaNum.textContent = verseNum || '—';
        if (elements.execTimeValue) elements.execTimeValue.textContent = execTime || '—';
        if (elements.chipLLMVal && provider) elements.chipLLMVal.textContent = provider;
        if (elements.chipProvVal) elements.chipProvVal.textContent = status || 'Not Analyzed';

        if (elements.badgeCacheStatus) {
            if (status === 'Cached') {
                elements.badgeCacheStatus.textContent = 'Cached';
                elements.badgeCacheStatus.className = 'badge badge-cache';
            } else if (status === 'Fresh Analysis') {
                elements.badgeCacheStatus.textContent = 'Fresh Analysis';
                elements.badgeCacheStatus.className = 'badge badge-cache';
            } else {
                elements.badgeCacheStatus.textContent = 'Not Analyzed';
                elements.badgeCacheStatus.className = 'badge badge-subtle';
            }
        }
    }

    function setViewMode(mode) {
        currentViewMode = mode;
        if (mode === 'accordion') {
            if (elements.btnViewTabs) elements.btnViewTabs.classList.remove('active');
            if (elements.btnViewAccordion) elements.btnViewAccordion.classList.add('active');
            if (elements.tabsNavBar) elements.tabsNavBar.style.display = 'none';
            if (elements.tabContentPanel) elements.tabContentPanel.style.display = 'none';
            if (elements.accordionContainer) elements.accordionContainer.style.display = 'flex';
            renderAccordion();
        } else {
            if (elements.btnViewAccordion) elements.btnViewAccordion.classList.remove('active');
            if (elements.btnViewTabs) elements.btnViewTabs.classList.add('active');
            if (elements.accordionContainer) elements.accordionContainer.style.display = 'none';
            if (elements.tabsNavBar) elements.tabsNavBar.style.display = 'flex';
            if (elements.tabContentPanel) elements.tabContentPanel.style.display = 'flex';
            setActiveStep(activeStepNumber);
        }
    }

    function expandAllAccordion() {
        if (!elements.accordionList) return;
        elements.accordionList.querySelectorAll('.accordion-item').forEach(item => item.classList.add('open'));
    }

    function collapseAllAccordion() {
        if (!elements.accordionList) return;
        elements.accordionList.querySelectorAll('.accordion-item').forEach(item => item.classList.remove('open'));
    }

    // Expose functions globally for robust button click dispatch
    window.setViewMode = setViewMode;
    window.expandAllAccordion = expandAllAccordion;
    window.collapseAllAccordion = collapseAllAccordion;
    window.setActiveStep = setActiveStep;

    function appendSystemNotification(text) {
        if (!elements.chatMessagesContainer) return;
        const div = document.createElement('div');
        div.className = 'chat-system-notification';
        div.innerHTML = `<span class="chat-system-pill">${escapeHtml(text)}</span>`;
        elements.chatMessagesContainer.appendChild(div);
        elements.chatMessagesContainer.scrollTop = elements.chatMessagesContainer.scrollHeight;
    }

    function formatMarkdown(text) {
        if (!text) return '';
        let escaped = escapeHtml(text);
        escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        escaped = escaped.replace(/\*(.*?)\*/g, '<em>$1</em>');
        escaped = escaped.replace(/^### (.*$)/gim, '<h4 style="color: var(--text-gold); margin: 0.8rem 0 0.4rem;">$1</h4>');
        escaped = escaped.replace(/^## (.*$)/gim, '<h3 style="color: var(--text-gold); margin: 1rem 0 0.5rem;">$1</h3>');
        escaped = escaped.replace(/^# (.*$)/gim, '<h2 style="color: var(--text-gold); margin: 1.2rem 0 0.6rem;">$1</h2>');
        escaped = escaped.replace(/^\s*[-•]\s+(.*$)/gim, '• $1');
        return escaped;
    }

    function renderSidebarShlokaList(shlokas) {
        // Populate select options
        elements.shlokaSelect.innerHTML = '';
        shlokas.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.id;
            const verseLabel = s.shloka_number_display || s.shloka_number;
            opt.textContent = `Śloka ${verseLabel}: ${s.english_title || s.text.substring(0, 35)}`;
            elements.shlokaSelect.appendChild(opt);
        });

        // Populate card list
        elements.shlokaCardsList.innerHTML = '';
        shlokas.forEach(s => {
            const card = document.createElement('div');
            card.className = 'shloka-nav-card';
            card.dataset.id = s.id;

            const firstLine = s.text.split('\n')[0] || s.text;
            const verseLabel = s.shloka_number_display || s.shloka_number;

            card.innerHTML = `
                <div class="nav-card-top">
                    <span class="nav-card-number">Śloka ${verseLabel}</span>
                    <span class="nav-card-badge">Ch. 1</span>
                </div>
                <div class="nav-card-preview" title="${s.text}">${firstLine}</div>
                <div class="nav-card-topic">${s.english_title || 'Nidāna Sthāna'}</div>
            `;

            card.addEventListener('click', () => selectShloka(s.id));
            elements.shlokaCardsList.appendChild(card);
        });
    }

    function renderShlokaHero(shloka, isCached) {
        elements.badgeChapter.textContent = 'Chapter 1';
        const verseLabel = shloka.shloka_number_display || shloka.shloka_number;
        elements.badgeVerse.textContent = `Śloka ${verseLabel}`;
        elements.badgeSource.textContent = shloka.source;

        if (elements.chatScopeBadge) {
            elements.chatScopeBadge.textContent = `Active: Śloka ${verseLabel}`;
        }
        if (elements.chatSubtitle) {
            const topic = shloka.english_title || 'Vātavyādhi Nidāna';
            elements.chatSubtitle.textContent = `Grounded strictly in Śloka ${verseLabel} (${topic}). Answers derived from Sushruta Samhita context.`;
        }

        const pages = shloka.associated_pages || [];
        elements.shlokaPagesCitation.textContent = pages.length > 0 ? `PDF Pages: ${pages.join(', ')}` : 'Source: Sushruta Samhita';
        elements.shlokaDevanagari.textContent = shloka.text;
        elements.shlokaTranslit.textContent = shloka.transliteration || '';
        elements.shlokaEnglishTopic.textContent = shloka.english_title || 'Vātavyādhi Nidāna';
    }

    function setActiveStep(stepNumber) {
        activeStepNumber = stepNumber;

        elements.tabButtons.forEach(btn => {
            const step = parseInt(btn.getAttribute('data-step'), 10);
            if (step === stepNumber) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        renderStepPanel();
    }

    function renderStepPanel() {
        if (!currentDetail) return;

        const config = currentDetail.steps_config ? currentDetail.steps_config[String(activeStepNumber)] : null;
        if (config) {
            elements.stepNumberTag.textContent = `Step 0${activeStepNumber} / 07`;
            elements.stepNameSanskrit.textContent = config.name_sa || config.name_sanskrit || '';
            elements.stepNameEnglish.textContent = config.name_en || config.name_english || '';
            elements.stepDescription.textContent = config.desc || config.description || '';
        }

        const stepData = currentDetail.steps ? currentDetail.steps[String(activeStepNumber)] : null;

        if (stepData && stepData.output) {
            elements.emptyStepNotice.style.display = 'none';
            elements.stepTextOutput.style.display = 'block';
            elements.stepTextOutput.innerHTML = formatMarkdown(stepData.output);

            // Render retrieved chunks
            renderRetrievedContext(stepData.retrieved_contexts || stepData.retrieved_chunks || []);
        } else {
            elements.emptyStepNotice.style.display = 'flex';
            elements.stepTextOutput.style.display = 'none';
            renderRetrievedContext([]);
        }
    }

    function renderAccordion() {
        if (!currentDetail || !elements.accordionList) return;
        elements.accordionList.innerHTML = '';

        const hasAnyOutput = currentDetail.steps && Object.keys(currentDetail.steps).length > 0 &&
                             Object.values(currentDetail.steps).some(s => s && s.output);

        if (!hasAnyOutput) {
            elements.accordionList.innerHTML = `
                <div class="empty-step-notice" style="margin: 1.5rem 0;">
                    <div class="notice-icon">📜</div>
                    <h4>Analysis Not Yet Run</h4>
                    <p>Click <strong>"Run 7-Step Analysis"</strong> above to generate all seven analytical stages using RAG.</p>
                </div>
            `;
            return;
        }

        for (let stepNum = 1; stepNum <= 7; stepNum++) {
            const config = currentDetail.steps_config ? currentDetail.steps_config[String(stepNum)] : null;
            const stepData = currentDetail.steps ? currentDetail.steps[String(stepNum)] : null;
            const saName = config ? (config.name_sa || config.name_sanskrit || '') : `Step ${stepNum}`;
            const enName = config ? (config.name_en || config.name_english || '') : '';
            const outputText = stepData && stepData.output ? stepData.output : '';
            const chunks = stepData ? (stepData.retrieved_contexts || stepData.retrieved_chunks || []) : [];

            const item = document.createElement('div');
            item.className = 'accordion-item open';
            item.dataset.step = stepNum;

            let chunksHtml = '';
            if (chunks && chunks.length > 0) {
                const cardsHtml = chunks.map(chunk => {
                    const score = chunk.similarity_score ? (chunk.similarity_score * 100).toFixed(1) + '%' : 'Relevant';
                    const ref = chunk.shloka_number ? `Śloka ${chunk.shloka_number}` : 'Ayurvidya Context';
                    const contentType = chunk.content_type || 'passage';
                    return `
                        <details class="context-card">
                            <summary class="context-card-header">
                                <span class="context-card-source">
                                    <span>📜</span> ${chunk.source || 'Sushruta Samhita'} · ${ref}
                                    <span class="context-card-type-tag">${contentType}</span>
                                </span>
                                <span class="context-card-meta-right">
                                    <span class="context-card-score">Cosine: ${score}</span>
                                    <span class="context-card-chevron">▼</span>
                                </span>
                            </summary>
                            <div class="context-card-excerpt">${escapeHtml(chunk.text)}</div>
                        </details>
                    `;
                }).join('');

                chunksHtml = `
                    <details class="retrieved-context-expander" style="margin-top: 1rem;" open>
                        <summary class="context-expander-summary">
                            <span class="summary-left">
                                <span class="summary-icon">🔍</span>
                                <span class="summary-title">RAG Context & Retrieved Sources</span>
                            </span>
                            <span class="context-chunk-badge">${chunks.length} passages</span>
                        </summary>
                        <div class="context-cards-container">
                            ${cardsHtml}
                        </div>
                    </details>
                `;
            } else {
                chunksHtml = `
                    <details class="retrieved-context-expander" style="margin-top: 1rem;">
                        <summary class="context-expander-summary">
                            <span class="summary-left">
                                <span class="summary-icon">🔍</span>
                                <span class="summary-title">RAG Context & Retrieved Sources</span>
                            </span>
                            <span class="context-chunk-badge">0 passages</span>
                        </summary>
                        <div class="context-cards-container">
                            <div class="no-context-msg">No external RAG passages attached for this stage.</div>
                        </div>
                    </details>
                `;
            }

            item.innerHTML = `
                <div class="accordion-header">
                    <div class="accordion-header-left">
                        <span class="accordion-step-badge">Step 0${stepNum}</span>
                        <span class="accordion-step-sa">${saName}</span>
                        <span class="accordion-step-en">${enName}</span>
                    </div>
                    <span class="accordion-chevron">▼</span>
                </div>
                <div class="accordion-body">
                    <div class="step-text-output" style="display: block;">
                        ${outputText ? formatMarkdown(outputText) : '<em>No output generated yet for this step.</em>'}
                    </div>
                    ${chunksHtml}
                </div>
            `;

            const header = item.querySelector('.accordion-header');
            header.addEventListener('click', () => {
                item.classList.toggle('open');
            });

            elements.accordionList.appendChild(item);
        }
    }

    function renderRetrievedContext(chunks) {
        elements.contextCountBadge.textContent = `${chunks.length} passages`;
        elements.contextCardsContainer.innerHTML = '';

        if (!chunks || chunks.length === 0) {
            elements.contextCardsContainer.innerHTML = `
                <div class="no-context-msg">No external RAG passages attached for this stage.</div>
            `;
            return;
        }

        chunks.forEach((chunk, idx) => {
            const details = document.createElement('details');
            details.className = 'context-card';

            const score = chunk.similarity_score ? (chunk.similarity_score * 100).toFixed(1) + '%' : 'Relevant';
            const ref = chunk.shloka_number ? `Śloka ${chunk.shloka_number}` : 'Ayurvidya Context';
            const contentType = chunk.content_type || 'passage';

            details.innerHTML = `
                <summary class="context-card-header">
                    <span class="context-card-source">
                        <span>📜</span> ${chunk.source || 'Sushruta Samhita'} · ${ref}
                        <span class="context-card-type-tag">${contentType}</span>
                    </span>
                    <span class="context-card-meta-right">
                        <span class="context-card-score">Cosine: ${score}</span>
                        <span class="context-card-chevron">▼</span>
                    </span>
                </summary>
                <div class="context-card-excerpt">${escapeHtml(chunk.text)}</div>
            `;
            elements.contextCardsContainer.appendChild(details);
        });
    }

    // =========================================================================
    // Actions
    // =========================================================================

    async function handleRunAnalysis() {
        if (!activeShlokaId) return;

        const forceRefresh = elements.chkForceRefresh.checked;
        elements.btnRunAnalysis.disabled = true;
        elements.btnRunAnalysis.innerHTML = '<span class="btn-icon">⏳</span><span class="btn-text">Executing RAG Pipeline...</span>';

        // Show progress bar
        elements.progressContainer.style.display = 'flex';
        elements.progressBarFill.style.width = '15%';
        elements.progressStatusText.textContent = 'Step 1/7: Initializing Sanskrit chunk retrieval & analysis...';

        let progressTimer = setInterval(() => {
            let currentWidth = parseInt(elements.progressBarFill.style.width, 10) || 15;
            if (currentWidth < 85) {
                currentWidth += 12;
                elements.progressBarFill.style.width = currentWidth + '%';
                const stepNum = Math.min(7, Math.floor((currentWidth / 90) * 7) + 1);
                elements.progressStatusText.textContent = `Running Step ${stepNum} of 7 through RAG & LLM...`;
            }
        }, 400);

        try {
            const url = `/api/shlokas/${activeShlokaId}/analyze?force_refresh=${forceRefresh}`;
            const res = await fetch(url, { method: 'POST' });
            clearInterval(progressTimer);

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || `Analysis failed (${res.status})`);
            }
            const data = await res.json();

            // Progress finish
            elements.progressBarFill.style.width = '100%';
            elements.progressStatusText.textContent = 'Analysis Complete!';

            // Refresh current shloka detail
            currentDetail.steps = data.steps;
            currentDetail.is_cached = true;

            const verseLabel = currentDetail.shloka.shloka_number_display || currentDetail.shloka.shloka_number;
            const execTimeStr = `${data.execution_time_seconds.toFixed(2)}s`;

            if (data.cached) {
                updateAnalysisMetadata(
                    verseLabel,
                    `${execTimeStr} (SQLite Cache)`,
                    'Gemini 2.5 Flash',
                    'Cached'
                );
            } else {
                updateAnalysisMetadata(
                    verseLabel,
                    execTimeStr,
                    'Gemini 2.5 Flash',
                    'Fresh Analysis'
                );
            }

            renderShlokaHero(currentDetail.shloka, true);
            if (currentViewMode === 'accordion') {
                renderAccordion();
            } else {
                renderStepPanel();
            }

            setTimeout(() => {
                elements.progressContainer.style.display = 'none';
                elements.progressBarFill.style.width = '0%';
            }, 1200);

        } catch (err) {
            clearInterval(progressTimer);
            console.error('Analysis error:', err);
            elements.progressStatusText.textContent = 'Error during analysis: ' + err.message;
            elements.progressBarFill.style.background = '#ef4444';
        } finally {
            elements.btnRunAnalysis.disabled = false;
            elements.btnRunAnalysis.innerHTML = '<span class="btn-icon">⚡</span><span class="btn-text">Run 7-Step Analysis</span>';
        }
    }

    async function handleClearCache() {
        if (!activeShlokaId) return;
        try {
            const res = await fetch(`/api/shlokas/${activeShlokaId}/cache`, { method: 'DELETE' });
            if (!res.ok) throw new Error('Failed to clear cache');
            await selectShloka(activeShlokaId);
            updateAnalysisMetadata(
                '—',
                '—',
                'Gemini 2.5 Flash',
                'Not Analyzed'
            );
        } catch (err) {
            console.error('Error clearing cache:', err);
        }
    }

    // =========================================================================
    // Chatbot
    // =========================================================================

    async function handleChatSubmit(e) {
        e.preventDefault();
        const query = elements.chatInputText.value.trim();
        if (!query || !activeShlokaId) return;

        // Clear input
        elements.chatInputText.value = '';

        // Append user bubble
        appendChatMessage('user', query);

        // Append placeholder assistant bubble
        const assistantPlaceholder = appendChatMessage('assistant', 'Consulting Sushruta Samhita passages...', true);

        elements.btnChatSend.disabled = true;

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ shloka_id: activeShlokaId, message: query })
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || `Chat error (${res.status})`);
            }
            const data = await res.json();

            // Update assistant bubble with answer & sources
            assistantPlaceholder.querySelector('.chat-text').innerHTML = formatMarkdown(data.response);

            if (data.sources && data.sources.length > 0) {
                const sourcesList = document.createElement('div');
                sourcesList.className = 'chat-sources-list';
                data.sources.forEach(src => {
                    const item = document.createElement('div');
                    item.className = 'chat-source-item';
                    const score = src.similarity_score ? (src.similarity_score * 100).toFixed(0) + '%' : '';
                    const shlokaRef = src.shloka_number ? `Śloka ${src.shloka_number}` : 'Context';
                    item.innerHTML = `<span>📜</span> <strong>${src.source} (${shlokaRef})</strong> - <em>${src.excerpt}</em> [${score}]`;
                    sourcesList.appendChild(item);
                });
                assistantPlaceholder.querySelector('.chat-body').appendChild(sourcesList);
            }

        } catch (err) {
            console.error('Chat error:', err);
            assistantPlaceholder.querySelector('.chat-text').textContent = 'Unable to complete answer: ' + err.message;
        } finally {
            elements.btnChatSend.disabled = false;
            elements.chatMessagesContainer.scrollTop = elements.chatMessagesContainer.scrollHeight;
        }
    }

    function appendChatMessage(role, text, isTyping = false) {
        const msg = document.createElement('div');
        msg.className = `chat-message chat-${role}`;

        const avatar = role === 'user' ? '👤' : '🌿';

        msg.innerHTML = `
            <div class="chat-avatar">${avatar}</div>
            <div class="chat-body">
                <p class="chat-text">${escapeHtml(text)}</p>
            </div>
        `;

        elements.chatMessagesContainer.appendChild(msg);
        elements.chatMessagesContainer.scrollTop = elements.chatMessagesContainer.scrollHeight;
        return msg;
    }

    // =========================================================================
    // Semantic Vector Search Modal
    // =========================================================================

    function openSearchModal() {
        elements.searchModal.style.display = 'flex';
        elements.modalSearchInput.value = '';
        elements.modalSearchResults.innerHTML = `
            <div class="search-placeholder-msg">Type a query (e.g. <em>"प्राणो नाम देहधृक्"</em>, <em>"Samana Vayu digestion"</em>, or <em>"Padavibhaga rules"</em>) and press Enter.</div>
        `;
        setTimeout(() => elements.modalSearchInput.focus(), 50);
    }

    function closeSearchModal() {
        elements.searchModal.style.display = 'none';
    }

    async function executeModalSearch(query) {
        if (!query) return;

        elements.modalSearchResults.innerHTML = `<div class="search-placeholder-msg">Searching vector collection...</div>`;

        try {
            const res = await fetch(`/api/search?q=${encodeURIComponent(query)}&top_k=5`);
            if (!res.ok) throw new Error('Search failed');
            const results = await res.json();

            if (results.length === 0) {
                elements.modalSearchResults.innerHTML = `<div class="search-placeholder-msg">No passages matched your query.</div>`;
                return;
            }

            elements.modalSearchResults.innerHTML = '';
            results.forEach(item => {
                const card = document.createElement('div');
                card.className = 'search-result-card';

                const score = item.similarity_score ? (item.similarity_score * 100).toFixed(1) + '%' : 'Passage';
                const shlokaRef = item.shloka_number ? `Śloka ${item.shloka_number}` : 'Ayurvidya Passage';

                card.innerHTML = `
                    <div class="result-card-header">
                        <span class="result-source-tag">${item.source} · ${shlokaRef}</span>
                        <span class="result-similarity-score">Cosine: ${score}</span>
                    </div>
                    <div class="result-card-text">${escapeHtml(item.text)}</div>
                `;

                card.addEventListener('click', () => {
                    if (item.shloka_number) {
                        const matched = allShlokas.find(s => s.shloka_number === item.shloka_number);
                        if (matched) {
                            selectShloka(matched.id);
                            closeSearchModal();
                        }
                    }
                });

                elements.modalSearchResults.appendChild(card);
            });
        } catch (err) {
            console.error('Modal search error:', err);
            elements.modalSearchResults.innerHTML = `<div class="search-placeholder-msg">Search failed: ${err.message}</div>`;
        }
    }

    // Helper
    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Start on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initApp);
    } else {
        initApp();
    }
})();
