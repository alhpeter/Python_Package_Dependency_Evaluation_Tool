const state = { experiment: '', data: null, chatMessages: [] };
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const escapeHtml = (value) => String(value ?? '').replace(/[&<>'"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;', '"':'&quot;'}[char]));
const metricLabels = {centrality:'Structural influence (centrality)', depth:'Dependency depth', indegree:'Packages depending on it', outdegree:'Child dependencies', last_update_days:'Days since update', maintainer_count:'Maintainer count', stars:'Public stars'};
const readableMetric = (key) => metricLabels[key] || key.replaceAll('_',' ');
const scorePoints = (score) => `${(Number(score || 0) * 100).toFixed(1)}`;
const metricValue = (key, value) => {
  if (value == null) return '-';
  if (key === 'centrality') return `${Number(value).toFixed(3)} / 1`;
  if (key === 'depth') return `${value} hops`;
  if (key === 'last_update_days') return `${value} days`;
  return Number(value).toLocaleString();
};

const tourSteps = [
  {
    target: '[data-tour="extract"]',
    title: 'Start with the project’s dependency file',
    description: 'An analysis begins with a requirements.txt file: a plain text list of Python packages the project uses. IDRF reads the listed package names as its starting point. This dashboard shows the results of a run; it does not edit that file.',
  },
  {
    target: '[data-tour="metadata"]',
    title: 'Look up package information',
    description: 'IDRF asks PyPI (the Python Package Index, where Python projects publish and share packages) for package details and dependency lists. It may also use linked public GitHub repository data, such as stars and update time. The lookup is bounded so one run does not try to map every package on the internet.',
  },
  {
    target: '.graph-panel',
    title: 'See how packages connect',
    description: 'The graph maps the project’s dependencies. Arrows point from a package to a dependency; color indicates dependency depth, and larger nodes have higher investigation-priority scores. A big node is a prompt to review, not evidence that a package is bad.',
  },
  {
    target: '#stats',
    title: 'Read the overview',
    description: 'These summary cards describe the selected experiment: how many packages and links were analyzed, how deep the dependency paths go, and the highest IPS. IPS means Investigative Priority Score. A score such as 70.7 / 100 is a weighted ranking—not a 70.7% chance of a problem.',
  },
  {
    target: '.investigation-panel',
    title: 'Start with the priority queue',
    description: 'IDRF surfaces a short list of candidates and ranks them by IPS. A package appears because its graph structure and/or metadata triggered investigation signals. The ranking helps decide what to inspect first; it is not a vulnerability verdict.',
  },
  {
    target: '.detail-panel',
    title: 'Check the evidence behind a score',
    description: 'Choose a package in the queue to see its measurements and the points contributed by each weighted signal. For example, depth counts dependency links from the project; centrality is a graph measure from 0 to 1, not a probability. Review the inputs before drawing conclusions.',
    prepare: () => {
      if (state.data?.cards.length && !$$('.package-row').some((button) => button.classList.contains('active'))) {
        selectCard(0);
      }
    },
  },
  {
    target: '#chat-sidebar',
    title: 'Ask questions in the AI results guide',
    description: 'Ask for a plain-language explanation or a comparison. The guide uses this experiment’s results, but it can be wrong and cannot run analyses or change files. Questions and result data are sent to Groq to generate its replies.',
    prepare: () => toggleChat(true),
  },
];
let activeTourStep = -1;
let lastTourFocus = null;

function positionTourCard(targetRect) {
  const card = $('#tour-card');
  const margin = 16;
  const cardRect = card.getBoundingClientRect();
  const left = Math.max(margin, Math.min(
    window.innerWidth - cardRect.width - margin,
    targetRect.left + targetRect.width / 2 - cardRect.width / 2,
  ));
  const below = targetRect.bottom + 16;
  const top = below + cardRect.height <= window.innerHeight - margin
    ? below
    : Math.max(margin, targetRect.top - cardRect.height - 16);
  card.style.left = `${left}px`;
  card.style.top = `${top}px`;
}

