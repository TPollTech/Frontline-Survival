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
