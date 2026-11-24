# Inventário runtime — QA de cenas reais

Complemento ao inventário estático e contrato v1. A rotina de QA instancia a cena real e usa as receitas existentes, sem editar scripts do jogo nem gerar modelos substitutos. O workflow independente roda Godot 4.4.1/OpenGL3 via Xvfb e publica JSON, logs e quatro screenshots. Não publica release nem altera a baseline. O perfil de dados da execução CI é isolado.

## Cobertura planejada da captura

- Mapa e menu: cena de entrada, três estações, câmera briefing, luz/ambiente, todas as hierarquias de nós; transformações locais e globais em metros, matrizes coluna-major.
- Oito armas: repouso, ADS e recarga; óticas e acessórios suportados amostrados individualmente, não produto cartesiano. Montagem real, materiais efetivos, mãos e colisão do player.
- Inimigos de três tipos, classes de armamento usuais, aliado, humanoide experimental explicitamente habilitado apenas no QA, torreta, oito pickups de arma, munição, granada e efeitos de granada/sangue/evento visual de disparo.
- Registros de cada nó e hierarquia, malha e bounds locais, superfícies e contagem de vértices/índices/triângulos quando disponível, normais/UVs, material efetivo e texturas, shapes, layers, câmeras, luz, ossos e poses.

Não é captura de todos os estados de uma partida, nem exportador geométrico para o Studio. Não grava buffers completos de geometria, índices LOD ou shaders completos; consultas físicas, marcador/impacto aéreo, traçador inimigo e combinações não amostradas ainda precisam de evidência. Nenhum campo ausente deve ser inventado. O manifesto continua estático e só será promovido após conciliação dos resultados efetivos.

## Execução

Workflow: Asset inventory runtime evidence (.github/workflows/asset-inventory.yml). No checkout, após importação do Godot, definir FRONTLINE_INVENTORY_DIR para um diretório de QA isolado; executar `godot --path . --rendering-driver opengl3 --script res://tools/asset_pipeline/runtime/inventory_qa.gd` e `python docs/qa/verify_runtime_inventory.py <diretorio>/runtime_inventory.json`. Preferir perfil de usuário temporário (XDG_DATA_HOME no Linux); nenhum teste deve operar sobre partida pessoal. O verificador rejeita amostras faltantes, nós órfãos, transformações não finitas, superfícies vazias e falha de rig. Capturas geradas não equivalem a inspeção visual.

Estado desta entrega: implementação publicada para execução remota, não afirmar resultado antes de confirmar CI. Godot ausente e GitHub sem DNS no container local. A falha do arsenal do workflow principal não foi corrigida. A tarefa de inventário permanece parcial até execução e conciliação verificadas.

### Evidência da execução CI iniciada nesta entrega

