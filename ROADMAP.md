# Frontline Survival — Planejamento e Roadmap

**Documento mestre do projeto** · Atualizado: 10/11/2026 · **Base de referência:** protótipo `0.7`; **versão de desenvolvimento:** `0.9.1` · **Situação:** planejamento; novas mecânicas somente após aprovação da etapa.

> **Visão:** FPS 3D offline de sobrevivência por ondas, com combate satisfatório, progressão, dinheiro, compras em estações e suporte tático. Inspiração de mecânicas: Survival dos FPS militares da geração PS3, com identidade, modelos, efeitos e sons próprios. **Não** copiar mapas, arquivos ou personagens de Call of Duty.

## 1. Regras do produto que não podem se perder

1. **Partida contínua:** inimigos aparecem por ondas; ao eliminar todos, há preparação; depois começa automaticamente a próxima onda. Não encerrar a partida ao concluir uma onda.
2. **Preparação utilizável:** padrão **75 s**, ajustável de 45 a 120 s; avisos de contagem; tecla `N` para antecipar apenas se o jogador escolher. Na preparação é possível andar, comprar, recarregar e preparar defesas.
3. **Campo de Testes permanente:** mapa atual com textura do asfalto preservado. Usado para testar física, IA, armas, efeitos e métricas. Mapas definitivos serão separados, com vários setores e rotas.
4. **Lojas físicas:** acessar com `F` próximo de cada estação. **Não** voltar com o menu global de compras no `B`. Ataque aéreo, esquadrão e outros recursos são comprados na estação de suporte e acionados por atalhos depois.
5. **Dois modos de morte:** no Campo de Testes, reanimação opcional preserva onda/armas/dinheiro para ensaiar; no Survival clássico, a morte encerra a partida e mostra recorde.
6. **HUD discreto:** vida, colete, munição, créditos, onda/fase, inimigos restantes e avisos contextuais; sem painel fixo com lista de atalhos.
7. **Áudio controlável:** volume geral, combate e UI separados; sem sons estourados; configurações persistentes.
8. **Alvo de hardware:** Ryzen 5 7530U, GPU Radeon integrada e **8 GB RAM**; renderizador Godot **Compatibility** como referência. Otimização durante cada etapa.
9. **Não quebrar sistemas aprovados:** cada atualização precisa preservar ondas, compras, reforços, tela de pausa, configurações e mapa atual.
10. **Processo novo:** planejar -> revisar escopo -> implementar uma etapa -> testar no Godot -> validar no notebook -> documentar -> commit. Não introduzir várias mecânicas sem teste.

## 2. Estado atual e débito técnico (protótipo 0.7)

| Subsistema | O que existe | O que falta validar / melhorar |
| --- | --- | --- |
| FPS / jogador | Movimentação, mira, recarga, armas modulares, recuo procedural | Sensação de peso, câmera, colisões, animações de mãos com rig e transições |
| Combate | Cinco classes de armas, tiros, headshot, impacto, granada | Cadência consistente, diferenças entre armas, efeitos realistas, áudio espacial, feedback de dano |
| Inimigos | IA de perseguição, armas por faixa de onda, reações e articulações | Navegação, cobertura simples, não atravessar obstáculos, comportamento de grupo, variedade visual |
| Ondas | Loop contínuo e preparação de 75 s | Teste prolongado (15+ ondas), spawn seguro, progressão equilibrada e consistência do contador |
| Economia | Dinheiro, compras nas três estações, armas/equipamentos/suporte | Preços e recompensas balanceados, comparação de armas e feedback de compra |
| Reforços | Torretas, esquadrão, ataque aéreo | Comportamentos previsíveis, indicadores claros, chamadas sem conflito de teclas |
| HUD/menus | Vida, colete, munição, onda, créditos; pausa/configurações | Hierarquia visual, fontes, estados, acessibilidade e mensagens curtas |
| Gráficos | Mapa de testes, asfalto, armas e personagens procedurais | Modelos 3D mais críveis, materiais, silhuetas, LOD, animação e iluminação |
| Qualidade | Verificador estático e guia de testes | **Execução real do Godot ainda não confirmada neste ambiente**, testes automatizados e perfil de FPS |

**Critério mínimo para considerar uma versão estável:** sem erros no Debugger, pelo menos 15 ondas completas sem travar, compras e acionamentos testados, sem perda involuntária de progresso no modo de teste, menus e áudio funcionando após reiniciar, FPS medido em combate.

