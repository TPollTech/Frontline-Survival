# Auditoria integrada e portões de homologação — 00-34

25/11/2026. Base 338f34e0af67b358771470d8fb1c9de672452584, conferida na main. Escopo exclusivamente 00-34. Referência [GUIA_PIPELINE_3D.md](GUIA_PIPELINE_3D.md), [ASSET_STUDIO_SPEC.md](ASSET_STUDIO_SPEC.md) e AGENTS.md. Sem Actions, sem promoção de outros IDs. **Parcial: auditoria estática e regressões isoladas realizadas; homologação integral não demonstrada.**

## Reconciliação estática desta revisão

As consultas ao GitHub leram os 14 scripts/shader distintos das 24 famílias godot_recipe do manifesto histórico. Todas as fontes existem, todos os nomes de funções declarados foram encontrados por expressão regular de declaração GDScript, e os 24 IDs são mencionados em inventory_qa.gd. Isso verifica referência textual, não importação, semântica ou cobertura de instâncias.

- Baseline: 50 IDs, 60 recursos, 49 vínculos de output (inclui recursos não geométricos; não significa 49 modelos), zero IDs duplicados, nenhuma referência interna a assets/resources/sources fora do manifesto, 50/50 validation.approved=false. Não foi verificado o conteúdo binário de todos os recursos atuais; não confundir baseline com catálogo vivo gerado.
- Famílias e fontes conferidas:

| Família | Fonte |
|---|---|
| ally:legacy | scripts/ally.gd |
| camera:briefing | scripts/main.gd |
| character:quaternius_equipment | scripts/quaternius_soldier_visual.gd |
| effect:blood | scripts/blood_impact.gd |
| effect:combat | scripts/main.gd |
| effect:enemy_tracer | scripts/enemy.gd |
| effect:grenade | scripts/frag_grenade.gd |
| effect:muzzle | scripts/player.gd |
| effect:scope_overlay | scripts/scope.gdshader |
| enemy:legacy | scripts/enemy.gd |
| environment:lighting | scripts/main.gd |
| geometry:model_surface | scripts/model_surface.gd |
| map:campo_de_testes | scripts/main.gd |
| material:weapon_overrides | scripts/weapon_materials.gd |
| object:grenade | scripts/frag_grenade.gd |
| object:loot | scripts/loot_pickup.gd |
| object:turret | scripts/turret.gd |
| player:collision | scripts/player.gd |
| query:enemy_tactics | scripts/enemy_tactics.gd |
| query:spawn | scripts/spawn_selector.gd |
| query:turret | scripts/main.gd |
| viewmodel:assembly | scripts/player.gd |
| viewmodel:attachments | scripts/player.gd |
| viewmodel:hands | scripts/player.gd |

## Matriz de homologação

| Área | Evidência histórica e situação atual | Próximo portão |
|---|---|---|
| 00-28 arsenal | 8 armas/31 GLBs/7 acessórios indexados; coletor e receitas legadas, não reprodução comprovada. | Rebuild isolado duas vezes, hashes e inspeção FPS repouso/ADS/recarga/acessórios. |
| 00-29 personagens | 5 receitas compartilhadas e 4 consumidores, vínculo de catálogo implementado; fonte editável do humanoide importado ainda não confirmada. | Importação, buffers/transforms/rig/poses e revisão visual. |
| 00-30 objetos | 6 receitas e 5 famílias vinculadas; utility_cart QA-only. | QA de geometria, cena real, paridade e cobertura adicional. |
| 00-31 mapa | Receita Campo de Testes, composição original; QA específico preparado. | Teste real de layout, navegação, iluminação e reconstrução. |
| 00-32 runtime | 13 papéis em 10 famílias, captura e vínculo de escopo implementados. | Novo inventário real, escopos, ciclo de vida/limpeza, browser e inspeção. |
| 00-10 física/LOD | 207/207 transições, 24/24 varreduras, 15 comparações fixas e 960 intervalos llvmpipe em revisões anteriores; 23 assemblies/5 famílias. | Cobertura restante, captura --motion e inspeção, WebGL e iGPU alvo. |
| Catálogo/Studio | Histórico de 86 amostras/24 famílias, 225 buffers preparados em b6f1d43; Chromium encerrou aba ao carregar módulos nessa tentativa. | Captura e catálogo da mesma revisão, hashes, reconstrução e browser real. |
| Paridade visual | Histórico de reconstrução e comparação de projeção de câmera, não prova igualdade de render; triplanar aproximado, skinning em repouso, diferenças de shader/sombras/céu e TPS nativo não implementado. | Correções de fidelidade, comparação visual real e aprovação por asset/estado. |
| Hardware | Benchmark anterior por software, não Ryzen 5 7530U/iGPU/8 GB. | Medição no hardware-alvo e regressão de partida. |

## Lacuna corrigida no gate browser

