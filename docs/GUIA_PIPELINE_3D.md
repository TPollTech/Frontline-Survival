# Guia operacional do pipeline 3D — Frontline Survival (00-33)

25/11/2026. Referência: a7342f5198395ad4ba7dede0768c67ded7c98d65. Este guia consolida a operação atual; complementa [AGENTS.md](../AGENTS.md), [especificação obrigatória](ASSET_STUDIO_SPEC.md), [contrato v1](ARQUITETURA_ASSET_PIPELINE.md) e [Checklist Mestre](CHECKLIST_MESTRE.md). Os demais documentos mantêm histórico por revisão. Não confundir evidência histórica, código implementado e homologação da revisão atual. Actions sem cota nesta entrega: não disparar workflows; alterações justificadas na main com [skip ci], sem force push.

> Política de aceite de 25/11/2026: [matriz por ID](CRITERIOS_ACEITE_1_0.md). Os comandos são ferramentas reutilizáveis, não roteiro obrigatório completo para toda tarefa. Fundamento técnico e piloto exigem medições representativas; benchmark final no hardware-alvo e otimização integral pertencem à etapa 10. Manter inspeção real e rastreabilidade dos modelos alterados. Evidência histórica não é nova execução.

## 1. Arquitetura e fontes

Existem duas rotas de produção, com uma única fonte verdadeira por asset:
- Receita editável → IR paramétrica/backend Python ou Blender → GLB/glTF original → validação/importação → Godot. Studio carrega os bytes originais verificados.
- Receita/cena GDScript → composição real Godot → inventário, buffers, transforms, materiais e escopos capturados → catálogo vivo → reconstrução Studio. Não criar modelo independente para preview.

| Camada | Responsabilidade |
|---|---|
| Contrato histórico | tools/asset_pipeline/manifest_contract.mjs, build_manifest.mjs e assets/catalog/manifest.json. Baseline imutável, não editar manualmente. |
| Biblioteca | tools/asset_pipeline/parametric/: model, recipes, advanced, organic, shading, pbr, rig, lod, exporter e backend Blender opcional. MeshSpec/NodeSpec/SceneSpec/Transform, RenderMesh, ColliderSpec, AssetLOD. |
| Arsenal | tools/build_weapons.py e scripts/player.gd, materiais e GLBs originais. arsenal_sources.mjs rastreia receitas e variantes; não substitui o gerador. |
| Personagens | scripts/character_geometry.gd, consumidores player, enemy, ally, quaternius_soldier_visual. Montagem, física e poses permanecem nos consumidores. |
| Mundo | scripts/world_asset_geometry.gd, model_surface.gd, campo_de_testes_layout.gd, main.gd, scenes/main.tscn; WorldLOD altera malhas registradas, não colisores. |
| QA Godot | tools/asset_pipeline/runtime/: inventory_qa.gd, capture_views.gd e QA de LOD, contato, benchmark, movimento. Cena real, estados finitos. |
| Catálogo atual | tools/asset_pipeline/live_catalog.py, runtime_catalog_evidence.py, runtime_asset_scopes.py. Descoberta, dependências, hashes, evidências e composições. |
| Studio | tools/asset_studio/: prepare.py, Three.js, câmera/luz, inspeção, runtime-composition, vistas anexadas e servidor offline. |
| Verificação | validate_gltf.py, testes Python/Node, QA Godot e browser_test.mjs/offline_test.mjs. |

## 2. Contrato e convenções

Metro, sistema destro, +Y para cima, câmera -Z. Armas legadas frente -Z; declarar frente de cada asset (não impor uma rotação genérica). Blender +Z cima/+Y frente: C(x,y,z)=(x,z,-y); transforms por conjugação, normais por inversa transposta; converter uma vez. Matrizes coluna-major, world=parent_world*local, quaternions xyzw; pivô e origem explícitos. Enquadrar movendo a câmera, não alterando a malha. Dimensão física não é escala do viewmodel.

ID estável, categoria, fonte editável e funções, revisão, licença/procedência, hashes dos outputs e fontes, materiais/texturas, hierarquia, pivôs, rig/animações, dimensões, shapes, LOD, orçamento e evidências. Dados desconhecidos ficam nulos; GLB ou nota de licença não provam fonte editável. PBR: fatores lineares, base color/emissive sRGB, normal/ORM lineares (R AO, G roughness, B metallic); normal tangent-space +Y.

