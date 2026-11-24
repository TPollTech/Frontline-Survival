# Frontline Survival — Checklist mestre até a versão 1.0

Atualizado em 24/11/2026. Mantém as 96 tarefas anteriores e adiciona a fundação de modelagem/Studio e a regressão de QA. Fonte de requisitos: [especificação obrigatória](ASSET_STUDIO_SPEC.md). Estado verificado: main v0.9.34 de desenvolvimento; última release v0.9.31; [CI do arsenal corrigido e aprovado](https://github.com/TPollTech/Frontline-Survival/actions/runs/45504785421) na revisão 446f31eb. Nova revisão de assets posterior em revalidação. Priorizar 00. Estados: [ ] pendente/parcial; [x] somente tarefa integralmente validada. Os trabalhos anteriores não são descartados; reavaliar na arquitetura nova. Nenhuma homologação visual manual foi confirmada nesta revisão.

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
- [ ] Implementar colisões independentes e LOD com orçamentos por categoria — Parcial: relatório de orçamento e seletor runtime com histerese; nove verificações aprovadas no [Godot 45504658358](https://github.com/TPollTech/Frontline-Survival/actions/runs/45504658358), colisor invariável; preload relativo revalidado no CI 45504785018. Integração em produção e benchmark pendentes. [Biblioteca](BIBLIOTECA_PARAMETRICA.md).
- [x] Implementar exportação determinística GLB/glTF 2.0 e rastreabilidade de fontes — Fundação validada: 117/117 testes Blender/Python, manifesto de fontes canônico, reprodução byte a byte e importação de ambos os formatos no [Godot CI 45501055855](https://github.com/TPollTech/Frontline-Survival/actions/runs/45501055855). Dois joints autorais e helper sem peso conferidos. Sem homologação de assets de produção. [Biblioteca](BIBLIOTECA_PARAMETRICA.md).
- [ ] Implementar descoberta automática e catálogo de todos os assets reais — Parcial: 14/14 testes, 52 registros, 100 recursos, 86 amostras; integração Studio aprovada no CI 45504785180. Quatro referências dinâmicas e buffers procedurais pendentes. [Catálogo](CATALOGO_VIVO.md).
- [ ] Criar Asset Studio HTML/CSS/JS com Three.js e WebGL — Parcial: CI 45504785180 aprovou 32 GLBs, 86 amostras reconciliadas, cinco vistas reais e ZIP offline. Composições 3D runtime e revisão visual pendentes; nova revisão dos assets em validação.
- [x] Implementar iluminação HDRI, sombras, antialiasing, sRGB, ACES e piso técnico — 32/32 GLBs e controles aprovados no [CI 45473901798](https://github.com/TPollTech/Frontline-Survival/actions/runs/45473901798), duas capturas reais inspecionadas. Sem homologação de modelos ou benchmark.
- [x] Implementar OrbitControls, damping, enquadramento por bounding box, zoom, pan e reset — 32/32 GLBs, interação, resize e reset aprovados no CI 45475002613; capturas inspecionadas.
- [x] Implementar seis vistas ortográficas, perspectiva e tela cheia — seis eixos, fullscreen e retorno aprovados no CI 45475002613; capturas inspecionadas.
- [ ] Implementar vistas reais de primeira e terceira pessoa e prévia de mapas completos — Parcial: cinco capturas reais aprovadas no CI 45502974998, incluindo colisões; TPS nativo do jogador e mapa interativo 3D ausentes.
- [ ] Implementar inspeção de materiais, texturas, UVs, wireframe, sólido e texturizado — Parcial: modos e UV dos buffers aprovados no CI 45502974998; cobertura de materiais/compostos e revisão visual pendentes.
- [ ] Implementar visualização de normais, pivôs, colisões e LOD — Parcial: auxiliares e captura de colisões reais aprovados no CI 45502974998; bias medido, índices/troca dos LODs de produção e revisão visual pendentes.
- [ ] Implementar métricas de vértices, triângulos, materiais e dimensões reais — Parcial: métricas de arquivos e amostras runtime aprovadas no CI 45504785180. Dimensões de repouso e triângulos auditados nos GLBs no CI 45511716190; cobertura de composições pendente.
- [ ] Implementar animações, componentes articulados e controle de poses — Parcial: interpolação e restauração de pose aprovadas no CI 45502974998; animação procedural Godot, limites articulares e revisão visual pendentes.
- [x] Implementar screenshots e versão offline sem CDN — PNG, ZIP de 10.563.017 bytes, servidor local e execução extraída com conexões externas bloqueadas aprovados no [CI 45502974998](https://github.com/TPollTech/Frontline-Survival/actions/runs/45502974998). Fundação funcional, sem homologação visual de modelos.
- [x] Implementar validação de geometria, normais, UVs, texturas e materiais — Fundação técnica validada: 17 testes, 32 GLBs, índices, atributos, degeneração, orientação das normais, PBR, UV e referências de imagens. CI 45511716190 identificou 31 avisos NORMAL_MISSING; legado não homologado. Extensões/sparse, decodificação completa e composições não cobertas. [Validação](VALIDACAO_ASSETS.md).
- [ ] Implementar validação de escala, orientação, pivôs, hierarquias e referências — Parcial: contratos de dimensão, pivô e direção, transforms, AABB e hierarquia validados em fixture GLB/glTF; testes negativos aprovados no CI 45511716190. Contratos físicos e semânticos dos assets reais e composições pendentes. [Validação](VALIDACAO_ASSETS.md).
- [ ] Implementar validação de exportação, orçamento de polígonos e importação no Godot — Parcial: exportação reproduzível GLB/glTF, fonte/hash, orçamentos provisórios por arquivo, 32/32 importações e 32/32 contagens coincidentes no CI 45511716190. Orçamento agregado por instância/LOD e benchmark físico pendentes. [Validação](VALIDACAO_ASSETS.md).
- [x] Integrar validação, geração reproduzível e evidências ao CI — Workflow asset-validation.yml validado no CI 45511716190: 17 testes, duas exportações estritas reproduzíveis, auditoria e relatórios determinísticos, importação Godot e reconciliação SHA-256/triângulos 32/32, zero falhas impeditivas. Artefatos publicados; sem homologação visual. [Validação](VALIDACAO_ASSETS.md).
- [ ] Validar um asset piloto de cada categoria no Studio e no jogo
- [ ] Migrar todo o arsenal e acessórios para fontes canônicas
- [ ] Migrar personagens, mãos, equipamentos e aliados/inimigos
- [ ] Migrar objetos, estações, veículos, estruturas e elementos ambientais
- [ ] Migrar terreno, arquitetura, mapas completos e cenas compostas
- [ ] Migrar objetos procedurais em runtime, colisões e efeitos 3D para o catálogo
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
