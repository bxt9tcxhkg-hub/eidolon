from __future__ import annotations

from eidolon.chat_runtime_patterns import lower_text, normalize_text


def candidate_directions(runtime_context: dict) -> list[dict[str, str]]:
    workflow_state = runtime_context.get('workflow_state') or {}
    project_context = runtime_context.get('project_context') or {}
    workspace_context = runtime_context.get('workspace_context') or {}
    active_workspace = workspace_context.get('active_workspace') or {}
    candidate_workspace = workspace_context.get('candidate_workspace') or {}
    suggestions = list(workspace_context.get('visible_suggestions') or [])
    directions: list[dict[str, str]] = []
    for blocker in list(workflow_state.get('blockers') or [])[:2]:
        label = normalize_text(blocker.get('label')); reason = normalize_text(blocker.get('reason'))
        if label:
            directions.append({'title': f'Blocker lösen: {label}', 'why': reason or 'Der aktive Kontext ist blockiert und braucht Entstörung.', 'next_step': f"Ich zerlege den Blocker '{label}' in Ursache, Hebel und ersten Reparaturschritt."})
    for action in list(active_workspace.get('next_actions') or [])[:2]:
        text = normalize_text(action)
        if text:
            directions.append({'title': text, 'why': 'Der aktive Workspace hat bereits einen sichtbaren nächsten Schritt.', 'next_step': f"Ich konkretisiere '{text}' in einen belastbaren Arbeitszug mit Ziel und Prüfkriterium."})
    candidate_title = normalize_text(candidate_workspace.get('topic_label'))
    if candidate_title:
        directions.append({'title': f'Projektkandidat schärfen: {candidate_title}', 'why': 'Es gibt einen Kandidaten, aber noch keinen klaren operativen Projektvertrag.', 'next_step': f'Ich forme {candidate_title} in Ziel, Scope, Risiken und nächsten Übergang.'})
    for label in list(project_context.get('topic_labels') or [])[:2]:
        text = normalize_text(label)
        if text:
            directions.append({'title': f'Gesprächsthema strukturieren: {text}', 'why': 'Es gibt wiederkehrende Live-Signale, die noch nicht in einen belastbaren Arbeitsrahmen überführt sind.', 'next_step': f'Ich leite aus {text} Ziel, Spannungen und 2-3 plausible Arbeitsrichtungen ab.'})
    for item in suggestions[:2]:
        label = normalize_text(item.get('topic_label')); message = normalize_text(item.get('message'))
        if label:
            directions.append({'title': f'Proaktive Richtung aufnehmen: {label}', 'why': message or 'Die Runtime sieht hier handlungsnahen Kontext.', 'next_step': f'Ich verdichte {label} auf den sinnvollsten direkten Einstieg.'})
    deduped=[]; seen=set()
    for item in directions:
        key = lower_text(item.get('title'))
        if not key or key in seen:
            continue
        seen.add(key); deduped.append(item)
    return deduped[:4]


def build_non_work_fallback_reply(runtime_context: dict) -> str:
    message = normalize_text((runtime_context.get('user_intent') or {}).get('latest_message'))
    lowered = lower_text(message)
    if any(token in lowered for token in ('wer bist du', 'stell dich vor', 'erzähl mir von dir', 'erzaehl mir von dir')):
        return 'Ich bin Eidolon, das zentrale agentische Hauptsystem dieses Produkts. Aber wir können auch ganz normal sprechen — nicht jede Unterhaltung muss sofort in Arbeit übersetzt werden.'
    if 'kennenlern' in lowered:
        return 'Gern. Ich bin Eidolon, und du kannst mich auch einfach normal kennenlernen: Wir können locker reden, Interessen abklopfen oder über irgendetwas sprechen, ohne daraus sofort etwas Operatives zu machen.'
    if any(token in lowered for token in ('wie geht', 'how are you')):
        return 'Gut und ansprechbar. Wenn du einfach normal reden willst, ist das völlig okay — es muss nicht sofort um Arbeit gehen.'
    return 'Wir können hier auch ganz normal sprechen. Wenn du plaudern, etwas diskutieren oder mich einfach kennenlernen willst, antworte ich darauf ohne es künstlich in Projektarbeit umzudeuten.'


def _work_focus(runtime_context: dict) -> str:
    project_context = runtime_context.get('project_context') or {}
    focus = project_context.get('active_project_title') or project_context.get('candidate_project_title') or (project_context.get('topic_labels') or [None])[0]
    return normalize_text(focus)


def build_grounded_fallback_reply(runtime_context: dict) -> str:
    intent = runtime_context.get('user_intent') or {}
    if intent.get('classification') in {'casual_chat', 'general_chat', 'general_chat_with_work_context'}:
        return build_non_work_fallback_reply(runtime_context)
    workflow_state = runtime_context.get('workflow_state') or {}
    directions = candidate_directions(runtime_context)
    current_state = workflow_state.get('current_context_state') or 'no_live_context'
    focus = _work_focus(runtime_context)
    focus_bit = f' {focus}' if focus else ''
    if intent.get('classification') == 'repair_or_unblock' and directions:
        lead = f'Zuerst den Engpass{focus_bit}.'
    elif current_state == 'active_project':
        lead = f'Wir sind im Projekt{focus_bit}.' if focus else 'Wir sind in einem aktiven Projekt.'
    elif current_state == 'project_candidate':
        lead = f'Kandidat{focus_bit} ist noch kein Vertrag.'
    elif current_state == 'chat_topic':
        lead = f'Thema{focus_bit} ist da, aber noch kein Projekt.'
    else:
        lead = 'Noch kein belastbarer Projektkontext — ich erfinde nichts.'
    if not directions:
        return f'{lead}\nSag ein Ziel oder einen Blocker, dann lege ich es als Karte an.'
    item = directions[0]
    title = normalize_text(item.get('title')) or 'nächster Zug'
    return f'{lead}\nNächster Zug: {title}.\nLege ich als Karte an — oder willst du etwas anderes zuerst?'