## 3. Prioridades e ordem de execução

### Etapa 0 — Estabilização e base de qualidade (P0, primeiro trabalho)

- [ ] Importar o projeto 0.7 em Godot 4.x Standard e registrar erros/avisos reais.
- [ ] Criar checklist de regressão: início, tiro, headshot, compra, troca, recarga, reforços, morte, revive, pausa e ondas 1–15.
- [ ] Verificar principalmente transição após matar último inimigo (não dar "Fim de Jogo" por engano).
- [ ] Padronizar componentes e separar, gradualmente, o `main.gd` em gerenciadores de onda, economia, HUD, lojas e efeitos; refatorar sem alterar jogabilidade.
- [ ] Adicionar indicador de versão e FPS de depuração desativável.
- [ ] Criar teste básico de abertura do projeto e análise de scripts no Godot (headless/CI, quando disponível).

**Pronto quando:** a versão abre sem erros, permite comprar a LMG e sobreviver/avançar 15 ondas consecutivas; o modo clássico encerra apenas por morte; não há regressões P0.

### Etapa 1 — Sensação de FPS e qualidade das armas (P1)

- [ ] Definir regras por categoria: cadência, dano, recuo vertical/horizontal, dispersão, alcance, troca e recarga.
- [ ] Refinar posição da arma em primeira pessoa, mira ADS, sway/bob e câmera sem excesso de movimento.
- [ ] Substituir mãos geométricas por modelo anatômico leve, com mãos/antebraços consistentes e rig de animação.
- [ ] Recriar flashes discretos na boca, ejeção de cartucho, fumaça breve e decalques/impactos por superfície; nenhuma esfera amarela gigante.
- [ ] Sons de arma espacializados e equalizados sem clipping; controle de volume separado.
- [ ] Feedback claro de acerto, headshot, dano recebido e falta de munição.

**Pronto quando:** pistola, SMG, fuzil, escopeta e LMG são distinguíveis ao mirar, atirar, ouvir, recarregar e se mover; a cena permanece legível mesmo com efeitos simultâneos.

### Etapa 2 — Inimigos, combate e dificuldade por ondas (P1)

- [ ] Planejar arquétipos: escopeteiro, SMG, fuzileiro, blindado, metralhador e especial.
- [ ] Evolução de armas por faixas (não apenas aumentar HP): 1–3 introdutória; 4–6 SMG; 7–10 mistura; 11–15 fuzis; 16+ combinações; ajustar após testes.
- [ ] Criar composição de grupos, intervalos de spawn, limites simultâneos e inimigos especiais em ondas definidas.
- [ ] Navegação 3D com prevenção de travas, colisão e lógica de aproximação/flanqueamento simples.
- [ ] Soldados com silhuetas e equipamentos distintos, animações leves de locomoção, disparo, dano e morte.
- [ ] Balancear munição, economia e dificuldade para evitar ondas impossíveis ou tediosas.

**Pronto quando:** as armas inimigas mudam de forma visível/audível ao avançar ondas; não há spawns dentro do jogador nem bloqueio permanente que impeça o término de uma onda.

### Etapa 3 — Economia, estações e suporte tático (P1)

- [ ] Interface de loja física rápida, navegável com mouse e teclado, comparação e compra com feedback claro.
- [ ] Ajustar preços e economia com dados reais de 10–20 ondas de teste.
- [ ] Granadas, mina, proteção e cura com regras de inventário claras.
- [ ] Torretas com limites, duração, posicionamento e indicação de munição/vida.
- [ ] Esquadrão aliado com duração, comandos simples e identificação clara.
- [ ] Ataque aéreo com mira/área indicada, aviso antes do impacto e efeitos otimizados.
- [ ] Personalização simples de armas em estação (miras/carregador) apenas após núcleo estável.

**Pronto quando:** comprar, equipar e usar cada opção não interrompe ondas, não tira o controle da câmera indevidamente e informa custo/resultado.

### Etapa 4 — Primeiro mapa definitivo com setores (P2)

