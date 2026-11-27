# 02-07 — Candidato IK analítico

Base `f062fed257e8769e5c376c2e08da4f3cb4c01d9c`, 26/11/2026. Consultados AGENTS.md, checklist, critérios, especificação, padrão artístico e relatório 02-06. O 02-06 permanece parcial, com novas extremidades arredondadas e inspeções anteriores em Godot; não promover 02-06 ou 02-08 por consequência.

## Fonte e escopo

`tools/asset_pipeline/parametric/rig.py` (blob 9d8137260abbaa29c41b6bef781f1658e1b23d6f) já define BoneSpec, SkeletonSpec, SkinSpec, RigSpec, hierarquias, matrizes de bind e deformação linear. Não foi alterado. O viewmodel real `scripts/player.gd` (16b9a1673d5bd2059acca254d2cd1d670753f8e4) ainda usa articulações Node3D e malhas locais; não confundir com skin anatômica. `scripts/fps_hand_mesh.gd` (1cc13d9224c8674afc8c7320dff95e13626eb9e7) consome as receitas orgânicas integradas.

Novo módulo candidato `tools/asset_pipeline/parametric/limb_ik.py`, blob cf13a4c7990e400a3054022b1e4dea704ddad2dd. Soluciona posições de cotovelo e punho em um mesmo referencial por geometria analítica de dois segmentos, preserva comprimentos, limita alcance por flexão e orienta o plano de flexão por polo. Alvo coincidente e polo degenerado exigem fallback explícito do chamador; o módulo não escolhe um lado arbitrário. Retorna erro residual, indicação de alcance limitado e direção da dobra. Não resolve rotações de ossos/twist, pesos, contatos, transições reais ou colisão. Limites iniciais de 0,02 a 2,5 rad são parâmetros provisórios, não calibração anatômica. Continuidade ao atravessar polo quase degenerado depende da integração e não foi homologada.

## Testes novos efetivamente executados

Em Python 3.13.5, diretório temporário com os dois arquivos novos, importação por namespaces, sem checkout completo. Comando `python -m unittest discover -s tests -v`: 7/7 OK, 0,010 s. Teste blob 301483c72992fa70f2d6d6f1a1412bef5e80c778. Cobertura: alvo alcançável; limites e alvos fora do alcance; espelhamento e polo; singularidades com/sem fallback; 101 amostras de uma trajetória sintética; 500 casos pseudoaleatórios com seed 207 e invariantes de comprimento/limite/erro; entradas inválidas. Os dois blobs publicados coincidem com os hashes Git locais testados. Não reexecutadas auditorias do 02-06.

Verificação matemática adicional usando coordenadas de ombro, cotovelo e punho anteriores ao ajuste compensatório de rotação do pulso, extraídas de player.gd, com deslocamento longitudinal comum removido e o cotovelo original como polo. Não são poses capturadas da engine; apoio genérico, não caso especial da escopeta.

| Caso | Comprimentos dos segmentos (unidades de jogo) | Erro no cotovelo | Erro no punho |
|---|---|---|---|
| Principal | 0,4168932717 / 0,3925557285 | 8,31e-16 | 5,55e-17 |
| Apoio genérico | 0,4805205511 / 0,4109671520 | 2,24e-16 | 6,36e-17 |

Ambos sem limitação de alcance. Isso demonstra reprodução da posição de referência idealizada, não validação de animação.

## Bloqueios e continuidade

Verificação local nesta sessão: Python disponível; command -v godot godot4 blender sem resultado; git ls-remote falhou por DNS para github.com; sem checkout completo. Nenhuma execução de Godot, Blender ou Asset Studio, nenhuma alteração de geometria, gameplay, animação, rig de produção ou outros IDs. Sem Actions ou instaladores. Para concluir, integrar o solucionador à hierarquia canônica em ambiente funcional, calibrar limites e twist por personagem/mão, validar pesos e deformações e inspecionar poses e transições de produção no Godot e Studio, preservando as interfaces e os resultados do 02-06. Estado parcial.