Baseline guarda hashes Git históricos; catálogo vivo calcula SHA-256 e Git blob SHA-1 atuais (não são iguais), preserva IDs, descobre file:<path> e candidate:<path>. Candidato não prova uso. Referências ausentes e dinâmicas não resolvidas ficam explícitas. Alterar schema apenas com migração e testes; não reinterpretar dados antigos. Captura exige revisão correspondente e recursos reais, distingue material carregado de atribuído. Escopos asset_scope_schema:1 da 00-32 selecionam nós reais e separam efeito da subárvore integral; não recortam visualmente a composição. Consultas temporárias não são colisores persistentes. LOD bias não é índice de LOD. Catálogo automático mantém approved:false.

## 3. Categorias e orçamentos

Extração de tools/asset_pipeline/parametric/lod.py na revisão de referência. Limites provisórios por instância (mapa/terreno em chunks), não metas de FPS.

| Categoria | Tri LOD0 | Tri LOD1 | Tri LOD2 | Colisores máx. | Tri proxy máx. | Slots máx. |
|---|---:|---:|---:|---:|---:|---:|
| weapon | 18000 | 7000 | 1800 | 8 | 256 | 8 |
| accessory | 6000 | 2400 | 600 | 4 | 128 | 4 |
| first_person | 24000 | 10000 | 3000 | 12 | 512 | 8 |
| character | 22000 | 8000 | 2200 | 16 | 512 | 8 |
| object | 8000 | 2800 | 700 | 8 | 256 | 4 |
| environment | 12000 | 4000 | 1000 | 12 | 512 | 6 |
| vehicle | 30000 | 12000 | 3000 | 16 | 768 | 8 |
| structure | 20000 | 8000 | 2000 | 24 | 2048 | 8 |
| terrain | 16000 | 6000 | 1500 | 8 | 4096 | 4 |
| map | 24000 | 9000 | 2500 | 32 | 8192 | 12 |
| effect | 2000 | 800 | 200 | 2 | 128 | 2 |
| collision | 2000 | 800 | 200 | 32 | 8192 | 2 |
| geometry_library | 24000 | 9000 | 2500 | 16 | 1024 | 8 |

Não geométricas: audio, camera, shader, material, physics_query, texture. Categorias de descoberta (weapon_mesh, character_mesh, procedural_candidate, import_metadata) não são automaticamente categorias de orçamento; mapear explicitamente. Não usar object como default silencioso.

ColliderSpec independente: box, sphere, capsule, convex fechado/orientado e concave apenas estático. Altura da cápsula inclui hemisférios. Conservar corpo, owner, transform, dimensão, camada/máscara e estado enabled ao trocar LOD. AssetLOD mantém hierarquia, pivôs, materiais e bounds dentro da tolerância; três níveis e distâncias/histerese declaradas. WorldLOD existente: 0/12/30 m, histerese 1 m, nas famílias registradas. Justificar ausência de LOD quando inaplicável; não inventar níveis. Contagem registrada não é triângulo submetido à GPU.

## 4. Adicionar asset ou categoria

1. Conferir ID, licença, fonte existente e critério de aceite. Nova categoria geométrica exige BUDGETS, mapeamento, contratos e testes; preservar IDs legados. Não criar preview separado.
2. Definir escala, frente, proporções, pivôs, silhueta, detalhes, PBR, UV/normais/tangentes, rig/encaixes e colisores independentes. Escolher backend adequado e registrar versões.
3. Gerar em pasta temporária. Comparar duas gerações independentes, hashes e manifestos; validar a categoria correta e contrato explícito. Não substituir produção antes da paridade.
4. Para novo arquivo, testar descoberta e dependências reais; para família procedural, ligar ID, consumidor, funções e fonte; atualizar domínios finitos, captura e verificadores pertinentes. Preservar baseline; testar ausência, duplicidade, drift e falsa aprovação. Não tratar candidate como família homologada.
5. Integrar por lote; preservar transforms, cache, ordem de montagem, material, física e comportamento. Capturar na mesma revisão, reconstruir Studio, verificar poses e estados reais nos dois renderizadores; corrigir na fonte e repetir antes de remover legado.

## 5. Comandos locais

Pré-requisitos: Git, Python 3.10+ (CI 3.11), Node 22/npm, Godot 4.4.1 Compatibility/OpenGL3, display real ou Xvfb, Blender opcional (histórico 3.0.1) quando exigido. Three.js 0.170.0 e Playwright 1.51.1; navegador WebGL2. Instalação inicial requer rede; execução do pacote Studio sem CDN. Verificar versões instaladas; não confundir presença com execução.