- [ ] Documento de layout (*blockout*) antes de modelar detalhes: tamanho, pontos de spawn, rotas e estações.
- [ ] Mapa 01 **Complexo Industrial**: pátio, depósito, galpão, administração e setor de manutenção conectados por múltiplas rotas.
- [ ] Criar posições de defesa variadas, linhas de visão, flancos, cobertura e caminhos de fuga.
- [ ] Definir setores por área para otimizar spawn, culling e IA sem telas de carregamento entre ondas.
- [ ] Testar colisões, acessibilidade de lojas e navegação dos inimigos em todo o mapa.
- [ ] Adicionar um seletor de mapas, mantendo **Campo de Testes** como opção de desenvolvimento.
- [ ] Só depois: Mapa 02 urbano e cenários adicionais.

**Pronto quando:** uma partida completa funciona em todos os setores e o FPS fica dentro do orçamento de desempenho.

### Etapa 5 — Menus, HUD, experiência e audiovisual (P2)

- [ ] HUD compacto e escalável em 720p/900p/1080p; evitar excesso de números e dicas.
- [ ] Telas de início, pausa, morte clássica, recordes, estatísticas e configurações completas.
- [ ] Informações entre ondas: número, tempo até próxima, recompensa e compras disponíveis.
- [ ] Sons ambientes, trilha opcional e efeitos de alerta; ajustes de volume salvos.
- [ ] Qualidade gráfica configurável (sombras, partículas, resolução/escala), sem opções falsas.
- [ ] Acessibilidade básica: tamanho do HUD, indicador de dano, opções de sensibilidade/FOV.

**Pronto quando:** o jogo pode ser usado sem consultar o README para entender os elementos essenciais do HUD e das lojas.

### Etapa 6 — Performance, testes e distribuição (P0 transversal; entrega P2)

- [ ] Medir CPU, GPU, RAM e FPS no Ryzen 5 7530U / 8 GB em repouso, onda 5, 10, 15 e com reforços.
- [ ] Meta inicial: **30 FPS estáveis como piso de jogabilidade em 720p baixo**, buscando **60 FPS** em condições comuns. **São metas, não benchmarks já medidos.**
- [ ] Ajustar LOD, distância de visão, materiais, draw calls, partículas, luzes e limite de IA.
- [ ] Evitar vazamentos de instâncias de projéteis/efeitos e reinicializações que quebrem o estado da partida.
- [ ] Criar exportação Windows e checklist de instalação sem exigir editor Godot para jogar.
- [ ] Documentar falhas conhecidas e versões com changelog.

**Pronto quando:** build Windows inicia no notebook, mantém o piso de desempenho medido nos cenários-alvo e resiste a uma sessão longa sem degradação contínua.

## 4. Backlog futuro (não implementar antes do núcleo)

- [ ] Mais mapas com temas e estratégias distintas.
- [ ] Novas armas, acessórios e armaduras.
- [ ] Inimigos especiais, helicóptero e chefes com anúncios e contrajogo.
- [ ] Desafios, conquistas, estatísticas e ranking local.
- [ ] Coop local/rede **somente depois** de validar o jogo solo e a arquitetura.
- [ ] Efeitos climáticos e horário do dia, se couberem no orçamento gráfico.

## 5. Processo de trabalho por etapa

1. **Planejar:** abrir/atualizar esta checklist com descrição, mudanças propostas, riscos, dependências e critérios de aceite.
2. **Aprovar:** revisar a proposta antes de alterar scripts. Alterações sem aceite ficam em backlog.
3. **Implementar isoladamente:** branch específica da etapa; commits com mensagens claras; sem misturar sistemas não relacionados.
4. **Verificar:** rodar check estático + abrir Godot + smoke test no notebook; registrar resultados reais (sem inventar números de FPS).
5. **Entregar:** atualizar README/roadmap/changelog, gerar ZIP executável ou projeto, informar limitações e concluir merge.

**Convenção sugerida de branches:** `feat/fps-armas`, `feat/ia-ondas`, `feat/mapa-industrial`, `fix/loop-ondas`, `docs/roadmap`.

**Regra de versão:** mudanças pequenas `0.7.x`; etapas novas jogáveis `0.8`, `0.9`, etc. Evitar subir número sem experiência validada.

## 6. Próxima decisão

**Próximo trabalho recomendado: validar a 0.9 visualmente no Windows.** A 0.8 já foi aberta pelo usuário e a captura mostra preparação da onda 2 com 138 FPS instantâneos. A 0.9 corrige malhas com normais invertidas e poses de armas/soldados. Confirmar visual, jogabilidade, 15 ondas, compras, morte, revive e desempenho antes de encerrar as Etapas 0–2.

