# Checklist Mestre 1.0 — critérios de aceite revisados

25/11/2026. Revisão autorizada dos critérios; base d9cc6fc65366dd60938a9ae04b939933c5222213. [Checklist oficial e evidências](CHECKLIST_MESTRE.md) preservam os 131 IDs, títulos, ordem e estados. Este documento define o aceite prospectivo por ID; não é um relatório de execução nem reclassifica os resultados antigos.

## Separação de responsabilidades e regras de encerramento

- Etapa 00 = fundação operacional do pipeline para todo o conteúdo 3D. Deve abrir no Studio local e no Godot real, usar fontes/recursos autênticos, demonstrar funções e pilotos por categoria, migrar tecnicamente as categorias existentes e reconciliar cobertura. Não exigir remodelagem artística final, IK de todos os personagens, novos mapas ou otimização integral da release. Não transformar ferramenta auxiliar em produto.
- Etapa 01 = corrigir defeitos visuais/funcionais urgentes das armas de produção. Etapa 02 = produção artística, rig/IK, materiais, texturas e encaixes definitivos. Etapas 03–09 = jogo, movimento, combate, áudio, IA, ondas, UI e mapas. Etapa 10 = otimização global, regressão, partida, hardware-alvo e publicação.
- Não apagar requisito: a matriz abaixo localiza a validação técnica na 00 e o acabamento, cobertura de estados de gameplay e otimização nas tarefas de produção. Normais/tangentes, escala, fonte, shader ou vazamento que cause falha impeditiva, erro de representação ou quebra de gameplay continuam bloqueadores do escopo técnico. Aviso legado não impeditivo só pode ser registrado com evidência, efeito, ID responsável e correção prevista; não alterar o resultado bruto do teste, nem marcar modelo aprovado. Fonte editável continua obrigatória; para terceiros, documentar licença/origem e rota canônica editável ou obter autorização explícita para exceção. Não usar ausência de fonte como aprovação.
- Aceite técnico não equivale a aprovação artística. Para alterações de modelo permanecem as 13 etapas da especificação, incluindo revisão visual no Studio e Godot. Piloto QA-only pode ser instanciado em sessão de teste real do Godot sem substituir produção. Não precisa virar um item do jogo. Categorias não geométricas são verificadas pelos dados/comportamentos próprios; não criar malha falsa. Cobertura de todo o inventário atual é reconciliada; testes visuais de fundação são amostras representativas por categoria, função e estado aplicável, com limites declarados. A etapa de produção exige revisão individual dos assets alterados.
- Reutilizar evidências anteriores se revisão, arquivos/dependências, configuração e critério forem comprovadamente equivalentes; citar SHA original e limites, distinguir evidência anterior de novo teste. Se não for possível comprovar equivalência, executar o teste afetado. Não repetir suítes integrais sem justificativa. Cada critério precisa de evidência inspecionável proporcional: logs/relatórios/hashes para testes técnicos; capturas reais inspecionadas para visual; revisão, plataforma e cenário para medições; documentação conferida para tarefas documentais. Testes sintéticos não provam engine.
- Orçamentos da fundação são provisórios; medir um cenário técnico representativo e registrar hardware real e limites, sem substituir o benchmark de release. O alvo Ryzen 5 7530U/iGPU/8 GB e Compatibility permanece obrigatório em 10-08. LOD de produção, popping de todas as famílias aplicáveis e carga prolongada são 10-01/05/08.
- Os 34 IDs da etapa 00 permanecem bloqueio obrigatório. 00-34 só é aceito após 00-01 a 00-33 aceitos e execução integrada de verdade; depois liberar 01–10. Nenhum ID concluído por reescrever critérios, mover responsabilidades ou instalar dependências. Se não houver ambiente, registrar bloqueio; não criar runners/instaladores redundantes. QA All-in-One é opcional, usar o fluxo existente ou testes focados, sem impor comandos manuais Godot ao responsável. Preservar main, [skip ci] enquanto Actions sem cota.