### 5.1 Verificação sem engine

Na raiz, checkout limpo:
```sh
git status --short
git rev-parse HEAD
node tools/asset_pipeline/build_manifest.mjs
python -m unittest discover -s tests -p 'test_parametric*.py' -v
python -m unittest discover -s tests -p test_validate_gltf.py -v
python -m unittest discover -s tests -p test_live_catalog.py -v
python -m unittest discover -s tests -p test_runtime_asset_scopes.py -v
python -m unittest discover -s tests -p 'test_world_lod*.py' -v
node --test tests/test_arsenal_sources.mjs
```
Manifesto verifica baseline; --write regenera somente baseline, não usar para migrar. Para exigir Blender real, Linux: FRONTLINE_REQUIRE_BLENDER=1 python -m unittest discover -s tests -p 'test_parametric_library.py' -v. Em PowerShell, definir e depois remover $env:FRONTLINE_REQUIRE_BLENDER. Relatar skips separadamente.

Exemplos Linux, pastas novas externas ao repo; trocar REVISION por SHA completo:
```sh
python tools/asset_pipeline/live_catalog.py --output /tmp/frontline-live.json
python -m tools.asset_pipeline.validate_gltf --output /tmp/frontline-production.json
python -m tools.asset_pipeline.parametric.export_fixture /tmp/frontline-fixture REVISION
python -m tools.asset_pipeline.validate_gltf --root /tmp/frontline-fixture --source-root . --strict --category object --contract tools/asset_pipeline/parametric/export_fixture_contract.json --file asset.glb --file asset.gltf --output /tmp/frontline-fixture-report.json
python -m tools.asset_pipeline.parametric.pilot_object /tmp/frontline-pilot REVISION
python -m tools.asset_pipeline.parametric.pilot_suite /tmp/frontline-suite REVISION
node tools/asset_pipeline/arsenal_sources.mjs /tmp/frontline-arsenal.json
```
Pilotos/fixtures QA-only. Rebuild do arsenal: node tools/asset_pipeline/arsenal_sources.mjs /tmp/frontline-arsenal-rebuild.json --rebuild python, com dependências instaladas; duas gerações em temporários, não sobrescreve produção, divergências falham. Versões candidatas não provam ambiente original. --audit-only do validador pode retornar sucesso com erros: não é gate. Ver [validação](VALIDACAO_ASSETS.md).

### 5.2 Inventário e Studio da mesma revisão (Bash/Linux)

Importação pode reescrever .import e criar .uid. Isolar em worktree Git descartável (não git archive sem metadados para catálogo), perfil QA, arquivos externos. Roteiro abaixo é referência proposta, não novo script homologado. Usar display; se necessário prefixar cada Godot com xvfb-run. Interromper em caso de erro ou marker ausente.

```bash
set -euo pipefail
test -z "$(git status --porcelain)"
REV=$(git rev-parse HEAD)
QA=$(mktemp -d)
git worktree add --detach "$QA/project" "$REV"
cd "$QA/project"
export GITHUB_SHA="$REV"
export XDG_DATA_HOME="$QA/profile"
export FRONTLINE_INVENTORY_DIR="$QA/inventory"
export FRONTLINE_VIEWS_DIR="$QA/views"
mkdir -p "$XDG_DATA_HOME" "$FRONTLINE_INVENTORY_DIR" "$FRONTLINE_VIEWS_DIR"
godot --version
godot --path . --rendering-driver opengl3 --audio-driver Dummy --editor --import 2>&1 | tee "$QA/import.log"
godot --path . --rendering-driver opengl3 --audio-driver Dummy --script res://tools/asset_pipeline/runtime/inventory_qa.gd 2>&1 | tee "$QA/inventory.log"
grep -q ASSET_RUNTIME_INVENTORY_PASS "$QA/inventory.log"
python docs/qa/verify_runtime_inventory.py "$FRONTLINE_INVENTORY_DIR/runtime_inventory.json" "$QA/reconciliation.json"
godot --path . --rendering-driver opengl3 --audio-driver Dummy --script res://tools/asset_pipeline/runtime/capture_views.gd 2>&1 | tee "$QA/views.log"
grep -q RUNTIME_VIEWS_PASS "$QA/views.log"
if grep -E 'SCRIPT ERROR:|Parse Error|ASSET_RUNTIME_ERROR|RUNTIME_VIEW_FAIL' "$QA/"*.log; then exit 1; fi
python tools/asset_pipeline/live_catalog.py --runtime "$FRONTLINE_INVENTORY_DIR/runtime_inventory.json" --output "$QA/catalog.json"
python tools/asset_pipeline/live_catalog.py --runtime "$FRONTLINE_INVENTORY_DIR/runtime_inventory.json" --output "$QA/catalog-repeat.json"
cmp "$QA/catalog.json" "$QA/catalog-repeat.json"
npm --prefix tools/asset_studio install --ignore-scripts
(cd tools/asset_studio && npx playwright install chromium)
python tools/asset_studio/prepare.py "$QA/studio" --runtime "$FRONTLINE_INVENTORY_DIR/runtime_inventory.json"
python tools/asset_studio/attach_runtime_views.py "$QA/studio" "$FRONTLINE_VIEWS_DIR"
printf 'QA=%s\n' "$QA"
python -m http.server 8765 --bind 127.0.0.1 --directory "$QA/studio"
```

