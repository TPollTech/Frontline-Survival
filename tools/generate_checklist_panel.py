"""Generate the interactive 131-ID master checklist from the canonical docs.

Reads the acceptance matrix and the master checklist, keeps their ID order and
wording, and writes a self-contained HTML panel (no CDN, no server needed).
Run from the repository root: python tools/generate_checklist_panel.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRITERIA = ROOT / 'docs/CRITERIOS_ACEITE_1_0.md'
CHECKLIST = ROOT / 'docs/CHECKLIST_MESTRE.md'
OUTPUT = ROOT / 'docs/CHECKLIST_INTERATIVO_131.html'


def parse():
    criteria = CRITERIA.read_text(encoding='utf-8')
    checklist = CHECKLIST.read_text(encoding='utf-8')
    stages = {m.group(1): m.group(2).strip()
              for m in re.finditer(r'^## (\d\d) — (.+)$', criteria, re.M)}
    rows = []
    for line in criteria.splitlines():
        m = re.match(r'^\| (\d\d-\d\d) \| (.+?) \| (.+?) \|$', line.strip())
        if m:
            rows.append({'id': m.group(1), 'title': m.group(2).strip(),
                         'criteria': m.group(3).strip()})
    marks = []
    for line in checklist.splitlines():
        m = re.match(r'^- \[( |x)\] (.+?)$', line.strip())
        if m:
            marks.append((m.group(1) == 'x', m.group(2).strip()))
    if not (len(rows) == len(marks) == 131):
        raise SystemExit(f'expected 131 IDs, got {len(rows)} criteria and {len(marks)} lines')
    items = []
    for row, (done, text) in zip(rows, marks):
        _, _, evidence = text.partition(' — ')
        items.append({**row, 'done': done, 'evidence': evidence.strip()})
    return items, stages


def rich(text):
    """Escape text but keep the documentation's links and inline code usable."""
    escaped = html.escape(text)
    escaped = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                     lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noreferrer">{m.group(1)}</a>',
                     escaped)
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', escaped)