## Sequência recomendada para desbloquear a etapa 00

1. 00-13: concluir catálogo vivo e abrir Studio atual com uma composição real e GLB. Resolver drift/caminhos com reteste focado, não outro instalador.
2. 00-17 a 00-21: completar e demonstrar inspeção e controles sobre os recursos reais no Studio.
3. 00-24/25/27: gerar e validar pilotos existentes, abrir no Studio e Godot, inspecionar e cruzar dados; compartilhar evidências sem contar uma execução como vários testes independentes.
4. 00-28 a 00-32 e 00-10: concluir rastreabilidade/paridade técnica e lacunas LOD do escopo de fundação; manter defeitos de arte atribuídos a 01/02/04/06/09/10.
5. 00-34: verificar a matriz e integração real, sem novo sistema QA. Só então avançar para correções urgentes e produção.

## Evidências preservadas

A execução Windows de 95c7ac8 tem 26/47 passos aprovados, 7 falhos, 14 bloqueados, 551 hashes reconciliados, 32/32 importações e comparações, 207/207 verificações LOD, 24/24 contatos, 441 frames, 86 amostras e 188 escopos. Ryzen 7520U não é hardware-alvo; os resultados não demonstram homologação visual integral. Correções de compatibilidade e sondagem Python ainda exigem reteste. Consultar [QA Windows](QA_RETESTE_WINDOWS.md), [auditoria](AUDITORIA_HOMOLOGACAO_PIPELINE.md) e histórico no checklist. Não iniciar novo desenvolvimento do instalador como tarefa de aceite.

## Critérios por ID

## 00 — Fundação do sistema 3D e Asset Studio