Abrir http://127.0.0.1:8765. Em outro terminal no mesmo worktree, substituir /caminho/qa pelo valor impresso: REQUIRE_RUNTIME_VIEWS=1 STUDIO_EVIDENCE=/caminho/qa/studio-evidence node tools/asset_studio/browser_test.mjs. Bibliotecas do Chromium podem exigir instalação (histórico --with-deps). Offline: node tools/asset_studio/offline_test.mjs com serviço local; para comprovar ZIP, conferir hash/conteúdo, extrair e servir com python serve_offline.py, repetir teste com STUDIO_URL se porta diferente. Não confundir pacote Studio com executável Windows. Abrir imagens/canvas e registrar revisão visual, não apenas marker. Comparar câmera, FOV, transforms, materiais, LOD e aparência. Conservar evidências antes de remover worktree; conferir git status; sidecars regenerados registrados não autorizam drift de fontes ou malhas reais. Não publicar mudanças de importação por acidente.

Windows: worktree separado, caminhos absolutos em TEMP; definir $env:GITHUB_SHA, $env:APPDATA, $env:LOCALAPPDATA para perfil (GITHUB_SHA recebe revisão, APPDATA/LOCALAPPDATA recebem pasta QA), $env:FRONTLINE_INVENTORY_DIR e $env:FRONTLINE_VIEWS_DIR; usar executável console Godot, verificar $LASTEXITCODE e logs a cada comando. Studio sem runtime: python tools/asset_studio/prepare.py CAMINHO_NOVO_FORA_DO_REPO; não alegar reconstrução de runtime sem --runtime.

### 5.3 LOD/contato/benchmark/movimento

Usar runner no checkout principal limpo, não no worktree importado. Snapshot e perfil isolados; saída externa nova para cada execução. PowerShell:
```powershell
$godot = "C:\Godot\Godot_v4.4.1-stable_win64_console.exe"
$base = "$env:TEMP\frontline-qa-$(Get-Date -Format yyyyMMdd-HHmmss)"
python tools/asset_pipeline/world_lod_local.py "$base-lod" --godot "$godot"
python tools/asset_pipeline/world_lod_local.py "$base-bench" --godot "$godot" --benchmark
python tools/asset_pipeline/world_lod_local.py "$base-motion" --godot "$godot" --motion
```
Ajustar executável; Linux mesmas opções e pastas /tmp externas. --verify-only só confere QA padrão existente; não combinar modos. QA padrão: 207 transições/raios e 24 contatos previstos; verificador confere 207 e cabeçalhos de 30 PNGs, contato consta no log/relatório Godot. Benchmark A/B/B/A mede intervalos de frames do mapa congelado; --motion prevê 441 PNGs, delta simulado 0,1 s; não mede FPS. Cabeçalho não equivale a imagem decodificada ou inspecionada. Ver [LOD](LOD_COLISOES_RUNTIME.md).

## 6. Política de QA e aceite

Cumprir os 13 passos da especificação: referências, proporções, silhueta, detalhes, materiais, exportação, validação técnica, abrir Studio, inspeção visual, corrigir fonte/repetir, integrar, abrir/testar Godot e registrar evidências. Documentação sem mudança de modelagem não requer nova captura; nenhuma alteração visual dispensa o gate.

