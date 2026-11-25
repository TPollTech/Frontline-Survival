# Frontline Survival — Checklist mestre até a versão 1.0

Atualizado em 24/11/2026. Mantém as 96 tarefas anteriores e adiciona a fundação de modelagem/Studio e a regressão de QA. Fonte de requisitos: [especificação obrigatória](ASSET_STUDIO_SPEC.md). Estado verificado: main v0.9.34 de desenvolvimento; última release v0.9.31; [CI do arsenal corrigido e aprovado](https://github.com/TPollTech/Frontline-Survival/actions/runs/45504785421) na revisão 446f31eb. Nova revisão de assets posterior em revalidação. Priorizar 00. Estados: [ ] pendente/parcial; [x] somente tarefa integralmente validada. Os trabalhos anteriores não são descartados; reavaliar na arquitetura nova. Nenhuma homologação visual manual foi confirmada nesta revisão.

### Continuidade e execução individual

O checklist é a fonte oficial dos estados e das evidências. Os IDs seguem a etapa e a posição já atribuída nesta revisão, de `00-01` a `10-11` por etapa. Preserve o vínculo entre ID e tarefa. Para novas tarefas autorizadas, atribua o próximo ID livre na etapa. Exclusão, renumeração ou reorganização requer autorização.

Em cada conversa, consulte a main e reconstrua o painel completo a partir deste documento. A porcentagem oficial usa apenas tarefas concluídas. A ação de uma linha solicita a execução exclusiva daquele ID ou a revalidação, caso esteja concluído. Inclua estado anterior, justificativa, evidências, dependências, documentação e commit de referência no comando.

Antes de alterar o projeto, siga AGENTS.md, confira critérios de aceite e integre a main atual. Registre os testes executados, resultados, limitações e bloqueios. Mantenha em parcial o que ainda requer implementação, validação ou homologação. Atualize apenas os estados sustentados por evidência e verifique o commit remoto. Enquanto o GitHub Actions estiver sem cota, use testes locais e `[skip ci]`. Após cada execução, reenvie o painel integral com todos os IDs e a próxima tarefa recomendada.

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
- [ ] Implementar colisões independentes e LOD com orçamentos por categoria — Parcial: 13 categorias com orçamento canônico. Godot 4.4.1 Compatibility/Linux aprovou 207/207 transições e raios em 23 conjuntos de cinco famílias (86 peças) e 24/24 varreduras com a cápsula real do jogador nos oito bloqueadores. Totais de 49.248/10.584/4.128 triângulos por nível. Runner com importação renderizada em snapshot isolado; 30 capturas conferidas e 15 comparações de câmera fixa inspecionadas. Benchmark A/B/B/A executado com 960 intervalos no Linux/llvmpipe. Inventário atualizado, 86 amostras e cinco vistas nativas. WebGL do Studio, ampliação para as demais famílias aplicáveis, popping em movimento e benchmark no Ryzen 5 7530U/iGPU/8 GB pendentes. [Evidências e histórico](LOD_COLISOES_RUNTIME.md). Modo de captura em movimento preparado (441 frames previstos, 10/10 testes sintéticos do verificador); coleta/inspeção real ainda pendente.
- [x] Implementar exportação determinística GLB/glTF 2.0 e rastreabilidade de fontes — Fundação validada: 117/117 testes Blender/Python, manifesto de fontes canônico, reprodução byte a byte e importação de ambos os formatos no [Godot CI 45501055855](https://github.com/TPollTech/Frontline-Survival/actions/runs/45501055855). Dois joints autorais e helper sem peso conferidos. Sem homologação de assets de produção. [Biblioteca](BIBLIOTECA_PARAMETRICA.md).
- [x] Implementar descoberta automática e catálogo de todos os assets reais — Concluída no escopo de descoberta/catalogação da versão atual: 52 registros, 100 recursos, 24/24 famílias, 86 composições, 167 buffers reais com SHA-256 verificado, 48 candidatos de quatro expressões dinâmicas (44 existentes e quatro opcionais ausentes), 32/32 GLBs, zero lacunas de referências literais/runtime; quatro assemblies com três LODs registrados. CIs 45535740278 e 45535950057 aprovados, artefatos inspecionados. Renderização integral das composições e publicação final são etapas distintas; sem homologação visual. [Catálogo](CATALOGO_VIVO.md).
- [ ] Criar Asset Studio HTML/CSS/JS com Three.js e WebGL — Parcial: 201 buffers portáveis (167 procedurais + 34 importados), seis texturas, 86/86 composições reconstruídas, 32 GLBs, seis cenas renderizadas e offline aprovados no CI 45538009975. Comparação real na câmera nativa do mapa, 12 pontos, erro máximo 0,00003791 px; capturas comparadas e inspecionadas. Albedo triplanar aproximado, skinning em repouso, diferenças de sombras/céu/labels/shaders e deploy final pendentes. [Studio](ASSET_STUDIO.md).
- [x] Implementar iluminação HDRI, sombras, antialiasing, sRGB, ACES e piso técnico — 32/32 GLBs e controles aprovados no [CI 45473901798](https://github.com/TPollTech/Frontline-Survival/actions/runs/45473901798), duas capturas reais inspecionadas. Sem homologação de modelos ou benchmark.
- [x] Implementar OrbitControls, damping, enquadramento por bounding box, zoom, pan e reset — 32/32 GLBs, interação, resize e reset aprovados no CI 45475002613; capturas inspecionadas.
- [x] Implementar seis vistas ortográficas, perspectiva e tela cheia — seis eixos, fullscreen e retorno aprovados no CI 45475002613; capturas inspecionadas.
- [ ] Implementar vistas reais de primeira e terceira pessoa e prévia de mapas completos — Parcial: cinco capturas reais aprovadas no CI 45502974998, incluindo colisões; TPS nativo do jogador e mapa interativo 3D ausentes.
- [ ] Implementar inspeção de materiais, texturas, UVs, wireframe, sólido e texturizado — Parcial: modos e UV dos buffers aprovados no CI 45502974998; cobertura de materiais/compostos e revisão visual pendentes.
- [ ] Implementar visualização de normais, pivôs, colisões e LOD — Parcial: auxiliares e captura de colisões reais aprovados no CI 45502974998; bias medido, índices/troca dos LODs de produção e revisão visual pendentes.
- [ ] Implementar métricas de vértices, triângulos, materiais e dimensões reais — Parcial: métricas de arquivos e amostras runtime aprovadas no CI 45504785180. Dimensões de repouso e triângulos auditados nos GLBs no CI 45511716190; cobertura de composições pendente.
- [ ] Implementar animações, componentes articulados e controle de poses — Parcial: seis LODs skinned, pesos e controles de pose aprovados em 45528961593; 72 amostras combinadas dos GLBs 1aba84b9 passaram localmente, testes canônicos em 50579e2e. IK, animações de produção e limites articulares pendentes.
- [x] Implementar screenshots e versão offline sem CDN — PNG, ZIP de 10.563.017 bytes, servidor local e execução extraída com conexões externas bloqueadas aprovados no [CI 45502974998](https://github.com/TPollTech/Frontline-Survival/actions/runs/45502974998). Fundação funcional, sem homologação visual de modelos.
- [x] Implementar validação de geometria, normais, UVs, texturas e materiais — Fundação técnica validada: 17 testes, 32 GLBs, índices, atributos, degeneração, orientação das normais, PBR, UV e referências de imagens. CI 45511716190 identificou 31 avisos NORMAL_MISSING; legado não homologado. Extensões/sparse, decodificação completa e composições não cobertas. [Validação](VALIDACAO_ASSETS.md).
- [ ] Implementar validação de escala, orientação, pivôs, hierarquias e referências — Parcial: contratos de 14 pilotos e rigs contínuos aprovados em 45528961593; orientação frontal do atlas do personagem corrigida em f93d7076, novo teste pendente. Contratos de produção pendentes.
- [ ] Implementar validação de exportação, orçamento de polígonos e importação no Godot — Parcial: 39 GLBs da suíte 1aba84b9 aprovados no CI 45528961593 e três do balizador em 45528961605. Zero contatos nos rigs em repouso e poses individuais; 72 amostras combinadas dos GLBs aprovadas localmente. Benchmark e orçamento de produção pendentes.
- [x] Integrar validação, geração reproduzível e evidências ao CI — Workflow asset-validation.yml validado no CI 45511716190: 17 testes, duas exportações estritas reproduzíveis, auditoria e relatórios determinísticos, importação Godot e reconciliação SHA-256/triângulos 32/32, zero falhas impeditivas. Artefatos publicados; sem homologação visual. [Validação](VALIDACAO_ASSETS.md).
- [ ] Validar um asset piloto de cada categoria no Studio e no jogo — Parcial: CIs 45528961593 e 45528961629 aprovados, artefato 14982624984 aberto, oito capturas LOD0 inspecionadas. Zero contatos nos seis LODs em repouso e quatro poses individuais; 72 amostras combinadas locais aprovadas. Testes canônicos 50579e2e; atlas frontal corrigido f93d7076. Pages 45528961601 em execução ao registrar; novo Pages 45529734340 pendente. Sem homologação artística. [Pilotos](PILOTOS_ASSETS.md).
- [ ] Migrar todo o arsenal e acessórios para fontes canônicas — Parcial (25/11): índice de fontes reais e verificador isolado em main; 8 armas, 31 GLBs, 7 acessórios, 6 arquivos fonte/dependências, 9/9 verificações da lógica central em V8 com dados remotos. CI/CLI de checkout, reprodução dos GLBs, integração ao motor central/Studio, revisão visual Godot e benchmark pendentes. Nenhum GLB ou gameplay alterado. [Evidências](ARSENAL_FONTES_CANONICAS.md).
- [ ] Migrar personagens, mãos, equipamentos e aliados/inimigos — Parcial (25/11): cinco receitas geométricas compartilhadas por quatro consumidores reais, vínculo ao catálogo vivo e 10/10 verificações estáticas de preservação. Python/Godot/Studio e benchmark pendentes; CI sem cota, sem ativar pilotos ou substituir anatomia/rig. [Evidências](PERSONAGENS_FONTES_CANONICAS.md).
- [ ] Migrar objetos, estações, veículos, estruturas e elementos ambientais — Parcial (25/11): seis receitas visuais canônicas, quatro consumidores reais, cinco famílias no catálogo vivo, 12/12 verificações estáticas; veículo utility_cart permanece QA-only. Testes Python/Godot/Studio, paridade e benchmark pendentes; sem CI. [Evidências](OBJETOS_FONTES_CANONICAS.md).
- [ ] Migrar terreno, arquitetura, mapas completos e cenas compostas — Parcial (25/11): receita canônica de distribuição do Campo de Testes integrada à montagem real e ao catálogo vivo, 12/12 verificações estáticas (main reversível); QA headless e regressão de catálogo adicionados, não executados. Reconstrução Godot/Studio, navegação e benchmark pendentes; sem CI. [Evidências](MAPAS_FONTES_CANONICAS.md).
- [ ] Migrar objetos procedurais em runtime, colisões e efeitos 3D para o catálogo — Parcial (25/11): contrato de 13 papéis em 10 famílias, escopos de nós reais por amostra, validação de colisores e shader, catálogo e metadados de inspeção no Studio. 9/9 testes Python sintéticos aprovados. Captura Godot, catálogo integral, WebGL, efeitos em movimento/limpeza e desempenho pendentes. [Evidências](RUNTIME_FONTES_CANONICAS.md).
- [ ] Documentar arquitetura, comandos, extensão de categorias e política de QA
- [ ] Auditar cobertura integral do Studio e homologar o pipeline no jogo

## 01 — Correções urgentes

- [ ] Corrigir as iron sights flutuantes das snipers — Código e CI da v0.9.28 aprovados; revisão visual manual pendente.
- [ ] Restaurar e validar o ajuste de FOV — Código e release v0.9.29 publicados; revalidar na main atual.
- [ ] Padronizar o enquadramento de todas as armas — Código e release v0.9.30 publicados; revisão visual manual pendente.
- [ ] Separar o FOV da câmera do enquadramento das armas — Código e release v0.9.31 publicados; revisão visual manual pendente.
- [ ] Corrigir alinhamento das miras e lunetas — Código v0.9.32 na main; CI cancelado ou bloqueado pela falha posterior; validação pendente.
- [ ] Eliminar peças flutuantes, transparentes ou sobrepostas — Código v0.9.33 na main; CI cancelado ou bloqueado; validação pendente.
- [x] Testar individualmente todas as armas — QA automatizado 8/8 armas no CI 45504785421 (249 verificações individuais), revisão 446f31eb. Nova revisão dos modelos em validação; não equivale à homologação visual.
- [x] Corrigir falha do QA individual do arsenal na v0.9.34 — Carregamento diferido do jogador após GameSettings e referência relativa corrigidos. CI 45504785421 aprovado integralmente, QA_ARSENAL_PASS. Nova revisão dos modelos em validação.

## 02 — Modelagem 3D

- [ ] Desenvolver um padrão híbrido de modelagem 3D
- [ ] Remodelar completamente o arsenal
- [ ] Melhorar proporções e silhuetas das armas
- [ ] Implementar materiais PBR realistas
- [ ] Implementar texturas e normal maps
- [ ] Remodelar mãos, dedos, luvas e antebraços
- [ ] Implementar rig anatômico e IK
- [ ] Corrigir encaixes das mãos nas armas
- [ ] Remodelar soldados e equipamentos
- [ ] Remodelar objetos e estruturas do cenário

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
