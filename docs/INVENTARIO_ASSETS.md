# Inventário de assets e fontes — baseline v0.9.34

Data: 24/11/2026. Baseline imutável: [5b47000](https://github.com/TPollTech/Frontline-Survival/tree/5b47000bdb82f15e6cfda6227d785e4c2e3584fd). O inventário de máquina está em [asset_inventory_baseline.json](asset_inventory_baseline.json). Este é um levantamento estático de recursos, não o manifesto canônico final do Asset Studio e não uma homologação visual.

## Cobertura

| Item | Quantidade |
|---|---:|
| Recursos rastreados em assets/ | 60 |
| GLBs | 32 |
| Texturas PNG | 6 |
| Áudios (10 WAV e 1 OGG) | 11 |
| Metadados Godot .import | 11 |
| Arquivos scripts/ (GDScript + shader) | 22 |
| Cenas .tscn | 1 |
| Famílias de runtime mapeadas | 24 |
| Pontos de construção identificados no código | 290 |
| Referências literais verificadas | 57 |
| Referências literais não resolvidas | 0 |
| Pontos de construção identificados sem família | 0 |

A contagem de famílias e pontos de código não representa número de objetos ou nós instanciados em uma partida. Foram analisados os scripts visuais, seus helpers, referências res://, consultas físicas e cena de entrada; a varredura é heurística, não um parser completo de GDScript.

## Conteúdo físico e fontes

- 8 armas: 8 GLBs unidos para uso em mundo e 23 variantes (8 body, 8 action, 7 mag); shotgun não tem mag separado. Fonte: tools/build_weapons.py. Cada arquivo tem caminho, tamanho, hash Git blob SHA-1, consumidores e variante.
- Humanoide Quaternius: GLB com rig, experimental desativado na configuração atual; fonte editável upstream não rastreada. Procedência CC0 conforme docs/ASSET_QUATERNIUS_CC0.md.
- 6 texturas: asfalto, concreto e quatro mapas de metal/polímero. Fonte dos quatro mapas: tools/generate_foley_textures.py; aplicação real em scripts/weapon_materials.gd via override triplanar e vertex colors. Fonte de edição/procedência do asfalto e concreto não confirmada.
- 10 WAV: gravações de disparo e recarga, 5 classes; os três fuzis de precisão usam gravações compartilhadas no WeaponAudio. Proveniência específica/masters dos WAV precisam de revisão. OGG de granada: Kenney CC0 conforme docs/ASSET_EXPLOSION_CC0.md; hash registrado e conferido com árvore.
- 11 .import: metadados, não novos assets. Todos apontam para fonte existente.
- Uma cena rastreada (scenes/main.tscn), que instancia o mapa por scripts/main.gd; não existem mapas GLB completos nem cenas adicionais de mapa no snapshot. O inventário também registra scripts, ferramentas, QA e capturas históricas.

## Famílias construídas durante execução

- **map:campo_de_testes** — `scripts/main.gd` / `_create_world`, `_add_box`, `_add_container`, `_add_sandbags`, `_add_barrel`, `_add_cylinder`, `_add_depot_decor`, `_add_shop`. Piso, paredes, containers, sacos, tambores, pintura, decoração e três estações; composição e colisões runtime. Estado: active; captura runtime pendente.
- **environment:lighting** — `scripts/main.gd` / `_create_world`. Céu, luz, ambiente e névoa; configuração Godot. Estado: active; captura runtime pendente.
- **viewmodel:assembly** — `scripts/player.gd` / `_ready`, `_update_gun_mesh`, `_piece`, `_gun_box`, `_gun_tube`. GLBs separados, projeção, mãos e recursos construídos por código; helpers não necessariamente chamados. Estado: active_with_legacy_helpers; captura runtime pendente.
- **viewmodel:hands** — `scripts/player.gd` / `_arm_piece`, `_arm_link`, `_arm_capsule_link`, `_add_first_person_arm`. Mãos, dedos, braços, luvas e juntas; poses procedurais. Estado: active; captura runtime pendente.
- **viewmodel:attachments** — `scripts/player.gd` / `_build_attachment_models`, `_build_sniper_scope`. Ópticas e acessórios definidos no código; materiais e hierarquia runtime. Estado: active; captura runtime pendente.
- **player:collision** — `scripts/player.gd` / `_ready`, `_can_expand_to_height`. Capsula e consulta de postura; não equivalem à malha visual. Estado: active; captura runtime pendente.
- **enemy:legacy** — `scripts/enemy.gd` / `_ready`, `_joint`, `_part`, `_box`, `_capsule`. Corpo, equipamento, arma GLB, juntas e colisão; variantes por configuração. Estado: active; captura runtime pendente.
- **ally:legacy** — `scripts/ally.gd` / `_ready`, `_joint`, `_piece`, `_box`, `_capsule`. Corpo, equipamento, arma, articulações e colisão. Estado: active; captura runtime pendente.
- **character:quaternius_equipment** — `scripts/quaternius_soldier_visual.gd` / `_paint_character_meshes`, `_create_tactical_equipment`, `_equip_capsule`, `_equip_box`. Rig importado com peças e materiais adicionais. Estado: experimental_disabled; captura runtime pendente.
- **object:loot** — `scripts/loot_pickup.gd` / `_ready`. Arma ou caixa de munição criada por código. Estado: active; captura runtime pendente.
- **object:turret** — `scripts/turret.gd` / `_ready`. Base e componentes ModelSurface. Estado: active; captura runtime pendente.
- **object:grenade** — `scripts/frag_grenade.gd` / `_ready`, `_make_body`. Corpo visual e colisão física. Estado: active; captura runtime pendente.
- **effect:grenade** — `scripts/frag_grenade.gd` / `_effect_sphere`, `_spawn_explosion_effects`. Flash, anel e efeitos transitórios. Estado: active; captura runtime pendente.
- **effect:combat** — `scripts/main.gd` / `_call_airstrike`, `_airstrike_impact`, `_on_shot_fired`. Marcador e efeito de apoio, traçadores, cápsulas, impactos. Estado: active; captura runtime pendente.
- **effect:enemy_tracer** — `scripts/enemy.gd` / `_brief_enemy_tracer`. Efeito transitório. Estado: active; captura runtime pendente.
- **effect:blood** — `scripts/blood_impact.gd` / `_ready`. Gotas transitórias. Estado: active; captura runtime pendente.
- **effect:muzzle** — `scripts/player.gd` / `_ready`, `_build_muzzle_flash`. Clarão de disparo; malha criada em código. Estado: active; captura runtime pendente.
- **effect:scope_overlay** — `scripts/scope.gdshader`. Shader canvas_item; não é malha GLB. Estado: active; captura runtime pendente.
- **geometry:model_surface** — `scripts/model_surface.gd` / `body`, `_grid`. Receita compartilhada, cache, UV, normais e LOD; instâncias em vários scripts. Estado: active; captura runtime pendente.
- **material:weapon_overrides** — `scripts/weapon_materials.gd` / `_build_surface`, `_paint_recursive`. Texturas e material efetivo do jogo; seleção por nome. Estado: active; captura runtime pendente.
- **query:spawn** — `scripts/spawn_selector.gd`. Forma de consulta de spawn; não renderizável. Estado: active; captura runtime pendente.
- **query:enemy_tactics** — `scripts/enemy_tactics.gd`. Forma de consulta tática; não renderizável. Estado: active; captura runtime pendente.
- **query:turret** — `scripts/main.gd` / `_turret_position`. Consulta de colocação; não renderizável. Estado: active; captura runtime pendente.
- **camera:briefing** — `scripts/main.gd` / `_ready`. Câmera de apresentação do menu inicial; distinta da câmera do jogador. Estado: active; captura runtime pendente.

A composição estática do Campo de Testes inclui piso 52×52 m, 4 paredes de limite, 4 containers, 4 grupos de sacos, 8 tambores, 3 grupos de fachada, 4 grupos de postes e 3 estações físicas. Estes são totais derivados das chamadas da fonte, não contagens de nós renderizados. Os componentes têm geometrias e materiais próprios e devem aparecer no catálogo futuro.

## Dependências e lacunas

Godot Compatibility; CI de exportação usa 4.4.1, QA de 15 ondas usa 4.6.3; Python 3.11 com NumPy >=2.0,<2.5, Trimesh 4.11.1, SciPy >=1.11,<1.18 e Pillow >=10,<13. O CI usa Xvfb/OpenGL3 e templates Windows. Não existe lockfile completo, Three.js, Blender integrado ou Asset Studio na baseline. As dependências futuras não foram instaladas nesta tarefa.

Quatro padrões dinâmicos de caminho foram expandidos conservadoramente: GLB completo de NPC/pickup, GLB agrupado FPS e WAV de recarga NPC. Candidatos ausentes: shotgun_mag.glb (não exportado); bolt_sniper.wav, sentinela.wav e sniper.wav de recarga (a rotina NPC verifica existência; WeaponAudio usa rifle compartilhado no jogador). A ausência de um candidato não comprova bug; validar as configurações alcançáveis em Godot. Não foi detectada referência literal inexistente.

## Validação efetuada

- [x] All 60 tracked asset paths covered exactly once
- [x] Exact git blob SHA-1 and sizes for every asset
- [x] All tracked script and scene paths represented
- [x] All literal references resolve
- [x] All conservative dynamic expansions match tree
- [x] All import metadata have matching source
- [x] All 290 identified constructor sites assigned to families
- [x] Unique stable family IDs and tracked source paths
- [x] All families explicitly pending runtime capture

As verificações acima foram executadas sobre a árvore Git remota e o JSON gerado; não são testes de importação GLB ou de gameplay. Para reproduzir no checkout com histórico Git disponível: `python docs/qa/verify_asset_inventory.py`. O verificador compara hashes, cobertura, caminhos, ancoragem das referências e os pontos registrados no snapshot; não substitui inventário vivo.

O [CI anterior](https://github.com/TPollTech/Frontline-Survival/actions/runs/45412943170) falhou no QA individual do arsenal. A falha não foi corrigida nesta tarefa. O ambiente atual não tem Godot, Blender ou checkout local acessível; sem renderização e sem captura real de nós em execução. Não foi alterado nenhum asset, script de gameplay, versão ou workflow.

**Estado da tarefa:** levantamento estático concluído e verificado; manter tarefa parcial/desmarcada no checklist, pois a verificação integral das instâncias runtime, materiais efetivos, hierarquias, colisões, LOD, dimensões, procedência e variações reais ainda precisa ser executada. Não usar este JSON como se fosse um catálogo de assets homologados. A próxima fase deve implementar/validar um extrator de cena real no Godot, conciliando seus resultados com este inventário, sem reconstituir modelos fictícios no Studio.

## Complemento runtime

Veja [INVENTARIO_RUNTIME.md](INVENTARIO_RUNTIME.md) para o novo extrator de cenas e workflow isolado. A baseline histórica permanece imutável; não equivale a catálogo vivo.

## Estado final da baseline

Inventário da versão existente concluído: 60/60 recursos físicos, 30/30 fontes/configurações da baseline sem divergências na main, 32/32 GLBs observados, 86 amostras e cobertura de 24/24 famílias por captura/consulta. [Relatório e limites](INVENTARIO_RUNTIME.md), [evidência final](qa/runtime_inventory_final_evidence.json). As lacunas de proveniência, atribuição de materiais, LOD, exportação e homologação seguem registradas nas tarefas subsequentes; não representam recursos omitidos do inventário. Não confundir inventário concluído com catálogo vivo ou modelos aprovados.