| ID | Tarefa | Aceite verificável |
|---|---|---|
| 00-01 | Auditar SNC Energies e SNC Adventures e arquitetura atual do Frontline Survival | Registrar fontes, caminhos, revisões, componentes reutilizáveis e limites dos dois projetos de referência e do Frontline. |
| 00-02 | Inventariar todos os assets, fontes, dependências e cenas existentes | Inventariar recursos, fontes, cenas, referências e famílias runtime reais; reconciliar contagens e explicitar lacunas. |
| 00-03 | Definir arquitetura modular, manifesto canônico e convenções de escala e eixos | Contrato versionado com IDs, unidades, eixos, transforms, hierarquia e manifesto; validar conversões e preservação de IDs. |
| 00-04 | Implementar biblioteca paramétrica Python e backend Blender quando necessário | Biblioteca editável Python/IR e backend Blender quando necessário, com operações e erros verificados em exemplos reais. |
| 00-05 | Implementar geometrias avançadas, extrusão, revolução, booleanas e bevels | Demonstrar extrusão, revolução, booleanas e bevels em malhas válidas, não remodelar o arsenal. |
| 00-06 | Implementar curvas, superfícies orgânicas e topologia personalizada | Demonstrar curvas, superfícies orgânicas e topologia personalizada em fixtures verificadas. |
| 00-07 | Implementar normais suavizadas e ponderadas, UV mapping e tangentes | Gerar normais suaves/ponderadas, UV e tangentes corretas em exemplos, verificar atributos exportados; defeitos dos modelos legados são da migração/produção. |
| 00-08 | Implementar materiais PBR, texturas e biblioteca de materiais | Biblioteca PBR com texturas e espaços de cor corretos, materiais reutilizáveis e exemplo exportado; acabamento realista de produção fica em 02. |
| 00-09 | Implementar hierarquias, pivôs, encaixes, rigging e skeleton | Hierarquia, pivôs, sockets, skeleton, pesos e deformação demonstrados em rig técnico; anatomia/IK de produção em 02-07. |
| 00-10 | Implementar colisões independentes e LOD com orçamentos por categoria | Contrato de orçamento por categoria, LOD decrescente e colisores independentes; validar troca por distância/histerese e contatos no Godot, inspecionar movimento representativo e documentar famílias aplicáveis/limites. Otimização de cada modelo e metas de FPS em 10-01/08. |
| 00-11 | Implementar exportação determinística GLB/glTF 2.0 e rastreabilidade de fontes | Exportar GLB/glTF com fonte e hashes rastreáveis, duas gerações equivalentes e importação real de fixture. |
| 00-12 | Implementar descoberta automática e catálogo de todos os assets reais | Descoberta automática sem editar o Studio; conciliar todos os recursos e famílias atuais, dependências e referências ausentes/dinâmicas explicitadas. |
| 00-13 | Criar Asset Studio HTML/CSS/JS com Three.js e WebGL | Abrir Studio local em WebGL real; pesquisar, selecionar e renderizar GLBs e composições reais do catálogo atual; verificar hashes, contagens, transforms e diferenças de renderização. Disponibilizar acesso utilizável, sem exigir deploy público. |
| 00-14 | Implementar iluminação HDRI, sombras, antialiasing, sRGB, ACES e piso técnico | Demonstrar HDRI, sombras, antialiasing, sRGB, ACES e piso neutro no Studio com captura real. |
| 00-15 | Implementar OrbitControls, damping, enquadramento por bounding box, zoom, pan e reset | Demonstrar OrbitControls, damping, enquadramento por bounds, zoom, pan e reset sem alterar a geometria. |
| 00-16 | Implementar seis vistas ortográficas, perspectiva e tela cheia | Demonstrar seis direções ortográficas, perspectiva e tela cheia com retorno correto. |
| 00-17 | Implementar vistas reais de primeira e terceira pessoa e prévia de mapas completos | Capturar vistas FPS e TPS da cena/jogador real e permitir explorar mapa completo no Studio; não exigir implementar TPS como modo jogável. |
| 00-18 | Implementar inspeção de materiais, texturas, UVs, wireframe, sólido e texturizado | Inspecionar material, textura, UV, wireframe, sólido e texturizado em GLB e composição runtime representativos; explicitar atributos ausentes e diferenças de shader. |
| 00-19 | Implementar visualização de normais, pivôs, colisões e LOD | Exibir normais, pivôs, shapes e níveis LOD reais com controles e valores verificáveis; distinguir bias de LOD e consultas de colisores. |
| 00-20 | Implementar métricas de vértices, triângulos, materiais e dimensões reais | Conciliar vértices, triângulos, materiais e dimensões de arquivos e composições representativas com dados Godot; distinguir instâncias e bounds deformados. |
| 00-21 | Implementar animações, componentes articulados e controle de poses | Demonstrar reprodução de animação, articulações e controle de poses em rig/piloto e componente real aplicável; não exigir animações/IK definitivos de todos os personagens. |
| 00-22 | Implementar screenshots e versão offline sem CDN | Salvar screenshots e abrir pacote Studio local extraído com dependências locais, sem CDN e com rede externa bloqueada. |
| 00-23 | Implementar validação de geometria, normais, UVs, texturas e materiais | Validadores detectam casos válidos/inválidos de geometria, normais, UVs, texturas e materiais; avisos reais explicitados, sem confundir validação de ferramenta com aprovação artística. |
| 00-24 | Implementar validação de escala, orientação, pivôs, hierarquias e referências | Contratos de escala, orientação, pivôs, hierarquia e referências verificados nos pilotos aplicáveis em export e Godot/Studio; detectar casos negativos; inventariar lacunas legadas com dono e correção em produção. |
| 00-25 | Implementar validação de exportação, orçamento de polígonos e importação no Godot | Validar exportação, contagem e orçamento provisório dos pilotos por categoria, importar no Godot Compatibility e medir cenário técnico representativo com hardware registrado; metas e benchmark final no 10-08. |
| 00-26 | Integrar validação, geração reproduzível e evidências ao CI | Mecanismo CI existente executa geração reproduzível, validação e preserva logs/relatórios; evidência histórica aceita no escopo inalterado; sem exigir disparo durante falta de cota. |
| 00-27 | Validar um asset piloto de cada categoria no Studio e no jogo | Um piloto técnico por categoria geométrica do contrato (incluindo previstas), com fonte, hashes, contrato, export ou composição real, validação e inspeção efetiva no Studio e Godot; categorias não geométricas usam sua evidência própria. Reutilizar pilotos existentes; qualidade suficiente para demonstrar o fluxo, não arte final nem integração permanente de QA-only. |
| 00-28 | Migrar todo o arsenal e acessórios para fontes canônicas | Todos os oito tipos de arma, variantes/partes GLB e sete acessórios atuais rastreados à fonte canônica e ao consumidor real; reprodução verificável e comparação de repouso/ADS/partes móveis de casos representativos, sem alterar gameplay. Normal/tangente ou drift que impeça paridade deve ser corrigido; remodelagem, proporções e acabamento em 01/02/04. |
| 00-29 | Migrar personagens, mãos, equipamentos e aliados/inimigos | Rastrear mãos, personagens, equipamento, aliados e inimigos às fontes e montagem reais; validar equivalência de malhas, transforms, materiais, rig/poses existentes e visibilidade em exemplos no Studio/Godot. Anatomia, rigs definitivos, IK e animações em 02/06. |
| 00-30 | Migrar objetos, estações, veículos, estruturas e elementos ambientais | Rastrear objetos, estações, estruturas, ambiente e veículos existentes às receitas/arquivos e consumidores; testar paridade visual/técnica e colisão aplicável de exemplos reais; categorias sem produção cobertas por piloto, não criar conteúdo de gameplay só para o QA. Remodelagem em 02-10/09. |
| 00-31 | Migrar terreno, arquitetura, mapas completos e cenas compostas | Composição canônica do terreno, arquitetura e mapas atuais preserva layout, transforms, materiais, colisão e referências; abrir mapa completo no Studio e Godot, conferir vistas representativas. Novos mapas, rotas, iluminação artística e navegação de produção em 06/09. |
| 00-32 | Migrar objetos procedurais em runtime, colisões e efeitos 3D para o catálogo | Conciliar famílias runtime atuais e escopos com nós, hashes, materiais e colisores reais; amostrar efeitos representativos em estados relevantes, conferir no Studio/Godot e documentar limitações de shader/consulta. Refinamento e carga prolongada em 04/06/10. |
| 00-33 | Documentar arquitetura, comandos, extensão de categorias e política de QA | Documentar arquitetura, comandos, extensão de categorias, contratos e rotina de revisão com exemplos existentes. |
| 00-34 | Auditar cobertura integral do Studio e homologar o pipeline no jogo | Com 00-01 a 00-33 aceitas, executar fluxo integrado em revisão identificada: fonte, geração, validação, catálogo, Studio aberto e Godot renderizado. Conferir cobertura de recursos/famílias/pilotos, paridade técnica e inspeções representativas, sem falha impeditiva ou lacuna silenciosa. Registrar limites e débitos não impeditivos por ID posterior. Não exigir instalador universal, arte final ou benchmark de release. |

