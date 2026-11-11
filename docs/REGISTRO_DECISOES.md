# Frontline Survival — Registro de Decisões e Propostas

**Atualizado:** 10/11/2026  
**Propósito:** registrar o que o usuário já definiu, separar propostas ainda sem aprovação e impedir mudanças acidentais nas regras do jogo.

## Convenções

- **APROVADO / ESTABELECIDO:** requisito explicitamente definido ao longo do planejamento e do teste das versões 0.1–0.7.
- **PROPOSTO:** sugestão de projeto que ainda pode mudar e não autoriza implementação automática.
- **PENDENTE:** depende de experiência no jogo, medição ou escolha posterior.
- **IMPLEMENTADO MAS NÃO VALIDADO:** consta no código atual, mas não passou por teste real no Godot neste ciclo.

## A. Decisões estabelecidas

| Código | Decisão | Implicações |
| --- | --- | --- |
| D-001 | Jogo solo FPS 3D focado exclusivamente no modo Survival por ondas | Não há campanha nem mundo aberto no jogo base |
| D-002 | Inspiração nas mecânicas de Survival do MW3 (2011) com identidade original | Não copiar modelos, mapas, sons ou interface protegidos |
| D-003 | Loop contínuo de ondas | Concluir onda nunca deve encerrar partida |
| D-004 | Preparação de cerca de um minuto ou pouco mais; valor adotado de 75 segundos | Jogador compra, recarrega e se reposiciona entre ondas |
| D-005 | Campo de Testes atual será permanente | Preservar mapa, funcionalidade de laboratório e textura de asfalto |
| D-006 | Criar futuramente mapas dedicados com vários setores | Planejar rotas, spawns, setores e lojas antes de produzir artes |
| D-007 | Compras por estações físicas com F | Não reintroduzir menu global de compras no B |
| D-008 | Atalhos de ativação para suporte e esquadrão comprados | Conservar a configuração de trabalho 3 = esquadrão, 4 = aéreo |
| D-009 | Soldados variam armamento conforme as ondas | Progredir de kits de curta distância a kits de maior alcance, sem só aumentar HP |
| D-010 | Armas precisam ser reconhecíveis, com disparo sem esfera amarela exagerada | Refinar modelos, mãos, animações e VFX |
| D-011 | HUD essencial e discreto; sem lista fixa de controles durante partida | Vida, colete, munição, dinheiro, onda e avisos contextualizados |
| D-012 | Configurações de volume, principalmente efeitos de tiro | Evitar clipping e salvar preferências |
| D-013 | Notebook-alvo Ryzen 5 7530U + Radeon integrada + 8 GB | Medir desempenho e otimizar desde o início |
| D-014 | Planejar e registrar em Markdown antes de implementar novas etapas | Mudanças devem ter escopo, aceite e revisão de QA |
| D-015 | GitHub oficial: TPollTech/Frontline-Survival | Documentação e código versionados com commits claros |
| D-016 | Jogador solicitou retirar a crosshair e alinhar a mira física ADS | Não reintroduzir retícula como padrão; validar mira com a arma e tiro no centro |

## B. Configurações presentes no protótipo 0.7

Estas são características descritas no código/README, não equivalem a comprovação de execução: cinco classes de armas, três estações de compras, capital de treino de $1.200, intervalo de ondas configurável de 45 a 120s, N para antecipar, reanimação opcional, suporte, esquadrão, menus e preferências persistentes.

**Status real:** implementação registrada; execução de ponta a ponta no Godot ainda não aferida aqui.

## C. Propostas ainda não aprovadas

