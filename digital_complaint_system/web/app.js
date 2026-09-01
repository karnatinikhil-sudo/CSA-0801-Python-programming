/**
 * Digital Complaint & Crime Zone Tracking System - Client GIS Controller
 */

// Application State
const state = {
  complaints: [],
  categories: [],
  mappings: {},
  criticalCrimes: [],
  zones: {},
  standardZones: {},
  analytics: {},
  activeTab: 'map',
  statusFilter: 'ALL',
  priorityFilter: 'ALL',
  mapFilter: 'ALL', // 'ALL', 'RED_ZONES', 'SOLVED', 'ACTIVE_ROUTINE'
  searchQuery: '',
  selectedComplaintId: null,
};

// Leaflet Map Instances
let mainMap = null;
let mainMapLayerGroup = null;
let mainMapHeatGroup = null;

let pickerMap = null;
let pickerMarker = null;

// DOM Element References
const elements = {
  // Navigation Tabs
  tabMapBtn: document.getElementById('tabMapBtn'),
  tabRegistryBtn: document.getElementById('tabRegistryBtn'),
  tabAnalyticsBtn: document.getElementById('tabAnalyticsBtn'),
  tabCategoriesBtn: document.getElementById('tabCategoriesBtn'),
  tabMap: document.getElementById('tabMap'),
  tabRegistry: document.getElementById('tabRegistry'),
  tabAnalytics: document.getElementById('tabAnalytics'),
  tabCategories: document.getElementById('tabCategories'),

  // KPI Elements
  kpiTotalVal: document.getElementById('kpiTotalVal'),
  kpiCriticalVal: document.getElementById('kpiCriticalVal'),
  kpiPendingVal: document.getElementById('kpiPendingVal'),
  kpiResolvedVal: document.getElementById('kpiResolvedVal'),
  kpiAvgTimeVal: document.getElementById('kpiAvgTimeVal'),
  kpiTotal: document.getElementById('kpiTotal'),
  kpiCritical: document.getElementById('kpiCritical'),
  kpiPending: document.getElementById('kpiPending'),
  kpiResolved: document.getElementById('kpiResolved'),

  // Map Filter Counts
  countMapAll: document.getElementById('countMapAll'),
  countMapRed: document.getElementById('countMapRed'),
  countMapSolved: document.getElementById('countMapSolved'),
  countMapActive: document.getElementById('countMapActive'),

  // Map Elements
  crimeMapCanvas: document.getElementById('crimeMapCanvas'),
  zoneThreatCardsList: document.getElementById('zoneThreatCardsList'),

  // Registry & Search
  searchInput: document.getElementById('searchInput'),
  statusFilter: document.getElementById('statusFilter'),
  priorityFilter: document.getElementById('priorityFilter'),
  refreshBtn: document.getElementById('refreshBtn'),
  complaintsTableBody: document.getElementById('complaintsTableBody'),
  emptyState: document.getElementById('emptyState'),

  // Analytics & Reports
  categoryDistributionBars: document.getElementById('categoryDistributionBars'),
  departmentWorkloadBars: document.getElementById('departmentWorkloadBars'),
  summaryReportPre: document.getElementById('summaryReportPre'),
  copySummaryReportBtn: document.getElementById('copySummaryReportBtn'),
  categoryCardsGrid: document.getElementById('categoryCardsGrid'),

  // Register Modal & Mini Map
  openRegisterModalBtn: document.getElementById('openRegisterModalBtn'),
  registerModal: document.getElementById('registerModal'),
  registerForm: document.getElementById('registerForm'),
  complainantName: document.getElementById('complainantName'),
  complaintCategory: document.getElementById('complaintCategory'),
  criticalCrimeAlertBox: document.getElementById('criticalCrimeAlertBox'),
  complaintPriority: document.getElementById('complaintPriority'),
  complaintLocation: document.getElementById('complaintLocation'),
  routingPreviewDept: document.getElementById('routingPreviewDept'),
  complaintDescription: document.getElementById('complaintDescription'),
  pickerMapCanvas: document.getElementById('pickerMapCanvas'),
  gpsBadge: document.getElementById('gpsBadge'),
  selectedLat: document.getElementById('selectedLat'),
  selectedLon: document.getElementById('selectedLon'),

  // Detail Modal
  detailModal: document.getElementById('detailModal'),
  detailModalId: document.getElementById('detailModalId'),
  detailModalComplainant: document.getElementById('detailModalComplainant'),
  detailModalCategoryDept: document.getElementById('detailModalCategoryDept'),
  detailModalLocation: document.getElementById('detailModalLocation'),
  detailModalDesc: document.getElementById('detailModalDesc'),
  detailModalPriority: document.getElementById('detailModalPriority'),
  detailModalStatus: document.getElementById('detailModalStatus'),
  detailModalDateReg: document.getElementById('detailModalDateReg'),
  detailModalDateRes: document.getElementById('detailModalDateRes'),
  assignStaffInput: document.getElementById('assignStaffInput'),
  saveAssignBtn: document.getElementById('saveAssignBtn'),
  updateStatusSelect: document.getElementById('updateStatusSelect'),
  saveStatusBtn: document.getElementById('saveStatusBtn'),
  escalateActionBtn: document.getElementById('escalateActionBtn'),
  quickResolveBtn: document.getElementById('quickResolveBtn'),
  detailTimelineContainer: document.getElementById('detailTimelineContainer'),
  viewDetailPlainReportBtn: document.getElementById('viewDetailPlainReportBtn'),

  // Categories Modal
  openAddCategoryModalBtn: document.getElementById('openAddCategoryModalBtn'),
  addCategoryModal: document.getElementById('addCategoryModal'),
  addCategoryForm: document.getElementById('addCategoryForm'),
  newCategoryName: document.getElementById('newCategoryName'),
  newDeptName: document.getElementById('newDeptName'),

  toastContainer: document.getElementById('toastContainer'),
};