- [Primeira execução 45417210856](https://github.com/TPollTech/Frontline-Survival/actions/runs/45417210856): falhou antes de iniciar job; contexto runner.temp movido para env do step em 06bdb68.
- [Execução corrigida 45417303193](https://github.com/TPollTech/Frontline-Survival/actions/runs/45417303193): checkout, verificação estática Python, contrato Node e importação Godot concluídos com sucesso; coleta OpenGL e validação do relatório ainda em execução na última consulta. Não há artefatos visualmente inspecionados nem promoção de estado nesta entrega.

## Correção após a execução 45417303193

O log confirmou aprovação do inventário estático e dos 18 testes do manifesto, importação dos assets com sucesso e falha durante o coletor. As causas observadas foram compilação antecipada de scripts que dependem de GameSettings, chamada de surface_get_primitive_type em PrimitiveMesh e atribuição de Array não tipado a Array[String]. O coletor agora carrega dependências após inicialização do projeto, distingue ArrayMesh de primitivas e usa Array compatível. A correção precisa passar em nova execução; nenhuma aprovação visual é inferida. O log também apontou falta de tangentes em GLBs existentes, registrada como pendência de materiais/geometria, sem alterar assets nesta entrega.

## Execução aprovada e conciliação — 24/11/2026

[Run 45439036106](https://github.com/TPollTech/Frontline-Survival/actions/runs/45439036106), commit `1726a0d`: todos os steps concluídos, Godot 4.4.1 X11/OpenGL3. Baseline Python e contrato Node (18 testes) executados no checkout real; importação, coleta e verificador aprovados. [ZIP de evidência 14941018963](https://github.com/TPollTech/Frontline-Survival/actions/runs/45439036106/artifacts/14941018963) baixado e SHA-256 conferido com o GitHub; JSON e quatro PNG de 1280×720 abertos e analisados. O resumo persistente com hashes é [qa/runtime_inventory_evidence.json](qa/runtime_inventory_evidence.json). O ZIP original expira conforme retenção do Actions; o resumo preserva a referência, não substitui os dados brutos.

- 83 amostras, 57 FPS; 6.350 registros de nós, 2.993 de malha, 100 de colisão e 1 de skeleton. São somas entre amostras, não instâncias únicas nem orçamento por frame. Todos os 32 caminhos GLB do manifesto encontrados nos recursos de malha da engine. Das 24 famílias runtime, 20 têm tags de amostra; tag não garante que toda variante/estado tenha sido observado. Sem tag: effect:enemy_tracer, query:enemy_tactics, query:spawn, query:turret. O efeito de combate contém disparo visual, não os estados de ataque aéreo.
- 4/6 texturas foram observadas nos materiais efetivos registrados; ausentes na coleta: assets/textures/weapon_polymer_albedo.png, assets/textures/weapon_polymer_normal.png. Não significa ausência física. Revisar seleção por nome do material polimérico. 578 registros de superfície sem UV e 248 sem normais; 2.801 registros de malha sem caminho de recurso, típicos da geração runtime. Esses totais incluem repetições e não são contagem de defeitos únicos. Logs reais avisam falta de tangentes em GLBs. Registrar para tarefas de normais, UVs e materiais.
- Inspeção das imagens: menu/briefing real, porém overlay escurece parte do mapa; mira red dot visível no centro em uma pose de rifle; mãos e personagem legado com volumes simplificados; Quaternius experimental em T-pose no snapshot (o QA congela a física), sem evidência de animação ou empunhadura adequada. Não é homologação artística, de todas as perspectivas ou de partida interativa.
- [Run Windows 45439035738](https://github.com/TPollTech/Frontline-Survival/actions/runs/45439035738): importação, smoke, 50 ondas, core e integração aprovados; QA individual do arsenal falhou; exportação ignorada. Não existe ZIP novo do jogo validado nesta rodada.

**Estado:** captura inicial real aprovada e conciliada com os caminhos GLB e famílias do manifesto. Inventário permanece parcial: faltam amostras do traçador inimigo/ataque aéreo, verificação das consultas físicas (não renderizáveis), investigação de materiais poliméricos, cobertura das variantes e estados, proveniência e dados LOD completos. Nenhum modelo/gameplay mudou; nenhuma aprovação de Studio ou de modelo individual. O manifesto histórico v1 permanece imutável; evidência runtime separada evita promover dados parciais.

## Complemento de cobertura — implementação

A segunda rodada acrescenta carregamento verificável de todos os recursos físicos da baseline, inspeção das duas superfícies reais da biblioteca de materiais (separada de atribuição efetiva em malhas), contagem de tangentes, streams de áudio nos nós, execução das consultas de spawn, cobertura e posicionamento de torreta por funções reais, traçador inimigo e marcador/impacto aéreo real. A reconciliação exige 32/32 GLBs, todos os 60 recursos e as 24 famílias por tags de amostras ou consultas efetivamente chamadas. As formas de consulta são descritas a partir da fonte; resultados são capturados da engine. Não equivale a todas as combinações nem a aprovação artística. Os novos testes aguardam execução; a evidência aprovada anterior continua válida para o commit 1726a0d. Não houve alteração no gameplay, assets ou manifesto estático.

## Fechamento do inventário da versão existente — 24/11/2026

[Execução 45440510150](https://github.com/TPollTech/Frontline-Survival/actions/runs/45440510150), commit `50e9699f3a93de6a42493bb446b58ee6cffc9ae4`: **aprovada**, incluindo inventário estático, 18 testes do manifesto, importação, coleta e reconciliação automática. [Artefato 14942578969](https://github.com/TPollTech/Frontline-Survival/actions/runs/45440510150/artifacts/14942578969) baixado; SHA-256 conferido, JSON sem falhas, quatro PNG 1280×720 inspecionados. Resumo persistente e rastreável: [qa/runtime_inventory_final_evidence.json](qa/runtime_inventory_final_evidence.json).

| Critério do inventário existente | Evidência |
|---|---|
| Recursos físicos | 60/60 (49 carregados pela engine e 11 metadados conferidos) |
| Fontes e configuração históricas | 30/30 hashes iguais à baseline na árvore atual; três novos scripts do pipeline listados separadamente |
| GLB efetivamente observados | 32/32 |
| Famílias runtime | 24/24 associadas a amostras ou consultas realmente executadas |
| Áudios em nós | 11/11 |
| Texturas | 6/6 carregadas; 4/6 materiais efetivos das malhas; 2 polímero carregadas pela biblioteca mas não atribuídas nas amostras |
| Amostras | 86; 6.353 registros de nós, 2.996 malhas, 100 colisores, 1 skeleton; totais entre amostras |
| Efeitos adicionais | Traçador, marcador e impacto aéreo capturados |
| Consultas | Spawn e posicionamento de torreta retornaram resultado válido; consulta tática executou e não encontrou cobertura nessa amostra. Não afirmar validação completa da IA. |

A revisão das novas imagens confirma mapa e mira reais, mãos e soldado legado simplificados, e humanoide experimental em T-pose na captura. 248 registros de superfícies sem tangentes, incluindo repetições; não são 248 defeitos distintos. A cobertura do inventário **não é aprovação de qualidade dos modelos**.

**Critério de encerramento:** esta tarefa enumera e rastreia o conteúdo existente, as fontes, dependências e famílias de geração. A baseline estática foi confrontada com a main sem divergências e a cobertura das famílias identificadas foi conferida na engine. É suficiente para iniciar a migração incremental, sem exigir a execução de todas as combinações infinitas de estados dinâmicos. Fontes originais de terceiros ou licenças ainda desconhecidas permanecem explicitamente desconhecidas; não foram certificadas. Dados de geometria completos, índices LOD, cobertura de todas as poses, verificação de atribuição polimérica, validação de IA e Studio ficam nas tarefas específicas posteriores. Preservar todos os registros e não promover approved no manifesto.

O [CI Windows 45440510474](https://github.com/TPollTech/Frontline-Survival/actions/runs/45440510474) continua com conclusão failure (Arsenal QA - isolated individual tests of all eight weapons). Nenhum novo executável aprovado e nenhum asset ou gameplay alterado. A tarefa de inventário da baseline fica concluída; homologação visual e catálogo vivo continuam pendentes.