function showTourStep(index) {
  if (index < 0 || index >= tourSteps.length) {
    endTour();
    return;
  }
  if (activeTourStep < 0) lastTourFocus = document.activeElement;
  activeTourStep = index;
  const step = tourSteps[index];
  step.prepare?.();
  const target = $(step.target);
  if (!target) {
    endTour();
    return;
  }
  target.scrollIntoView({block: 'center', behavior: 'auto'});
  $('#tour-step').textContent = `STEP ${index + 1} OF ${tourSteps.length}`;
  $('#tour-title').textContent = step.title;
  $('#tour-description').textContent = step.description;
  $('#tour-previous').disabled = index === 0;
  $('#tour-next').textContent = index === tourSteps.length - 1 ? 'Finish' : 'Next';
  $('#tour-card').hidden = false;
  $('#tour-spotlight').hidden = false;
  requestAnimationFrame(() => {
    const rect = target.getBoundingClientRect();
    const spotlight = $('#tour-spotlight');
    spotlight.style.left = `${Math.max(4, rect.left - 6)}px`;
    spotlight.style.top = `${Math.max(4, rect.top - 6)}px`;
    spotlight.style.width = `${Math.min(window.innerWidth - 8, rect.width + 12)}px`;
    spotlight.style.height = `${Math.min(window.innerHeight - 8, rect.height + 12)}px`;
    positionTourCard(rect);
    $('#tour-next').focus();
  });
}

function startTour() {
  showTourStep(0);
}

function endTour() {
  activeTourStep = -1;
  $('#tour-card').hidden = true;
  $('#tour-spotlight').hidden = true;
  lastTourFocus?.focus?.();
}

function handleTourKeydown(event) {
  if (activeTourStep < 0) return;
  if (event.key === 'Escape') {
    event.preventDefault();
    endTour();
  } else if (event.key === 'ArrowRight') {
    event.preventDefault();
    showTourStep(activeTourStep + 1);
  } else if (event.key === 'ArrowLeft' && activeTourStep > 0) {
    event.preventDefault();
    showTourStep(activeTourStep - 1);
  } else if (event.key === 'Tab') {
    const controls = $$('#tour-card button').filter((button) => !button.disabled);
    const first = controls[0];
    const last = controls[controls.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }
}

function moveTourSpotlight() {
  if (activeTourStep < 0) return;
  const target = $(tourSteps[activeTourStep].target);
  if (!target) return;
  const rect = target.getBoundingClientRect();
  const spotlight = $('#tour-spotlight');
  spotlight.style.left = `${Math.max(4, rect.left - 6)}px`;
  spotlight.style.top = `${Math.max(4, rect.top - 6)}px`;
  spotlight.style.width = `${Math.min(window.innerWidth - 8, rect.width + 12)}px`;
  spotlight.style.height = `${Math.min(window.innerHeight - 8, rect.height + 12)}px`;
  positionTourCard(rect);
}

function renderInlineMarkdown(text) {
  const tokens = [];
  const token = (html) => {
    const marker = `\u0000${tokens.length}\u0000`;
    tokens.push(html);
    return marker;
  };
  let rendered = text
    .replace(/`([^`\n]+)`/g, (_, code) => token(`<code>${escapeHtml(code)}</code>`))
    .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/gi, (_, label, url) => token(
      `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`,
    ));
  rendered = escapeHtml(rendered)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/_(.+?)_/g, '<em>$1</em>');
  return rendered.replace(/\u0000(\d+)\u0000/g, (_, index) => tokens[Number(index)]);
}

function renderMarkdown(markdown) {
  const lines = String(markdown ?? '').replace(/\r\n?/g, '\n').split('\n');
  const blocks = [];
  let paragraph = [];
  let listItems = [];
  let listType = '';
  let codeLines = [];
  let inCode = false;

  const flushParagraph = () => {
    if (paragraph.length) {
      blocks.push(`<p>${paragraph.map(renderInlineMarkdown).join('<br>')}</p>`);
      paragraph = [];
    }
  };
  const flushList = () => {
    if (listItems.length) {
      blocks.push(`<${listType}>${listItems.map((item) => `<li>${renderInlineMarkdown(item)}</li>`).join('')}</${listType}>`);
      listItems = [];
      listType = '';
    }
  };
  const tableCells = (line) => line.trim().replace(/^\||\|$/g, '').split('|').map((cell) => cell.trim());

  for (let lineIndex = 0; lineIndex < lines.length; lineIndex += 1) {
    const line = lines[lineIndex];
    if (/^\s*```/.test(line)) {
      flushParagraph();
      flushList();
      if (inCode) {
        blocks.push(`<pre><code>${escapeHtml(codeLines.join('\n'))}</code></pre>`);
        codeLines = [];
      }
      inCode = !inCode;
      continue;
    }
    if (inCode) {
      codeLines.push(line);
      continue;
    }
    const heading = line.match(/^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$/);
    const listItem = line.match(/^\s*(?:[-+*]\s+|\d+[.)]\s+)(.+)$/);
    const quote = line.match(/^\s*>\s?(.*)$/);
    const nextLine = lines[lineIndex + 1] || '';
    const tableSeparator = /^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(nextLine);
    if (!line.trim()) {
      flushParagraph();
      flushList();
    } else if (line.includes('|') && tableSeparator) {
      flushParagraph();
      flushList();
      const headers = tableCells(line);
      const rows = [];
      lineIndex += 1;
      while (lineIndex + 1 < lines.length && lines[lineIndex + 1].includes('|') && lines[lineIndex + 1].trim()) {
        lineIndex += 1;
        rows.push(tableCells(lines[lineIndex]));
      }
      blocks.push(`<div class="markdown-table-wrap"><table><thead><tr>${headers.map((cell) => `<th>${renderInlineMarkdown(cell)}</th>`).join('')}</tr></thead><tbody>${rows.map((row) => `<tr>${headers.map((_, index) => `<td>${renderInlineMarkdown(row[index] || '')}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`);
    } else if (heading) {
      flushParagraph();
      flushList();
      const level = heading[1].length;
      blocks.push(`<h${level}>${renderInlineMarkdown(heading[2])}</h${level}>`);
    } else if (listItem) {
      flushParagraph();
      const nextType = /^\s*\d/.test(line) ? 'ol' : 'ul';
      if (listType && listType !== nextType) flushList();
      listType = nextType;
      listItems.push(listItem[1]);
    } else if (quote) {
      flushParagraph();
      flushList();
      blocks.push(`<blockquote>${renderInlineMarkdown(quote[1])}</blockquote>`);
    } else {
      flushList();
      paragraph.push(line);
    }
  }
  flushParagraph();
  flushList();
  if (inCode) blocks.push(`<pre><code>${escapeHtml(codeLines.join('\n'))}</code></pre>`);
  return blocks.join('');
}