| Código | Proposta | Documento | Decisão necessária |
| --- | --- | --- | --- |
| P-001 | Matriz de 27 testes e validação de 15 ondas | [Etapa 0](ETAPA_0_ESTABILIZACAO.md) | Aprovar padrão de QA e executar |
| P-002 | Meta inicial de 30 FPS em 720p baixo, buscando 60 nas situações comuns | [Etapa 0](ETAPA_0_ESTABILIZACAO.md) | Medir e decidir compromisso visual |
| P-003 | Estilo "realismo estilizado" militar de geração PS3/Xbox 360 | [Etapa 1](ETAPA_1_FPS_ARMAS.md) | Aprovar direção visual |
| P-004 | Fuzil como arma piloto da biblioteca de animações | [Etapa 1](ETAPA_1_FPS_ARMAS.md) | Aprovar ordem de produção |
| P-005 | Rig leve de mãos/antebraços e estados completos de FPS | [Etapa 1](ETAPA_1_FPS_ARMAS.md) | Aprovar padrão e nível de detalhe |
| P-006 | Faixas iniciais de capacidade, cadência e comportamento por classe | [Etapa 1](ETAPA_1_FPS_ARMAS.md) | Validar após testes de sensação |
| P-007 | Primeiro mapa definitivo "Complexo Industrial" com setores definidos | [Plano de mapas](PLANO_MAPAS.md) | Aprovar layout depois do núcleo |
| P-008 | Separar main.gd em módulos após estabilizar | [Etapa 0](ETAPA_0_ESTABILIZACAO.md) | Decidir necessidade a partir de bugs |
| P-009 | Manter até 12 inimigos ativos inicialmente, aguardando benchmark | [Etapa 2](ETAPA_2_INIMIGOS_ONDAS.md) | Medir FPS/CPU em 720p antes de elevar teto |
| P-010 | Composição gradual por armamento e ondas marco 10/15/20 com pesado anunciado | [Etapa 2](ETAPA_2_INIMIGOS_ONDAS.md) | Aprovar faixas, marcos e regras de contrajogo |
| P-011 | IA com percepção, navegação anti-travamento e flanco simples | [Etapa 2](ETAPA_2_INIMIGOS_ONDAS.md) | Validar custo e implementação incremental |
| P-012 | Spawn contextual com distância mínima inicial sugerida de 10 metros | [Etapa 2](ETAPA_2_INIMIGOS_ONDAS.md) | Ajustar pelo mapa e executar 100 testes de spawn |

| P-013 | Economia sem softlock nas primeiras ondas | [Etapa 3](ETAPA_3_ECONOMIA_SUPORTE.md) | Validar saldo inicial e munição em sessões reais |
| P-014 | Três decisões concorrentes: armas, sobrevivência e suporte | [Etapa 3](ETAPA_3_ECONOMIA_SUPORTE.md) | Aprovar princípios de balanceamento |
| P-015 | Diferenciar capital do treino ($1.200) e modo clássico ($0–$300 a testar) | [Etapa 3](ETAPA_3_ECONOMIA_SUPORTE.md) | Aprovar saldo clássico após teste |
| P-016 | Preços estáveis inicialmente, sem inflação automática por onda | [Etapa 3](ETAPA_3_ECONOMIA_SUPORTE.md) | Balancear 20 ondas |
| P-017 | Compra transacional: validar antes de debitar, sem cobrança em falhas | [Etapa 3](ETAPA_3_ECONOMIA_SUPORTE.md) | Aprovar contrato e testes |
| P-018 | Interface física com efeito, duração, preço, limite e estado legíveis | [Etapa 3](ETAPA_3_ECONOMIA_SUPORTE.md) | Aprovar proposta de UX |
| P-019 | Complexo Industrial com cinco setores e duas camadas de altura | [Etapa 4](ETAPA_4_MAPAS_ARQUITETURA.md) | Aprovar layout e ajustar tamanho após blockout |
| P-020 | Estações distribuídas entre galpão, oficina e administração | [Etapa 4](ETAPA_4_MAPAS_ARQUITETURA.md) | Medir acesso nos 75 segundos de preparação |
| P-021 | Um mapa definitivo na primeira versão completa, além do Campo de Testes | [Etapa 4](ETAPA_4_MAPAS_ARQUITETURA.md) | Aprovar escopo fechado de lançamento |
| P-022 | Cenas de mapa independentes, MapLoader e recordes por mapa e modo | [Etapa 4](ETAPA_4_MAPAS_ARQUITETURA.md) | Aprovar contrato e migração sem regressão |

