# Padrão artístico híbrido 3D — 02-01

26/11/2026. Estado: definição documental, demonstração de produção pendente. Base técnica: 98e1390059d7d1d30c26fcc480015e59ca7de9af. Complementa [especificação](ASSET_STUDIO_SPEC.md), [contrato v1](ARQUITETURA_ASSET_PIPELINE.md), [guia operacional](GUIA_PIPELINE_3D.md) e [critério de aceite](CRITERIOS_ACEITE_1_0.md). Não substitui o portão de 13 passos nem promove homologação artística.

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