def render(items, stages):
    done = sum(item['done'] for item in items)
    first_pending = next((item['id'] for item in items if not item['done']), '—')
    stage_counts = {}
    for item in items:
        counts = stage_counts.setdefault(item['id'][:2], {'done': 0, 'total': 0})
        counts['total'] += 1
        counts['done'] += int(item['done'])

    cards = []
    for item in items:
        state = 'done' if item['done'] else 'pending'
        badge = 'Concluído' if item['done'] else 'Pendente/parcial'
        evidence = (f'<p class="evidence">{rich(item["evidence"])}</p>'
                    if item['evidence'] else '')
        search = html.escape((item['id'] + ' ' + item['title'] + ' ' +
                              item['criteria'] + ' ' + item['evidence']).lower(),
                             quote=True)
        cards.append(f'''<article class="card {state}" data-id="{item['id']}" data-stage="{item['id'][:2]}" data-state="{state}" data-search="{search}">
  <header><span class="id">{item['id']}</span><span class="badge {state}">{badge}</span><h3>{html.escape(item['title'])}</h3></header>
  <p class="crit"><strong>Aceite:</strong> {rich(item['criteria'])}</p>
  {evidence}
  <button class="copy" data-id="{item['id']}">Copiar comando deste ID</button>
</article>''')

    stage_chips = ' '.join(
        f'<button class="chip stage" data-stage="{stage}">{stage} · {counts["done"]}/{counts["total"]}</button>'
        for stage, counts in sorted(stage_counts.items()))
    payload = json.dumps({'items': items, 'stages': stages}, ensure_ascii=False)

    return f'''<!doctype html>
<html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Frontline Survival — checklist mestre interativo (131 IDs)</title>
<style>
 :root{{--bg:#0f1215;--panel:#161b20;--line:#2a323a;--text:#e6edf3;--muted:#93a1ad;--ok:#2ea043;--todo:#c9a227;--accent:#58a6ff}}
 *{{box-sizing:border-box}}
 body{{margin:0;background:var(--bg);color:var(--text);font:14px/1.45 system-ui,Segoe UI,sans-serif}}
 header.top{{padding:18px 22px;border-bottom:1px solid var(--line);background:linear-gradient(180deg,#161b20,#101418)}}
 h1{{font-size:19px;margin:0 0 6px}} .sub{{color:var(--muted);font-size:12px;margin:0}}
 .progress{{margin-top:12px;height:10px;background:#222a31;border-radius:999px;overflow:hidden;max-width:620px}}
 .progress i{{display:block;height:100%;background:linear-gradient(90deg,#2ea043,#58a6ff);width:{done / len(items) * 100:.1f}%}}
 .stats{{margin-top:8px;display:flex;gap:18px;flex-wrap:wrap;font-size:12px;color:var(--muted)}}
 .stats b{{color:var(--text)}}
 .toolbar{{position:sticky;top:0;z-index:5;display:flex;gap:10px;flex-wrap:wrap;align-items:center;padding:12px 22px;background:#101418e6;backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}}
 input[type=search]{{flex:1;min-width:220px;background:#0b0f13;border:1px solid var(--line);color:var(--text);border-radius:6px;padding:8px 10px}}
 .chip,.copy{{background:#1c242c;border:1px solid var(--line);color:var(--text);border-radius:999px;padding:5px 11px;font-size:12px;cursor:pointer}}
 .chip[aria-pressed=true]{{border-color:var(--accent);color:var(--accent)}}
 .copy{{border-radius:6px;margin-top:8px}} .copy:hover{{border-color:var(--accent)}}
 main{{padding:16px 22px 60px;display:grid;gap:10px}}
 .next{{border:1px solid #3a4a2c;background:#16211a;border-radius:8px;padding:10px 14px;font-size:13px}}
 .next b{{color:#7ee787}}
 .card{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px 14px}}
 .card.done{{border-left:4px solid var(--ok)}}
 .card.pending{{border-left:4px solid var(--todo)}}
 .card header{{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}}
 .card h3{{font-size:14px;margin:0;font-weight:600}}
 .id{{font:600 12px ui-monospace,monospace;color:var(--accent)}}
 .badge{{font-size:11px;border-radius:999px;padding:2px 8px;border:1px solid var(--line)}}
 .badge.done{{color:#7ee787;border-color:#2f6f3a}} .badge.pending{{color:#e3c45b;border-color:#6b5a1d}}
 .crit{{margin:8px 0 4px;color:#c7d1da;font-size:13px}}
 .evidence{{margin:4px 0 0;color:var(--muted);font-size:12.5px;border-left:2px solid #2a323a;padding-left:10px}}
 .stage-filter{{display:flex;gap:6px;flex-wrap:wrap;width:100%}}
 a{{color:#79c0ff}} a:hover{{text-decoration:none}} code{{font:12px ui-monospace,monospace;background:#0b0f13;padding:0 3px;border-radius:3px}}
 .hidden{{display:none!important}}
 footer{{color:var(--muted);font-size:12px;padding:0 22px 30px}}
 @media(max-width:640px){{.toolbar{{padding:10px 14px}} main{{padding:12px 14px 40px}}}}
</style>
<header class="top">
 <h1>Frontline Survival — Checklist mestre interativo</h1>
 <p class="sub">131 IDs · padrão híbrido aplicado às oito armas (02-01/02-02) · atualizado 26/11/2026</p>
 <div class="progress" aria-label="progresso"><i></i></div>
 <div class="stats"><span><b>{done}</b> concluídos</span><span><b>{len(items) - done}</b> pendentes/parciais</span><span><b>{done / len(items) * 100:.1f}%</b> oficial</span><span>Próxima recomendada: <b>{first_pending}</b></span></div>
</header>
<div class="toolbar">
 <input id="q" type="search" placeholder="Pesquisar ID, título, critério ou evidência  ( / )" aria-label="Pesquisar">
 <button class="chip" data-state="pending" aria-pressed="false">Pendentes</button>
 <button class="chip" data-state="done" aria-pressed="false">Concluídos</button>
 <button class="chip" data-state="all" aria-pressed="true">Todos</button>
 <div class="stage-filter">{stage_chips}</div>
</div>
<main id="list">
 <div class="next">Próxima tarefa recomendada: <b>{first_pending}</b> — uma execução por vez, preservando estado anterior, evidências e dependências. Use “Copiar comando deste ID” para gerar o comando.</div>
 {''.join(cards)}
</main>
<footer>Estados oficiais: docs/CHECKLIST_MESTRE.md. Critérios: docs/CRITERIOS_ACEITE_1_0.md. Evidência 02-01: docs/VALIDACAO_02_01_PADRAO_HIBRIDO.md.</footer>
<script>
const DATA={payload};
let stateFilter='all', stageFilter='';
function apply(){{
  const q=document.getElementById('q').value.trim().toLowerCase();
  let visible=0;
  document.querySelectorAll('.card').forEach(card=>{{
    const show=(stateFilter==='all'||card.dataset.state===stateFilter)
      &&(!stageFilter||card.dataset.stage===stageFilter)
      &&(!q||card.dataset.search.includes(q));
    card.classList.toggle('hidden',!show);
    if(show)visible++;
  }});
  document.querySelector('.next').textContent=visible+' de '+DATA.items.length+' IDs exibidos.';
}}
document.querySelectorAll('.chip[data-state]').forEach(b=>b.addEventListener('click',()=>{{
  stateFilter=b.dataset.state;
  document.querySelectorAll('.chip[data-state]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
  apply();
}}));
document.querySelectorAll('.chip.stage').forEach(b=>b.addEventListener('click',()=>{{
  stageFilter=stageFilter===b.dataset.stage?'':b.dataset.stage;
  document.querySelectorAll('.chip.stage').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.stage===stageFilter)));
  apply();
}}));
document.getElementById('q').addEventListener('input',apply);
document.addEventListener('keydown',e=>{{if(e.key==='/'&&document.activeElement!==document.getElementById('q')){{e.preventDefault();document.getElementById('q').focus();}}}});
document.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',async()=>{{
  const item=DATA.items.find(i=>i.id===b.dataset.id);
  const stage=DATA.stages[item.id.slice(0,2)];
  const cmd='Execute exclusivamente '+item.id+' · '+item.title+' (etapa '+stage+'). Estado atual: '+(item.done?'concluído':'pendente/parcial')+'. Critério de aceite: '+item.criteria+' Evidência registrada: '+(item.evidence||'nenhuma')+'. Consulte AGENTS.md, checklist, critérios e padrão artístico; preserve auditorias anteriores e dependências; atualize somente este ID com evidências reais e reenvie o checklist interativo completo de 131 IDs.';
  try{{await navigator.clipboard.writeText(cmd);b.textContent='Copiado ✓';setTimeout(()=>b.textContent='Copiar comando deste ID',1400);}}
  catch(e){{b.textContent='Selecione e copie manualmente';}}
}}));
</script>
</html>'''


def main():
    items, stages = parse()
    OUTPUT.write_text(render(items, stages), encoding='utf-8')
    done = sum(item['done'] for item in items)
    print(f'CHECKLIST_PANEL_WRITTEN {OUTPUT.name} ids={len(items)} done={done} pending={len(items) - done}')


if __name__ == '__main__':
    main()