async function loadExperiments() {
  const response = await fetch('/api/experiments');
  const experiments = await response.json();
  const select = $('#experiment-select');
  select.innerHTML = experiments.map((item) => `<option value="${escapeHtml(item.experiment)}">${escapeHtml(item.experiment)}</option>`).join('');
  $('#comparison-body').innerHTML = experiments.map((item) => `<tr><td>${escapeHtml(item.experiment)}</td><td>${item.packages_analyzed}</td><td>${item.cards_generated}</td><td>${Number(item.mean_depth || 0).toFixed(2)}</td><td>${scorePoints(item.max_score)} points</td></tr>`).join('');
  if (experiments.length) { state.experiment = experiments[0].experiment; await loadData(); }
}

async function loadData() {
  const response = await fetch(`/api/data/${encodeURIComponent(state.experiment)}`);
  if (!response.ok) { $('#package-list').innerHTML = '<p class="muted">Experiment artifacts are unavailable.</p>'; return; }
  state.data = await response.json();
  renderOverview(); renderPackages(); renderGraph();
}

function renderOverview() {
  const summary = state.data.summary;
  const packages = state.data.packages;
  const maxDepth = packages.reduce((max, item) => Math.max(max, item.depth || 0), 0);
  const values = [[packages.length,'Packages analyzed'], [packages.reduce((sum, item) => sum + (item.outdegree || 0), 0),'Dependency links'], [state.data.cards.length,'Investigation candidates'], [`${Number(summary.mean_depth || 0).toFixed(2)} hops`,'Average depth'], [`${scorePoints(summary.max_investigative_score)} / 100`,'Maximum priority'], [`${maxDepth} hops`,'Maximum depth']];
  $('#stats').innerHTML = values.map(([value, label]) => `<div class="stat"><div class="stat-value">${value}</div><div class="stat-label">${label}</div></div>`).join('');
  $('#queue-count').textContent = `${state.data.cards.length} surfaced`; $('#selected-name').textContent = 'Choose a package'; $('#detail-content').className = 'empty-state'; $('#detail-content').textContent = 'Select a surfaced dependency to inspect its evidence bundle.';
  state.chatMessages = [];
  renderChat();
}