| Portão | Evidência necessária |
|---|---|
| Fonte | ID, revisão, hash, licença, dependências, escala, pivôs e receita real; lacunas explícitas. |
| Técnico | Topologia, UV, normal/tangente, materiais/texturas, rig, bounds, referência, orçamento e colisores; resultados e skips. |
| Reprodução e importação | Duas gerações comparáveis, hashes, Godot Compatibility real, sem erros. |
| Runtime/catálogo | Revisão correspondente, hierarquias, materiais efetivos, buffers, escopos, LOD e física; casos negativos. |
| Studio | WebGL, vistas, material, UV/wireframe/normais, pivôs, colisões, LOD, poses, composição, offline; inspeção real. |
| Godot | Câmera e luz normais; armas repouso/ADS/recarga/acessórios, personagens anatomia/poses, mapa navegação/colisão, efeitos ciclo de vida e limpeza; comparar antes/depois. |
| Desempenho | Ryzen 5 7530U/iGPU/8 GB: registrar driver, renderer, resolução, VSync, condições, FPS, frame time, memória, triângulos e slots; repetir percursos/partidas. llvmpipe não é a iGPU alvo. |
| Entrega | Commit integrado na main sem force, remoto conferido, evidências/limitações e checklist; ZIP Windows validado quando houver exportação/distribuição aplicável. |

Registro mínimo: ID da tarefa, base e revisão testada, fonte/asset/hashes, CPU/GPU/RAM/driver/engine/browser, comando/retorno, cenário/pose/câmera/seed, testes aprovados/falhos/pulados, logs/imagens/hashes, quem inspecionou/quando/observações, desempenho, limitações e decisão técnica/visual separadas. Não preencher desconhecido com zero. Sintético testa verificador, não engine. Concluído só quando critério específico demonstrado; parcial distingue implementação de validação; pendente sem implementação suficiente. Não promover outros IDs por documentar.

## 7. Referências e estado consolidado

| Documento | Situação na base de referência |
|---|---|
| [Biblioteca](BIBLIOTECA_PARAMETRICA.md) | Fundação validada historicamente, IR/backends, PBR, rig e exportação. |
| [Validação](VALIDACAO_ASSETS.md), [Pilotos](PILOTOS_ASSETS.md) | Auditoria GLBs e pilotos técnicos; produção e homologação artística com lacunas. |
| [Inventário](INVENTARIO_RUNTIME.md), [Catálogo](CATALOGO_VIVO.md), [Studio](ASSET_STUDIO.md) | 86 amostras/24 famílias históricas; relato LOD 225 buffers/86 composições preparados, Chromium falhou no Studio nessa revisão. |
| [Arsenal 00-28](ARSENAL_FONTES_CANONICAS.md) | 8 armas, 31 GLBs, 7 acessórios indexados; reprodução/migração/visual pendentes. |
| [Personagens 00-29](PERSONAGENS_FONTES_CANONICAS.md) | 5 receitas compartilhadas; anatomia, rig, testes específicos; Quaternius experimental não é produção padrão. |
| [Objetos 00-30](OBJETOS_FONTES_CANONICAS.md) | 6 receitas/5 famílias, paridade pendente; utility_cart QA-only. |
| [Mapas 00-31](MAPAS_FONTES_CANONICAS.md) | Composição canônica do Campo de Testes; QA específico e navegação pendentes. |
| [Runtime 00-32](RUNTIME_FONTES_CANONICAS.md) | 13 papéis/10 famílias, 9/9 testes sintéticos; captura atual, WebGL, estados e limpeza pendentes. |
| [LOD 00-10](LOD_COLISOES_RUNTIME.md) | 207/207 transições, 24/24 contatos, 15 comparações fixas inspecionadas, 960 intervalos llvmpipe históricos; --motion preparado, 10/10 testes sintéticos; execução/inspeção, ampliação, WebGL e hardware-alvo pendentes. |

00-33 é exclusivamente documental. 00-34 é auditoria integral e homologação distintas; não declarar sucesso de comandos de runtime só por estarem descritos.

## 8. Evidência da 00-33

11/11 verificações estáticas executadas sobre fontes reais consultadas e texto proposto: 13 categorias e valores correspondentes ao código; 6 categorias não geométricas documentadas; CLI catálogo; CLI LOD; CLI prepare; CLI validação; versões Studio; links do guia apontam para documentos consultados nesta sessão; links de entrada inseridos; 131 tarefas e somente linha 33 alterada; somente Markdown alterado. Não foram executados os comandos de build, Godot, browser, Blender, benchmark ou suites listados. Esta entrega é exclusivamente documental. Não houve captura nova, mudança de modelo, gameplay, exportação ou release. A sequência integrada proposta ainda deve ser executada na auditoria 00-34.