A regressão existente conferia hashes dos payloads e cobertura de composições, mas não exigia os escopos exatos da 00-32, e o bloco de reconstrução era opcional caso faltasse surface_payload. Em REQUIRE_RUNTIME_VIEWS=1, browser_test.mjs agora exige o payload portável e as 10 famílias de escopos; compara cada registro de escopo do catálogo com raízes/nós da amostra original, verifica amostras, IDs, papéis, não duplicidade por par amostra/papel, total reconciliado, aprovação falsa; abre um exemplo de cada um dos 13 papéis na interface, checa rótulos, raízes, contagens, colisões e visibilidade quando aplicável. Preserva os gates anteriores. Marker STUDIO_RUNTIME_SCOPES_PASS apenas após as verificações executadas. Não é nova geometria ou homologação visual. A UI continua mostrando a amostra integral e seus metadados, não isolamento visual.

## Testes efetivamente executados

- Python 3.13.5: 9/9 test_runtime_asset_scopes.py e 10/10 test_world_lod_motion.py passaram nesta sessão, em cópias isoladas; quatro blobs conferidos por git hash-object com a revisão remota antes da execução. Fixtures sintéticas, não prova de engine/WebGL. Não repetidos os 207 testes históricos.
- Conferência estática real do manifesto, das fontes das 24 famílias e das declarações de função/IDs, como acima. Verificada correspondência dos 13 papéis da nova regressão com SPECS, 13 chamadas no inventário e textos da interface; não executado Playwright.
- Godot e Blender não encontrados no PATH. Node 22, Python, Chromium e Xvfb disponíveis, mas clone Git falhou por DNS; sem checkout integral, dependências do Studio ou captura nova. Não há nova inspeção, benchmark ou pacote Windows. Não atribuir a falha histórica do Chromium a esta revisão: execução WebGL atual não realizada.

## Continuidade

Executar o roteiro integrado do guia num checkout limpo com perfil isolado, capturar inventário/vistas da mesma revisão e gerar catálogo/Studio. Conferir 24 famílias por amostra/consulta, dependências e recursos atuais, escopos e hashes, casos de cobertura e exceções; executar browser_test.mjs com REQUIRE_RUNTIME_VIEWS=1, guardar logs e capturas reais, abrir/inspecionar Godot e Studio; tratar falhas e repetir. Registrar diferenças visuais e benchmarks reais, inclusive movimento e hardware-alvo. Não usar os dados históricos como aprovação automática. A auditoria não encerra as lacunas de implementação de outras tarefas. 00-34 permanece parcial.

## Coleta unificada Windows

Preparado [QA All-in-One](QA_ALL_IN_ONE.md) para executar os runners existentes sem comandos manuais no Godot. Somente inicializador, dependente de internet; não há bundle offline ou homologação nesta entrega. Aguardar resultados reais e solucionar todas as lacunas da etapa 00 antes de avançar.

## Evidência Windows recebida — 95c7ac8

Ver [QA_RETESTE_WINDOWS.md](QA_RETESTE_WINDOWS.md): 26/47 passos, 7 falhas, 14 bloqueados; inventário, vistas, LOD, objetos/mapa e importação reais aprovados nos gates executados. Catálogo e WebGL ainda bloqueados. Corrigidos caminhos canônicos, preservação dos bytes e preparado reteste incremental; warnings de normais/tangentes e teste de limpeza permanecem abertos. Nenhum ID promovido.

## Delimitação de aceite revisada (25/11/2026)

A [matriz por ID](CRITERIOS_ACEITE_1_0.md) distingue auditoria da fundação (00-34) de homologação artística de todos os modelos e benchmark de release (02/10-08). Manter cobertura do inventário real, pilotos por categoria, WebGL real, comparação técnica/visual representativa e Godot renderizado na integração. As evidências históricas acima não mudam; falhas impeditivas seguem abertas, débitos não impeditivos têm ID responsável e evidência. Nenhum instalador é gate. Executar apenas testes afetados e integração necessária; não promover ID nesta revisão documental.


## Auditoria do portão 00-34 — revisão 9784e4e8f1a5c678080fc2a0ce82a7ae825b7663 (25/11/2026)

Escopo exclusivo 00-34. Comparação remota confirma que a revisão do reteste integrado `7a1d0f05a6c313826ad718b58ddd51f91e154ab6` é ancestral da main consultada e o diff contém apenas docs/CHECKLIST_MESTRE.md e docs/PILOTOS_ASSETS.md. O código, assets, configuração e testes não mudaram nesse intervalo. Portanto os resultados registrados para aquele reteste permanecem pertinentes ao mesmo escopo técnico, não são novas execuções. Consultados AGENTS.md, matriz normativa, checklist, especificação, ASSET_STUDIO.md, PILOTOS_ASSETS.md, LOD_COLISOES_RUNTIME.md, MAPAS_FONTES_CANONICAS.md, RUNTIME_FONTES_CANONICAS.md e QA_RETESTE_WINDOWS.md. As 131 linhas do checklist correspondem em ordem aos 131 IDs da matriz.