function renderPackages() {
  const cards = state.data.cards;
  $('#package-list').innerHTML = cards.length ? cards.map((card, index) => { const evidence = card.evidence || {}; return `<button class="package-row" data-index="${index}"><span><span class="package-name">${escapeHtml(card.package)}</span><span class="package-meta">${escapeHtml((card.investigation_profile || []).join(' · '))} · depth ${evidence.depth ?? '-'} hops</span></span><span class="score">${scorePoints(card.investigative_priority_score)} pts</span></button>`; }).join('') : '<p class="muted">No surfaced insight cards are available.</p>';
  document.querySelectorAll('.package-row').forEach((button) => button.addEventListener('click', () => selectCard(Number(button.dataset.index))));
}

function selectCard(index) {
  document.querySelectorAll('.package-row').forEach((button) => button.classList.toggle('active', Number(button.dataset.index) === index));
  const card = state.data.cards[index]; const evidence = card.evidence || {};
  $('#selected-name').textContent = card.package;
  $('#detail-content').className = '';
  const scoreBreakdown = (state.data.score_guide || []).map((item) => {
    const contribution = Number((evidence.score_components || {})[item.key] || 0) * 100;
    const value = evidence[item.evidence_key];
    const basis = item.threshold != null
      ? `${value} (full points at ${item.threshold} or below)`
      : `${value} (full points at ${item.saturation})`;
    return `<div class="score-breakdown-row"><div><strong>${escapeHtml(item.label)}</strong><span>${contribution.toFixed(1)} / ${Number(item.max_points).toFixed(0)} points</span></div><p>${escapeHtml(item.explanation)} Input: ${escapeHtml(basis)}.</p></div>`;
  }).join('');
  $('#detail-content').innerHTML = `<div class="detail-score">${scorePoints(card.investigative_priority_score)}<span> / 100</span></div><p class="muted">IDRF’s investigation-priority score is a weighted sum of six signals. It helps rank what to review; it is not a probability, risk percentage, or proof of a problem.</p><div class="detail-block"><h3>Why look at this package?</h3><p>${escapeHtml(card.finding || card.rationale)}</p><p class="muted" style="margin-top:8px">${escapeHtml(card.rationale || '')}</p></div><div class="detail-block"><h3>What the measurements mean</h3><div class="evidence-grid">${['centrality','depth','indegree','outdegree','last_update_days','maintainer_count','stars'].map((key) => `<div title="${key === 'centrality' ? 'How often this package lies on shortest dependency paths, normalized from 0 to 1; it is not a probability.' : ''}"><b>${readableMetric(key)}</b><span>${escapeHtml(metricValue(key, evidence[key]))}</span></div>`).join('')}</div><p class="muted metric-note">Centrality is a normalized graph measure from 0 to 1, not a percentage. Depth counts dependency links from the project.</p></div><div class="detail-block"><h3>How the score was built</h3><p class="muted score-explainer">The six weighted contributions below add to the score above. Some factors reach their maximum at the stated cap.</p><div class="score-breakdown">${scoreBreakdown}</div></div><div class="detail-block"><h3>Signals found</h3><div class="chips">${(card.triggered_rules || []).concat(card.investigation_profile || []).map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join('')}</div></div><div class="detail-block"><h3>Suggested next step</h3><p>${escapeHtml(card.recommended_question || '')}</p><button class="explain-btn" id="explain-button">Ask Groq for a plain-English explanation</button><div id="explanation" class="explanation" aria-live="polite"></div></div>`;
  $('#explain-button').addEventListener('click', explainCard);
}

