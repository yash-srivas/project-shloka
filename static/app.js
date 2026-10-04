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
    let currentViewMode = 'accordion'; // 'tabs' or 'accordion'

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
        btnExportAnalysis: document.getElementById('btnExportAnalysis'),
        execTimeValue: document.getElementById('execTimeValue'),
        chipShlokaNum: document.getElementById('chipShlokaNum'),
        chipLLMVal: document.getElementById('chipLLMVal'),
        chipProvVal: document.getElementById('chipProvVal'),
        progressContainer: document.getElementById('progressContainer'),
        progressBarFill: document.getElementById('progressBarFill'),
        progressStatusText: document.getElementById('progressStatusText'),

        // Final Explanation
        finalExplanationSection: document.getElementById('finalExplanationSection'),
        synthesisStatusChip: document.getElementById('synthesisStatusChip'),
        emptySynthesisNotice: document.getElementById('emptySynthesisNotice'),
        synthesisTextOutput: document.getElementById('synthesisTextOutput'),
        detailedAnalysisExpander: document.getElementById('detailedAnalysisExpander'),

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

        // Export Dossier action
        if (elements.btnExportAnalysis) {
            elements.btnExportAnalysis.addEventListener('click', handleExportDossier);
        }

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
            renderFinalExplanation(currentDetail.final_synthesis);

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

    function renderFinalExplanation(synthesisData) {
        if (!elements.finalExplanationSection) return;

        if (synthesisData && synthesisData.content) {
            if (elements.emptySynthesisNotice) elements.emptySynthesisNotice.style.display = 'none';
            if (elements.synthesisTextOutput) {
                elements.synthesisTextOutput.style.display = 'block';
                elements.synthesisTextOutput.innerHTML = renderStructuredSynthesis(synthesisData.content);
            }
            if (elements.synthesisStatusChip) {
                const status = (synthesisData.status || 'fresh').toLowerCase();
                if (status === 'cached') {
                    elements.synthesisStatusChip.textContent = 'Cached Synthesis';
                    elements.synthesisStatusChip.className = 'status-chip chip-cached';
                } else if (status === 'fallback') {
                    elements.synthesisStatusChip.textContent = 'Synthesis Notice';
                    elements.synthesisStatusChip.className = 'status-chip chip-fallback';
                } else {
                    elements.synthesisStatusChip.textContent = 'Fresh Synthesis';
                    elements.synthesisStatusChip.className = 'status-chip chip-fresh';
                }
            }
        } else {
            if (elements.emptySynthesisNotice) elements.emptySynthesisNotice.style.display = 'flex';
            if (elements.synthesisTextOutput) {
                elements.synthesisTextOutput.style.display = 'none';
                elements.synthesisTextOutput.innerHTML = '';
            }
            if (elements.synthesisStatusChip) {
                elements.synthesisStatusChip.textContent = 'Not Synthesized';
                elements.synthesisStatusChip.className = 'status-chip';
            }
        }
    }

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

    function formatInline(str) {
        if (!str) return '';
        let s = escapeHtml(str);
        s = s.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        s = s.replace(/\*(.*?)\*/g, '<em>$1</em>');
        s = s.replace(/`([^`]+)`/g, '<code class="md-inline-code">$1</code>');
        return s;
    }

    function formatMarkdown(text) {
        if (!text) return '';

        // Safe HTML escape first
        let src = escapeHtml(text);
        src = src.replace(/\r\n/g, '\n').replace(/\r/g, '\n');

        // Protect code blocks
        const codeBlocks = [];
        src = src.replace(/```([a-zA-Z0-9]*)\n([\s\S]*?)```/g, (match, lang, code) => {
            const id = `___CODE_BLOCK_${codeBlocks.length}___`;
            codeBlocks.push(`<pre class="md-code-block"><code>${code}</code></pre>`);
            return id;
        });

        // Protect inline code
        const inlineCodes = [];
        src = src.replace(/`([^`\n]+)`/g, (match, code) => {
            const id = `___INLINE_CODE_${inlineCodes.length}___`;
            inlineCodes.push(`<code class="md-inline-code">${code}</code>`);
            return id;
        });

        // Helper for inline styles
        function inlineFmt(s) {
            return s
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>');
        }

        // Parse Markdown pipe tables
        src = src.replace(/(?:^|\n)(\|[^\n]+\|\n\|[\s\-:|]+\|\n(?:\|[^\n]+\|\n?)+)/g, (match) => {
            const lines = match.trim().split('\n');
            if (lines.length < 3) return match;
            const headerCells = lines[0].split('|').slice(1, -1).map(c => c.trim());
            const bodyLines = lines.slice(2);

            let html = '<div class="table-responsive-wrapper"><table class="md-table"><thead><tr>';
            headerCells.forEach(cell => {
                html += `<th>${inlineFmt(cell)}</th>`;
            });
            html += '</tr></thead><tbody>';
            bodyLines.forEach(line => {
                const cells = line.split('|').slice(1, -1).map(c => c.trim());
                if (cells.length > 0) {
                    html += '<tr>';
                    cells.forEach(cell => {
                        html += `<td>${inlineFmt(cell)}</td>`;
                    });
                    html += '</tr>';
                }
            });
            html += '</tbody></table></div>';
            return '\n' + html + '\n';
        });

        // Line-by-line block processing
        const lines = src.split('\n');
        const out = [];
        let inUl = false;
        let inOl = false;
        let paraBuffer = [];

        function flushPara() {
            if (paraBuffer.length > 0) {
                const content = paraBuffer.join('<br>').trim();
                if (content) {
                    out.push(`<p class="md-para">${content}</p>`);
                }
                paraBuffer = [];
            }
        }

        function closeLists() {
            if (inUl) { out.push('</ul>'); inUl = false; }
            if (inOl) { out.push('</ol>'); inOl = false; }
        }

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];

            // Passthrough protected blocks
            if (line.includes('___CODE_BLOCK_') || line.includes('<div class="table-responsive-wrapper">') || line.includes('</table></div>')) {
                flushPara();
                closeLists();
                out.push(line);
                continue;
            }

            // Blank line
            if (!line.trim()) {
                flushPara();
                closeLists();
                continue;
            }

            // Horizontal rule
            if (/^(\-{3,}|\*{3,}|_{3,})$/.test(line.trim())) {
                flushPara();
                closeLists();
                out.push('<hr class="md-divider">');
                continue;
            }

            // Headings (# through ######)
            const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
            if (headingMatch) {
                flushPara();
                closeLists();
                const level = headingMatch[1].length;
                const headingText = inlineFmt(headingMatch[2]);
                const tagLevel = Math.min(6, level + 1);
                out.push(`<h${tagLevel} class="md-heading-${level}">${headingText}</h${tagLevel}>`);
                continue;
            }

            // Unordered list item (- item, * item, • item)
            const ulMatch = line.match(/^(\s*)[-*•]\s+(.*)$/);
            if (ulMatch) {
                flushPara();
                if (inOl) { out.push('</ol>'); inOl = false; }
                if (!inUl) { out.push('<ul class="md-list">'); inUl = true; }
                out.push(`<li>${inlineFmt(ulMatch[2])}</li>`);
                continue;
            }

            // Ordered list item (1. item)
            const olMatch = line.match(/^(\s*)\d+[\.\)]\s+(.*)$/);
            if (olMatch) {
                flushPara();
                if (inUl) { out.push('</ul>'); inUl = false; }
                if (!inOl) { out.push('<ol class="md-list">'); inOl = true; }
                out.push(`<li>${inlineFmt(olMatch[2])}</li>`);
                continue;
            }

            // Blockquote
            const bqMatch = line.match(/^&gt;\s*(.*)$/);
            if (bqMatch) {
                flushPara();
                closeLists();
                out.push(`<blockquote class="md-blockquote">${inlineFmt(bqMatch[1])}</blockquote>`);
                continue;
            }

            // Regular paragraph line
            closeLists();
            paraBuffer.push(inlineFmt(line));
        }

        flushPara();
        closeLists();

        let result = out.join('\n');

        // Restore protected blocks
        codeBlocks.forEach((block, idx) => {
            result = result.replace(`___CODE_BLOCK_${idx}___`, block);
        });
        inlineCodes.forEach((code, idx) => {
            result = result.replace(`___INLINE_CODE_${idx}___`, code);
        });

        return result;
    }

    function renderStructuredSynthesis(rawText) {
        if (!rawText) return '';

        // Match numbered sections: 1. to 8.
        const sectionRegex = /(?:^|\n)(?:#{1,6}\s*|\*\*)?([1-8])[\.\)]\s*([^\n]+)/g;
        const matches = [...rawText.matchAll(sectionRegex)];

        // If not formatted with 1-8 sections, use robust markdown renderer
        if (matches.length < 3) {
            return formatMarkdown(rawText);
        }

        const sections = {};
        for (let i = 0; i < matches.length; i++) {
            const m = matches[i];
            const num = parseInt(m[1], 10);
            const title = m[2].trim().replace(/[*#]+$/, '');
            const start = m.index + m[0].length;
            const end = (i + 1 < matches.length) ? matches[i + 1].index : rawText.length;
            const body = rawText.slice(start, end).trim();
            sections[num] = { title, body };
        }

        let html = '<div class="synthesis-grid">';

        // 8. FINAL CONCISE SUMMARY (Prominent banner at the very top!)
        if (sections[8] && sections[8].body) {
            const summaryText = formatInline(sections[8].body.replace(/^[#*\s-]+/, ''));
            html += `
                <div class="final-summary-banner">
                    <div class="summary-banner-icon">🎯</div>
                    <div class="summary-banner-body">
                        <div class="summary-banner-title">संक्षिप्त निष्कर्ष · Concluding Takeaway</div>
                        <div class="summary-banner-text">${summaryText}</div>
                    </div>
                </div>
            `;
        }

        // 1. ORIGINAL SHLOKA (मूल श्लोक) - Dedicated Verse Card
        if (sections[1] && sections[1].body) {
            const rawBody = sections[1].body;
            const lines = rawBody.split('\n').map(l => l.trim()).filter(l => l.length > 0 && !l.startsWith('```'));
            
            let stanzasHtml = '';
            let currentStanzaLines = [];

            lines.forEach((line) => {
                let norm = line.replace(/\|\|/g, '॥').replace(/(?<![॥|])\|(?![॥|])/g, '।');
                // Detect verse number at end: e.g. ॥५॥ or ।९। or ||5||
                const vnumMatch = norm.match(/[॥।]\s*([०-९\d]+)\s*[॥।]$/);
                if (vnumMatch) {
                    const vnum = vnumMatch[1];
                    const cleanVerse = norm.slice(0, vnumMatch.index).trim();
                    currentStanzaLines.push(`
                        <div class="sanskrit-verse-line">
                            <span>${escapeHtml(cleanVerse)}</span>
                            <span class="verse-num-pill">॥ ${escapeHtml(vnum)} ॥</span>
                        </div>
                    `);
                    stanzasHtml += `<div class="verse-stanza">${currentStanzaLines.join('')}</div>`;
                    currentStanzaLines = [];
                } else {
                    currentStanzaLines.push(`
                        <div class="sanskrit-verse-line">
                            <span>${escapeHtml(norm)}</span>
                        </div>
                    `);
                }
            });

            if (currentStanzaLines.length > 0) {
                stanzasHtml += `<div class="verse-stanza">${currentStanzaLines.join('')}</div>`;
            }

            // Insert ornaments between stanzas
            const stanzasSplit = stanzasHtml.split('</div><div class="verse-stanza">');
            const ornamentedStanzas = stanzasSplit.join('</div><div class="stanza-ornament">✦ ✦ ✦</div><div class="verse-stanza">');

            html += `
                <div class="synthesis-card">
                    <div class="synthesis-card-header">
                        <div class="header-left">
                            <span class="card-icon">🕉️</span>
                            <span class="card-title">मूल श्लोक · Original Sanskrit Verse</span>
                        </div>
                        <span class="card-badge">Samhita Text</span>
                    </div>
                    <div class="shloka-verse-display">
                        ${ornamentedStanzas || `<div class="sanskrit-verse-line">${escapeHtml(rawBody)}</div>`}
                    </div>
                </div>
            `;
        }

        // 4. LITERAL / SENTENCE MEANING (सरलार्थ) - Placed directly below the verse for instant comprehension!
        if (sections[4] && sections[4].body) {
            const rawBody = sections[4].body;
            // Split long sentences/paragraphs (>200 chars)
            const sentences = rawBody.split(/(?<=[.।!])\s+/);
            const paras = [];
            let currPara = [];
            let currLen = 0;

            sentences.forEach(s => {
                currPara.push(s);
                currLen += s.length;
                if (currLen > 220) {
                    paras.push(currPara.join(' '));
                    currPara = [];
                    currLen = 0;
                }
            });
            if (currPara.length > 0) paras.push(currPara.join(' '));

            const parasHtml = paras.map(p => `<p class="sentence-meaning-para">${formatInline(p)}</p>`).join('');

            html += `
                <div class="synthesis-card">
                    <div class="synthesis-card-header">
                        <div class="header-left">
                            <span class="card-icon">📜</span>
                            <span class="card-title">अन्वयार्थ एवं सरलार्थ · Continuous Sentence Meaning</span>
                        </div>
                        <span class="card-badge">Translation</span>
                    </div>
                    <div class="prose-content">
                        ${parasHtml}
                    </div>
                </div>
            `;
        }

        // 2. WORD-BY-WORD MEANING (पदविभाग एवं अन्वयार्थ) - Structured Table
        if (sections[2] && sections[2].body) {
            const rawBody = sections[2].body;
            const lines = rawBody.split('\n').map(l => l.trim()).filter(l => l.length > 0);
            const tableRows = [];

            lines.forEach((line) => {
                // If it is a pipe table row, parse columns
                if (line.startsWith('|') && line.endsWith('|')) {
                    const cells = line.split('|').slice(1, -1).map(c => c.trim());
                    if (cells.length >= 2 && !cells[0].includes('---')) {
                        const sk = cells[0];
                        const mean = cells[1];
                        const gram = cells[2] || '—';
                        tableRows.push({ sanskrit: sk, meaning: mean, grammar: gram });
                    }
                    return;
                }

                // If bullet line: e.g. - **तस्य** (सुश्रुतस्य) — His
                if (line.match(/^[-*•]\s+/)) {
                    const cleanLine = line.replace(/^[-*•]\s+/, '').trim();
                    // Split on separator
                    const parts = cleanLine.split(/\s+[—–]\s+|\s+:\s+|\s+-\s+/);
                    let left = parts[0] || '';
                    let right = parts[1] || '';

                    // Extract Sanskrit from **...** or left
                    const boldMatch = left.match(/\*\*([^*]+)\*\*/);
                    let sanskrit = boldMatch ? boldMatch[1].trim() : left.replace(/[*_]/g, '').trim();

                    let grammar = '';

                    // Check for grammar in left parentheses
                    const leftParenMatch = left.match(/\(([^)]+)\)/);
                    if (leftParenMatch) {
                        const content = leftParenMatch[1].trim();
                        if (/[\+लङ्क्त्वाक्विप्णिनिविभक्तिसमासवचनपुरुषकृदन्ततिङन्त]/i.test(content)) {
                            grammar = content;
                        } else {
                            sanskrit += ` (${content})`;
                        }
                    }

                    // Check for grammar in right parentheses (e.g. at end of meaning)
                    const rightParenMatch = right.match(/\(([^)]+)\)$/);
                    if (rightParenMatch && !grammar) {
                        const content = rightParenMatch[1].trim();
                        if (/(?:case|noun|verb|singular|plural|past|present|root|participle|masculine|feminine|neuter)/i.test(content)) {
                            grammar = content;
                            right = right.replace(/\s*\([^)]+\)$/, '').trim();
                        }
                    }

                    const meaning = right || '—';
                    tableRows.push({
                        sanskrit: sanskrit,
                        meaning: meaning,
                        grammar: grammar || '—'
                    });
                }
            });

            if (tableRows.length > 0) {
                let rowsHtml = '';
                tableRows.forEach((r, idx) => {
                    const rowClass = (idx % 2 === 0) ? 'row-even' : 'row-odd';
                    const grammarHtml = (r.grammar && r.grammar !== '—') 
                        ? `<span class="grammar-pill">${escapeHtml(r.grammar)}</span>` 
                        : '<span style="color: var(--text-dim);">—</span>';
                    
                    rowsHtml += `
                        <tr class="${rowClass}">
                            <td class="td-sanskrit">${escapeHtml(r.sanskrit)}</td>
                            <td class="td-meaning">${formatInline(r.meaning)}</td>
                            <td class="td-grammar">${grammarHtml}</td>
                        </tr>
                    `;
                });

                html += `
                    <div class="synthesis-card">
                        <div class="synthesis-card-header">
                            <div class="header-left">
                                <span class="card-icon">📖</span>
                                <span class="card-title">पदविभाग एवं अन्वयार्थ · Word-by-Word Gloss</span>
                            </div>
                            <span class="card-badge">${tableRows.length} Words</span>
                        </div>
                        <div class="table-responsive-wrapper">
                            <table class="word-meaning-table">
                                <thead>
                                    <tr>
                                        <th><span class="th-icon">🔤</span> Sanskrit (पदम्)</th>
                                        <th><span class="th-icon">📝</span> Meaning (अन्वयार्थ)</th>
                                        <th><span class="th-icon">🏷️</span> Grammar / Morphology (व्याकरणम्)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${rowsHtml}
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
            } else {
                html += `
                    <div class="synthesis-card">
                        <div class="synthesis-card-header">
                            <div class="header-left">
                                <span class="card-icon">📖</span>
                                <span class="card-title">पदविभाग एवं अन्वयार्थ · Word-by-Word Gloss</span>
                            </div>
                            <span class="card-badge">Analysis</span>
                        </div>
                        <div class="prose-content">
                            ${formatMarkdown(sections[2].body)}
                        </div>
                    </div>
                `;
            }
        }

        // 3. ANVAYA (व्याकरणात्मक अन्वय)
        if (sections[3] && sections[3].body) {
            const rawBody = sections[3].body;
            // Separate Sanskrit prose from English notes if present
            const lines = rawBody.split('\n').map(l => l.trim()).filter(l => l.length > 0);
            const sanskritLines = [];
            const notesLines = [];

            lines.forEach(line => {
                // If line contains predominant Latin characters without Sanskrit
                const latinCount = (line.match(/[a-zA-Z]/g) || []).length;
                if (latinCount > 15 && !line.match(/[क-ह]/)) {
                    notesLines.push(line);
                } else {
                    sanskritLines.push(line);
                }
            });

            let formattedSanskrit = escapeHtml(sanskritLines.join(' '));
            // Highlight supplied words in parentheses
            formattedSanskrit = formattedSanskrit.replace(/\(([^)]+)\)/g, '<span class="adhythara-word">($1)</span>');
            // Style dandas
            formattedSanskrit = formattedSanskrit.replace(/([।॥])/g, '<span class="sanskrit-danda">$1</span>');

            let notesHtml = '';
            if (notesLines.length > 0) {
                notesHtml = `
                    <div class="anvaya-notes-container">
                        ${notesLines.map(n => `<p class="anvaya-explanation">${formatInline(n)}</p>`).join('')}
                    </div>
                `;
            }

            html += `
                <div class="synthesis-card">
                    <div class="synthesis-card-header">
                        <div class="header-left">
                            <span class="card-icon">🔗</span>
                            <span class="card-title">व्याकरणात्मक अन्वय · Syntactic Reordering (Anvaya)</span>
                        </div>
                        <span class="card-badge">Grammatical Prose</span>
                    </div>
                    <div class="anvaya-body">
                        <div class="anvaya-prose-container">
                            <div class="anvaya-prose-badge">वाक्य-अन्वयक्रमः (Syntactic Order: Kartā → Karma → Kriyā)</div>
                            <div class="anvaya-sanskrit-text">${formattedSanskrit}</div>
                        </div>
                        ${notesHtml}
                    </div>
                </div>
            `;
        }

        // 5. BHAVARTHA / OVERALL MEANING (भावार्थ)
        if (sections[5] && sections[5].body) {
            const rawBody = sections[5].body;
            const lines = rawBody.split('\n').map(l => l.trim()).filter(l => l.length > 0);
            
            let bhavarthaHtml = '';
            const bulletItems = lines.filter(l => l.match(/^[-*•]\s+/));

            if (bulletItems.length > 0) {
                bhavarthaHtml = bulletItems.map(item => {
                    const text = item.replace(/^[-*•]\s+/, '');
                    return `
                        <div class="bullet-item">
                            <span class="bullet-dot">◆</span>
                            <div>${formatInline(text)}</div>
                        </div>
                    `;
                }).join('');
            } else {
                // Split into smaller readable paragraphs
                const sentences = rawBody.split(/(?<=[.।!])\s+/);
                const paras = [];
                let currPara = [];
                let currLen = 0;
                sentences.forEach(s => {
                    currPara.push(s);
                    currLen += s.length;
                    if (currLen > 240) {
                        paras.push(currPara.join(' '));
                        currPara = [];
                        currLen = 0;
                    }
                });
                if (currPara.length > 0) paras.push(currPara.join(' '));
                bhavarthaHtml = paras.map(p => `<p class="sentence-meaning-para">${formatInline(p)}</p>`).join('');
            }

            html += `
                <div class="synthesis-card">
                    <div class="synthesis-card-header">
                        <div class="header-left">
                            <span class="card-icon">💡</span>
                            <span class="card-title">भावार्थ · Overall Meaning & Clinical Purport</span>
                        </div>
                        <span class="card-badge">Central Teaching</span>
                    </div>
                    <div class="prose-content">
                        ${bhavarthaHtml}
                    </div>
                </div>
            `;
        }

        // 6. AYURVEDIC CONTEXT & SIGNIFICANCE (आयुर्वेदीय संदर्भ एवं महत्व)
        if (sections[6] && sections[6].body) {
            const rawBody = sections[6].body;
            const lines = rawBody.split('\n').map(l => l.trim()).filter(l => l.length > 0);

            let ayurvedaHtml = '';
            const subblocks = [];

            lines.forEach(line => {
                // Check for - **Title:** Description or **Title:** Description
                const match = line.match(/^[-*•]?\s*\*\*([^*]+)\*\*[:\s—–-]\s*(.*)$/);
                if (match) {
                    subblocks.push({ title: match[1].trim(), body: match[2].trim() });
                }
            });

            if (subblocks.length > 0) {
                ayurvedaHtml = subblocks.map(b => `
                    <div class="ayurvedic-subblock">
                        <div class="subblock-title">${escapeHtml(b.title)}</div>
                        <div class="subblock-body">${formatInline(b.body)}</div>
                    </div>
                `).join('');
            } else {
                // Split long paragraphs into readable blocks
                const paras = rawBody.split(/\n\n+/);
                ayurvedaHtml = paras.map(p => `
                    <div class="ayurvedic-subblock">
                        <div class="subblock-body">${formatInline(p)}</div>
                    </div>
                `).join('');
            }

            html += `
                <div class="synthesis-card">
                    <div class="synthesis-card-header">
                        <div class="header-left">
                            <span class="card-icon">🌿</span>
                            <span class="card-title">आयुर्वेदीय संदर्भ एवं महत्व · Ayurvedic Context & Significance</span>
                        </div>
                        <span class="card-badge">Clinical Context</span>
                    </div>
                    <div class="ayurveda-content">
                        ${ayurvedaHtml}
                    </div>
                </div>
            `;
        }

        // 7. DHVANITARTHA & TANTRAYUKTI (ध्वनितार्थ एवं तन्त्रयुक्ति)
        if (sections[7] && sections[7].body) {
            let content = formatInline(sections[7].body);
            // Highlight Tantrayukti mentions
            content = content.replace(/(उद्देश|निर्देश|अर्थापत्ति|प्रसङ्ग|समुच्चय|विपर्यय|अतिदेश|पदार्थ|संशय|निर्णय|वाक्यशेष|व्याख्यान|हेत्वर्थ)/g, '<span class="tantrayukti-chip">$1</span>');

            // Split into paragraphs if double newline or long
            const paras = content.split(/\n\n+/);
            const parasHtml = paras.map(p => `<p class="sentence-meaning-para">${p}</p>`).join('');

            html += `
                <div class="synthesis-card">
                    <div class="synthesis-card-header">
                        <div class="header-left">
                            <span class="card-icon">🔍</span>
                            <span class="card-title">ध्वनितार्थ एवं तन्त्रयुक्ति · Deeper Meaning & Tantrayukti</span>
                        </div>
                        <span class="card-badge">Hermeneutics</span>
                    </div>
                    <div class="dhvanitartha-content">
                        ${parasHtml}
                    </div>
                </div>
            `;
        }

        html += '</div>'; // close .synthesis-grid
        return html;
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
            item.className = 'accordion-item';
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
        elements.btnRunAnalysis.innerHTML = '<span class="btn-icon">⏳</span><span class="btn-text">Analyzing & Synthesizing...</span>';

        // Show progress bar with multi-phase indication
        elements.progressContainer.style.display = 'flex';
        elements.progressBarFill.style.width = '15%';
        elements.progressBarFill.style.background = 'var(--gold-gradient)';
        elements.progressStatusText.textContent = 'Generating 7-step analysis (Step 1/7)...';

        let progressTimer = setInterval(() => {
            let currentWidth = parseInt(elements.progressBarFill.style.width, 10) || 15;
            if (currentWidth < 70) {
                currentWidth += 10;
                elements.progressBarFill.style.width = currentWidth + '%';
                const stepNum = Math.min(7, Math.floor((currentWidth / 70) * 7) + 1);
                elements.progressStatusText.textContent = `Generating 7-step analysis (Step ${stepNum}/7)...`;
            } else if (currentWidth < 92) {
                currentWidth += 4;
                elements.progressBarFill.style.width = currentWidth + '%';
                elements.progressStatusText.textContent = 'Generating final explanation (अन्तिम-संश्लेषणम्)...';
            }
        }, 350);

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
            elements.progressStatusText.textContent = 'Final explanation ready!';

            // Refresh current shloka detail
            currentDetail.steps = data.steps;
            currentDetail.final_synthesis = data.final_synthesis;
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
            renderFinalExplanation(data.final_synthesis);

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

    function handleExportDossier() {
        if (!activeShlokaId) return;
        window.open(`/api/shlokas/${activeShlokaId}/export?format=markdown`, '_blank');
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
