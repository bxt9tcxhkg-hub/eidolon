async function loadIdentity() {
    try {
        const d = await api('GET', '/identity');
        const el = document.getElementById('identity-text');
        if (!el) return;
        const activeRoles = Array.isArray(d.active_roles) ? d.active_roles : [];
        const definedRoles = Array.isArray(d.defined_roles) ? d.defined_roles : [];
        let html = '<div style="margin-bottom:12px;font-size:0.92rem;line-height:1.5;color:var(--text);">' + escapeHtml(d.identity || '-') + '</div>';
        html += '<div class="comp-row"><span class="comp-name">Name</span><span class="comp-detail">' + escapeHtml(d.name || '-') + '</span></div>';
        html += '<div class="comp-row"><span class="comp-name">Rolle</span><span class="comp-detail">' + escapeHtml(d.product_role || '-') + '</span></div>';
        html += '<div class="comp-row"><span class="comp-name">Modell</span><span class="comp-detail">' + escapeHtml(d.model || '-') + '</span></div>';
        html += '<div class="comp-row"><span class="comp-name">Provider</span><span class="comp-detail">' + escapeHtml(d.provider || '-') + '</span></div>';
        html += '<div class="comp-row"><span class="comp-name">Direktes Gegenüber</span><span class="comp-detail">' + escapeHtml(d.direct_counterpart_role || '-') + '</span></div>';
        html += '<div class="comp-row"><span class="comp-name">Aktive Rollen</span><span class="comp-detail">' + escapeHtml(String(d.active_role_count ?? 0)) + '</span></div>';
        html += '<div class="comp-row"><span class="comp-name">Definierte Vorlagenrollen</span><span class="comp-detail">' + escapeHtml(String(d.defined_role_count ?? 0)) + '</span></div>';
        html += '<div class="comp-row"><span class="comp-name">Rollentypen</span><span class="comp-detail">' + escapeHtml(Array.isArray(d.role_kinds) && d.role_kinds.length ? d.role_kinds.join(', ') : '—') + '</span></div>';
        html += '<div style="margin-top:16px;font-size:0.78rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:0.08em;">Aktiv wirksame Rollen</div>';
        html += activeRoles.length
            ? activeRoles.map(role => '<div class="comp-row"><span class="comp-name">' + escapeHtml(role.name || role.role_id || 'Rolle') + '</span><span class="comp-detail">' + escapeHtml((role.visibility || '—') + ' · ' + (role.requires_user_approval ? 'mit Freigabe' : 'ohne Freigabe')) + '</span></div><div style="margin:-4px 0 8px 0;color:var(--text-dim);font-size:0.78rem;line-height:1.4;">' + escapeHtml(role.description_for_user || '') + '</div>').join('')
            : '<div class="empty">Keine aktiv wirksamen Rollen</div>';
        html += '<div style="margin-top:16px;font-size:0.78rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:0.08em;">Definierte Vorlagen</div>';
        html += definedRoles.length
            ? definedRoles.map(role => '<div class="comp-row"><span class="comp-name">' + escapeHtml(role.name || role.role_id || 'Vorlage') + '</span><span class="comp-detail">' + escapeHtml((role.role_kind || '—') + ' · ' + (role.instantiation_policy || '—')) + '</span></div><div style="margin:-4px 0 8px 0;color:var(--text-dim);font-size:0.78rem;line-height:1.4;">' + escapeHtml(role.description_for_user || '') + '</div>').join('')
            : '<div class="empty">Keine definierten Vorlagen</div>';
        el.innerHTML = html;
    } catch (e) { const el = document.getElementById('identity-text'); if (el) el.innerHTML = '<span class="tag err">' + e.message + '</span>'; }
}
