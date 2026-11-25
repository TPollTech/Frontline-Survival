# Pilotos de assets — revisão 00-24, 00-25, 00-27

24/11/2026. Preservados os recursos e código do gameplay existentes. Revisão anterior d4e9a126 com [Windows 45511716282](https://github.com/TPollTech/Frontline-Survival/actions/runs/45511716282) e [Studio 45511716406](https://github.com/TPollTech/Frontline-Survival/actions/runs/45511716406) aprovada. A main também continha a3ac48ad (sincronização de capturas), preservada.

## Piloto canônico 1 — objeto industrial

Balizador de proteção de área industrial, conceito genérico autoral, sem alegação de réplica, marca ou referência fotográfica analisada. Fonte editável: tools/asset_pipeline/parametric/pilot_object.py. Base 0,22 × 0,045 × 0,22 m, altura total 0,835 m; corpo torneado com perfil não trivial e faixa elevada. Três malhas, biblioteca PBR existente (texturas base color, ORM e normal), normais, UV e tangentes autorais. Pivô da raiz no chão; base com offset local de 0,0225 m; orientação canônica Y-up, direção da raiz -Z (referência de transform, não prova de orientação de uma forma rotacionalmente simétrica). Três LODs com 48/24/12 segmentos e distâncias propostas 0/15/35 m, orçamento provisório da categoria object. Colisor de caixa de 0,22 × 0,835 × 0,22 m separado do visual, centro 0,4175 m.

```sh
python -m tools.asset_pipeline.parametric.pilot_object /tmp/frontline-pilot REVISION
```

Gera GLB/glTF de cada LOD, report com SHA-256 e contrato, executa Audit estrito sobre cada exportação, verifica orçamento de triângulos por nível e slots por instância. CI gera duas cópias e compara diretórios byte a byte. Stage separado injeta exatamente os GLBs no Studio de QA, sem publicar no Pages de produção. O script Godot carrega os mesmos GLBs no mapa real em sessão isolada, mede atributos, contagem, dimensões e identidade do colisor e captura a câmera do jogador. Chromium confere o mesmo SHA-256, contagens, dimensões, normais e UVs e salva três capturas. Não substitui nenhuma geometria de produção. Troca de LOD durante a captura é controlada pelo teste, não ligada a distância no gameplay.

## Matriz de cobertura

pilot_coverage.py gera evidência a partir do catálogo vivo reconciliado: categorias existentes, IDs, arquivos GLB/glTF, amostras reais e um candidato por categoria. Inclui também categorias previstas nos BUDGETS sem asset existente. As amostras e os candidatos legados não equivalem a pilotos de fonte canônica nem aprovação visual. Categorias não geométricas (áudio, textura, material, shader, câmera, física) exigem verificações próprias; não inventar uma malha substituta para representá-las. Somente object possui o novo piloto canônico nesta rodada.

## Evidências e limites

[CI 45514843046](https://github.com/TPollTech/Frontline-Survival/actions/runs/45514843046): geração e reprodução estrita das seis exportações aprovadas; etapas Godot/Studio ainda em execução ao registrar. O primeiro workflow 45514798558 não iniciou por uso do contexto runner.temp no env do job; corrigido no commit beb9316a com GITHUB_ENV. Capturas automatizadas não equivalem a inspeção visual efetiva. Não houve integração permanente do piloto, homologação de aparência, benchmark no hardware-alvo ou cobertura de pilotos de todas as categorias. 00-24, 00-25 e 00-27 permanecem parciais. 
