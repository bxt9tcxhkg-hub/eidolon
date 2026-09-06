// Skills
async function loadSkills() {
    try {
        const d = await api('GET', '/skills');
        const el = document.getElementById('skills-summary');
        const listEl = document.getElementById('skills-list');
        const skills = d.skills || [];
        const notice = '<div class="empty" style="margin-bottom:10px;">' + escapeHtml(d.detail || 'Katalog hinterlegter Fähigkeiten — nicht als Runtime verdrahtet. Ein/Aus nur im Speicher, nicht persistent.') + '</div>';
        if (!skills.length) {
            if (el) el.innerHTML = notice + '<div class="empty">Keine Skills</div>';
            if (listEl) listEl.innerHTML = notice + '<div class="empty">Keine Skills</div>';
            return;
        }
        const rows = skills.map(s => {
            const executable = s.executable === true && s.runtime_wired === true;
            const label = executable ? (s.description || '') : ((s.description ? s.description + ' · ' : '') + 'Katalog · nicht verdrahtet');
            return '<div class="comp-row"><span class="comp-dot ' + (executable ? 'ok' : 'warn') + '"></span><span class="comp-name">' + escapeHtml(s.name) + '</span><span class="comp-detail">' + escapeHtml(label) + '</span></div>';
        }).join('');
        if (el) el.innerHTML = notice + rows;
        if (listEl) listEl.innerHTML = notice + rows;
    } catch (e) {
        const err = '<span class="tag err">' + e.message + '</span>';
        const el = document.getElementById('skills-summary');
        const listEl = document.getElementById('skills-list');
        if (el) el.innerHTML = err;
        if (listEl) listEl.innerHTML = err;
    }
}

// Backups
let armedBackupAction = null;

async function loadBackups() {
    try {
        const d = await api('GET', '/backups');
        const backups = d.backups || [];
        const statsEl = document.getElementById('backups-stats');
        if (statsEl) {
            statsEl.innerHTML = '<div class="comp-row"><span class="comp-name">Backups</span><span class="comp-detail">' + escapeHtml(String(d.count ?? backups.length ?? 0)) + ' / ' + escapeHtml(String(d.max_backups ?? d.max ?? '—')) + '</span></div>' +
                '<div class="comp-row"><span class="comp-name">Speicher</span><span class="comp-detail">' + escapeHtml(String(d.total_size_mb ?? 0)) + ' MB</span></div>';
        }
        const el = document.getElementById('backups-list');
        if (!backups.length) { el.innerHTML = '<div class="empty">Keine Backups</div>'; return; }
        el.innerHTML = backups.map(b => {
            const id = String(b.id || '');
            const restoreArmed = armedBackupAction === 'restore:' + id;
            const deleteArmed = armedBackupAction === 'delete:' + id;
            const sizeMb = b.size_bytes ? (Number(b.size_bytes) / 1024 / 1024).toFixed(1) + ' MB' : '-';
            return '<div class="comp-row"><span class="comp-dot ok"></span><span class="comp-name">' + escapeHtml(id) + '</span><span class="comp-detail">' + escapeHtml((b.reason || 'backup') + ' · ' + sizeMb) + '</span><button class="btn btn-sm" onclick="restoreBackupById(' + escapeHtml(JSON.stringify(id)) + ')">' + (restoreArmed ? 'Restore bestätigen' : 'Wiederherstellen') + '</button><button class="btn btn-sm" onclick="deleteBackupById(' + escapeHtml(JSON.stringify(id)) + ')">' + (deleteArmed ? 'Löschen bestätigen' : 'Löschen') + '</button></div>';
        }).join('');
    } catch (e) { const el = document.getElementById('backups-list'); if (el) el.innerHTML = '<span class="tag err">' + e.message + '</span>'; }
}
async function createBackup() {
    const label = 'manual-' + new Date().toISOString().replace(/[:.]/g, '-');
    try {
        var d = await api('POST', '/backups/create', { reason: label });
        if (d?.ok === false) { showNotice(d.error || 'Backup fehlgeschlagen', 'error'); return; }
        showNotice('Backup: ' + (d.id || label), 'success');
        loadBackups();
    } catch (e) { showNotice(e.message, 'error'); }
}
function armBackupAction(action, id) {
    armedBackupAction = action + ':' + id;
    loadBackups();
    setTimeout(() => { if (armedBackupAction === action + ':' + id) { armedBackupAction = null; loadBackups(); } }, 3000);
}
async function restoreBackupById(id) {
    if (armedBackupAction !== 'restore:' + id) { armBackupAction('restore', id); showNotice('Wiederherstellen ist scharf gestellt', 'warning', 3000); return; }
    armedBackupAction = null;
    try {
        const d = await api('POST', '/backups/' + encodeURIComponent(id) + '/restore', {});
        if (d?.ok === false) { showNotice(d.error || 'Wiederherstellen fehlgeschlagen', 'error'); return; }
        showNotice('Wiederhergestellt: ' + id, 'success');
        loadBackups();
    } catch (e) { showNotice(e.message, 'error'); }
}
async function deleteBackupById(id) {
    if (armedBackupAction !== 'delete:' + id) { armBackupAction('delete', id); showNotice('Löschen ist scharf gestellt', 'warning', 3000); return; }
    armedBackupAction = null;
    try {
        const d = await api('DELETE', '/backups/' + encodeURIComponent(id));
        if (d?.ok === false) { showNotice(d.error || 'Löschen fehlgeschlagen', 'error'); return; }
        showNotice('Backup gelöscht: ' + id, 'success');
        loadBackups();
    } catch (e) { showNotice(e.message, 'error'); }
}