**Status:** entregas pequenas comprovadas em CI são **CONCLUÍDAS (CI)**; funcionalidades implementadas sem teste de partida são **PARCIAIS**; uma etapa inteira não é marcada como concluída sem seus critérios de aceite.

## 7. Especificações e registro de decisões (planejamento)

Os documentos abaixo detalham critérios e hipóteses sem autorizar implementação automática:

- [Etapa 0 — Estabilização e qualidade](docs/ETAPA_0_ESTABILIZACAO.md): matriz de testes, sessão de 15 ondas, defeitos bloqueantes e desempenho.
- [Etapa 1 — FPS, armas e animações](docs/ETAPA_1_FPS_ARMAS.md): direção visual proposta, arma piloto, feedback, áudio e critérios de aceitação.
- [Etapa 2 — Inimigos, IA e progressão de ondas](docs/ETAPA_2_INIMIGOS_ONDAS.md): arquétipos, faixas de armas, diretor de ondas, spawn seguro, navegação e matriz de testes.
- [Etapa 3 — Economia, estações e suporte tático](docs/ETAPA_3_ECONOMIA_SUPORTE.md): inventário 0.7, transações, limites, torretas, esquadrão, ataque aéreo, balanceamento e QA.
- [Etapa 4 — Mapas multissetoriais e arquitetura](docs/ETAPA_4_MAPAS_ARQUITETURA.md): Complexo Industrial (cinco setores propostos), rotas, lojas, spawn, MapLoader, desempenho e 18 cenários de QA.
- [Etapa 5 — HUD, menus, áudio e acessibilidade](docs/ETAPA_5_HUD_AUDIO_ACESSIBILIDADE.md): hierarquia de informações, estados, mixagem, configurações, acessibilidade e 18 testes pendentes.
- [Etapa 6 — Desempenho, testes e distribuição Windows](docs/ETAPA_6_DESEMPENHO_TESTES_DISTRIBUICAO.md): orçamento proposto de FPS/RAM, 18 testes, gates CI/Windows/15 ondas/release e dependências.
- [Registro de decisões e propostas](docs/REGISTRO_DECISOES.md): requisitos já estabelecidos versus ideias pendentes.
- [Plano de mapas](docs/PLANO_MAPAS.md): Campo de Testes permanente e proposta de mapa multissetores.
- [Testes de regressão existentes da 0.7](docs/TESTES_0_7.md): roteiro técnico anterior, complementado pela Etapa 0.

**Observação:** nenhuma tarefa de QA foi marcada como concluída apenas por escrever estes documentos. Não foram alterados scripts, cenas, modelos ou áudio nesta atualização documental.

## 8. Acompanhamento da pré-produção

| Documento | Situação documental | Implementação e QA |
| --- | --- | --- |
| Etapa 0 — Estabilidade | Especificada; 27 verificações de QA | **PARCIAL** — importação Godot 4.4.1, análise de scripts, integridade estática e exportação Windows passaram no CI; teste jogando 15 ondas no notebook pendente |
| Etapa 1 — Armas e FPS | Especificada; propostas aguardam aprovação | **PARCIAL** — v0.9.1 aplica paleta COLOR_0, visor físico centrado e recuo pós-raycast; inspeção visual e rig profissional pendentes |
| Etapa 2 — Inimigos e ondas | **Especificada em 10/11/2026**; propostas aguardam aprovação | **PARCIAL** — v0.9.1 usa IK de dois segmentos e modelos de arma coloridos em aliados/inimigos; IA de ondas ainda pendente |
| Etapa 3 — Economia e reforços | **Especificada em 10/11/2026**; preços finais e propostas pendentes de aprovação | Não iniciada |
| Etapa 4 — Mapas | **Especificada em 10/11/2026**; layout de cinco setores e arquitetura ainda sujeitos a aprovação | Não iniciada |
| Etapa 5 — HUD, áudio e UX | **Especificada em 10/11/2026**; propostas aguardam aprovação | **PARCIAL** — v0.9.1 retira crosshair/hit beep e adiciona som grave de fim de onda; validação auditiva pendente |
| Etapa 6 — desempenho e distribuição | **Especificada em 10/11/2026**; metas e gates pendentes de aprovação | **PARCIAL** — release [v0.9.1](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.1) e CI aprovados; benchmark/15 ondas pendentes |
| GDD consolidado | **Ainda não concluído**; consolidar após as etapas | Não aplicável |

