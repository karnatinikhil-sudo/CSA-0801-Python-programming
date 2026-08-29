/**
 * Digital To-Do & Wellness Manager — Core Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    initCSRF();
    initQuickTask();
    initMobileQuickTask();
    initTaskToggles();
    initWellnessActions();
    initReminderStream();
    initConflictChecker();
    initPWA();
    initConnectivity();
});

// Helper: Haptic touch vibration for mobile responsiveness
function triggerHaptic(pattern = 35) {
    if ('vibrate' in navigator) {
        try {
            navigator.vibrate(pattern);
        } catch (e) {
            // Safe fallback
        }
    }
}

// 1. CSRF Token Helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function initCSRF() {
    // Attach default headers
}

// 2. Quick Task Creation (< 10 Seconds flow) & Natural Language Parser
function initQuickTask() {
    const quickInput = document.getElementById('quick-task-title');
    const quickForm = document.getElementById('quick-task-form');
    if (!quickInput) return;

    // Real-time Natural Language Detection debounce
    let debounceTimer;
    quickInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const val = e.target.value;
        if (val.length < 5) return;

        debounceTimer = setTimeout(() => {
            fetch(`/tasks/parse-nl/?text=${encodeURIComponent(val)}`)
                .then(res => res.json())
                .then(data => {
                    const dateInput = document.getElementById('quick-task-date');
                    const timeInput = document.getElementById('quick-task-time');
                    const prioritySelect = document.getElementById('quick-task-priority');
                    const categorySelect = document.getElementById('quick-task-category');

                    if (dateInput && data.due_date) dateInput.value = data.due_date;
                    if (timeInput && data.due_time) timeInput.value = data.due_time;
                    if (prioritySelect && data.priority) prioritySelect.value = data.priority;
                    if (categorySelect && data.category) categorySelect.value = data.category;
                })
                .catch(err => console.log('NL parse err:', err));
        }, 350);
    });

    if (quickForm) {
        quickForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const title = quickInput.value.trim();
            if (!title) return;

            const priority = document.getElementById('quick-task-priority')?.value || 'MEDIUM';
            const category = document.getElementById('quick-task-category')?.value || 'Work';
            const dueDate = document.getElementById('quick-task-date')?.value || '';
            const dueTime = document.getElementById('quick-task-time')?.value || '';

            const submitBtn = quickForm.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.disabled = true;

            fetch('/tasks/quick-create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    title: title,
                    priority: priority,
                    category: category,
                    due_date: dueDate,
                    due_time: dueTime
                })
            })
            .then(res => res.json())
            .then(data => {
                if (submitBtn) submitBtn.disabled = false;
                if (data.success) {
                    quickInput.value = '';
                    // Reload page or dynamically insert
                    window.location.reload();
                } else {
                    alert(data.error || 'Failed to add task.');
                }
            })
            .catch(err => {
                if (submitBtn) submitBtn.disabled = false;
                console.error(err);
            });
        });
    }
}

// 3. Single-Tap Task Checkbox Status Toggle (AJAX)
function initTaskToggles() {
    document.querySelectorAll('.task-checkbox-custom').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const taskId = e.target.getAttribute('data-task-id');
            const row = document.getElementById(`task-row-${taskId}`);
            const timeTrackEl = document.getElementById(`task-duration-${taskId}`);
            const statusBadge = document.getElementById(`task-status-badge-${taskId}`);

            fetch(`/tasks/${taskId}/toggle/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (row) {
                        if (data.is_completed) {
                            row.classList.add('is-completed');
                        } else {
                            row.classList.remove('is-completed');
                        }
                    }
                    if (timeTrackEl) {
                        timeTrackEl.textContent = data.time_tracking;
                    }
                    if (statusBadge) {
                        statusBadge.textContent = data.status_display;
                        statusBadge.className = `badge badge-status-${data.new_status.toLowerCase().replace('_', '')}`;
                    }

                    // Update live counter badges if present
                    if (data.counts) {
                        updateLiveBadgeCounts(data.counts);
                    }
                }
            })
            .catch(err => {
                console.error(err);
                // Revert checkbox state
                e.target.checked = !e.target.checked;
            });
        });
    });
}

function updateLiveBadgeCounts(counts) {
    const totalEl = document.getElementById('count-badge-total');
    const pendingEl = document.getElementById('count-badge-pending');
    const completedEl = document.getElementById('count-badge-completed');
    const overdueEl = document.getElementById('count-badge-overdue');

    if (totalEl) totalEl.textContent = counts.total;
    if (pendingEl) pendingEl.textContent = counts.pending;
    if (completedEl) completedEl.textContent = counts.completed;
    if (overdueEl) overdueEl.textContent = counts.overdue;
}

// 4. Health & Wellness Spotlight Actions (Hydration + Meds + Tips)
function initWellnessActions() {
    // Water Log (+1 Glass)
    const logWaterBtn = document.getElementById('btn-log-water');
    if (logWaterBtn) {
        logWaterBtn.addEventListener('click', () => {
            fetch('/health/water/log/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({ action: 'add' })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const countEl = document.getElementById('water-count-display');
                    const progressEl = document.getElementById('water-progress-bar');
                    if (countEl) countEl.textContent = `${data.water_count} / ${data.water_target} glasses`;
                    if (progressEl) {
                        progressEl.style.width = `${data.water_percent}%`;
                        progressEl.setAttribute('aria-valuenow', data.water_percent);
                    }
                    showToastNotification({
                        id: 'water-' + Date.now(),
                        title: 'Hydration Logged! 💧',
                        message: `You've drunk ${data.water_count} of ${data.water_target} glasses today. Keep it up!`,
                        stage: 'GENTLE'
                    });
                }
            })
            .catch(err => console.error(err));
        });
    }

    // Rotate Tip Button
    const nextTipBtn = document.getElementById('btn-next-tip');
    if (nextTipBtn) {
        nextTipBtn.addEventListener('click', () => {
            fetch('/health/tips/next/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.tip) {
                    const tipTitle = document.getElementById('wellness-tip-title');
                    const tipText = document.getElementById('wellness-tip-text');
                    const tipCat = document.getElementById('wellness-tip-category');
                    if (tipTitle) tipTitle.textContent = data.tip.title;
                    if (tipText) tipText.textContent = data.tip.tip_text;
                    if (tipCat) tipCat.textContent = data.tip.category;
                }
            })
            .catch(err => console.error(err));
        });
    }

    // Medicine Action Buttons (Taken / Skipped / Snooze)
    document.querySelectorAll('.btn-med-action').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const medId = btn.getAttribute('data-med-id');
            const timeStr = btn.getAttribute('data-time');
            const action = btn.getAttribute('data-action');

            fetch('/health/medicines/log-action/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    medicine_id: medId,
                    time: timeStr,
                    action: action
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const doseItem = document.getElementById(`med-dose-${medId}-${timeStr.replace(':', '')}`);
                    if (doseItem) {
                        if (action === 'TAKEN') {
                            doseItem.classList.add('bg-light', 'text-muted');
                            doseItem.innerHTML = `<span class="badge bg-success"><i class="bi bi-check-circle me-1"></i> Taken</span> <span class="ms-2 fw-medium">${data.message}</span>`;
                        } else if (action === 'SKIPPED') {
                            doseItem.innerHTML = `<span class="badge bg-secondary">Skipped</span>`;
                        } else {
                            doseItem.innerHTML = `<span class="badge bg-warning text-dark"><i class="bi bi-alarm me-1"></i> Snoozed 15m</span>`;
                        }
                    }
                    const adhText = document.getElementById('med-adherence-summary');
                    if (adhText && data.adherence_summary) {
                        adhText.textContent = data.adherence_summary;
                    }
                }
            })
            .catch(err => console.error(err));
        });
    });
}

// 5. Audio Alarm Synthesizer & Toast Notification Stream
function playAlarmChime(isUrgent = false, reminderType = 'TASK') {
    try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        const ctx = new AudioContext();
        const now = ctx.currentTime;

        if (reminderType === 'MEDICINE') {
            // Vital 3-Tone Health & Medication Alarm
            [587.33, 783.99, 1046.50].forEach((freq, idx) => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(freq, now + idx * 0.18);
                gain.gain.setValueAtTime(0.25, now + idx * 0.18);
                gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.18 + 0.35);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(now + idx * 0.18);
                osc.stop(now + idx * 0.18 + 0.35);
            });
        } else if (reminderType === 'HYDRATION') {
            // Refreshing 2-Tone Hydration Chime
            [523.25, 659.25].forEach((freq, idx) => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(freq, now + idx * 0.15);
                gain.gain.setValueAtTime(0.2, now + idx * 0.15);
                gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.15 + 0.3);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(now + idx * 0.15);
                osc.stop(now + idx * 0.15 + 0.3);
            });
        } else {
            // 5-Min Task Urgent Alarm
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = isUrgent ? 'sawtooth' : 'sine';
            osc.frequency.setValueAtTime(isUrgent ? 880 : 523.25, now);
            if (isUrgent) {
                osc.frequency.exponentialRampToValueAtTime(1174.66, now + 0.25);
            }
            gain.gain.setValueAtTime(0.22, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + (isUrgent ? 0.7 : 0.4));
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(now);
            osc.stop(now + (isUrgent ? 0.7 : 0.4));
        }
    } catch (e) {
        console.log('Audio chime not allowed yet by browser interaction policy.');
    }
}

function initReminderStream() {
    checkActiveReminders();
    setInterval(checkActiveReminders, 25000);
}

function checkActiveReminders() {
    fetch('/reminders/active/')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.notifications && data.notifications.length > 0) {
                data.notifications.forEach(n => {
                    showToastNotification(n);
                    if (n.is_alarm_urgent || n.reminder_type === 'MEDICINE') {
                        playAlarmChime(true, n.reminder_type);
                    }
                });
            }
        })
        .catch(err => console.log('Reminders poll err:', err));
}

function showToastNotification(notification) {
    const container = document.getElementById('toast-notification-container');
    if (!container) return;

    if (document.getElementById(`toast-item-${notification.id}`)) return;

    const isUrgent = notification.stage === 'URGENT' || notification.stage === 'OVERDUE' || notification.reminder_type === 'MEDICINE';
    const isMed = notification.reminder_type === 'MEDICINE';
    const isWater = notification.reminder_type === 'HYDRATION';

    const toastDiv = document.createElement('div');
    toastDiv.id = `toast-item-${notification.id}`;
    toastDiv.className = `toast show align-items-center shadow-lg mb-2 card-custom ${isMed ? 'border-start border-success border-5' : (isUrgent ? 'toast-alert-urgent' : 'toast-alert-gentle')}`;
    toastDiv.setAttribute('role', 'alert');
    toastDiv.setAttribute('aria-live', 'assertive');

    let actionButtonsHtml = '';
    if (isMed) {
        actionButtonsHtml = `
            <button class="btn btn-sm btn-outline-warning text-dark" onclick="snoozeToast(${notification.id}, 15)">
                <i class="bi bi-alarm me-1"></i> Snooze 15m
            </button>
            <button class="btn btn-sm btn-success fw-bold" onclick="dismissToast(${notification.id})">
                <i class="bi bi-check-circle-fill me-1"></i> Taken
            </button>
        `;
    } else if (isWater) {
        actionButtonsHtml = `
            <button class="btn btn-sm btn-outline-secondary" onclick="snoozeToast(${notification.id}, 30)">
                <i class="bi bi-clock me-1"></i> Remind in 30m
            </button>
            <button class="btn btn-sm btn-info text-white fw-bold" onclick="document.getElementById('btn-log-water')?.click(); dismissToast(${notification.id});">
                <i class="bi bi-droplet-fill me-1"></i> Drank +1 Glass
            </button>
        `;
    } else {
        actionButtonsHtml = `
            <button class="btn btn-sm btn-outline-secondary" onclick="snoozeToast(${notification.id}, 15)">
                <i class="bi bi-alarm me-1"></i> Snooze 15m
            </button>
            <button class="btn btn-sm ${isUrgent ? 'btn-danger' : 'btn-primary'} fw-bold" onclick="dismissToast(${notification.id})">
                <i class="bi bi-check2 me-1"></i> Acknowledge
            </button>
        `;
    }

    toastDiv.innerHTML = `
        <div class="toast-header bg-transparent border-0 pb-0">
            <i class="bi ${isMed ? 'bi-capsule-pill text-success fs-5' : (isWater ? 'bi-droplet-fill text-info fs-5' : (isUrgent ? 'bi-exclamation-octagon-fill text-danger fs-5' : 'bi-bell-fill text-primary fs-5'))} me-2"></i>
            <strong class="me-auto ${isMed ? 'text-success' : (isUrgent ? 'text-danger' : 'text-primary')}">${notification.title}</strong>
            <small class="text-muted">${notification.created_at || 'Just now'}</small>
            <button type="button" class="btn-close ms-2" onclick="dismissToast(${notification.id})"></button>
        </div>
        <div class="toast-body pt-1">
            <p class="mb-2 text-dark">${notification.message}</p>
            <div class="d-flex gap-2 mt-2">
                ${actionButtonsHtml}
            </div>
        </div>
    `;

    container.appendChild(toastDiv);
}

window.dismissToast = function(id) {
    const el = document.getElementById(`toast-item-${id}`);
    if (el) el.remove();
    if (typeof id === 'number') {
        fetch(`/reminders/${id}/dismiss/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken }
        }).catch(err => console.error(err));
    }
};

window.snoozeToast = function(id, minutes) {
    const el = document.getElementById(`toast-item-${id}`);
    if (el) el.remove();
    if (typeof id === 'number') {
        fetch(`/reminders/${id}/snooze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ minutes: minutes })
        }).catch(err => console.error(err));
    }
};

// 6. Conflict Checker when scheduling tasks
function initConflictChecker() {
    const dateInput = document.getElementById('task-date-input');
    const timeInput = document.getElementById('task-time-input');
    const bannerContainer = document.getElementById('calendar-conflict-banner');

    if (!dateInput || !bannerContainer) return;

    function checkConflict() {
        const d = dateInput.value;
        const t = timeInput ? timeInput.value : '';
        if (!d) return;

        fetch(`/calendar/check-conflict/?due_date=${encodeURIComponent(d)}&due_time=${encodeURIComponent(t)}`)
            .then(res => res.json())
            .then(data => {
                if (data.has_conflict) {
                    bannerContainer.innerHTML = `
                        <div class="conflict-banner">
                            <i class="bi bi-calendar-event text-warning fs-5"></i>
                            <div>
                                <strong>Calendar Notice:</strong> ${data.conflict_summary}
                                <span class="d-block text-muted small">You can still save this task anyway.</span>
                            </div>
                        </div>
                    `;
                    bannerContainer.style.display = 'block';
                } else {
                    bannerContainer.innerHTML = '';
                    bannerContainer.style.display = 'none';
                }
            })
            .catch(err => console.log('Conflict check err:', err));
    }

    dateInput.addEventListener('change', checkConflict);
    if (timeInput) timeInput.addEventListener('change', checkConflict);
}

// 7. Mobile Quick Task Bottom Sheet Modal Logic
function initMobileQuickTask() {
    const mobileForm = document.getElementById('mobile-quick-task-form');
    const mobileInput = document.getElementById('mobile-quick-task-title');
    if (!mobileForm || !mobileInput) return;

    let debounceTimer;
    mobileInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const val = e.target.value;
        if (val.length < 5) return;

        debounceTimer = setTimeout(() => {
            fetch(`/tasks/parse-nl/?text=${encodeURIComponent(val)}`)
                .then(res => res.json())
                .then(data => {
                    const dateInput = document.getElementById('mobile-quick-task-date');
                    const timeInput = document.getElementById('mobile-quick-task-time');
                    const prioritySelect = document.getElementById('mobile-quick-task-priority');
                    const categorySelect = document.getElementById('mobile-quick-task-category');

                    if (dateInput && data.due_date) dateInput.value = data.due_date;
                    if (timeInput && data.due_time) timeInput.value = data.due_time;
                    if (prioritySelect && data.priority) prioritySelect.value = data.priority;
                    if (categorySelect && data.category) categorySelect.value = data.category;
                })
                .catch(err => console.log('Mobile NL parse error:', err));
        }, 350);
    });

    mobileForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const title = mobileInput.value.trim();
        if (!title) return;

        const priority = document.getElementById('mobile-quick-task-priority')?.value || 'MEDIUM';
        const category = document.getElementById('mobile-quick-task-category')?.value || 'Work';
        const dueDate = document.getElementById('mobile-quick-task-date')?.value || '';
        const dueTime = document.getElementById('mobile-quick-task-time')?.value || '';

        const submitBtn = mobileForm.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;

        fetch('/tasks/quick-create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                title: title,
                priority: priority,
                category: category,
                due_date: dueDate,
                due_time: dueTime
            })
        })
        .then(res => res.json())
        .then(data => {
            if (submitBtn) submitBtn.disabled = false;
            if (data.success) {
                triggerHaptic([30, 40, 30]);
                mobileInput.value = '';
                // Close modal
                const modalEl = document.getElementById('mobileQuickAddModal');
                if (modalEl && window.bootstrap && window.bootstrap.Modal) {
                    const modal = window.bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                }
                window.location.reload();
            } else {
                alert(data.error || 'Failed to create task.');
            }
        })
        .catch(err => {
            if (submitBtn) submitBtn.disabled = false;
            console.error(err);
        });
    });
}

// 8. Progressive Web App (PWA) Registration & Install Experience
let deferredInstallPrompt = null;

function initPWA() {
    // Register Service Worker at root scope
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js', { scope: '/' })
                .then(reg => {
                    console.log('PWA ServiceWorker registered with root scope:', reg.scope);
                })
                .catch(err => {
                    console.log('PWA ServiceWorker registration notice:', err);
                });
        });
    }

    const banner = document.getElementById('pwa-install-banner');
    const installBtn = document.getElementById('pwa-install-btn');
    const dismissBtn = document.getElementById('pwa-dismiss-btn');

    // Check if already in standalone app mode
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    const isDismissed = localStorage.getItem('pwa_install_dismissed');

    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent Chrome 67 and earlier from automatically showing the prompt
        e.preventDefault();
        deferredInstallPrompt = e;

        if (!isStandalone && !isDismissed && banner) {
            banner.style.display = 'block';
        }
    });

    if (installBtn) {
        installBtn.addEventListener('click', () => {
            window.triggerPWAInstall();
        });
    }

    if (dismissBtn) {
        dismissBtn.addEventListener('click', () => {
            if (banner) banner.style.display = 'none';
            localStorage.setItem('pwa_install_dismissed', 'true');
        });
    }

    // iOS Detection
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    if (isIOS && !isStandalone && !isDismissed && banner) {
        // Show banner on iOS with link to iOS modal instructions
        banner.style.display = 'block';
    }
}

// Global Trigger for "Install Mobile App" (callable from navbar dropdown or button)
window.triggerPWAInstall = function() {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    const banner = document.getElementById('pwa-install-banner');

    if (deferredInstallPrompt) {
        deferredInstallPrompt.prompt();
        deferredInstallPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted PWA installation');
                if (banner) banner.style.display = 'none';
            }
            deferredInstallPrompt = null;
        });
    } else if (isIOS) {
        const iosModal = new bootstrap.Modal(document.getElementById('iosInstallModal'));
        iosModal.show();
    } else {
        // Already installed or unsupported browser instructions
        alert('To install the app, tap your browser menu (⋮ or Share) and select "Add to Home screen" or "Install App".');
    }
};

// 9. Connectivity Status Toast Listener
function initConnectivity() {
    const toast = document.getElementById('connectivity-toast');
    const icon = document.getElementById('connectivity-icon');
    const text = document.getElementById('connectivity-text');
    if (!toast || !icon || !text) return;

    function updateOnlineStatus() {
        if (navigator.onLine) {
            toast.className = 'connectivity-toast online';
            icon.className = 'bi bi-wifi';
            text.textContent = 'Back online! Syncing your data...';
            toast.style.display = 'block';
            setTimeout(() => {
                toast.style.display = 'none';
            }, 3000);
        } else {
            toast.className = 'connectivity-toast offline';
            icon.className = 'bi bi-wifi-off';
            text.textContent = 'You are currently offline. Showing cached view.';
            toast.style.display = 'block';
        }
    }

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
}