// =============================================================================
// API CLIENT
// =============================================================================

const api = {
  async get(endpoint) {
    const res = await fetch(`/api${endpoint}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: 'Network request failed' }));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
  },

  async post(endpoint, data) {
    const res = await fetch(`/api${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: 'Network request failed' }));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
  },
};

// =============================================================================
// TOAST NOTIFICATIONS
// =============================================================================

function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  elements.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

// =============================================================================
// LEAFLET CRIME MAP INITIALIZATION & RENDERING
// =============================================================================

function initMainMap() {
  if (mainMap) return;

  const defaultCenter = [13.0418, 80.2341]; // Center of Chennai (T. Nagar)
  mainMap = L.map('crimeMapCanvas', {
    center: defaultCenter,
    zoom: 12,
    zoomControl: true,
  });

  // Dark Mode CartoDB Tile Layer
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(mainMap);

  mainMapHeatGroup = L.layerGroup().addTo(mainMap);
  mainMapLayerGroup = L.layerGroup().addTo(mainMap);
}

function initPickerMap() {
  if (pickerMap) return;

  const initialLat = parseFloat(elements.selectedLat.value) || 13.0418;
  const initialLon = parseFloat(elements.selectedLon.value) || 80.2341;

  pickerMap = L.map('pickerMapCanvas', {
    center: [initialLat, initialLon],
    zoom: 13,
  });

  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap',
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(pickerMap);

  const customPinIcon = L.divIcon({
    className: 'custom-map-marker marker-critical-crime',
    html: `<svg width="18" height="18" viewBox="0 0 24 24" fill="white" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle></svg>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });

  pickerMarker = L.marker([initialLat, initialLon], {
    icon: customPinIcon,
    draggable: true,
  }).addTo(pickerMap);

  // Click on map to position pin
  pickerMap.on('click', (e) => {
    const { lat, lng } = e.latlng;
    updatePickerLocation(lat, lng);
  });

  pickerMarker.on('dragend', (e) => {
    const { lat, lng } = e.target.getLatLng();
    updatePickerLocation(lat, lng);
  });
}

function updatePickerLocation(lat, lng) {
  const roundedLat = parseFloat(lat.toFixed(6));
  const roundedLon = parseFloat(lng.toFixed(6));

  elements.selectedLat.value = roundedLat;
  elements.selectedLon.value = roundedLon;
  elements.gpsBadge.textContent = `Lat: ${roundedLat}, Lon: ${roundedLon}`;

  if (pickerMarker) {
    pickerMarker.setLatLng([roundedLat, roundedLon]);
  }
}

function renderCrimeMap() {
  if (!mainMap || !mainMapLayerGroup || !mainMapHeatGroup) return;

  mainMapHeatGroup.clearLayers();
  mainMapLayerGroup.clearLayers();

  // 1. Render Zone Heat Circles (Red for High Threat, Amber for Moderate, Green for Safe)
  for (const [zoneName, zoneData] of Object.entries(state.zones || {})) {
    const center = zoneData.center || [13.0418, 80.2341];
    const threat = zoneData.threat_level;

    let circleColor = '#10b981'; // Green Safe
    let fillColor = '#10b981';
    let fillOpacity = 0.12;
    let radius = 1400;

    if (threat === 'RED_HOTSPOT') {
      circleColor = '#ef4444'; // Red Hotspot
      fillColor = '#ef4444';
      fillOpacity = 0.28;
      radius = 1900;
    } else if (threat === 'AMBER_MODERATE') {
      circleColor = '#f59e0b';
      fillColor = '#f59e0b';
      fillOpacity = 0.18;
      radius = 1600;
    }

    const circle = L.circle(center, {
      color: circleColor,
      fillColor: fillColor,
      fillOpacity: fillOpacity,
      weight: threat === 'RED_HOTSPOT' ? 3 : 1.5,
      radius: radius,
    });

    circle.bindTooltip(`
      <div style="font-weight:700; font-size:0.85rem; color:${circleColor};">
        ${threat === 'RED_HOTSPOT' ? '🚨 HIGH CRIME RED ZONE' : threat === 'AMBER_MODERATE' ? '⚠️ MODERATE INCIDENT ZONE' : '🛡️ SAFE / RESOLVED ZONE'}
      </div>
      <div><strong>${escapeHtml(zoneName)}</strong></div>
      <div>Active Violent Crimes: <strong>${zoneData.active_critical_crimes}</strong></div>
      <div>Solved Cases: <strong>${zoneData.solved_cases}</strong></div>
    `);

    mainMapHeatGroup.addLayer(circle);
  }

  // 2. Filter & Render Case Markers
  let countAll = 0;
  let countRed = 0;
  let countSolved = 0;
  let countActive = 0;

  state.complaints.forEach((item) => {
    countAll++;
    const isSolved = ['RESOLVED', 'CLOSED'].includes(item.status);
    const isCritical = item.is_critical_crime || item.priority === 'HIGH' || item.status === 'ESCALATED';

    if (isSolved) countSolved++;
    if (isCritical && !isSolved) countRed++;
    if (!isSolved && !isCritical) countActive++;

    // Check Map Filter
    if (state.mapFilter === 'RED_ZONES' && (!isCritical || isSolved)) return;
    if (state.mapFilter === 'SOLVED' && !isSolved) return;
    if (state.mapFilter === 'ACTIVE_ROUTINE' && (isCritical || isSolved)) return;

    const lat = item.latitude || 13.0418;
    const lon = item.longitude || 80.2341;

    // Marker styling
    let markerClass = 'marker-routine';
    let iconSvg = `<svg width="14" height="14" viewBox="0 0 24 24" fill="white"><circle cx="12" cy="12" r="8"></circle></svg>`;

    if (isSolved) {
      markerClass = 'marker-solved-case';
      iconSvg = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    } else if (isCritical) {
      markerClass = 'marker-critical-crime';
      iconSvg = `<svg width="14" height="14" viewBox="0 0 24 24" fill="white"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path></svg>`;
    }

    const icon = L.divIcon({
      className: `custom-map-marker ${markerClass}`,
      html: iconSvg,
      iconSize: isCritical && !isSolved ? [28, 28] : [24, 24],
      iconAnchor: [12, 12],
    });

    const marker = L.marker([lat, lon], { icon });

    const statusBadgeClass = `badge-${item.status.toLowerCase()}`;
    const priBadgeClass = `badge-${item.priority.toLowerCase()}`;

    const popupContent = `
      <div class="popup-incident-card">
        <div class="popup-id-header">
          <strong style="color:var(--primary); font-family:monospace;">${item.complaint_id}</strong>
          <span class="badge ${statusBadgeClass}">${item.status}</span>
        </div>
        <div style="font-weight:700; color:#fff; font-size:0.9rem;">${escapeHtml(item.category)}</div>
        <div style="color:var(--blue); font-size:0.75rem;">📍 ${escapeHtml(item.location || 'City Grid')} • ${escapeHtml(item.department)}</div>
        <p style="color:var(--text-muted); font-size:0.78rem; margin: 0.25rem 0;">${escapeHtml(item.description)}</p>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.4rem;">
          <span class="badge ${priBadgeClass}">${item.priority}</span>
          <button class="btn btn-primary" style="padding:0.25rem 0.55rem; font-size:0.72rem;" onclick="openDetailModal('${item.complaint_id}')">
            Manage Case
          </button>
        </div>
      </div>
    `;

    marker.bindPopup(popupContent);
    mainMapLayerGroup.addLayer(marker);
  });

  // Update counts on filter chips
  elements.countMapAll.textContent = countAll;
  elements.countMapRed.textContent = countRed;
  elements.countMapSolved.textContent = countSolved;
  elements.countMapActive.textContent = countActive;
}

function renderZoneSidebar() {
  elements.zoneThreatCardsList.innerHTML = '';

  const zoneEntries = Object.entries(state.zones || {});
  // Sort: Red Hotspots first, then Amber, then Green
  zoneEntries.sort((a, b) => b[1].threat_score - a[1].threat_score);

  zoneEntries.forEach(([zoneName, z]) => {
    const card = document.createElement('div');
    let borderClass = 'zone-card-green';
    let pillClass = 'threat-pill-green';
    let label = '🛡️ SAFE ZONE';

    if (z.threat_level === 'RED_HOTSPOT') {
      borderClass = 'zone-card-red';
      pillClass = 'threat-pill-red';
      label = '🚨 RED CRIME ZONE';
    } else if (z.threat_level === 'AMBER_MODERATE') {
      borderClass = 'zone-card-amber';
      pillClass = 'threat-pill-amber';
      label = '⚠️ MODERATE';
    }

    card.className = `zone-card ${borderClass}`;
    card.innerHTML = `
      <div class="zone-card-top">
        <span class="zone-name">${escapeHtml(zoneName)}</span>
        <span class="threat-pill ${pillClass}">${label}</span>
      </div>
      <div class="zone-stats-row">
        <span class="stat-alert">Violent Crimes: ${z.active_critical_crimes}</span>
        <span>Active: ${z.active_pending}</span>
        <span class="stat-solved">Solved: ${z.solved_cases}</span>
      </div>
    `;

    card.addEventListener('click', () => {
      if (mainMap && z.center) {
        mainMap.flyTo(z.center, 14, { duration: 1.2 });
      }
    });

    elements.zoneThreatCardsList.appendChild(card);
  });
}

// =============================================================================
// REGISTRY & TABLE RENDERERS
// =============================================================================

function updateKPICards() {
  if (!state.analytics) return;
  const a = state.analytics;
  elements.kpiTotalVal.textContent = a.total ?? 0;
  elements.kpiCriticalVal.textContent = a.critical_crimes ?? 0;
  elements.kpiPendingVal.textContent = a.pending ?? 0;
  elements.kpiResolvedVal.textContent = a.resolved ?? 0;
  elements.kpiAvgTimeVal.textContent = `${(a.average_resolution_time ?? 0).toFixed(1)}h`;
}

function renderComplaintsTable() {
  const filtered = state.complaints.filter((item) => {
    if (state.statusFilter === 'PENDING') {
      if (['RESOLVED', 'CLOSED'].includes(item.status)) return false;
    } else if (state.statusFilter !== 'ALL') {
      if (item.status !== state.statusFilter) return false;
    }

    if (state.priorityFilter !== 'ALL' && item.priority !== state.priorityFilter) {
      return false;
    }

    if (state.searchQuery) {
      const query = state.searchQuery.toLowerCase();
      const matchId = item.complaint_id.toLowerCase().includes(query);
      const matchName = item.complainant.toLowerCase().includes(query);
      const matchCat = item.category.toLowerCase().includes(query);
      const matchDept = (item.department || '').toLowerCase().includes(query);
      const matchLoc = (item.location || '').toLowerCase().includes(query);
      const matchDesc = item.description.toLowerCase().includes(query);
      const matchStaff = (item.assigned_to || '').toLowerCase().includes(query);
      return matchId || matchName || matchCat || matchDept || matchLoc || matchDesc || matchStaff;
    }
    return true;
  });

  elements.complaintsTableBody.innerHTML = '';

  if (filtered.length === 0) {
    elements.emptyState.classList.remove('hidden');
    return;
  }
  elements.emptyState.classList.add('hidden');

  filtered.forEach((item) => {
    const tr = document.createElement('tr');
    tr.style.cursor = 'pointer';

    const priClass = `badge-${item.priority.toLowerCase()}`;
    const stClass = `badge-${item.status.toLowerCase()}`;
    const isCritical = item.is_critical_crime;

    tr.innerHTML = `
      <td>
        <span class="id-badge">${item.complaint_id}</span>
        ${isCritical ? '<span title="Critical Violent Crime" style="color:var(--rose); font-size:0.8rem; margin-left:4px;">⚠️</span>' : ''}
      </td>
      <td class="complainant-cell">${escapeHtml(item.complainant)}</td>
      <td>
        <strong>${escapeHtml(item.category)}</strong>
        <span class="dept-tag">${escapeHtml(item.department || 'General Administration')}</span>
      </td>
      <td><span style="color:var(--blue); font-size:0.8rem;">📍 ${escapeHtml(item.location || 'Downtown Central')}</span></td>
      <td><div class="desc-truncate" title="${escapeHtml(item.description)}">${escapeHtml(item.description)}</div></td>
      <td><span class="badge ${priClass}">${item.priority}</span></td>
      <td><span class="badge ${stClass}">${item.status}</span></td>
      <td>${item.assigned_to ? `<span style="color:var(--blue)">${escapeHtml(item.assigned_to)}</span>` : '<span style="color:var(--text-dim)">Unassigned</span>'}</td>
      <td style="font-size:0.75rem; color:var(--text-dim);">${escapeHtml(item.date_registered)}</td>
      <td>
        <button class="btn btn-secondary" style="padding:0.35rem 0.65rem; font-size:0.75rem;" onclick="openDetailModal('${item.complaint_id}', event)">
          Manage
        </button>
      </td>
    `;

    tr.addEventListener('click', (e) => {
      if (e.target.tagName !== 'BUTTON') {
        openDetailModal(item.complaint_id);
      }
    });

    elements.complaintsTableBody.appendChild(tr);
  });
}

function renderAnalyticsView() {
  if (!state.analytics) return;
  const { category_frequency, department_breakdown } = state.analytics;

  // Category Distribution
  elements.categoryDistributionBars.innerHTML = '';
  const maxCatCount = Math.max(...Object.values(category_frequency || {}), 1);
  for (const [cat, count] of Object.entries(category_frequency || {})) {
    const pct = ((count / maxCatCount) * 100).toFixed(0);
    const item = document.createElement('div');
    item.className = 'bar-item';
    item.innerHTML = `
      <div class="bar-header">
        <span><strong>${escapeHtml(cat)}</strong></span>
        <span>${count} incident(s)</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width: ${pct}%"></div>
      </div>
    `;
    elements.categoryDistributionBars.appendChild(item);
  }

  // Department Workload
  elements.departmentWorkloadBars.innerHTML = '';
  const maxDeptCount = Math.max(...Object.values(department_breakdown || {}), 1);
  for (const [dept, count] of Object.entries(department_breakdown || {})) {
    const pct = ((count / maxDeptCount) * 100).toFixed(0);
    const item = document.createElement('div');
    item.className = 'bar-item';
    item.innerHTML = `
      <div class="bar-header">
        <span><strong>${escapeHtml(dept)}</strong></span>
        <span>${count} cases</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width: ${pct}%; background: linear-gradient(90deg, #f43f5e, #6366f1)"></div>
      </div>
    `;
    elements.departmentWorkloadBars.appendChild(item);
  }
}

function renderCategoriesView() {
  elements.categoryCardsGrid.innerHTML = '';
  for (const [cat, dept] of Object.entries(state.mappings)) {
    const card = document.createElement('div');
    card.className = 'cat-card';
    card.innerHTML = `
      <span class="cat-name">${escapeHtml(cat)}</span>
      <span class="dept-name">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
        ${escapeHtml(dept)}
      </span>
    `;
    elements.categoryCardsGrid.appendChild(card);
  }
}

function populateCategoryDropdown() {
  elements.complaintCategory.innerHTML = '';
  state.categories.forEach((cat) => {
    const opt = document.createElement('option');
    opt.value = cat;
    const isCrit = (state.criticalCrimes || []).includes(cat);
    opt.textContent = `${isCrit ? '⚠️ [CRITICAL] ' : ''}${cat}`;
    elements.complaintCategory.appendChild(opt);
  });
  checkCriticalCategorySelection();
}

function checkCriticalCategorySelection() {
  const selCat = elements.complaintCategory.value;
  const isCrit = (state.criticalCrimes || []).includes(selCat);
  const dept = state.mappings[selCat] || 'Special Crime Investigation Unit';
  elements.routingPreviewDept.textContent = dept;

  if (isCrit) {
    elements.criticalCrimeAlertBox.classList.remove('hidden');
    elements.complaintPriority.value = 'HIGH';
  } else {
    elements.criticalCrimeAlertBox.classList.add('hidden');
  }
}

// =============================================================================
// MODALS & ACTIONS
// =============================================================================

function openModal(modalId) {
  document.getElementById(modalId).classList.remove('hidden');
  if (modalId === 'registerModal') {
    setTimeout(() => {
      initPickerMap();
      if (pickerMap) pickerMap.invalidateSize();
    }, 200);
  }
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.add('hidden');
}

window.openDetailModal = function (complaintId, event) {
  if (event) event.stopPropagation();
  state.selectedComplaintId = complaintId;
  const item = state.complaints.find((c) => c.complaint_id === complaintId);
  if (!item) return;

  elements.detailModalId.textContent = item.complaint_id;
  elements.detailModalComplainant.textContent = item.complainant;
  elements.detailModalCategoryDept.textContent = `${item.category} • ${item.department}`;
  elements.detailModalLocation.textContent = `${item.location || 'Downtown Central'} (GPS: ${item.latitude || '17.3850'}, ${item.longitude || '78.4867'})`;
  elements.detailModalDesc.textContent = item.description;

  elements.detailModalPriority.innerHTML = `<span class="badge badge-${item.priority.toLowerCase()}">${item.priority}</span>`;
  elements.detailModalStatus.innerHTML = `<span class="badge badge-${item.status.toLowerCase()}">${item.status}</span>`;
  elements.detailModalDateReg.textContent = item.date_registered || 'N/A';
  elements.detailModalDateRes.textContent = item.date_resolved || 'Investigation Active';

  elements.assignStaffInput.value = item.assigned_to || '';
  elements.updateStatusSelect.value = item.status;

  // Timeline
  elements.detailTimelineContainer.innerHTML = '';
  const history = item.status_history || [];
  if (history.length === 0) {
    elements.detailTimelineContainer.innerHTML = '<span style="color:var(--text-dim); font-size:0.8rem;">No events logged.</span>';
  } else {
    history.forEach(([st, time], idx) => {
      const step = document.createElement('div');
      step.className = 'timeline-item';
      step.innerHTML = `
        <span class="timeline-status">${idx + 1}. ${escapeHtml(st)}</span>
        <span class="timeline-time">${escapeHtml(time)}</span>
      `;
      elements.detailTimelineContainer.appendChild(step);
    });
  }

  openModal('detailModal');
};

// =============================================================================
// REFRESH DATA & EVENT BINDINGS
// =============================================================================

async function refreshAllData() {
  try {
    const [cRes, catRes, aRes, zRes, repRes] = await Promise.all([
      api.get('/complaints'),
      api.get('/categories'),
      api.get('/analytics'),
      api.get('/zones'),
      api.get('/reports/summary'),
    ]);

    state.complaints = cRes.complaints || [];
    state.categories = catRes.categories || [];
    state.mappings = catRes.mappings || {};
    state.criticalCrimes = catRes.critical_crimes || [];
    state.analytics = aRes.analytics || {};
    state.zones = zRes.zones || {};
    state.standardZones = zRes.standard_zones || {};

    updateKPICards();
    renderCrimeMap();
    renderZoneSidebar();
    renderComplaintsTable();
    renderAnalyticsView();
    renderCategoriesView();
    populateCategoryDropdown();

    if (repRes.report) {
      elements.summaryReportPre.textContent = repRes.report;
    }
  } catch (err) {
    showToast(`Failed to load data: ${err.message}`, 'error');
  }
}

function setupEventListeners() {
  // Navigation Tabs
  const tabButtons = [
    { btn: elements.tabMapBtn, target: elements.tabMap },
    { btn: elements.tabRegistryBtn, target: elements.tabRegistry },
    { btn: elements.tabAnalyticsBtn, target: elements.tabAnalytics },
    { btn: elements.tabCategoriesBtn, target: elements.tabCategories },
  ];

  tabButtons.forEach(({ btn, target }) => {
    btn.addEventListener('click', () => {
      tabButtons.forEach((t) => {
        t.btn.classList.remove('active');
        t.target.classList.remove('active');
      });
      btn.classList.add('active');
      target.classList.add('active');

      if (target === elements.tabMap && mainMap) {
        setTimeout(() => mainMap.invalidateSize(), 150);
      }
    });
  });

  // Map Filter Buttons
  document.querySelectorAll('[data-map-filter]').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-map-filter]').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      state.mapFilter = btn.getAttribute('data-map-filter');
      renderCrimeMap();
    });
  });

  // KPI Clicks
  elements.kpiCritical.addEventListener('click', () => {
    elements.tabMapBtn.click();
    document.getElementById('mapFilterRed').click();
  });

  elements.kpiResolved.addEventListener('click', () => {
    elements.tabMapBtn.click();
    document.getElementById('mapFilterSolved').click();
  });

  // Search & Registry Filter
  elements.searchInput.addEventListener('input', (e) => {
    state.searchQuery = e.target.value.trim();
    renderComplaintsTable();
  });

  elements.statusFilter.addEventListener('change', (e) => {
    state.statusFilter = e.target.value;
    renderComplaintsTable();
  });

  elements.priorityFilter.addEventListener('change', (e) => {
    state.priorityFilter = e.target.value;
    renderComplaintsTable();
  });

  elements.refreshBtn.addEventListener('click', async () => {
    await refreshAllData();
    showToast('Incident radar updated!');
  });

  // Modal Triggers
  elements.openRegisterModalBtn.addEventListener('click', () => openModal('registerModal'));
  elements.openAddCategoryModalBtn.addEventListener('click', () => openModal('addCategoryModal'));

  document.querySelectorAll('[data-close]').forEach((btn) => {
    btn.addEventListener('click', () => closeModal(btn.getAttribute('data-close')));
  });

  elements.complaintCategory.addEventListener('change', checkCriticalCategorySelection);

  // When selecting Zone in dropdown, pan mini-map to that zone
  elements.complaintLocation.addEventListener('change', (e) => {
    const zoneName = e.target.value;
    const coords = state.standardZones[zoneName];
    if (coords && pickerMap) {
      updatePickerLocation(coords[0], coords[1]);
      pickerMap.setView(coords, 14);
    }
  });

  // Submit Registration
  elements.registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      name: elements.complainantName.value,
      category: elements.complaintCategory.value,
      description: elements.complaintDescription.value,
      priority: elements.complaintPriority.value,
      location: elements.complaintLocation.value,
      latitude: parseFloat(elements.selectedLat.value),
      longitude: parseFloat(elements.selectedLon.value),
    };

    try {
      const res = await api.post('/complaints/register', payload);
      showToast(`Incident ${res.complaint_id} recorded & broadcast on Crime Map!`);
      closeModal('registerModal');
      elements.registerForm.reset();
      await refreshAllData();
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
  });

  // Assign Staff
  elements.saveAssignBtn.addEventListener('click', async () => {
    const staff = elements.assignStaffInput.value.trim();
    if (!staff) {
      showToast('Officer name cannot be empty.', 'error');
      return;
    }
    try {
      await api.post('/complaints/assign', {
        complaint_id: state.selectedComplaintId,
        staff,
      });
      showToast(`Assigned ${state.selectedComplaintId} to ${staff}.`);
      await refreshAllData();
      window.openDetailModal(state.selectedComplaintId);
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
  });

  // Update Status
  elements.saveStatusBtn.addEventListener('click', async () => {
    const newStatus = elements.updateStatusSelect.value;
    try {
      await api.post('/complaints/status', {
        complaint_id: state.selectedComplaintId,
        status: newStatus,
      });
      showToast(`Status updated to ${newStatus}.`);
      await refreshAllData();
      window.openDetailModal(state.selectedComplaintId);
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
  });

  // Escalate
  elements.escalateActionBtn.addEventListener('click', async () => {
    try {
      await api.post('/complaints/escalate', {
        complaint_id: state.selectedComplaintId,
      });
      showToast(`Incident ${state.selectedComplaintId} escalated to HIGH priority!`);
      await refreshAllData();
      window.openDetailModal(state.selectedComplaintId);
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
  });

  // Quick Resolve
  elements.quickResolveBtn.addEventListener('click', async () => {
    try {
      await api.post('/complaints/status', {
        complaint_id: state.selectedComplaintId,
        status: 'RESOLVED',
      });
      showToast(`Case ${state.selectedComplaintId} marked as SOLVED! Green status set.`);
      await refreshAllData();
      window.openDetailModal(state.selectedComplaintId);
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
  });

  // Copy Summary Report
  elements.copySummaryReportBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(elements.summaryReportPre.textContent).then(() => {
      showToast('Summary report copied to clipboard!');
    });
  });

  // View Plain Text Report
  elements.viewDetailPlainReportBtn.addEventListener('click', async () => {
    try {
      const res = await api.get(`/reports/complaint?id=${state.selectedComplaintId}`);
      if (res.report) alert(res.report);
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Initial Load
document.addEventListener('DOMContentLoaded', async () => {
  initMainMap();
  setupEventListeners();
  await refreshAllData();
});