## 01 — Correções urgentes

| ID | Tarefa | Aceite verificável |
|---|---|---|
| 01-01 | Corrigir as iron sights flutuantes das snipers | Inspecionar todas as snipers em repouso e ADS; miras ligadas à arma, sem peças flutuantes nem regressão de recarga. |
| 01-02 | Restaurar e validar o ajuste de FOV | Variar FOV nos limites suportados, verificar persistência e aplicação na câmera durante gameplay. |
| 01-03 | Padronizar o enquadramento de todas as armas | Conferir as oito armas em repouso, ADS e recarga, sem corte ou enquadramento indevido na resolução suportada. |
| 01-04 | Separar o FOV da câmera do enquadramento das armas | Testar combinações de FOV de câmera e viewmodel; arma não distorce/desloca indevidamente e ADS permanece alinhado. |
| 01-05 | Corrigir alinhamento das miras e lunetas | Conferir alinhamento de todas as miras e lunetas e combinações compatíveis na câmera real. |
| 01-06 | Eliminar peças flutuantes, transparentes ou sobrepostas | Inspecionar armas/partes móveis em estados relevantes e corrigir transparências, sobreposições ou peças soltas indevidas. |
| 01-07 | Testar individualmente todas as armas | QA individual das oito armas cobre tiro, mira, recarga, troca e estados aplicáveis; logs por arma e sem falhas. |
| 01-08 | Corrigir falha do QA individual do arsenal na v0.9.34 | Regressão de carregamento GameSettings e referências relativas executada no QA individual sem erro. |

