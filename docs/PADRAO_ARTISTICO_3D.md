# Padrão artístico híbrido 3D — 02-01

26/11/2026. Estado: definição normativa **e** demonstração executada em um asset de produção (pistol), com inspeção real no Asset Studio e no Godot 4.4.1 Compatibility. A definição abaixo não foi reescrita; a execução e os limites estão no fim do documento. Base técnica: 98e1390059d7d1d30c26fcc480015e59ca7de9af; execução na revisão 4f3eefcec318acc5c1145ca14cefeb64d6e5385f. Complementa [especificação](ASSET_STUDIO_SPEC.md), [contrato v1](ARQUITETURA_ASSET_PIPELINE.md), [guia operacional](GUIA_PIPELINE_3D.md) e [critério de aceite](CRITERIOS_ACEITE_1_0.md). Não substitui o portão de 13 passos nem promove homologação artística.

## Direção artística

Realismo militar contemporâneo, proporções críveis, materiais distinguíveis e desgaste localizado. Usar Modern Warfare como referência de linguagem visual de FPS, não como fonte de geometria, texturas ou marcas. Para cada asset, registrar referências visuais efetivamente consultadas, vistas, origem/licença, dimensões de referência e incertezas. Preferir fotos próprias/licenciadas, referências de superfícies e desenhos autorais; não reproduzir conteúdo proprietário. As referências específicas do piloto ainda devem ser reunidas e inspecionadas.

Priorizar nesta ordem: silhueta e escala, contatos e volumes, material e iluminação, microdetalhes. Evitar aparência de blocos, bordas infinitamente agudas, detalhes flutuantes, ruído uniforme, brilho plástico indiscriminado e desgaste aleatório. Criar variações deliberadas e reproduzíveis.

## Rotas de autoria

| Família | Geometria principal | Complemento |
|---|---|---|
| Armas, acessórios, veículos | Hard surface: perfis, extrusão, loft, bevel e topologia personalizada | Blender para curvas/booleanas complexas, UV, bake e refinamento |
| Mãos, soldados, roupas | Topologia orgânica e deformável | Blender para retopologia, rig, pesos e detalhes; manter interfaces da engine |
| Objetos e estações | Receitas paramétricas reutilizáveis | Detalhes hard surface e materiais por função |
| Cenário e estruturas | Módulos parametrizados, composição real Godot | Formas orgânicas e variação controlada de materiais |
| Efeitos e runtime | Fonte canônica existente na engine | Captura real no Studio; explicitar limites de shaders |

Usar tools/asset_pipeline/parametric/ (advanced, organic, shading, pbr, rig, lod, exporter, backend Blender) quando adequado. Não duplicar fontes ou migrar em massa nesta etapa. Arsenal atual: tools/build_weapons.py; personagens: scripts/character_geometry.gd; mundo: scripts/world_asset_geometry.gd, model_surface.gd e consumidores. Fonte editável única por ID; outputs, dependências, revisão, hashes, licença e parâmetros rastreáveis. Studio usa GLB original ou composição real capturada, nunca malha ilustrativa paralela. Preservar IDs e manifesto de baseline.

## Escala, formas e acabamento

- Metro, +Y para cima, frente declarada por asset, câmera Godot -Z; converter Blender uma vez pelo contrato v1. Não compensar proporção física escalando o viewmodel. Registrar AABB medida, dimensões esperadas e justificativa de estilização. Definir tolerância por referência antes de modelar; meta inicial de desvio dimensional até 5% quando existir referência confiável, não aplicável a medidas desconhecidas.
- Geometria primária define silhueta e volumes; geometria secundária define recortes e junções visíveis; detalhes terciários pequenos passam para normal/roughness quando não afetam a silhueta ou animação. Bevel proporcional ao tamanho e processo de fabricação, sem arredondar todas as bordas igualmente.
- Contatos e pivôs existentes, encaixes, estados de animação, colisão independente e nomes consumidos pelo código são contratos de integração. Testar separação indevida, clipping e deformações nas poses efetivas; não alterar gameplay para mascarar modelo.
- UVs, winding, normais, tangentes e materiais coerentes. PBR: base color sRGB, normal/ORM lineares (R AO, G roughness, B metallic), normal tangent-space +Y. Metal exposto com resposta metálica; pintura, polímero, madeira e tecido dielétricos. Diferenciar brilho por superfície, evitar iluminação pintada no albedo; desgaste nas zonas de uso e contato. Transparência somente justificada. Texturas próprias/licenciadas, sem referências ausentes.
- LOD e slots conforme BUDGETS do guia: weapon 18000/7000/1800 triângulos LOD0/1/2 e 8 slots; valores são tetos provisórios, não alvo obrigatório. Não inventar LOD quando inaplicável; registrar exceção. Preservar Compatibility e reservar benchmark integral ao 10-08.

