# Frontline Survival — Checklist mestre até a versão 1.0

Atualizado em 24/11/2026. Mantém as 96 tarefas anteriores e adiciona a fundação de modelagem/Studio e a regressão de QA. Fonte de requisitos: [especificação obrigatória](ASSET_STUDIO_SPEC.md). Estado verificado: main v0.9.34 de desenvolvimento; última release v0.9.31; [CI do arsenal corrigido e aprovado](https://github.com/TPollTech/Frontline-Survival/actions/runs/45504785421) na revisão 446f31eb. Nova revisão de assets posterior em revalidação. Priorizar 00. Estados: [ ] pendente/parcial; [x] somente tarefa integralmente validada. Os trabalhos anteriores não são descartados; reavaliar na arquitetura nova. Nenhuma homologação visual manual foi confirmada nesta revisão.

### Continuidade e execução individual

O checklist é a fonte oficial dos estados e das evidências. Os IDs seguem a etapa e a posição já atribuída nesta revisão, de `00-01` a `10-11` por etapa. Preserve o vínculo entre ID e tarefa. Para novas tarefas autorizadas, atribua o próximo ID livre na etapa. Exclusão, renumeração ou reorganização requer autorização.

Em cada conversa, consulte a main e reconstrua o painel completo a partir deste documento. A porcentagem oficial usa apenas tarefas concluídas. A ação de uma linha solicita a execução exclusiva daquele ID ou a revalidação, caso esteja concluído. Inclua estado anterior, justificativa, evidências, dependências, documentação e commit de referência no comando.

Antes de alterar o projeto, siga AGENTS.md, confira critérios de aceite e integre a main atual. Registre os testes executados, resultados, limitações e bloqueios. Mantenha em parcial o que ainda requer implementação, validação ou homologação. Atualize apenas os estados sustentados por evidência e verifique o commit remoto. Enquanto o GitHub Actions estiver sem cota, use testes locais e `[skip ci]`. Após cada execução, reenvie o painel integral com todos os IDs e a próxima tarefa recomendada.

### Critérios revisados em 25/11/2026

A matriz normativa [Critérios de aceite 1.0](CRITERIOS_ACEITE_1_0.md) define o aceite verificável de cada um dos 131 IDs, separando fundação operacional (00), correções urgentes (01), produção artística (02), gameplay (03–09) e otimização/lançamento (10). As linhas abaixo preservam evidências e estados históricos literalmente; seus relatos de lacunas não são novos critérios nem transferem aprovação. Quando um relato histórico exigir acabamento de produção ou benchmark final para a fundação, aplicar a matriz: o requisito permanece no ID posterior indicado. Nenhuma tarefa promovida nesta revisão. Priorizar 00-13, 00-17 a 00-21, 00-24/25/27, 00-28 a 00-32 e 00-10, por fim 00-34. O QA Universal é auxiliar opcional. O painel completo deve exibir a matriz por ID e preservar o bloqueio até 34/34.

## 00 — Fundação do sistema 3D e Asset Studio

- [x] Auditar SNC Energies e SNC Adventures e arquitetura atual do Frontline Survival — Auditoria estática concluída e evidências em [AUDITORIA_ARQUITETURA_3D.md](AUDITORIA_ARQUITETURA_3D.md); não equivale a aprovação visual.
- [x] Inventariar todos os assets, fontes, dependências e cenas existentes — Baseline existente inventariada e conciliada: 60/60 recursos, 32/32 GLBs, 24/24 famílias por amostra/consulta, 86 amostras e revisão de quatro screenshots. [Evidências e lacunas](INVENTARIO_RUNTIME.md). Não equivale a homologação dos modelos.
- [x] Definir arquitetura modular, manifesto canônico e convenções de escala e eixos — Contrato v1 implementado e validado com baseline; [arquitetura](ARQUITETURA_ASSET_PIPELINE.md). Motor, catálogo vivo e captura runtime ainda pendentes.
- [x] Implementar biblioteca paramétrica Python e backend Blender quando necessário — API, IR e backends validados: 22/22 testes, incluindo Blender 3.0.1 real, no [CI 45442588521](https://github.com/TPollTech/Frontline-Survival/actions/runs/45442588521). [Biblioteca](BIBLIOTECA_PARAMETRICA.md). Sem homologação de modelos.
- [x] Implementar geometrias avançadas, extrusão, revolução, booleanas e bevels — 45/45 testes Blender real aprovados no [CI 45453292708](https://github.com/TPollTech/Frontline-Survival/actions/runs/45453292708). [Biblioteca](BIBLIOTECA_PARAMETRICA.md). Sem homologação de modelos.
- [x] Implementar curvas, superfícies orgânicas e topologia personalizada — 59/59 testes aprovados com Blender real no [CI 45454861861](https://github.com/TPollTech/Frontline-Survival/actions/runs/45454861861). Sem homologação de modelos.
- [x] Implementar normais suavizadas e ponderadas, UV mapping e tangentes — 71/71 testes com Blender real no [CI 45456153062](https://github.com/TPollTech/Frontline-Survival/actions/runs/45456153062). Sem homologação de modelos.
- [x] Implementar materiais PBR, texturas e biblioteca de materiais — PBR validado no [CI 45459161051](https://github.com/TPollTech/Frontline-Survival/actions/runs/45459161051), 96/96 testes incluindo 18 texturas e seis materiais. Sem homologação visual.
- [x] Implementar hierarquias, pivôs, encaixes, rigging e skeleton — 96/96 testes no [CI 45459161051](https://github.com/TPollTech/Frontline-Survival/actions/runs/45459161051), armature e skinning Blender aprovados. Sem homologação visual.
- [x] Implementar colisões independentes e LOD com orçamentos por categoria — Fundação validada: 207 transições/raios, 24 contatos, 441 quadros e 84 trocas registradas em movimento. Cinco famílias com LOD explícito, demais peças estáticas auditadas por LOD nativo ou geometria mínima. Revisão representativa e exclusões documentadas. [Evidências](LOD_COLISOES_RUNTIME.md).
- [x] Implementar exportação determinística GLB/glTF 2.0 e rastreabilidade de fontes — Fundação validada: 117/117 testes Blender/Python, manifesto de fontes canônico, reprodução byte a byte e importação de ambos os formatos no [Godot CI 45501055855](https://github.com/TPollTech/Frontline-Survival/actions/runs/45501055855). Dois joints autorais e helper sem peso conferidos. Sem homologação de assets de produção. [Biblioteca](BIBLIOTECA_PARAMETRICA.md).
- [x] Implementar descoberta automática e catálogo de todos os assets reais — Concluída no escopo de descoberta/catalogação da versão atual: 52 registros, 100 recursos, 24/24 famílias, 86 composições, 167 buffers reais com SHA-256 verificado, 48 candidatos de quatro expressões dinâmicas (44 existentes e quatro opcionais ausentes), 32/32 GLBs, zero lacunas de referências literais/runtime; quatro assemblies com três LODs registrados. CIs 45535740278 e 45535950057 aprovados, artefatos inspecionados. Renderização integral das composições e publicação final são etapas distintas; sem homologação visual. [Catálogo](CATALOGO_VIVO.md).
- [x] Criar Asset Studio HTML/CSS/JS com Three.js e WebGL — Aceite técnico local concluído na revisão 0cb6667. No Firefox/WebGL, pesquisa e seleção funcionaram, 32 GLBs foram carregados, 86 composições reconciliadas e seis renderizadas para conferência. Os 100 recursos passaram na validação SHA-256. Comparação do mapa na câmera Godot: 12 pontos e erro máximo de 0,00003791 px. ZIP atual testado após extração, sem rede externa. [Evidências e limites](ASSET_STUDIO.md).
- [x] Implementar iluminação HDRI, sombras, antialiasing, sRGB, ACES e piso técnico — 32/32 GLBs e controles aprovados no [CI 45473901798](https://github.com/TPollTech/Frontline-Survival/actions/runs/45473901798), duas capturas reais inspecionadas. Sem homologação de modelos ou benchmark.
- [x] Implementar OrbitControls, damping, enquadramento por bounding box, zoom, pan e reset — 32/32 GLBs, interação, resize e reset aprovados no CI 45475002613; capturas inspecionadas.
- [x] Implementar seis vistas ortográficas, perspectiva e tela cheia — seis eixos, fullscreen e retorno aprovados no CI 45475002613; capturas inspecionadas.
- [x] Implementar vistas reais de primeira e terceira pessoa e prévia de mapas completos — Aceite técnico: FPS nativo e TPS de inspeção da instância real do jogador, com corpo piloto skinned anexado durante a captura. Seis vistas Godot e mapa completo interativo verificados no Firefox. [Evidências](ASSET_STUDIO.md).
- [x] Implementar inspeção de materiais, texturas, UVs, wireframe, sólido e texturizado — Firefox/WebGL: inspeção no GLB Quaternius e na composição Campo de Testes, incluindo canal de textura real do mapa e comunicação dos canais ausentes. [Evidências](ASSET_STUDIO.md).
- [x] Implementar visualização de normais, pivôs, colisões e LOD — Aceite técnico: normais/pivôs verificados, shapes ativas reconstruídas das dimensões e transforms capturados, e seletor WebGL de LOD explícito validado com os buffers reais. [Evidências](ASSET_STUDIO.md).
- [x] Implementar métricas de vértices, triângulos, materiais e dimensões reais — 32 GLBs conciliados nas verificações anteriores. Na composição real do mapa, 90.434 vértices, 139.710 triângulos, 68 configurações de material, 239 slots e AABB 53 × 5,735 × 53 m conciliados com Godot. [Evidências](ASSET_STUDIO.md).
- [x] Implementar animações, componentes articulados e controle de poses — Aceite técnico: dois clipes autorais de inspeção, no osso do piloto Quaternius e no cotovelo da composição runtime do aliado, com avanço, reprodução e reset verificados em WebGL. [Evidências](ASSET_STUDIO.md).
- [x] Implementar screenshots e versão offline sem CDN — PNG, ZIP de 10.563.017 bytes, servidor local e execução extraída com conexões externas bloqueadas aprovados no [CI 45502974998](https://github.com/TPollTech/Frontline-Survival/actions/runs/45502974998). Fundação funcional, sem homologação visual de modelos.
- [x] Implementar validação de geometria, normais, UVs, texturas e materiais — Fundação técnica validada: 17 testes, 32 GLBs, índices, atributos, degeneração, orientação das normais, PBR, UV e referências de imagens. CI 45511716190 identificou 31 avisos NORMAL_MISSING; legado não homologado. Extensões/sparse, decodificação completa e composições não cobertas. [Validação](VALIDACAO_ASSETS.md).
- [x] Implementar validação de escala, orientação, pivôs, hierarquias e referências — 13 categorias verificadas em export estrito, Godot e Studio; 39 GLBs e casos negativos automatizados. Preservação de caminho e bytes retestada no Linux. [Evidências](PILOTOS_ASSETS.md#reteste-integrado-da-fundação).
- [x] Implementar validação de exportação, orçamento de polígonos e importação no Godot — 39 GLBs e 39 glTFs estritos gerados duas vezes, orçamentos provisórios conferidos e 39 GLBs importados no Godot Compatibility. Medição representativa anterior no Ryzen 7520U preservada. [Evidências](PILOTOS_ASSETS.md#reteste-integrado-da-fundação).
- [x] Integrar validação, geração reproduzível e evidências ao CI — Workflow asset-validation.yml validado no CI 45511716190: 17 testes, duas exportações estritas reproduzíveis, auditoria e relatórios determinísticos, importação Godot e reconciliação SHA-256/triângulos 32/32, zero falhas impeditivas. Artefatos publicados; sem homologação visual. [Validação](VALIDACAO_ASSETS.md).
- [x] Validar um asset piloto de cada categoria no Studio e no jogo — 13/13 categorias geométricas, com 39 GLBs conciliados no Godot e Studio e inspeção LOD0 em ambas as plataformas. Categorias não geométricas verificadas pelo inventário. [Evidências](PILOTOS_ASSETS.md#reteste-integrado-da-fundação).
- [x] Migrar todo o arsenal e acessórios para fontes canônicas — O export canônico agora inclui normais e tangentes nos 31 GLBs. Duas gerações byte a byte e importação Godot verificadas. O Studio reproduz a projeção triplanar local. O efeito do normal map foi verificado com comparação ligado/desligado nos dois renderizadores. [Reteste](AUDITORIA_HOMOLOGACAO_PIPELINE.md#reteste-integrado-de-26112026).
- [x] Migrar personagens, mãos, equipamentos e aliados/inimigos — Poses do Godot capturadas e reproduzidas no Studio em três superfícies skinned do Quaternius. [Reteste](AUDITORIA_HOMOLOGACAO_PIPELINE.md#reteste-integrado-de-26112026).
- [x] Migrar objetos, estações, veículos, estruturas e elementos ambientais — Contratos 13/13 em Godot headless, inventário e composição de mapa/objetos conferidos no Studio, cobertura de colisão existente e veículo QA-only verificados. O aviso de encerramento da sonda isolada GLES3 permanece registrado. [Evidências](PILOTOS_ASSETS.md#reteste-integrado-da-fundação).
- [x] Migrar terreno, arquitetura, mapas completos e cenas compostas — Campo de Testes aberto no Godot e Studio. Layout 49/49, 543 nós, 234 superfícies visíveis e 12 pontos da câmera conciliados. [Reteste](AUDITORIA_HOMOLOGACAO_PIPELINE.md#reteste-integrado-de-26112026).
- [x] Migrar objetos procedurais em runtime, colisões e efeitos 3D para o catálogo — Godot e WebGL reconciliaram 86 amostras, 188 escopos, 13 papéis e dez famílias. Seis composições de efeitos foram abertas no Studio. [Reteste](AUDITORIA_HOMOLOGACAO_PIPELINE.md#reteste-integrado-de-26112026).
- [x] Documentar arquitetura, comandos, extensão de categorias e política de QA — Concluída no escopo documental (25/11): [guia operacional](GUIA_PIPELINE_3D.md), arquitetura real, 13 orçamentos extraídos da fonte, extensão, comandos locais isolados e QA. Verificações estáticas dos contratos e referências; execução integrada e homologação permanecem nas tarefas próprias.
- [x] Auditar cobertura integral do Studio e homologar o pipeline no jogo — 33/33 predecessores aceitos. Reteste integrado com Godot e Firefox conciliou 86 amostras e 32 GLBs, com inspeção representativa de mapa, personagem e rifle. [Reteste](AUDITORIA_HOMOLOGACAO_PIPELINE.md#reteste-integrado-de-26112026).

## 01 — Correções urgentes

- [ ] Corrigir as iron sights flutuantes das snipers — Código e CI da v0.9.28 aprovados; revisão visual manual pendente. Validação 26/11: 6/6 GLBs com geometria/hierarquia preservadas frente a 95c7ac8; 15/15 contatos positivos dos suportes; seis poses históricas Godot com corpo fixo e carregador móvel na recarga. Falta inspeção visual atual e recarga completa em execução; engine indisponível. [Evidências](VALIDACAO_01_01_SNIPERS.md).
- [ ] Restaurar e validar o ajuste de FOV — Código e release v0.9.29 publicados; revalidar na main atual. Validação 26/11: 7/7 blobs de configuração/câmera/teste idênticos à captura Windows 95c7ac8; 57/57 estados de FOV padrão conciliados (24 hip, 25 ADS, 8 recarga). Limites 60–100 e persistência confirmados apenas no código; falta executar teste existente e inspeção em gameplay, incluindo persistência real. Godot indisponível. [Evidências](VALIDACAO_01_02_FOV.md).
- [ ] Padronizar o enquadramento de todas as armas — Código e release v0.9.30 publicados; revisão visual manual pendente. Validação 26/11: projeção dos vértices de 24 poses históricas reais (8 armas x 3 estados, 1280x720), 24/24 sem corte near plane; 23/24 com recorte de viewport que exige avaliação visual, não defeito automaticamente. Duas imagens históricas inspecionadas. Faltam 24 vistas atuais e recarga em execução; Godot indisponível. [Evidências](VALIDACAO_01_03_ENQUADRAMENTO.md).
- [ ] Separar o FOV da câmera do enquadramento das armas — Código e release v0.9.31 publicados; revisão visual manual pendente. Validação 26/11: 513 combinações matemáticas sobre 57 poses históricas reais, 225 ADS, 2.481.009 instâncias projetadas; erro máximo dentro da tela 0,000027 px e profundidade invariável ao variar FOV do cenário. Falta executar teste existente e inspeção visual atual, inclusive ADS; Godot indisponível. [Evidências](VALIDACAO_01_04_FOV_INDEPENDENTE.md).
- [ ] Corrigir alinhamento das miras e lunetas — Código v0.9.32 na main; CI cancelado ou bloqueado pela falha posterior; validação pendente. Validação 26/11: 25/25 combinações históricas em ADS conciliadas (17 emissores com desvio zero, oito marcadores originais com desvio <0,00005 px); 125 superfícies opacas de acessórios sem interseção central antes do emissor. Uma imagem histórica do rifle inspecionada. Faltam teste existente e inspeção das 25 combinações atuais, incluindo overlay; Godot indisponível. [Evidências](VALIDACAO_01_05_MIRAS.md).
- [ ] Eliminar peças flutuantes, transparentes ou sobrepostas — Código v0.9.33 na main; CI cancelado ou bloqueado; validação pendente. Validação 26/11: 8/8 GLBs completos atuais, 10.601 vértices e 19.954 triângulos sem alpha indevido, índices inválidos, degeneração ou duplicatas exatas; 164 superfícies históricas opacas em 57 poses, sem triângulos coincidentes entre grupos. Três imagens históricas inspecionadas. Comparação integral das 23 partes atuais interrompida pelo limite de chamadas; falta inspeção visual atual e animações no Godot. [Evidências](VALIDACAO_01_06_INTEGRIDADE_VISUAL.md).
- [x] Testar individualmente todas as armas — QA automatizado 8/8 armas no CI 45504785421 (249 verificações individuais), revisão 446f31eb. Nova revisão dos modelos em validação; não equivale à homologação visual.
- [x] Corrigir falha do QA individual do arsenal na v0.9.34 — Carregamento diferido do jogador após GameSettings e referência relativa corrigidos. CI 45504785421 aprovado integralmente, QA_ARSENAL_PASS. Nova revisão dos modelos em validação.

## 02 — Modelagem 3D

- [x] Desenvolver um padrão híbrido de modelagem 3D — Concluída 26/11: [padrão artístico híbrido](PADRAO_ARTISTICO_3D.md) definido (referências GLOCK G19, escala, silhueta, detalhes, materiais, portões) e demonstrado no asset de produção `weapon:pistol`. Fonte canônica `tools/build_weapons.py`: punho esculpido por `OrganicLoft` da biblioteca central somado às peças maquinadas originais; 47 peças, grupos 23/22/2, contatos frame/heel preservados, 3952 triângulos (22% do teto), AABB 0,1188 × 0,3875 × 0,393 m, duas gerações byte a byte idênticas, `validate_gltf` sem erros/avisos e NORMAL/TANGENT presentes. Inspeção real no Asset Studio (6 vistas, hash a9823dd4…, zero rede externa) e no Godot 4.4.1 Compatibility (repouso, ADS e recarga, AMD Radeon iGPU, 1280×720) sem peças soltas, frestas ou recorte relevante. Proporções estilizadas, materiais/texturas autorais e as demais armas permanecem em 02-02 a 02-05. [Relatório e evidências](VALIDACAO_02_01_PADRAO_HIBRIDO.md), [capturas](qa/02-01/comparativa.html). ZIP Windows bloqueado por templates ausentes; CI sem cota.
- [x] Remodelar completamente o arsenal — Concluída 26/11: as oito armas de produção foram remodeladas na fonte canônica `tools/build_weapons.py` com a regra híbrida de 02-01 (peças maquinadas paramétricas + superfícies esculpidas por `OrganicLoft` da biblioteca central). Punhos, coronhas, pump e guarda-mão inferior das oito armas passaram a loft; a biblioteca ganhou `section_power` (superelipse) para seção de retângulo arredondado, com elipse histórica preservada. Contratos mantidos: nomes de peça, grupos body/mag/action, pivôs, estados e envelope externo (desvio máximo 1,1 mm; AABB e teto fixados em `tests/test_hybrid_arsenal.py`). Contrato de 31 variantes mantido (a escopeta continua sem `shotgun_mag.glb`; a entrada histórica do manifesto segue sem arquivo). 31 GLBs regenerados de forma determinística (três builds byte a byte idênticos e iguais à árvore), `validate_gltf` 31/31 sem erros/avisos, `live_catalog` PASS (52 assets, 8 armas), maior arma com 6 914 triângulos (38,4% do teto de 18 000). Inspeção real no Asset Studio WebGL (8 × 6 vistas + zoom 3×, zero rede externa/erros; dois defeitos de envelope e o efeito tubo foram encontrados e corrigidos na fonte antes da entrega) e no Godot 4.7.2 Compatibility (24 poses reais: repouso, ADS e recarga, AMD Radeon iGPU, 1280×720) sem peças soltas, frestas ou transparências. Evidências: [relatório](VALIDACAO_02_02_ARSENAL_HIBRIDO.md), [capturas](qa/02-02/arsenal.html). Proporções (02-03), PBR/texturas (02-04/02-05) e mãos/encaixe (02-06/02-08) permanecem abertos; ZIP Windows bloqueado por templates ausentes; sem benchmark (10-08).
- [ ] Melhorar proporções e silhuetas das armas — Parcial (26/11): contornos autorais refinados nas oito famílias e 31 variantes regeneradas. Envelopes preservados, comparação real no Studio e 24 poses por revisão no Godot. A divergência dimensional da pistola e as referências dimensionais das demais famílias seguem abertas. [Evidências](VALIDACAO_02_03_SILHUETAS.md). Conciliação adicional: 31/31 GLBs atuais preservam exatamente os triângulos orientados e contagens de vértices da revisão de contornos 3461e5b após a integração PBR; nenhuma alteração geométrica nova ou homologação dimensional nesta execução. Comparação externa de comprimento das oito famílias já registrada no relatório (8ce71a5); não equivale ao aceite dimensional. Conciliação preservada até d8fed23: diff desde ec99f6f sem alterações nos GLBs ou fonte tools/build_weapons.py. player.gd mudou com 02-06, portanto as capturas históricas não homologam o conjunto FPS atual. Correções dimensionais e inspeção integrada continuam pendentes.
- [x] Implementar materiais PBR realistas — Seis perfis aplicados por superfície, 31 GLBs reproduzíveis e oito armas inspecionadas no Studio e Godot. Perfis efetivos verificados no jogador, inimigo, aliado e pickup. [Evidências](VALIDACAO_02_04_MATERIAIS_PBR.md).
- [x] Implementar texturas e normal maps — 18 mapas autorais em seis perfis, madeira refinada e projeção triplanar no Godot e no Studio. Tangentes e canais ORM verificados com inspeção das oito armas. [Evidências](VALIDACAO_02_05_TEXTURAS.md).
- [ ] Remodelar mãos, dedos, luvas e antebraços — Parcial (26/11): [diagnóstico de produção](VALIDACAO_02_06_MAOS.md); fontes runtime e capturas históricas inspecionadas, três blobs de geometria conciliados entre 02-03/02-04 e main; 5/5 reconstruções numéricas da topologia das mangas sem degeneração e com bordas fechadas. Identificadas cápsulas dos dedos, palma simplificada e ausência de UV/tangentes das mangas. Remodelagem e inspeção FPS após alteração pendentes; nenhuma geometria nova publicada. Segunda execução: receitas orgânicas candidatas de palma espelhada, painel dorsal, segmentos dos cinco dedos e mangas implementadas em fps_hand_geometry.py; 6/6 testes locais, 15/15 peças de referência fechadas e orientadas, 3960 triângulos por braço de referência. Inspeção isolada, sem integração runtime, deformação ou FPS; continua parcial. Terceira execução: Receitas orgânicas integradas ao viewmodel FPS com pivôs e animações preservados. Seis testes passaram e 18 poses foram renderizadas e revisadas no Godot 4.7.2 em Windows. A oclusão dos dedos limita a revisão. Inspeção das deformações durante as transições, integração e inspeção no Asset Studio e exportação Windows permanecem abertas. Quarta execução: 16 templates reais do runtime recuperados; 18/18 reconstruções numéricas fechadas e sem degeneração, 30/30 extremos de eixo internos aos respectivos segmentos. Dois dos dez centros de pivô dos dedos/polegares ficam fora do volume da palma, exigindo inspeção da continuidade visual nas transições. Sem alteração de geometria ou nova renderização; permanece parcial. Quinta execução: 78/78 amostras numéricas de flexão dos dois dedos com pivôs externos apresentaram vértices do segmento proximal no interior da palma. Sobreposição demonstrada nas amostras, não homologação visual contínua. Sem nova renderização; permanece parcial. Sexta execução: Recargas de rifle, escopeta e pistola amostradas na câmera FPS real no Godot 4.7.2 em Windows. A mão de apoio do rifle volta ao guarda-mão, mas o enquadramento encobre as duas junções investigadas. Inspeção próxima e no Asset Studio abertas. Inspeção próxima no Godot: dez quadros da recarga do rifle, com câmera auxiliar e arma ocultada, mostram as bases dos dois dedos em contato nas vistas amostradas. Ainda há facetas e transições marcadas. Falta homologação da composição no Asset Studio. Extremidades do painel dorsal e dos dedos arredondadas na fonte, com templates regenerados. Seis testes passaram e a comparação visual no Godot 4.7.2 incluiu dez quadros aproximados e 15 poses FPS de recarga. Homologação no Asset Studio aberta. Em 27/11, o catálogo foi atualizado para vincular as receitas e templates reais. Nove poses de pistola, rifle e escopeta foram inspecionadas no Studio WebGL. Permanecem abertos o serrilhado nas junções e a revisão das deformações em movimento. [Captura](qa/02-06/studio-maos.jpg).
- [ ] Implementar rig anatômico e IK — Parcial (26/11): [solucionador IK analítico candidato](VALIDACAO_02_07_RIG_IK.md); 7/7 testes locais aprovados, incluindo 500 casos determinísticos e 101 amostras de transição. Reprodução matemática dos dois braços de referência. Integração ao skeleton/runtime, pesos anatômicos, limites de produção e homologação visual pendentes; 02-06 preservado.
- [ ] Corrigir encaixes das mãos nas armas — Parcial (26/11): [diagnóstico dos encaixes](VALIDACAO_02_08_ENCAIXES.md). Identificado desvio entre centro animado da palma e referência de repouso no cálculo de deslocamento do apoio. 231 amostras matemáticas demonstram compensação de translação candidata, sem alteração do runtime. Inspeção e correção visual nas oito famílias em repouso, ADS, recarga e troca pendentes; dependências 02-03/06/07 preservadas. Em 27/11, a compensação foi integrada ao animador FPS. Em 427 poses de recarga, o desvio máximo em relação aos alvos caiu de 0,04984907 para 0,00000056 unidade. QA nas oito armas aprovado no Godot para Windows. A comparação FPS mostra o apoio da escopeta, com oclusão nos demais casos. Contato dos dedos, trocas e inspeção no Asset Studio seguem pendentes. Em novo teste a 60 passos/s, a correção por quadro reduziu o desvio máximo da palma em relação ao ponto do guarda-mão da escopeta de 0,00854343 para 0,00000039 unidade em 130 passos. Foram inspecionadas poses FPS das oito famílias, incluindo quadros de troca. A oclusão dos dedos e a revisão anterior publicada no Studio mantêm a homologação aberta. O antebraço e o punho agora compartilham uma âncora, corrigindo uma separação calculada de 52,66 mm. Falta inspecionar a continuidade da luva e a curvatura dos dedos.
- [ ] Remodelar soldados e equipamentos — Parcial (27/11). Primeiro lote nas mochilas de aliado e inimigo da família procedural: bolso externo e duas tiras foram integrados ao nó do tronco, com a paleta de cada uniforme. Rig e colisores existentes preservados. Comparação da mesma posição no Campo de Testes em Godot 4.5.2 Compatibility, Windows e AMD Radeon. Inspeção traseira dos buffers reais no Studio WebGL, com 37 superfícies no aliado e 39 no inimigo. O corpo completo, as demais peças de equipamento e a revisão das variantes em movimento continuam em aberto. [Godot](qa/02-09/godot-antes-depois.jpg), [aliado no Studio](qa/02-09/studio-aliado.png), [inimigo no Studio](qa/02-09/studio-inimigo.png).
- [ ] Remodelar objetos e estruturas do cenário — Parcial (27/11). Primeiro lote na caixa de munição do Campo de Testes: tampa e dois fechos remodelados com a biblioteca usada em produção. Quantidade e identificação do pickup conferidas na cena. O escopo do catálogo passou a verificar as quatro malhas reais sem colisor. Comparação no Godot 4.5.2 Compatibility, Windows e AMD Radeon, e inspeção lateral no Studio WebGL, com 1.728 triângulos. Ainda faltam os demais objetos e as estruturas do cenário. [Godot](qa/02-10/godot-antes-depois.jpg), [Studio](qa/02-10/studio-municao.png).

## 03 — Câmera e movimentação

- [ ] Aprimorar a câmera em primeira pessoa
- [ ] Melhorar animação de corrida
- [ ] Melhorar movimentação ao caminhar
- [ ] Refinar movimentação agachado
- [ ] Refinar movimentação deitado
- [ ] Corrigir colisões durante mudanças de postura
- [ ] Melhorar transições entre movimentos
- [ ] Revisar sway, bob e recuo da câmera
- [ ] Corrigir armas atravessando paredes

## 04 — Armas e combate

- [ ] Revisar funcionamento de todas as armas
- [ ] Melhorar animações de recarga
- [ ] Melhorar animações de troca de armas
- [ ] Refinar animação bolt action
- [ ] Aprimorar quick scope
- [ ] Revisar funcionamento dos acessórios
- [ ] Melhorar flash dos disparos
- [ ] Implementar ejeção de cápsulas convincente
- [ ] Melhorar fumaça e impactos por superfície
- [ ] Aprimorar granadas e explosões
- [ ] Refinar hitmarker e feedback de dano

## 05 — Sons e ambientação

- [ ] Auditar e remover sons sintetizados legados
- [ ] Revisar individualmente os sons WAV das armas
- [ ] Melhorar sons de recarga
- [ ] Adicionar sons específicos de bolt action
- [ ] Melhorar sons de passos
- [ ] Implementar áudio espacial
- [ ] Adicionar sons ambientes
- [ ] Balancear volumes e eliminar distorções

## 06 — Inimigos e inteligência artificial

- [ ] Melhorar navegação dos inimigos
- [ ] Corrigir inimigos presos em obstáculos
- [ ] Implementar comportamento de cobertura
- [ ] Melhorar movimentação em grupo
- [ ] Aprimorar flanqueamento
- [ ] Melhorar animações dos soldados
- [ ] Corrigir empunhadura das armas dos inimigos
- [ ] Melhorar animações de morte
- [ ] Refinar efeitos de sangue
- [ ] Revisar permanência dos cadáveres
- [ ] Aprimorar sistema de drop de armas e munição

## 07 — Survival e economia

- [ ] Revisar progressão das ondas
- [ ] Balancear dificuldade das ondas
- [ ] Balancear dinheiro e recompensas
- [ ] Revisar preços das armas e equipamentos
- [ ] Revisar as três estações de compra
- [ ] Aprimorar sistema de perks
- [ ] Revisar Última Chance
- [ ] Melhorar torretas automáticas
- [ ] Melhorar esquadrão aliado
- [ ] Aprimorar ataque aéreo
- [ ] Revisar checkpoints e salvamento
- [ ] Melhorar resumo de cada onda

## 08 — Interface e configurações

- [ ] Redesenhar HUD profissional
- [ ] Aprimorar menu inicial
- [ ] Aprimorar menu de pausa
- [ ] Completar configurações gráficas
- [ ] Completar configurações de áudio
- [ ] Melhorar personalização dos controles
- [ ] Implementar ajuste de tamanho do HUD
- [ ] Melhorar interface das lojas
- [ ] Melhorar tela de fim de jogo
- [ ] Implementar estatísticas e recordes locais

## 09 — Mapas e expansão

- [ ] Aprimorar o Campo de Testes
- [ ] Desenvolver mapa Complexo Industrial
- [ ] Implementar setores e rotas alternativas
- [ ] Adicionar pontos de cobertura
- [ ] Melhorar iluminação dos cenários
- [ ] Implementar seletor de mapas
- [ ] Desenvolver mapa urbano adicional

## 10 — Otimização e lançamento

- [ ] Otimizar modelos e níveis de detalhe (LOD)
- [ ] Otimizar renderização e materiais
- [ ] Otimizar inteligência artificial
- [ ] Otimizar consumo de memória
- [ ] Revisar vazamentos de recursos
- [ ] Realizar testes automatizados de regressão
- [ ] Validar partida completa de 15 ondas
- [ ] Realizar benchmark no hardware-alvo
- [ ] Atualizar documentação e roadmap
- [ ] Gerar executável Windows validado
- [ ] Publicar versão 1.0