## 02 — Modelagem 3D

| ID | Tarefa | Aceite verificável |
|---|---|---|
| 02-01 | Desenvolver um padrão híbrido de modelagem 3D | Definir padrão artístico híbrido com referências, escala, detalhes e materiais; demonstrar em um asset de produção no Studio/Godot. |
| 02-02 | Remodelar completamente o arsenal | Remodelar cada arma a partir de fonte canônica, preservando encaixes, estados e funcionamento; revisão artística e visual das oito. |
| 02-03 | Melhorar proporções e silhuetas das armas | Conferir dimensões, proporções e silhuetas com referências e vistas coerentes; corrigir fontes das armas. |
| 02-04 | Implementar materiais PBR realistas | Aplicar materiais PBR de produção por superfície e verificar aparência no Godot sob iluminação normal. |
| 02-05 | Implementar texturas e normal maps | Texturas e normal maps próprios/licenciados, UV e tangentes consistentes; sem artefatos na distância de uso. |
| 02-06 | Remodelar mãos, dedos, luvas e antebraços | Modelos anatômicos de mãos, dedos, luvas e antebraços, com silhueta e deformações revisadas na câmera FPS. |
| 02-07 | Implementar rig anatômico e IK | Rig anatômico/IK integrado às mãos/personagens, pesos, limites e transições sem deformações indevidas nos estados de produção. |
| 02-08 | Corrigir encaixes das mãos nas armas | Verificar empunhadura, dedos, sockets e contato nas oito armas em repouso, ADS, recarga e troca. |
| 02-09 | Remodelar soldados e equipamentos | Soldados/equipamentos remodelados, com materiais, rig e visual coerentes no jogo. |
| 02-10 | Remodelar objetos e estruturas do cenário | Remodelar objetos/estruturas de produção por lotes, mantendo colisões, escala e função; inspeção no mapa real. |

## 03 — Câmera e movimentação

| ID | Tarefa | Aceite verificável |
|---|---|---|
| 03-01 | Aprimorar a câmera em primeira pessoa | Validar câmera FPS em movimento, ADS, colisões e diferentes resoluções, sem saltos ou desconforto evitável. |
| 03-02 | Melhorar animação de corrida | Animação de corrida natural, transições de início/fim e estados da arma sem clipping indevido. |
| 03-03 | Melhorar movimentação ao caminhar | Caminhada responsiva com bob e passos coerentes; testar direções e mudança de velocidade. |
| 03-04 | Refinar movimentação agachado | Agachar com altura/velocidade/pose coerentes e retorno válido ao ficar em pé. |
| 03-05 | Refinar movimentação deitado | Deitar com pose, câmera, movimento e retorno coerentes, preservando controle da arma. |
| 03-06 | Corrigir colisões durante mudanças de postura | Testar transições sob tetos/obstáculos; cápsula não atravessa geometria nem fica presa. |
| 03-07 | Melhorar transições entre movimentos | Transições caminhar/correr/agachar/deitar/ADS coerentes sem saltos ou estados inválidos. |
| 03-08 | Revisar sway, bob e recuo da câmera | Medir/revisar sway, bob e recuo em estados reais, mantendo mira e conforto. |
| 03-09 | Corrigir armas atravessando paredes | Testar aproximação de paredes/obstáculos; viewmodel não atravessa cenário de forma indevida. |

