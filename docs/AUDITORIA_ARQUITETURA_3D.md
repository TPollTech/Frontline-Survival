# Auditoria técnica 3D — SNC Energies, SNC Adventures e Frontline Survival

**Data:** 24/11/2026. **Escopo:** primeira tarefa da etapa 00 do [checklist mestre](CHECKLIST_MESTRE.md). Auditoria estática de código e árvores Git, não homologação visual dos modelos. Nenhuma alteração em gameplay, GLB, texturas, cenas, versão ou workflows.

## 1. Evidências reproduzíveis

| Repositório (main) | Commit inspecionado | Arquivos rastreados |
|---|---|---:|
| [SNC Energies](https://github.com/TPollTech/snc-energies/tree/5fb385de2987bb637c2c529bbc98282c16bc2a7e) | `5fb385de2987bb637c2c529bbc98282c16bc2a7e` | 1479 |
| [SNC Adventures](https://github.com/TPollTech/SNC-Adventures/tree/cdc84bb80bad032711861c056bc14b786c1ba6b0) | `cdc84bb80bad032711861c056bc14b786c1ba6b0` | 1261 |
| [Frontline Survival](https://github.com/TPollTech/Frontline-Survival/tree/feb0b3f85c3c2cc17780a9ad264b4988f6d681f5) | `feb0b3f85c3c2cc17780a9ad264b4988f6d681f5` | 207 |

Contagem por blobs da árvore recursiva, sem truncamento, não por modelos lógicos. Foram lidos AGENTS.md, ASSET_STUDIO_SPEC.md e CHECKLIST_MESTRE.md do Frontline. Presença dos caminhos solicitados confirmada nas árvores das duas referências:

| Arquivo | Energies | Adventures |
|---|---|---|
| tools/vehicle_library.py | presente, analisado | ausente |
| previews/vehicle-studio.js | presente, analisado | ausente |
| previews/vehicle-studio.css | presente, analisado | ausente |
| tools/vehicle_texture_kit.py | presente, analisado | ausente |
| tools/vehicle_verify_library.py | presente, analisado | ausente |
| tools/gen_estudio_armas.py | ausente | presente, analisado |
| AGENTS.md | ausente na árvore rastreada | presente, regras de modelagem analisadas |

O JS do Energies menciona uma regra do AGENTS.md, mas o arquivo não existe nessa revisão rastreada. Não inferir seu conteúdo. Adventures usa `preview/` singular; Energies usa `previews/`.

## 2. SNC Energies — biblioteca compartilhada

- `tools/vehicle_library.py`: VehicleScene (linhas 23–95) organiza grupos, cubos, pivôs, rotações e materiais em ordem de autoria; stable_id usa UUID5 (98–99). export_bbmodel e export_glb (106–243) convertem uma mesma receita em arquivos com hierarquias e animação demonstrativa. build_model (246–249) registra eixos, unidades e locators. Os geradores generate_tractor, generate_harvester e generate_planter importam essa biblioteca, validam e exportam GLB + Blockbench. Reaproveitar organização, IDs estáveis, contratos e separação de receitas/exportadores. **Não copiar** VehicleScene.disk/wheel, que usa faixas de cuboides, nem unidade Minecraft 16 por bloco.
- `previews/vehicle-studio.js`: createVehicleStudio(config) (31), renderizador antialias/sRGB/ACES/PCFSoftShadowMap, OrbitControls com damping, piso e grade (61–122), materiais (136–181), grupos e pivôs (184–245), enquadramento dos cantos da caixa projetada no aspecto da tela (256–285), reset/tela cheia (288+). CSS compartilhado usa sidebar, controles e métricas. **Limite decisivo:** createModel instancia BoxGeometry a partir do JSON, não carrega diretamente GLB; vistas padrão são quatro direções de uma câmera perspectiva, não seis vistas ortográficas. Luz hemisférica/direcional, não HDRI no trecho analisado. O novo Studio deve usar GLTFLoader e metrificação real, sem reconstruir a geometria.
- `tools/vehicle_texture_kit.py`: NumPy/Pillow, superfície com seed, ruído, pintura e detalhes compartilhados (21–86); referência para biblioteca de superfícies. Não transportar resolução fixa 128², filtro nearest ou UV voxel. No FPS, gerar mapas de albedo, normal, roughness, metallic e outros conforme necessidade, com convenções de cor e escala documentadas.
- `tools/vehicle_verify_library.py`: verifica cabeçalho/chunks/buffers GLB (54+), matrizes e quaternions, grafo sem ciclos (133+), interseções OBB (154+), correspondência entre cantos autorais e geometria exportada (220+). Reaproveitar validação independente e comparações matemáticas, generalizar para malhas arbitrárias e animações, não apenas caixas.
- `tools/export_tractor_game_assets.py`: copia JSON/texturas canônicos para recursos do mod e registra SHA-256 (31–43). GLB é exportação de autoria, mas o jogo Minecraft usa seus próprios recursos; não afirmar que o jogo carrega esse GLB. `tools/package_tractor_preview.py` embute Three.js, OrbitControls, materiais, assets e licença em HTML offline por data URI. Reaproveitar opção offline reproduzível, com dependências fixadas e licenças.

## 3. SNC Adventures — descoberta e fidelidade ao jogo

- `tools/gen_estudio_armas.py` (7–51, 174–250, 350–410) lê JSON real do mod, resolve PNG real, UVs e transforms display. Descobre modelos com elements no diretório models/item, ordenando arquivos, e permite metadados adicionais para articulações. Empacota preview/estudio-armas.html e dist/estudio-armas-offline.html + SHA256.
- As vistas FPS/TPS usam transforms do Minecraft; a conversão T e conjugação de rotação são explicitadas (16–34). Adotar o princípio de importar a pose da engine, não a matriz de eixos do Minecraft. O renderer constrói BufferGeometry de faces dos cuboides com UVs, normais e texturas reais; não é leitor de GLB. A descoberta pula JSON inválido e textura não resolvida; no novo pipeline isso precisa virar erro ou pendência explícita, sem asset invisível ao inventário. A tabela de articulações contém exceções manuais; nosso contrato deve referenciar nós/pivôs estáveis. O gerador embute data da execução e tenta baixar Three.js se ausente; separar timestamp de hashes canônicos e garantir build offline sem download implícito.
- `tools/gen_catalogo.py`: Geometry, catálogo e seleção, geração de recursos e preview a partir da fonte; aproveitar separação das receitas por categoria. `tools/gen_revolver.py` e `tools/gen_escopeta.py`: exemplos da fonte canônica e atlas UV, mas especificamente limitados aos elements vanilla; não transplantar geometrias.
- `AGENTS.md` (10–36, 49–51) exige silhueta e acabamento, proíbe improvisos de bloco, exige fonte canônica, prévia fiel e validação no jogo. O Frontline já tem sua própria regra das 13 etapas; não importar regras de aprovação/execução específicas do mod que conflitem com AGENTS.md local.

## 4. Frontline Survival — arquitetura existente e lacunas

Baseline 0.9.34, Godot 4 Compatibility, 1280×720. A árvore tem 32 GLBs: 31 arquivos em assets/models (8 modelos completos, 8 body, 8 action e 7 mag; shotgun não tem mag separado) e 1 humanoide experimental em assets/characters. Há seis PNG de textura em assets/textures: asphalt, depot_concrete e quatro mapas de superfície de armas. Estes números não representam o total de objetos no jogo: grande parte nasce em GDScript.

| Componente | Evidência e situação | Direção proposta |
|---|---|---|
| Arsenal | tools/build_weapons.py: Gun, chamfer/cylinder/rod/ring, malhas personalizadas e validate_geometry, save concatena corpo inteiro e grupos body/mag/action (193–206) | Preservar gerador como adaptador legado; separar autoria/exportação; manter IDs, poses, encaixes e variantes. |
| Materiais | tools/generate_foley_textures.py: seed 9133 e quatro PNG 256²; scripts/weapon_materials.gd aplica overrides Godot por nome, vertex color, triplanar, metallic/roughness | Manifestar materiais efetivos por nó; UV/PBR reais; não assumir GLB bruto igual ao material visto em jogo. |
| Superfícies | scripts/model_surface.gd: superelipsoides MACHINED/MOLDED/PADDED, cache, ArrayMesh, normais analíticas, UVs por face e LOD de índices | Reusar para peças adequadas e inventariar usos em runtime; não confundir arredondamento de primitiva com remodelagem. |
| FPS | scripts/player.gd (181–213, 915–991): projeção independente por transform de nó, escala e profundidade por perfil, GLBs agrupados, mão/arma/attachments em runtime, animação procedural | Exportar captura/estado real da árvore Godot por configuração/pose; não aproximar FPS apenas com câmera Three.js. Manter gameplay desacoplado. |
| Personagens | scripts/enemy.gd e ally.gd criam articulações e volumes ModelSurface/cápsulas; usam GLB de arma; quaternius_soldier_visual.gd usa rig importado, materiais e equipamento programados | Manter visual legado durante migração; fonte editável e skin/skeleton; preservar comportamento e colisões; declarar procedência e limites da fonte de terceiros. |
| Humanoide experimental | scripts/main.gd linha 15: ENABLE_EXPERIMENTAL_HUMANOIDS=false; docs/ASSET_QUATERNIUS_CC0.md documenta GLB CC0 e rig, sem animações externas | Catálogo deve distinguir ativo e experimental. O doc histórico de um soldado por onda não significa que esteja ativo atualmente. |
| Mundo | scenes/main.tscn é cena de entrada; scripts/main.gd _create_world (397–445) cria Campo de Testes (piso 52×52 m), luz, céu, névoa, paredes, quatro containers, sacos, decoração e três lojas; _add_box separa malha/colisão (533–563) | Serializar composição real, transforms, materiais, colisões e ambiente; posteriormente receitas canônicas por módulo e mapa, sem alterar rotas e regras. |
| Objetos e efeitos | scripts/loot_pickup.gd, turret.gd, frag_grenade.gd, blood_impact.gd e main.gd geram objetos, pickups, torretas e efeitos 3D | Registrar receitas e amostras de estados reais; efeitos dinâmicos precisam de captura Godot quando glTF não representar o comportamento. |
| QA/CI | tools/verify_project.py, unittest, runtime_wave_qa.gd, arsenal_qa.gd, testes de FOV/miras/framing e capturas OpenGL em Xvfb | Manter verificadores e ampliar para inventário, hashes, geometria, importação, paridade Studio/Godot e inspeção visual registrada. |

Não há Asset Studio, manifesto global de assets, pipeline Blender, nem fonte canônica unificada na árvore auditada. Parte do conteúdo já tem fontes editáveis, porém dispersas. A existência de GLB não prova que sua aparência coincide com a cena real.

## 5. Decisões recomendadas para a próxima etapa (não implementadas)

A sequência deve seguir o checklist: inventário completo, arquitetura/manifesto, biblioteca, Studio/validação, pilotos, migração por categoria. Proposta inicial de separação:

- `tools/asset_pipeline/`: contratos, geradores, adaptadores de geometria, exportadores, verificação.
- `assets/source/`: receitas/fontes editáveis por categoria, com proveniência e dependências; evitar remover fontes existentes.
- `assets/catalog/`: manifesto gerado, IDs, hashes, exportações, estados de QA e associação com recursos reais.
- `previews/asset-studio/`: módulos web, GLTFLoader, controles, inspeção e empacotamento offline.
- `tools/` e Godot: exportador de árvore/captura de runtime para cenas, materiais, poses, colisões e efeitos que não residem em GLB. Usar fontes do engine, não réplica manual.

Esses nomes são sugestões, sujeitos à etapa de arquitetura. Backend Python para receitas e verificadores; Blender quando operações complexas/rigging exigirem. Preservar NumPy/Trimesh/SciPy/Pillow existentes. No CI auditado: trimesh 4.11.1 fixado; NumPy, SciPy e Pillow em faixas. Para determinismo futuro, fixar versões efetivas e hashes em lockfile, normalizar ordem, seeds e metadados. Three.js e módulos locais versionados/licenciados; medir orçamento por categoria e benchmark Ryzen 5 7530U/8GB, Compatibility.

Adoção segura: manter fallback e IDs existentes; validar transformação e material efetivo de cada piloto; comparar geometria e pose antes de substituir; testar renderização e desempenho; só remover legado depois de paridade aprovada. Nenhuma migração é autorizada por esta auditoria isoladamente.

## 6. Verificação, limitações e estado

- Conferência estática de árvores completas, caminhos solicitados e imports de biblioteca dos três geradores Energies; leitura de funções e regras citadas acima; revisão do código de geometria, materiais, cenas runtime e pipeline do Frontline. Evidências vinculadas aos commits da seção 1.
- Baseline CI [45412943170](https://github.com/TPollTech/Frontline-Survival/actions/runs/45412943170), v0.9.34: geração/verify/unittest, importação Godot, smoke, ondas, core Survival e integração passaram; Arsenal QA falhou; etapas de captura/exportação posteriores foram puladas. Última release v0.9.31. Não é uma execução nova desta auditoria.
- Ambiente atual não dispõe de checkout local nem executáveis Godot/Blender. Não foram executados novos builds, testes Python ou renderizações, nem aberto Studio dos projetos de referência. A auditoria é estática e não altera modelos; o portão de validação visual aplica-se à implementação futura. Não inferir qualidade artística a partir do código.
- A tarefa de auditoria de arquitetura pode ser marcada concluída: os três snapshots e todos os caminhos solicitados foram identificados, as lacunas e dependências registradas. A tarefa seguinte de inventariar **todos** os assets e instâncias de runtime continua pendente, assim como correção do CI e implementação do Studio. Não houve ZIP novo porque a entrega é documental.

## 7. Entregável esperado da próxima tarefa

Inventário rastreável por categoria: ID, fonte, export/arquivo, quem carrega, material real, tipo de hierarquia/animação, colisão, uso ativo/experimental/legado, dependências, licença e lacunas. Incluir cada recurso rastreado e cada família/receita de objetos de runtime com instâncias verificáveis; separar ativos em uso dos arquivos apenas presentes. Validar cobertura e reportar referências não resolvidas. Não iniciar remodelagem antes de estabelecer esse inventário.
