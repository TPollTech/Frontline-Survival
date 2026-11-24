# Arquitetura modular e contrato canônico 3D — v1

Data: 24/11/2026. Complementa ASSET_STUDIO_SPEC.md, AUDITORIA_ARQUITETURA_3D.md e INVENTARIO_ASSETS.md. Esta entrega define e implementa a camada de contrato, não o motor geométrico, Studio ou extrator Godot.

## Decisão de arquitetura

Fluxo único: fonte editável → receita/IR de cena → backend geométrico → exportador → validação → manifesto → Godot e Studio. O Studio não cria geometria de substituição. A engine continua usando os recursos e código atuais até migração validada.

| Módulo | Responsabilidade | Estado |
|---|---|---|
| tools/asset_pipeline/manifest_contract.mjs | Contrato v1, conversão de vetores, geração e validação da baseline | Implementado |
| tools/asset_pipeline/build_manifest.mjs | CLI sem dependências npm; gera/confere JSON a partir da baseline imutável | Implementado |
| assets/catalog/manifest.json | Catálogo inicial derivado do inventário | Implementado, estático |
| assets/source/{category}/ | Receitas Python, fontes Blender e referências licenciadas | Planejado, preservar fontes atuais |
| tools/asset_pipeline/{geometry,materials,rigging,exporters,validators}/ | Biblioteca Python, backend Blender opcional, interfaces de exportação/QA | Planejado |
| tools/asset_pipeline/runtime/ | Extrator Godot de árvores, transforms, recursos, materiais, colisões, animações e estados reais | Planejado |
| previews/asset-studio/ | Three.js/GLTFLoader, renderização e inspeção do catálogo; pacote offline | Planejado |

Node.js LTS (>=20) é uma dependência apenas de tooling para o contrato compartilhável com JS do futuro Studio; não é necessária para jogar. O núcleo geométrico permanece Python conforme a especificação. Não introduzimos dependência npm ou download de rede. O futuro backend Blender deve ser opcional, versionado e reproduzível. IR deve separar SceneSpec (nós/pivôs/transformações/instâncias) de MeshSpec (topologia/atributos/UVs), MaterialSpec (PBR), RigSpec, ColliderSpec e LODSpec; backend não depende do Studio, e Studio não depende da implementação da geometria. Definição de interfaces executáveis da biblioteca fica para sua tarefa específica.

## Coordenadas, escalas e transformações

- Unidade canônica: metro, 1 unidade de cena = 1 m; ângulos em radianos, eixos destros, +X direita, +Y cima, câmera olhando -Z. Armas do legado têm frente -Z. Frente de personagem/veículo/objeto deve ser declarada por categoria/asset a partir de evidência, não presumida.
- Blender: autoria em metros, +Z cima, +Y frente por convenção deste projeto; adaptador de posição/direção `C(x,y,z)=(x,z,-y)`, rotação própria (determinante +1), inversa `C^-1(x,y,z)=(x,-z,y)`. Para transforms completos usar conjugação `C M C^-1` e converter normais com inversa transposta; não aplicar conversão dupla no exportador glTF. Os helpers desta etapa convertem vetores; transformação de malha/rig completa é tarefa futura.
- glTF 2.0 já é destro, Y-up e metro; a convenção de frente de asset glTF (+Z) não é a direção de olhar de câmera Godot (-Z). Não aplicar rotação global automática a GLBs legados. Preservar e verificar basis e orientação efetivamente importados; diferenças de frente declaradas no asset/adaptador. Testar fiduciais assimétricos em ambos os renderizadores quando existirem.
- Matrizes 4x4 coluna-major, vetor coluna; world=parent_world*local; quaternions normalizados xyzw. Origem e pivô locais explícitos, sem recentralizar geometry para enquadrar Studio; deslocar a câmera de inspeção. Não confundir escala de inspeção/projeção FPS com dimensão física.
- Bounds locais e mundo separados, dimensões [X,Y,Z] em m, não inferir a partir de nomes/arquivos. Normais, UV, orientação de winding e tangentes precisam de verificação específica do backend. Three.js e Godot podem diferir em materiais/shaders; isso exige evidência Godot e não malha alternativa.

## Manifesto v1: baseline estática

`assets/catalog/manifest.json` é gerado, nunca corrigido à mão. O inventário histórico é entrada de bootstrap; não é descoberta contínua de arquivos novos. A futura tarefa de catálogo automático substituirá/adicionará uma entrada de descoberta atual, preservando IDs. Versionar schema e migrar explicitamente; não reinterpretar silenciosamente versões antigas.