## 04 — Armas e combate

| ID | Tarefa | Aceite verificável |
|---|---|---|
| 04-01 | Revisar funcionamento de todas as armas | Testar todas as armas: disparo, munição, recarga, cadência, mira, troca, dano e estados aplicáveis; sem regressões. |
| 04-02 | Melhorar animações de recarga | Recargas coerentes com carregadores, mãos, munição e cancelamentos; inspeção em jogo. |
| 04-03 | Melhorar animações de troca de armas | Trocas com animações/transições corretas e sem duplicação, disparo ou munição indevidos. |
| 04-04 | Refinar animação bolt action | Animação bolt action sincronizada ao estado do disparo e do ferrolho; validar interrupções e ADS. |
| 04-05 | Aprimorar quick scope | Transições ADS rápidas sem mira desalinhada ou estado inconsistente; verificar equilíbrio de gameplay. |
| 04-06 | Revisar funcionamento dos acessórios | Combinações compatíveis de acessórios, encaixe, efeitos e estados preservados; rejeitar incompatíveis. |
| 04-07 | Melhorar flash dos disparos | Flash legível e coerente com direção/iluminação, duração e custo; testar no Godot. |
| 04-08 | Implementar ejeção de cápsulas convincente | Ejeção de cápsulas visualmente coerente, com ciclo de vida controlado e sem interferência na jogabilidade. |
| 04-09 | Melhorar fumaça e impactos por superfície | Impactos e fumaça diferenciados por superfície, legíveis e com limpeza de recursos. |
| 04-10 | Aprimorar granadas e explosões | Granadas/explosões funcionam com feedback, dano, colisão e ciclo de vida previstos; testar casos reais. |
| 04-11 | Refinar hitmarker e feedback de dano | Hitmarker e feedback de dano correspondem aos eventos reais e não aparecem em falso positivo. |

## 05 — Sons e ambientação

| ID | Tarefa | Aceite verificável |
|---|---|---|
| 05-01 | Auditar e remover sons sintetizados legados | Inventariar caminhos de áudio antigos, remover ou substituir apenas os obsoletos e testar ausência de referências quebradas. |
| 05-02 | Revisar individualmente os sons WAV das armas | Ouvir e validar cada WAV de disparo, formato, sincronização, volume e ausência de distorção. |
| 05-03 | Melhorar sons de recarga | Recargas com áudio sincronizado às etapas das animações, inclusive cancelamentos. |
| 05-04 | Adicionar sons específicos de bolt action | Áudio bolt action específico sincronizado ao mecanismo de jogo. |
| 05-05 | Melhorar sons de passos | Passos distinguem superfícies e estados de movimento, sem sobreposição indevida. |
| 05-06 | Implementar áudio espacial | Testar direção, distância e atenuação espacial de fontes reais, preservando legibilidade. |
| 05-07 | Adicionar sons ambientes | Ambientação sonora coerente por mapa, loops limpos e volume ajustável. |
| 05-08 | Balancear volumes e eliminar distorções | Mixagem final sem clipping/distorção perceptível, volumes relativos e configurações verificados. |

## 06 — Inimigos e inteligência artificial