**Último avanço de produto:** versão 0.9 compilada e publicada no GitHub Actions, com 19 arquivos GLB regenerados e sincronizados na main. A versão 0.8 foi executada pelo usuário até a preparação da onda 2; a 0.9 exige validação visual/jogabilidade no Windows. Etapa 6 especificada documentalmente; próximo passo é consolidar o GDD mestre e conferir decisões pendentes. Sem alteração de código nesta rodada documental.

## 9. Registro de implementação e evidências — 0.8 (10/11/2026)

| ID | Incremento | Estado verificável | Evidência / pendência |
| --- | --- | --- | --- |
| V08-01 | Indicadores de ataque frente/direita/trás/esquerda | **PARCIAL** | Implementado em player.gd, enemy.gd e main.gd; ainda não observado no Windows real |
| V08-02 | Feedback âmbar de headshot na retícula | **PARCIAL** | Implementado em main.gd; validar acertando a cabeça em jogo |
| V08-03 | Menu e título com versão 0.8 | **PARCIAL** | Código atualizado; verificar aparência ao jogar |
| V08-08 | Movimento de mira ADS com velocidade e recuo distintos | **PARCIAL** | Código implementado no jogador, requer sensação de uso no Windows |
| V08-09 | Retícula dinâmica por dispersão das rajadas | **SUBSTITUÍDA NA 0.9.1** | Crosshair 2D removida a pedido do jogador; mira pelo visor da arma |
| V08-10 | Smoke test da cena principal no Godot headless | **CONCLUÍDO (CI)** | Importação, inicialização headless e exportação Windows passaram na execução 42936566841 |
| V08-04 | Exportador automático Windows via GitHub Actions | **CONCLUÍDO (CI)** | [Execução bem-sucedida](https://github.com/TPollTech/Frontline-Survival/actions/runs/42936566841), com artefato EXE + PCK |
| V08-05 | Importação Godot e checagens estáticas no CI | **CONCLUÍDO (CI)** | Steps de importação, testes e exportação aprovados na mesma execução |
| V08-06 | Executável jogado e aprovado no Windows | **PARCIAL** | Usuário confirmou execução da 0.8 e enviou captura na preparação para onda 2; testes completos e validação de arma/IA pendentes |
| V08-07 | Estabilidade de 15 ondas com compras/reforços | **PENDENTE** | Regressão longa da Etapa 0 ainda não executada pelo jogador |

**Regra das próximas versões:** entregar, quando houver build bem-sucedida, um ZIP Windows com EXE + PCK (se separado); anexar o link de build, changelog, status de cada tarefa e evidências. Se o workflow falhar, não chamar a versão de jogável. Documentos de planejamento continuam separados das entregas codificadas.

[Download/testes do executável](docs/BUILD_WINDOWS.md) · [Histórico de versões](docs/CHANGELOG.md)

## 10. Sprint visual 0.9 — feedback recebido no Windows

**Origem:** jogador executou a 0.8 e mostrou a preparação para onda 2, 7 abates e contador instantâneo de 138 FPS. Observação visual: armas parecem vazadas/incompletas e soldados seguram armas de modo incorreto. O contador exibido em uma captura **não** é benchmark nem aprovação de sessão prolongada.

| Item | Entrega | Status atual | Aceite ainda necessário |
| --- | --- | --- | --- |
| V09-01 | Corrigir normais dos GLBs e dos anéis dos canos | **CONCLUÍDO (CI)** — gerador, regeneração e 19 GLBs commitados | Validar resultado visual no Windows; [commit de assets](https://github.com/TPollTech/Frontline-Survival/commit/680a86643ac51841cbe835d8dd8e194b4079c8f7) |
| V09-02 | Corrigir escala e profundidade das cinco armas no FPS | **PARCIAL** — código atualizado | Validar a escopeta/LMG ao mirar e andar |
| V09-03 | Alinhar duas mãos do jogador às armas | **PARCIAL** — empunhadura procedural ajustada | Confirmar sem mão flutuante e sem clipping em recarga |
| V09-04 | Corrigir arma e braços de inimigos | **PARCIAL** — IK leve e alinhamento do modelo | Validar visualmente ataque, caminhada e disparo |
| V09-05 | Corrigir arma e braços dos aliados | **PARCIAL** — IK leve e alinhamento do modelo | Validar invocação do esquadrão e postura de rifle |
| V09-06 | Verificação de regressão das malhas | **CONCLUÍDO (CI)** | Verificador estático e smoke test passaram com GLBs regenerados na [execução 0.9](https://github.com/TPollTech/Frontline-Survival/actions/runs/42941790033) |
| V09-07 | Build Windows 0.9 com arquivo ZIP | **CONCLUÍDO (CI + RELEASES)** — build e ZIP publicados | [Release v0.9.0](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.0) e [CI bem-sucedido](https://github.com/TPollTech/Frontline-Survival/actions/runs/42943797046); jogabilidade visual ainda pendente |
| V09-08 | Teste 15 ondas, compras, morte e FPS | **PENDENTE** | Jogar sessão completa no Windows e registrar resultado |

**Nenhuma Etapa 1 ou 2 está 100% concluída.** A geração/exportação 0.9 foi concluída no CI e a primeira versão foi publicada em [GitHub Releases](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.0), com link permanente. A correção visual e a empunhadura continuam **PARCIAIS** até aprovação no Windows.

[Roteiro de testes da 0.9](docs/TESTES_0_9.md) · [Changelog](docs/CHANGELOG.md)

## 11. Avanço documental — Etapa 6 (10/11/2026)

A [Etapa 6](docs/ETAPA_6_DESEMPENHO_TESTES_DISTRIBUICAO.md) especifica métricas reproduzíveis no Ryzen 5 7530U/8 GB, 18 cenários de QA, gates de CI, Windows, 15 ondas e publicação versionada. **Nenhum teste foi executado nesta rodada documental.** Feedback de jogo recebido: armas brancas, aliados deformados, apitos de transição, ADS desalinhado e **remoção solicitada da crosshair**; retícula dinâmica descrita anteriormente não deve ser tratada como requisito vigente. Próxima lacuna: GDD mestre consolidado com matriz de consistência e propostas não aprovadas.

## 12. Sprint v0.9.1 — Correções e aprovação (10/11/2026)

**Evidência:** a v0.9.0 foi executada no Windows. Na captura da preparação da onda 3, havia 16 abates e 108 FPS naquele instante. Defeitos relatados: armas brancas, aliados com postura deformada, sons agudos na conclusão de onda e visor desalinhado. O usuário pediu explicitamente remover a crosshair. **108 FPS em um frame não comprova média sustentada.**

**Entrega CI verificada:** [Release v0.9.1](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.1) e [workflow aprovado](https://github.com/TPollTech/Frontline-Survival/actions/runs/42945928310), com ZIP Windows, executável, PCK e checksum SHA-256.

| ID | Trabalho | Estado verificado | O que falta validar |
| --- | --- | --- | --- |
| V091-01 | Aplicação de cores COLOR_0 em armas GLB | **PARCIAL** — material correto no código e importação CI | Verificar as cinco armas e NPCs sem branco intenso no Windows |
| V091-02 | Mira física centralizada e recuo após o disparo | **PARCIAL** — lógica e CI aprovados | Testar primeiro tiro e ADS em cada classe |
| V091-03 | Crosshair 2D removida | **CONCLUÍDO (CÓDIGO/CI)** | Conferir ausência visual na partida |
| V091-04 | Aliados: IK 2 segmentos e proporções reduzidas | **PARCIAL** — implementação e CI aprovados | Observar postura, movimentação e disparo |
| V091-05 | Inimigos: IK e materiais das armas | **PARCIAL** — implementação e CI aprovados | Observar durante o combate |
| V091-06 | Apitos de hit removidos, novo cue de onda e compra mais discreta | **PARCIAL** — scripts e CI aprovados | Ouvir em duas transições de onda e ajustar volume se necessário |
| V091-07 | Exportação e publicação do executável em Releases | **CONCLUÍDO (CI + RELEASES)** | [Download público](https://github.com/TPollTech/Frontline-Survival/releases/download/v0.9.1/FrontlineSurvival-v0.9.1-Windows.zip) validado no GitHub |
| V091-08 | Homologação real de jogabilidade e 15 ondas | **PENDENTE** | Teste no notebook com FPS, controles, apoio, economia e áudio |

**Etapas diretamente avançadas:** 1 (armas/FPS), 2 (representação dos combatentes), 5 (HUD/áudio) e 6 (distribuição). **Nenhuma etapa completa pode ser dada como 100% concluída só por compilar.** A release 0.9.0 permanece disponível para comparar/voltar.

[Checklist 0.9.1](docs/TESTES_0_9_1.md) · [Changelog](docs/CHANGELOG.md)