- `resources`: todos os 60 caminhos rastreados em assets/ no snapshot (inclui 11 .import, sem tratá-los como modelos); bytes, Git blob SHA-1, categoria, consumidores, uso/procedência. Hash é identificador de blob Git da baseline, não SHA-256 do arquivo. `source_registry`: fontes, ferramentas, cenas e configuração com hash. `baseline_commit/tree`: âncora imutável, não atestado de que a main futura não mudou.
- `assets`: 50 IDs lógicos estáveis: 8 armas, 1 humanoide importado, 17 recursos de textura/áudio, 24 famílias runtime. O ID não muda ao renomear arquivo; migrações futuras devem preservar aliases e IDs explicitamente. As variantes GLB de um asset compartilham ID e cada arquivo tem um único proprietário. Dependências apontam a IDs, arquivos ou fontes registradas; referências de composição podem ser recíprocas (arma ↔ viewmodel), não são um DAG de build. O futuro pipeline de execução deve ter DAG separado e rejeitar ciclos nele.
- Cada registro tem source (path, kind, functions, editable, hash), outputs (path, role), dependências, categoria/usage, preview (mode/resource/composition/fidelity), coordenadas, campos de dimensões, bounds, materiais, pivôs, hierarquia, animações, colisão, LOD, orçamento, proveniência, lacunas e validação. Dados não medidos são null; não inventar métricas. Fonte importada sem edição rastreada fica editable=false; não confundir binário/nota de licença com receita editável. Licenças pendentes permanecem explícitas.
- `preview.mode` separa GLB real bruto (com composição runtime pendente), inspeção de recurso, captura runtime, debug físico, inspeção de biblioteca e evidência da engine. Nenhuma família runtime recebe GLB fictício. O Studio futuro deve rotular bruto vs composição real, bloquear apresentação enganosa e resolver caminhos locais do manifesto, não aceitar paths externos/traversal.
- Validação v1 bootstrap: static=inventory_only; runtime=pending; studio_visual/godot_visual=pending (ou not_applicable para áudio/textura no gate 3D); evidence=[]; approved=false. O verificador rejeita aprovação nesse snapshot. Futuro schema de captura e promoção exige hashes dos recursos/receitas, commit, ferramenta/versão, plataforma, cenário/pose, captura e inspeção registrada, resultados automatizados, decisão e revisor. Estados de falha não podem desaparecer ao regenerar.
- O extrator Godot futuro deve produzir representação fiel da composição (árvore real, NodePath/ID, local/world, malha/recurso ou hash, material efetivo, câmera/FOV/projeção, pose, skin, LOD, colisões, estado/seed/tempo) e evidência para elementos não representáveis em GLB (shaders, efeitos, física, iluminação). Não reproduzir independentemente a geometria no browser. Inventário de todas as instâncias continua pendente.

## Execução e validação

```sh
node tools/asset_pipeline/build_manifest.mjs
node tools/asset_pipeline/build_manifest.mjs --write
python docs/qa/verify_asset_inventory.py
```

Primeiro comando verifica serialização exata e roda testes do contrato. Segundo regenera baseline (não escaneia main). Terceiro compara inventário com Git histórico. Os testes JS do contrato foram executados no ambiente V8 conectado ao GitHub, com o JSON real recuperado da main. Validam cobertura, determinismo, vetores, orientação, fontes, caminhos, IDs, dependências, ausência de exportação falsa/aprovação falsa e unidades. CLI Node no checkout não executada neste ambiente; Git remoto inacessível pelo container. Godot, Blender e Studio não estão disponíveis localmente. Nenhuma alteração visual nem gameplay foi realizada; inspeção visual não se aplica à definição de contrato. Nenhuma versão/ZIP nova. Não alegar que o manifesto representa toda a cena em execução.

## Próxima tarefa

Implementar biblioteca paramétrica Python com interface modular, backend básico e extensão Blender, sem alterar assets atuais; testar a API e seus contratos. Em paralelo, inventário runtime ainda precisa de extrator e verificação real, e a regressão do CI do arsenal permanece aberta.

## Estado após inventário runtime

O extrator de QA em tools/asset_pipeline/runtime/inventory_qa.gd foi implementado e validado na engine: 86 amostras e 24/24 famílias por captura/consulta. Consulte [INVENTARIO_RUNTIME.md](INVENTARIO_RUNTIME.md). O manifesto v1 permanece baseline estática; evidência de runtime separada, sem promover aprovação de modelo. Exportação fiel de geometria para Studio e catálogo vivo continuam tarefas futuras.

## Fundação paramétrica executável

A biblioteca em tools/asset_pipeline/parametric implementa IR de cena/malha, receitas iniciais, backend Python e adaptador Blender opcional. Ver [BIBLIOTECA_PARAMETRICA.md](BIBLIOTECA_PARAMETRICA.md). Rigging, materiais completos, colisões, LOD, exportação e Studio ficam nas tarefas próprias. Nenhuma substituição de modelos legados.

## Validação da fundação paramétrica

API Python e backend Blender real aprovados em 22/22 testes no CI 45442588521 (Blender 3.0.1). Ver [BIBLIOTECA_PARAMETRICA.md](BIBLIOTECA_PARAMETRICA.md) e [evidências](qa/parametric_foundation_evidence.json). Próxima tarefa estrutural: geometrias avançadas, extrusão, revolução, booleanas e bevels. Nenhuma migração de modelo aprovada.