| ID | Tarefa | Aceite verificável |
|---|---|---|
| 06-01 | Melhorar navegação dos inimigos | Inimigos alcançam objetivos por rotas válidas em cenários representativos; validar obstáculos e mudanças de posição. |
| 06-02 | Corrigir inimigos presos em obstáculos | Reproduzir casos de NPC preso e demonstrar recuperação sem atravessar colisões. |
| 06-03 | Implementar comportamento de cobertura | NPC identifica e usa cobertura adequada no jogo, abandona quando inválida; verificar comportamento. |
| 06-04 | Melhorar movimentação em grupo | Grupos se distribuem e movem sem aglomeração excessiva nem deadlocks em ondas. |
| 06-05 | Aprimorar flanqueamento | Flanqueamento usa rotas disponíveis e comportamento legível, sem quebrar navegação. |
| 06-06 | Melhorar animações dos soldados | Soldados animam locomoção, combate e transições coerentemente com rig e movimento. |
| 06-07 | Corrigir empunhadura das armas dos inimigos | Empunhaduras de inimigos acompanham arma e poses sem desalinhamento relevante. |
| 06-08 | Melhorar animações de morte | Mortes com transições coerentes, estado final e colisão/ciclo de vida corretos. |
| 06-09 | Refinar efeitos de sangue | Sangue com impacto visual coerente e custo/limpeza controlados, sem afetar gameplay. |
| 06-10 | Revisar permanência dos cadáveres | Cadáveres persistem conforme política de jogo e limites de recursos testados. |
| 06-11 | Aprimorar sistema de drop de armas e munição | Drop de armas/munição corresponde ao inimigo e regras; coleta/limites sem duplicação. |

## 07 — Survival e economia

| ID | Tarefa | Aceite verificável |
|---|---|---|
| 07-01 | Revisar progressão das ondas | Ondas iniciam, avançam e encerram corretamente, incluindo intervalo e condições de derrota. |
| 07-02 | Balancear dificuldade das ondas | Testar curva de dificuldade por ondas com métricas e sessões representativas, documentar equilíbrio. |
| 07-03 | Balancear dinheiro e recompensas | Dinheiro recebido/gasto corresponde a eventos e recompensas; testar progressão e ausência de duplicação. |
| 07-04 | Revisar preços das armas e equipamentos | Preços e utilidade das armas/equipamentos coerentes com economia e ondas. |
| 07-05 | Revisar as três estações de compra | Três estações acessíveis e funcionais; transações, saldo insuficiente e feedback verificados. |
| 07-06 | Aprimorar sistema de perks | Perks aplicam/removem efeitos previstos, com limites e persistência conforme regras. |
| 07-07 | Revisar Última Chance | Última Chance funciona nos cenários previstos, sem invulnerabilidade ou estado permanente indevidos. |
| 07-08 | Melhorar torretas automáticas | Torretas funcionam em aquisição, alvo, duração, remoção e feedback, com custo controlado. |
| 07-09 | Melhorar esquadrão aliado | Aliados seguem regras de combate, navegação e duração, sem bloquear o jogador. |
| 07-10 | Aprimorar ataque aéreo | Ataque aéreo respeita alvo, avisos, dano e ciclo de vida previstos. |
| 07-11 | Revisar checkpoints e salvamento | Salvar/carregar/checkpoints preservam estado previsto e tratam dados inválidos sem corromper progresso. |
| 07-12 | Melhorar resumo de cada onda | Resumo por onda reflete contagens, ganhos e resultados reais, exibido no momento correto. |

## 08 — Interface e configurações