### Evidência consolidada (resultados anteriores, não repetidos)

- Godot 4.4.1 Compatibility e Firefox 135/WebGL por software: catálogo com 52 registros e 100 recursos, SHA-256 conferidos, 32 GLBs, 86 árvores reconciliadas e seis composições renderizadas; seis vistas nativas na revisão posterior; diferenças de céu, sombras e shaders documentadas. O erro máximo dos 12 landmarks da câmera de mapa foi 0,0000379106108994165 px. O ensaio focado omitiu o bloco fullscreen que expirou no Xorg virtual; não declarar esse bloco aprovado nessa rodada. Evidências em ASSET_STUDIO.md.
- 13/13 categorias geométricas de pilotos: 39 GLBs e 39 glTFs, duas gerações equivalentes, 39 importações/renderizações Godot e conciliação Studio, inspeção de 26 vistas LOD0, testes negativos 17/17 e contrato de caminhos/bytes 2/2 em Linux. Não equivale a reteste Windows nem a aprovação artística. Evidência em PILOTOS_ASSETS.md.
- LOD: 207 transições/raios, 24 contatos e captura posterior de 441 quadros/84 transições, amostragem visual e auditoria de peças estáticas; benchmark representativo Windows Ryzen 7520U já registrado. Hardware-alvo 7530U/iGPU/8 GB e otimização global são 10-01/08, não gate de release nesta fundação.
- Histórico Windows 95c7ac8: 26/47 passos, 7 falhos, 14 bloqueados. Preservar o relatório bruto; o reteste Linux posterior demonstrou geração de catálogo/pilotos/arsenal com os contratos intactos, mas não reclassifica os 47 passos daquela execução. O instalador universal não é gate da 00-34.

### Dependências obrigatórias

29 de 33 IDs predecessores aceitos no checklist, 4 parciais; 00-34 não pode ser homologada antes de todos os 33.

| ID | Evidência já existente | Falta para o critério revisado |
|---|---|---|
| 00-28 | Índice 8 armas/31 GLBs/7 acessórios, 10/10 testes Node, duas reconstruções idênticas à produção, amostras repouso/ADS/recarga. | Corrigir normal/tangente de produção que impede paridade do normal map, reconstruir fonte e inspecionar no Studio/Godot sem alterar gameplay. |
| 00-29 | Malhas, transforms e estados representativos conciliados; rota editável CC0 no Blender com 65 ossos. | Demonstrar equivalência da deformação/pose skinned capturada, não somente pose de repouso; preservar a fonte e GLB de referência. Não exigir anatomia/IK definitivos. |
| 00-31 | Layout real 49/49 no Windows, composição mapa real no Firefox, métricas e câmera documentadas. | Reunir evidência por critério de layout/transforms/materiais/colisão/referências e vistas representativas do mapa atual. Verificar equivalência de revisões e preencher apenas lacunas reais. Novos mapas, navegação e benchmark final não bloqueiam este ID por si. |
| 00-32 | Inventário 86 amostras/24 famílias/188 escopos na captura Windows; catálogo e Studio posteriores funcionaram. | Confirmar registros e escopos atuais dos 13 papéis/10 famílias, estados representativos dos efeitos, nós/hashes/materiais/colisores no Studio/Godot e limites de shader/consulta. Não presumir que abrir seis composições valida todos os papéis. |
| 00-34 | Fluxo técnico integrado já demonstrado em partes/reteste anterior; cobertura e rastreabilidade documentadas. | Aceite dos quatro IDs acima, conferir fluxo integrado na revisão identificada após as correções, com equivalência dos resultados reutilizados e reteste somente dos pontos afetados. Sem falhas impeditivas ou lacunas silenciosas. |

Débitos posteriores: arte final de armas e mãos (01/02), animações definitivas (04/06), melhorias dos mapas (09), popping amplo e desempenho final (10-01/08), ciclo de vida prolongado/recursos (10-02/05). Duas alocações de 349.524 bytes no shutdown da sonda isolada, registradas em PILOTOS_ASSETS.md, permanecem abertas para investigação de recursos, sem evidência de vazamento durante partida. Se impedirem o fluxo técnico ou forem reproduzidas como erro de produção, tratar como bloqueador; não ocultar warning.

### Validação e decisão desta entrega

Auditoria documental/remota: 131 IDs e 131 critérios na mesma ordem, 29/33 predecessores concluídos, quatro parciais, 00-34 parcial, 31/131 concluídas, 11 parciais e 89 pendentes. Diff do reteste integrado até main verificado (somente dois documentos). Não executados novos testes de Godot, Blender, WebGL ou benchmark, nem repetido QA integral: o portão de dependências ainda não foi satisfeito, e executar outros IDs está fora do escopo solicitado. Sem mudança de código/assets, instalador, runner ou workflow. Nenhum estado promovido. Priorizar 00-28, 00-29, 00-31 e 00-32; depois voltar exclusivamente à 00-34. Etapas 01–10 permanecem bloqueadas até 34/34.