| P-023 | Hierarquia do HUD, estados de menus e feedback contextual | [Etapa 5](ETAPA_5_HUD_AUDIO_ACESSIBILIDADE.md) | Aprovar após avaliação visual em 720p |
| P-024 | Buses de áudio, acessibilidade e presets gráficos efetivos | [Etapa 5](ETAPA_5_HUD_AUDIO_ACESSIBILIDADE.md) | Validar mixagem, preferências e hardware-alvo |
| P-025 | Resultados e estatísticas locais sem misturar modos/mapas | [Etapa 5](ETAPA_5_HUD_AUDIO_ACESSIBILIDADE.md) | Aprovar dependência dos recordes da Etapa 4 |

| P-026 | Metas de 30 FPS piso/60 desejáveis, 720p baixo, medições em triplicata | [Etapa 6](ETAPA_6_DESEMPENHO_TESTES_DISTRIBUICAO.md) | Aprovar metas e executar benchmark real |
| P-027 | Profiling antes de otimizar IA/render e manter teto inicial de inimigos | [Etapa 6](ETAPA_6_DESEMPENHO_TESTES_DISTRIBUICAO.md) | Aprovar ordem e validar hardware |
| P-028 | Matriz de 18 testes integrados, 15 ondas e sessão prolongada | [Etapa 6](ETAPA_6_DESEMPENHO_TESTES_DISTRIBUICAO.md) | Aprovar gates e executar testes |
| P-029 | Gates de release CI → Windows → regressão longa → publicação | [Etapa 6](ETAPA_6_DESEMPENHO_TESTES_DISTRIBUICAO.md) | Aprovar critérios de estabilidade |

## D. Fora de escopo por enquanto

- Multiplayer e coop.
- Campanha com história.
- Mundo aberto ou mapas gigantescos sem setores.
- Fotorrealismo pesado, ray tracing e dependência de GPU dedicada.
- Adições de novas mecânicas enquanto existirem P0 na Etapa 0.
- Mapas definitivos sem validar primeiro o núcleo de combate e o orçamento de desempenho.

## E. Como atualizar este registro

1. Ao surgir uma ideia, adicionar como PROPOSTA com documento e justificativa.
2. Após aprovação explícita, mover para ESTABELECIDO e registrar data/impacto.
3. Se a decisão afetar escopo ou desempenho, atualizar ROADMAP e critério de aceite.
4. Implementar somente na etapa correspondente, com revisão e testes.
5. Registrar mudança de decisão como uma nova linha; preservar histórico dos motivos.

## F. Próxima rodada de planejamento

A **Etapa 2 — inimigos e progressão de ondas** foi especificada em 10/11/2026, sem implementação e sem aprovação das propostas. A **Etapa 4 — arquitetura e mapa multissetores** também foi especificada em 10/11/2026, sem alteração do jogo. A **Etapa 5 — interface, HUD, áudio e acessibilidade** foi especificada em 10/11/2026, ainda sem aprovação. A **Etapa 6 — desempenho, testes e distribuição** foi especificada em 10/11/2026, com propostas P-026–P-029 ainda pendentes. **GDD mestre consolidado em 11/11/2026:** [GDD_MESTRE.md](GDD_MESTRE.md) — **GDD PRONTO PARA REVISÃO**, não aprovado. Auditoria C-01–C-06; próximas execuções apenas verificam decisões novas ou conflitos resolvidos, sem repetir documentos. A Etapa 3 mantém suas propostas de economia e suporte pendentes de aprovação. As Etapas 0 e 1 continuam especificadas, mas ainda não testadas/aprovadas para implementação.