| ID | Tarefa | Aceite verificável |
|---|---|---|
| 08-01 | Redesenhar HUD profissional | HUD legível, coerente, sem sobreposições nas resoluções suportadas e com dados corretos em combate. |
| 08-02 | Aprimorar menu inicial | Menu inicial com novo jogo, carregar, configurações e sair funcionando nos estados previstos. |
| 08-03 | Aprimorar menu de pausa | Pausa/resume/configurações/saída funcionam sem avançar gameplay indevidamente. |
| 08-04 | Completar configurações gráficas | Opções gráficas aplicáveis, persistentes e validadas na engine Compatibility. |
| 08-05 | Completar configurações de áudio | Controles de áudio persistem e afetam canais previstos, inclusive menu e jogo. |
| 08-06 | Melhorar personalização dos controles | Remapeamento de controles funciona, trata conflitos e permite restaurar padrões. |
| 08-07 | Implementar ajuste de tamanho do HUD | Escala do HUD ajustável, persistente e sem cortes/sobreposição nas resoluções suportadas. |
| 08-08 | Melhorar interface das lojas | Interfaces das lojas exibem preços, saldo, disponibilidade e feedback de transações corretos. |
| 08-09 | Melhorar tela de fim de jogo | Tela de fim de jogo mostra resultados reais e permite reiniciar/voltar ao menu. |
| 08-10 | Implementar estatísticas e recordes locais | Estatísticas e recordes locais corretos, persistentes e sem corrupção de dados. |

## 09 — Mapas e expansão

| ID | Tarefa | Aceite verificável |
|---|---|---|
| 09-01 | Aprimorar o Campo de Testes | Campo de Testes refinado artisticamente e jogável, com escala, rotas, colisões e iluminação inspecionadas. |
| 09-02 | Desenvolver mapa Complexo Industrial | Complexo Industrial integrado e jogável, com assets reais, spawns, navegação, colisões e desempenho medido. |
| 09-03 | Implementar setores e rotas alternativas | Setores e rotas alternativas conectados e testados por jogador e NPCs. |
| 09-04 | Adicionar pontos de cobertura | Coberturas distribuídas com escala, colisão, utilidade e navegação verificadas. |
| 09-05 | Melhorar iluminação dos cenários | Iluminação de produção coerente, legível e com custo medido nos mapas. |
| 09-06 | Implementar seletor de mapas | Seleção de mapas inicia o cenário correto, com dados, spawns e estados consistentes. |
| 09-07 | Desenvolver mapa urbano adicional | Mapa urbano adicional integrado, visualmente revisado e jogável com as mesmas validações. |

## 10 — Otimização e lançamento

| ID | Tarefa | Aceite verificável |
|---|---|---|
| 10-01 | Otimizar modelos e níveis de detalhe (LOD) | Otimizar LOD de todos os modelos/famílias aplicáveis, medir popping, contatos e custo antes/depois, manter qualidade visual. |
| 10-02 | Otimizar renderização e materiais | Medir e reduzir custos de renderização/material com comparações reproduzíveis, preservar aparência e Compatibility. |
| 10-03 | Otimizar inteligência artificial | Medir custo da IA sob carga, otimizar sem regressões de navegação e comportamento. |
| 10-04 | Otimizar consumo de memória | Medir RAM/VRAM/recursos durante partidas e reduzir excessos com comparativos. |
| 10-05 | Revisar vazamentos de recursos | Testar ciclos repetidos de ondas, mapas, efeitos e encerramento; investigar/corrigir vazamentos de produção e retestar. |
| 10-06 | Realizar testes automatizados de regressão | Executar suíte de regressão da revisão candidata, sem falhas impeditivas e com logs/limites. |
| 10-07 | Validar partida completa de 15 ondas | Completar partida real de 15 ondas, verificar economia, IA, combate, salvamento, UI e estabilidade. |
| 10-08 | Realizar benchmark no hardware-alvo | Benchmark final Ryzen 5 7530U/iGPU/8 GB com driver, resolução, renderer, condições, FPS/frame time/memória e percurso/partida repetíveis; metas registradas e atendidas. |
| 10-09 | Atualizar documentação e roadmap | Documentação, roadmap, changelog e critérios/evidências correspondem à versão candidata. |
| 10-10 | Gerar executável Windows validado | Exportar executável Windows da revisão integrada, verificar pacote e jogar/testar o export real. |
| 10-11 | Publicar versão 1.0 | Publicar 1.0 somente com os 130 IDs anteriores aceitos, release/artefatos verificados e notas de versão. |