async function explainCard() {
  const output = $('#explanation'); output.textContent = 'Requesting an evidence-only explanation...';
  const packageName = $('#selected-name').textContent;
  const response = await fetch('/api/explain', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({experiment: state.experiment, package: packageName}) });
  const body = await response.json();
  if (!response.ok) { output.textContent = body.error || 'Groq explanation unavailable. The evidence-based IDRF analysis is still available.'; return; }
  const explanation = body.explanation || {}; const questions = Array.isArray(explanation.investigation_questions) ? explanation.investigation_questions : [explanation.investigation_questions]; output.innerHTML = `<strong>Groq explanation in plain English</strong><div class="explanation-block"><b>In short</b><p>${escapeHtml(explanation.summary)}</p></div><div class="explanation-block"><b>What the evidence means</b><p>${escapeHtml(explanation.evidence_interpretation)}</p></div><div class="explanation-block"><b>Why it deserves a closer look</b><p>${escapeHtml(explanation.why_it_matters)}</p></div><div class="explanation-block"><b>Questions to ask next</b><ul>${questions.filter(Boolean).map((question) => `<li>${escapeHtml(question)}</li>`).join('')}</ul></div><div class="explanation-block"><b>Keep in mind</b><p>${escapeHtml(explanation.limitations)}</p></div>`;
}

function renderChat() {
  const container = $('#chat-messages');
  if (!state.chatMessages.length) {
    container.innerHTML = '<p class="chat-empty">Try asking: “What does a score of 70 mean?” or “Which result should I look at first?”</p>';
    return;
  }
  container.innerHTML = state.chatMessages.map((message) => `<div class="chat-message ${message.role === 'user' ? 'chat-user' : 'chat-assistant'}"><strong>${message.role === 'user' ? 'You' : 'AI results guide'}</strong><div class="markdown-body">${message.role === 'user' ? `<p>${escapeHtml(message.content)}</p>` : renderMarkdown(message.content)}</div></div>`).join('');
  container.scrollTop = container.scrollHeight;
}

async function sendChatMessage(event) {
  event.preventDefault();
  const input = $('#chat-input');
  const question = input.value.trim();
  if (!question || !state.experiment) return;
  const experiment = state.experiment;
  state.chatMessages.push({role: 'user', content: question});
  renderChat();
  input.value = '';
  $('#chat-status').textContent = 'Checking this experiment’s evidence...';
  $('#chat-submit').disabled = true;
  $('#chat-reset').disabled = true;
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({experiment, messages: state.chatMessages.slice(-12)}),
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || 'The AI results guide is unavailable.');
    if (state.experiment !== experiment) return;
    state.chatMessages.push({role: 'assistant', content: body.answer});
    $('#chat-status').textContent = '';
    renderChat();
  } catch (error) {
    if (state.experiment === experiment) {
      state.chatMessages.pop();
      input.value = question;
      renderChat();
      $('#chat-status').textContent = error.message || 'The AI results guide is unavailable. Your dashboard data is still available.';
    }
  } finally {
    $('#chat-submit').disabled = false;
    $('#chat-reset').disabled = false;
    input.focus();
  }
}

function resetChat() {
  state.chatMessages = [];
  $('#chat-status').textContent = '';
  renderChat();
  $('#chat-input').focus();
}

function toggleChat(forceOpen) {
  const main = $('main');
  const open = forceOpen ?? main.classList.contains('chat-hidden');
  main.classList.toggle('chat-hidden', !open);
  $('#chat-toggle').setAttribute('aria-expanded', String(open));
  $('#chat-toggle').textContent = open ? 'Hide AI guide' : 'Show AI guide';
  updateSplitterBounds();
  if (open && window.matchMedia('(max-width: 1000px)').matches) $('#chat-input').focus();
}

function updateSplitterBounds() {
  const splitter = $('#chat-splitter');
  if (!splitter || window.matchMedia('(max-width: 1000px)').matches) return;
  const main = $('main');
  const minWidth = 280;
  const maxWidth = Math.max(minWidth, Math.min(640, window.innerWidth * 0.55, main.clientWidth - 420 - 12));
  const currentWidth = Number.parseFloat(getComputedStyle(main).getPropertyValue('--chat-sidebar-width')) || 360;
  const width = Math.max(minWidth, Math.min(maxWidth, currentWidth));
  main.style.setProperty('--chat-sidebar-width', `${width}px`);
  splitter.setAttribute('aria-valuemin', String(minWidth));
  splitter.setAttribute('aria-valuemax', String(Math.round(maxWidth)));
  splitter.setAttribute('aria-valuenow', String(Math.round(width)));
}