## Operações geométricas avançadas

A extensão tools/asset_pipeline/parametric/advanced.py implementa perfis e triangulação determinística, extrusão e revolução. O backend Blender recebe CSG exato e bevel configurável. Consulte [BIBLIOTECA_PARAMETRICA.md](BIBLIOTECA_PARAMETRICA.md). Sem alterar catálogo histórico ou recursos de gameplay; validação CI ampliada.

## Curvas e superfícies

Biblioteca organic.py estende a IR com curvas cúbicas, patches bicúbicos, loft elíptico e topologia personalizada. Validação de fan de vértice e bordas complementa MeshSpec; normais, UV, rigging, export e homologação permanecem tarefas próprias. Ver [BIBLIOTECA_PARAMETRICA.md](BIBLIOTECA_PARAMETRICA.md).

## Atributos de renderização

RenderMesh preserva MeshSpec e mapeamento de vértices fonte; normais e UVs por canto são convertidos em buffers indexados com splits explícitos. Tangentes Python e backend opcional Blender MikkTSpace. A integração do RenderMesh ao exportador será realizada na tarefa de exportação; não editar manifesto de baseline. Ver [BIBLIOTECA_PARAMETRICA.md](BIBLIOTECA_PARAMETRICA.md).

## Biblioteca PBR

PBRMaterial, TextureData e MaterialLibrary em parametric/pbr.py definem fatores lineares, papéis de texturas sRGB/linear, ORM e normal +Y, procedência e hashes. Receitas procedurais neutras geram biblioteca independente da baseline. O futuro exportador resolve IDs da biblioteca e converte a convenção UV/normal de forma consistente. Não migrar nem aprovar assets existentes nesta etapa.

## Rig e encaixes

RigSpec, SkeletonSpec, BoneSpec, SkinSpec e SocketSpec adicionados em parametric/rig.py. Pivô é transformação local, socket tem frame próprio, bind de skin no frame do anchor. Pose e inversas de bind avaliadas em Python, verificação cruzada por armature Blender. Exportação, animações, IK e migração permanecem tarefas próprias. Ver [BIBLIOTECA_PARAMETRICA.md](BIBLIOTECA_PARAMETRICA.md).

## Colisões e LOD

AssetLOD e ColliderSpec em parametric/lod.py estabelecem contrato independente de colisão, níveis de detalhe com hierarquia e orçamento, resampling por receita e histerese. BUDGETS provisório: medir no hardware-alvo antes de homologar; mapas são particionados. Fixture Godot isolada valida troca de ArrayMesh sem trocar colisor. Integração runtime, exportação e Studio ainda pendentes.

## Exportação

Exportador paramétrico em exporter.py: GLB e glTF autocontido, rastreabilidade por export.json, preservação de atributos, PBR, rig e sockets. LOD e colisão permanecem metadados independentes, animação e integração runtime posteriores. Não editar manifesto histórico; catálogo vivo consumirá bundles validados.

## Catálogo vivo

O gerador tools/asset_pipeline/live_catalog.py descobre arquivos atuais e concilia referências e amostras reais do Godot. O manifesto histórico permanece imutável; o novo JSON é gerado no CI, não editado manualmente. Ver [CATALOGO_VIVO.md](CATALOGO_VIVO.md). A composição runtime ainda não é exportada como geometria para o Studio.

## Asset Studio inicial

Interface independente em tools/asset_studio, Three.js local e catálogo vivo gerado na preparação. Arquivos originais copiados byte a byte, conferência SHA-256 antes de carregar GLB. Sem composição simulada. QA Chromium/WebGL separado; iluminação avançada, controles de inspeção, composições runtime e homologação permanecem tarefas próprias. Ver [ASSET_STUDIO.md](ASSET_STUDIO.md).

Iluminação do Studio em lighting.js: HDRI sintético local RGBE com PMREM, ACES/sRGB, MSAA, PCFSoft e piso/grade independentes. O ambiente de inspeção não modifica assets e não reproduz a iluminação exata do Godot.

Navegação do Studio em camera-navigation.js: fit analítico por oito cantos AABB e aspecto, OrbitControls e reset sem inércia residual; escala e transformações do asset preservadas. QA real no navegador. Vistas ortográficas e runtime seguem etapas próprias.

Studio: seis OrthographicCamera por eixos canônicos mundiais, perspectiva, zoom/pan e fullscreen nativo. Piso oculto na vista inferior para não ocluir o asset. Não implica câmera real do Godot.

Capturas reais Godot em capture_views.gd, vinculadas à revisão por attach_runtime_views.py. Quatro imagens estáticas de inspeção, sem afirmar TPS nativo nem mapa 3D navegável; nenhuma reconstrução substituta. Ver ASSET_STUDIO.md.