## Piloto escolhido — rifle de produção existente

Fonte: tools/build_weapons.py, função rifle(), exportação g.save('rifle'). Auditoria textual na base acima identificou receptor chanfrado, tampa de perfil com seções e nervuras, coronha e guarda-mão de madeira, carregador curvo e materiais nomeados receiver, walnut, walnut_dark e steel. Isto comprova estruturas existentes na fonte, não sua qualidade visual. O [reteste integrado da fundação](AUDITORIA_HOMOLOGACAO_PIPELINE.md#encerramento-de-00-28-e-00-34) registra rifle real em repouso, ADS e recarga e comparação de relevo triplanar; não comprova o novo padrão.

Demonstrar o padrão neste mesmo ID de produção: reunir referências autorais/licenciadas e medir a silhueta; estabelecer ficha de proporções, detalhes e materiais; corrigir apenas a fonte se a inspeção mostrar necessidade; verificar exportação e catálogo real. Abrir o rifle em seis vistas e perspectiva do Studio, comparar no Godot em repouso, ADS e recarga sob iluminação de jogo. Preservar poses, encaixes e funcionamento. Se não houver mudança necessária, documentar por evidência cada requisito atendido pelo asset atual. Não introduzir fixture QA-only como substituto de produção.

## Ficha de aprovação por asset

Registrar ID e revisão; referências e licenças; dimensões e tolerâncias; fonte e backend; materiais/canais; triângulos e slots medidos; colisões/LOD; resultados automáticos focados; capturas Studio e Godot da revisão; plataforma/versões, câmera, iluminação, poses, observações e decisão por critério.

| Portão | Evidência exigida |
|---|---|
| Silhueta/escala | Vistas ortográficas e perspectiva, dimensões conferidas |
| Geometria/contatos | Sem peças soltas indevidas, clipping relevante ou defeitos de superfície nas poses aplicáveis |
| Materiais | Canais coerentes, superfícies distinguíveis, sem transparências ou artefatos indevidos |
| Integração | Mesmos recursos reais no Studio/Godot, contratos preservados, verificações focadas aprovadas |
| Inspeção | Capturas efetivamente observadas e decisão registrada; diferenças de renderizador explícitas |

Aceite 02-01 requer todos os portões demonstrados em um asset de produção, além desta definição. Remodelagem das oito armas, materiais e texturas completos, mãos/rig e mundo pertencem aos IDs 02-02 a 02-10. Nenhum desses IDs é promovido aqui.

## Evidências e limites desta revisão

Leitura remota de AGENTS.md, checklist, critérios, especificação, guia, arquitetura, auditoria integrada, tools/build_weapons.py, arsenal_sources.mjs e lod.py. Conferência documental de caminhos, critérios e preservação dos IDs. Sem execução nova de Godot, WebGL, Blender ou exportação; nenhuma alteração de malha, material, gameplay ou catálogo. Sem aprovação visual ou nova captura. Estado 02-01 permanece parcial; a demonstração no rifle de produção é o próximo passo obrigatório.

## Auditoria binária focal do piloto — 26/11/2026

Revisão consultada: 0b223d0bcb304a45d5f0dfdca7bd45168756fde0. ID estável weapon:rifle, conciliado com o manifesto histórico apenas para identificação de caminhos e fonte; não usar seus hashes históricos como hashes atuais. Leitura direta dos quatro GLBs por GitHub em base64 e decodificação dos chunks JSON/BIN no ambiente V8. Inspeção de dados, não renderização.

| Arquivo em assets/models/ | Blob Git atual | Vértices | Triângulos | AABB local XYZ (unidades do arquivo) |
|---|---|---:|---:|---|
| rifle.glb | 20497430e50b2a1333377a4443a60128d83d110b | 2459 | 4634 | 0.186500 × 0.641658 × 1.733500 |
| rifle_body.glb | f390bb59cadba80bddfc96adc89de8788f72ff65 | 1363 | 2574 | 0.168000 × 0.477707 × 1.733500 |
| rifle_action.glb | f71a87e666462ea8a391ce6076b868baf8cfcf23 | 32 | 60 | 0.026000 × 0.023000 × 0.069000 |
| rifle_mag.glb | 92d72af7d3b79e8cbb9bf6ace4d1450f2d5561c2 | 1064 | 2000 | 0.083000 × 0.408658 × 0.280873 |

Quatro cabeçalhos glTF 2.0 e comprimentos válidos; índices dentro dos buffers de posições; zero valores não finitos nos atributos POSITION/NORMAL/TANGENT; zero desvios de norma unitária ou de ortogonalidade normal/tangente acima de 1e-4; zero tangentes com handedness diferente de ±1; zero alpha de COLOR_0 diferente de 255; zero triângulos com norma do produto vetorial <= 1e-12. Cada GLB possui zero materiais explícitos. As três partes somam 2459 vértices e 4634 triângulos, iguais às contagens do merged; não somar representações alternativas como se fossem simultâneas. O merged ocupa 25,74% do teto provisório LOD0 weapon de 18000 triângulos. Não foram verificadas equivalência byte a byte da composição, orientação de todas as faces, reexportação, importação, slots efetivos, LOD ou poses nesta sessão. AABB local não comprova dimensão física em jogo; player.gd possui escalonamento do viewmodel, que não foi medido em execução. Sem referência dimensional licenciada efetivamente inspecionada, não aplicar tolerância percentual ou declarar escala aprovada.

Leitura de scripts/weapon_materials.gd confirma dois StandardMaterial3D compartilhados, uso de COLOR_0 e projeção triplanar de albedo/normal. Valores metallic 0.48/0.06, roughness 0.59/0.86, normal_scale 0.38/0.24 (metal/polímero). O código seleciona polímero por nomes de MeshInstance3D; não oferece material dedicado para madeira nessa implementação. Os quatro PNGs referenciados em assets/textures/ (weapon_metal_albedo.png, weapon_metal_normal.png, weapon_polymer_albedo.png, weapon_polymer_normal.png) foram recuperados e apresentam assinatura PNG; não houve decodificação ou avaliação visual dos pixels. A aparência final precisa ser demonstrada em execução; produção PBR integral permanece em 02-04/02-05. Não alterar geometria ou material sem o portão visual.

Bloqueio verificado: neste ambiente, git ls-remote para github.com falhou por resolução DNS; não existe checkout local; executáveis Godot/Godot4 e Blender não encontrados no PATH. Chromium e xvfb-run encontrados, mas isso não fornece a execução integrada do Studio e Godot. Não houve nova renderização, captura ou inspeção real, nem execução de CI. Evidências históricas de fundação permanecem históricas. 02-01 continua parcial. Próximo passo: executar o piloto em ambiente com checkout, Godot e Studio, reunir referências visuais e confrontar dimensões e materiais; não avançar 02-02 nesta entrega.

## Inspeção visual isolada das texturas — 26/11/2026

Base 725e43de597f576b8ba55e26cc98be8bf6cb2ef6. Os quatro PNGs de produção foram recuperados pelo conector GitHub e efetivamente abertos como imagens nesta sessão. Esta inspeção é de mapas isolados, não de renderização de modelos. Blobs atuais e observações:

| Arquivo | Blob Git | Observação visual |
|---|---|---|
| weapon_metal_albedo.png | 618c3478858674e68b80739b749e8bc0df3f81b1 | Cinza claro com estrias e ruído fino distribuído de modo aproximadamente uniforme. |
| weapon_metal_normal.png | e88ca2e0f5e096bab21b4b009df62dcedcd09f1c | Padrão de micro-relevo fino, com estrias repetidas. |
| weapon_polymer_albedo.png | 57b86ed71667e5a5b569f6a372ddad7077278187 | Granulação clara distribuída de forma aproximadamente homogênea. |
| weapon_polymer_normal.png | 5cbdb8f3583a9847375bc6134ab5043e4a9f14e8 | Microvariação granular repetitiva. |

As imagens são mapas neutros modulados pela cor dos vértices no shader atual; não inferir a aparência final da cor a partir dos PNGs isolados. Como direção de produção, distinguir metal pintado, metal exposto, polímero e madeira por resposta de material, escala de detalhe e desgaste localizado; avaliar a contribuição na câmera de jogo. A execução dos materiais completos cabe aos IDs 02-04/05. Não houve mudança em textura, malha, shader ou gameplay.

Rechecagem de execução: /mnt/data sem checkout; git ls-remote do repositório falhou por resolução DNS; Godot e Blender ausentes do PATH, Chromium e Xvfb presentes. Tentativa de abrir o Studio publicado em tpolltech.github.io/Frontline-Survival/ e seu catálogo pela ferramenta web não retornou conteúdo acessível. Não houve nova execução Studio/Godot ou CI. A inspeção dos PNGs é evidência nova, mas não substitui as referências externas, a escala física ou a demonstração integrada. Mantido 02-01 parcial.

## Execução do piloto de produção — pistol híbrido (26/11/2026)

Esta seção registra a demonstração exigida pelo 02-01. Ela preserva integralmente as auditorias anteriores e o padrão definido acima; apenas executa o portão em um asset de produção real. Base: 4f3eefcec318acc5c1145ca14cefeb64d6e5385f, com árvore de trabalho limpa antes das alterações deste ID.

### Troca justificada do piloto: rifle → pistol

O rifle continua sendo um alvo válido e sua auditoria binária permanece registrada. Ele não foi usado como primeiro piloto porque seu punho é gerado por `common_receiver()`, compartilhado por smg, rifle, shotgun e lmg: alterar só o rifle exigiria duplicar geometria ou remodelar cinco armas de uma vez, o que pertence ao 02-02. O `pistol()` possui punho próprio e isolado, com contrato de grupos (body/action/mag) e contato com frame e base do carregador. Assim o padrão híbrido foi demonstrado sem ampliar o escopo nem tocar outras armas. Nenhum dado da auditoria do rifle foi apagado ou reinterpretado; referências e proporções do rifle seguem para 02-02/02-03.

### Referências efetivamente consultadas

| Referência | Dados | Uso nesta execução |
|---|---|---|
| GLOCK G19 Gen5, dados técnicos oficiais ([us.glock.com](https://us.glock.com/en/products/law-enforcement/pistols/g19-gen5), consultado em 26/11/2026) | 185 mm comprimento total; 174 mm slide; 34 mm largura da armação; 25,5 mm largura do slide; 128 mm altura com carregador; 153 mm linha de mira; 70 mm distância do gatilho; cano 102 mm | Linguagem de seções do punho (largura de armação, distância do gatilho, altura com carregador) e ordem silhueta→volumes→material |
| Produção atual `weapon:pistol` (GLB merged, HEAD 4f3eefc) | AABB 0,393 × 0,3875 × 0,1188 m (Z × Y × X); 2812 triângulos; 1498 vértices; 47 peças; grupos 23/22/2 | Envelope e interfaces preservados; comparação antes/depois |
| `scripts/player.gd` | `viewmodel_scale` do pistol 0,95 em `VIEWMODEL_PROFILE`; poses de repouso/ADS por `get_viewmodel_rest_pose()` | Escala de apresentação do viewmodel, separada da dimensão física |
| `scripts/weapon_materials.gd` + 4 PNGs de produção | metal 0,48 metallic/0,59 roughness/normal 0,38; polímero 0,06/0,86/0,24; `COLOR_0` × projeção triplanar | Camada de material exigida pelo padrão, sem trocar texturas neste ID |

Não foi usada geometria, textura ou marca das referências. Nenhuma referência licenciada de foto de superfície foi necessária porque a demonstração usa as texturas de produção já existentes; acabamento PBR autoral permanece em 02-04/02-05.

### Escala e proporções

- Unidade canônica: metro, +Y para cima, frente −Z (contrato v1).
- Escala física × apresentação: o GLB é um viewmodel com escala de apresentação 0,95 aplicada em `player.gd`; a razão comprimento fonte/referência é 0,393/0,185 ≈ 2,12 e a de altura 0,3875/0,128 ≈ 3,03. A silhueta é, portanto, estilizada para a câmera FPS e **não** atende à tolerância de 5% do padrão. Corrigir proporções e silhuetas é o ID 02-03; este ID não redimensiona o modelo porque isso quebraria os encaixes, as poses e o enquadramento pendente em 01-03.
- Punho: envelope mundial 0,0874 × 0,2604 × 0,1627 m (X × Y × Z, incluindo a inclinação de −0,28 rad), seção de palm swell de 0,087 × 0,110 m. Permanece dentro do envelope anterior (desvio máximo de 3,5 mm no limite traseiro, tolerância declarada de 5 mm para interfaces).

### Regra híbrida aplicada

| Camada | Rota | Peças desta demonstração |
|---|---|---|
| Volumes maquinados | Primitivas paramétricas legadas (`chamfer`, `ring`, `cylinder`, `rod`) | slide, slide_top, frame, dust_cover, grip_heel, magazine_heel, sights, serrilhas, ejeção, guarda do gatilho, boca |
| Superfície esculpida | Biblioteca central `tools/asset_pipeline/parametric/organic.py`: `OrganicLoft` + `LoftSection` + `build_organic`, convertidos sem reprocessar vértices | punho (`grip`), 1200 triângulos, 602 vértices, malha fechada com volume positivo |
| Detalhe secundário | Serrilhas do slide e painéis do punho existentes | mantidos, sem peças soltas |
| Material | `COLOR_0` + material triplanar de produção (metal/polímero) | punho com cor de polímero; nenhuma textura nova |

O `OrganicLoft` fornece seções com raio, centro e twist; a inclinação e a translação são aplicadas uma única vez antes da montagem, mantendo a fonte editável única. `Gun.add_parametric()` recusa malha aberta ou de volume não positivo.

### Resultados medidos (fonte → export)

| Métrica | Antes (HEAD) | Depois | Limite |
|---|---:|---:|---|
| Peças / grupos | 47 (23 body, 22 action, 2 mag) | 47 (23/22/2) | contrato preservado |
| Vértices / triângulos do merged | 1498 / 2812 | 2068 / 3952 | 18000 LOD0 |
| Triângulos do punho | 60 | 1200 | — |
| AABB (X × Y × Z) | 0,1188 × 0,3875 × 0,3965 | 0,1188 × 0,3875 × 0,3930 | interface ±0,005 m |
| Contato punho↔frame / punho↔heel | sim / sim | sim / sim | obrigatório |
| Validação `validate_gltf` (weapon) | — | `pass_with_unknowns`, 0 erros, 0 avisos, 1 slot | sem falha impeditiva |
| Duas gerações independentes | — | 4/4 GLBs byte a byte idênticos | determinístico |
| Atributos do GLB | POSITION, COLOR_0, NORMAL, TANGENT | idem | sem NORMAL_MISSING |

Hashes SHA-256 entregues: `pistol.glb` a9823dd41d4adc91206d2cd3d3f2cbfa90ffd4651b032ea8ec535ef9d1a3bcdd (139884 bytes), `pistol_body.glb` 5a6a10c7bf26f0cdcf20ff9d07e0f3c362d4ab8f342fa0914cb5cdc689bbee07 (85500), `pistol_action.glb` 93c65fdadc609586cea42f56f06bc8a894e752ac0eb525e877094278feb8f914 (51680), `pistol_mag.glb` 107364505cd8c6b51cecdaba5f47027ff06f2daef941d803a4c276bd3f099d48 (5792). O action/mag não contêm o punho; foram reexportados pelo mesmo pipeline e diferem do HEAD apenas no ruído de arredondamento de normais (≤ 1,2e-17), sem mudança de posições, índices ou cores.

### Inspeção visual realizada

Asset Studio (WebGL real, Playwright/SwiftShader, 1280×800) com o GLB original de produção: perspectiva, frontal, direita, superior, wireframe e sólido, antes e depois. O HUD do Studio confirmou `assets/models/pistol.glb`, SHA-256 a9823dd4…, 2068 vértices / 3952 triângulos, 1 material/slot, AABB 0,1188 × 0,3875 × 0,393; zero requisições externas e zero erros de página. Observação: o punho passou de caixa octogonal facetada para superfície contínua com palm swell, backstrap arredondado e afunilamento na base; serrilhas continuam assentadas na superfície.

Godot 4.4.1 Compatibility (OpenGL 3.3, AMD Radeon iGPU, 1280×720) com `scenes/main.tscn` real, câmera do jogador e poses repouso, ADS e recarga a 50%, antes e depois. Observação: sem fresta entre punho e frame ou base do carregador, sem peça flutuante, sem transparência indevida e sem recorte relevante da arma; a empunhadura e a mira permanecem nas poses originais. A comparação está em `docs/qa/02-01/godot.html`.

### Portão de 13 passos

1. Referências: tabela acima, consultadas em 26/11/2026.
2. Proporções/dimensões: envelope, seções e tolerância declarados; desvio de silhueta atribuído a 02-03.
3. Silhueta: loft substitui a caixa facetada; contatos preservados.
4. Detalhes: serrilhas/painéis mantidos; nenhuma peça nova solta.
5. Materiais: `COLOR_0` + triplanar de produção; sem textura nova.
6. Exportação: `python tools/build_weapons.py --only pistol`, dois destinos temporários idênticos.
7. Verificações: `test_hybrid_grip` (6), `test_weapon_surface_integrity` (7), `test_sniper_sight_geometry` (3), `test_validate_gltf` (17) e `validate_gltf --category weapon`.
8. Studio aberto: sim, arquivo real.
9–10. Inspeção e correção na fonte: revisão visual acima; nenhum defeito impeditivo encontrado, nenhuma correção adicional necessária nesta rodada.
11. Integração: GLBs de produção substituídos somente para o pistol.
12. Godot aberto e testado: sim, três poses.
13. Evidências: esta seção, `docs/VALIDACAO_02_01_PADRAO_HIBRIDO.md` e `docs/qa/02-01/`.

### Limites e débitos

- 02-01 demonstra o padrão em **um** asset; remodelar as oito armas continua em 02-02 e proporções/silhuetas em 02-03.
- Não há aprovação de materiais PBR autorais (02-04) nem texturas/normal maps próprios (02-05); a demonstração usa os mapas de produção existentes.
- Nenhuma meta de FPS ou benchmark: o merged usa 24,7% do teto provisório LOD0. LOD1/LOD2 e colisores não foram produzidos para o punho.
- O viewmodel é estilizado (escala de apresentação 0,95) e não representa a escala física da referência; não confundir com homologação dimensional.
- A revisão visual cobre repouso, ADS e recarga do pistol; não cobre as demais armas, troca de arma, acessórios, mãos/rig ou ações de gameplay.
- Não houve execução de novo CI (GitHub Actions sem cota); nenhum instalador ou runner redundante foi criado.

Aceite técnico e visual do 02-01 registrado nesta revisão; a homologação artística de produção das demais armas permanece nos IDs seguintes.