function setChatWidth(width) {
  const splitter = $('#chat-splitter');
  const minWidth = 280;
  const maxWidth = Number(splitter.getAttribute('aria-valuemax')) || 640;
  const nextWidth = Math.max(minWidth, Math.min(maxWidth, width));
  $('main').style.setProperty('--chat-sidebar-width', `${nextWidth}px`);
  splitter.setAttribute('aria-valuenow', String(Math.round(nextWidth)));
}

function startSplitterDrag(event) {
  if (event.button !== 0 || window.matchMedia('(max-width: 1000px)').matches) return;
  const splitter = $('#chat-splitter');
  const startX = event.clientX;
  const startWidth = $('#chat-sidebar').getBoundingClientRect().width;
  splitter.classList.add('is-dragging');
  splitter.setPointerCapture(event.pointerId);

  const move = (moveEvent) => {
    setChatWidth(startWidth + startX - moveEvent.clientX);
  };
  const finish = () => {
    splitter.classList.remove('is-dragging');
    splitter.removeEventListener('pointermove', move);
    splitter.removeEventListener('pointerup', finish);
    splitter.removeEventListener('pointercancel', finish);
  };
  splitter.addEventListener('pointermove', move);
  splitter.addEventListener('pointerup', finish);
  splitter.addEventListener('pointercancel', finish);
  event.preventDefault();
}

function resizeChatWithKeyboard(event) {
  const step = event.shiftKey ? 48 : 16;
  const currentWidth = Number.parseFloat(getComputedStyle($('main')).getPropertyValue('--chat-sidebar-width')) || 360;
  if (event.key === 'ArrowLeft') {
    setChatWidth(currentWidth + step);
  } else if (event.key === 'ArrowRight') {
    setChatWidth(currentWidth - step);
  } else if (event.key === 'Home') {
    setChatWidth(Number($('#chat-splitter').getAttribute('aria-valuemin')));
  } else if (event.key === 'End') {
    setChatWidth(Number($('#chat-splitter').getAttribute('aria-valuemax')));
  } else {
    return;
  }
  event.preventDefault();
}

function renderGraph() { const image = $('#graph-image'); image.hidden = false; image.src = `${state.data.graph}?t=${Date.now()}`; image.onerror = () => { image.hidden = true; $('#graph-empty').hidden = false; }; image.onload = () => { $('#graph-empty').hidden = true; }; }
$('#experiment-select').addEventListener('change', async (event) => { state.experiment = event.target.value; await loadData(); });
$('#chat-form').addEventListener('submit', sendChatMessage);
$('#chat-reset').addEventListener('click', resetChat);
$('#chat-toggle').addEventListener('click', () => toggleChat());
$('#chat-close').addEventListener('click', () => toggleChat(false));
$('#chat-splitter').addEventListener('pointerdown', startSplitterDrag);
$('#chat-splitter').addEventListener('keydown', resizeChatWithKeyboard);
window.addEventListener('resize', updateSplitterBounds);
window.addEventListener('resize', moveTourSpotlight);
window.addEventListener('scroll', moveTourSpotlight, true);
document.addEventListener('keydown', handleTourKeydown);
$('#tour-start').addEventListener('click', startTour);
$('#tour-next').addEventListener('click', () => showTourStep(activeTourStep + 1));
$('#tour-previous').addEventListener('click', () => showTourStep(activeTourStep - 1));
$('#tour-dismiss').addEventListener('click', endTour);
$('#tour-skip').addEventListener('click', endTour);
updateSplitterBounds();
if (window.matchMedia('(max-width: 1000px)').matches) toggleChat(false);
loadExperiments().catch(() => { $('#package-list').innerHTML = '<p class="muted">Dashboard data is unavailable. Start the Flask server from the project root.</p>'; });
