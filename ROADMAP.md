# Frontline Survival — Planejamento e Roadmap

**Documento mestre do projeto** · Atualizado: 10/11/2026 · **Base de referência:** protótipo `0.7`; **versão de desenvolvimento:** `0.9.16` (**código no main; CI/release pendentes**) · **Situação:** planejamento; novas mecânicas somente após aprovação da etapa.

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
- [GDD mestre — pronto para revisão](docs/GDD_MESTRE.md): síntese do jogo base, dependências, conflitos C-01–C-06 e checklist de consistência; **não aprovado**.
- [Registro de decisões e propostas](docs/REGISTRO_DECISOES.md): requisitos já estabelecidos versus ideias pendentes.
- [Plano de mapas](docs/PLANO_MAPAS.md): Campo de Testes permanente e proposta de mapa multissetores.
- [Testes de regressão existentes da 0.7](docs/TESTES_0_7.md): roteiro técnico anterior, complementado pela Etapa 0.

**Observação:** nenhuma tarefa de QA foi marcada como concluída apenas por escrever estes documentos. Não foram alterados scripts, cenas, modelos ou áudio nesta atualização documental.

## 8. Acompanhamento da pré-produção

| Documento | Situação documental | Implementação e QA |
| --- | --- | --- |
| Etapa 0 — Estabilidade | Especificada; 27 verificações de QA | **PARCIAL** — 2 transições de onda e checagem de spawn automatizadas em Godot headless na 0.9.2; ainda falta sessão real de 15 ondas no Windows |
| Etapa 1 — Armas e FPS | Especificada; decisões pendentes | **PARCIAL** — v0.9.3 apresenta texturas de metal/polímero, detalhes das cinco armas e foley de recarga por classe; acabamento visual/sonoro ainda precisa de teste |
| Etapa 2 — Inimigos e ondas | Especificada; decisões pendentes | **PARCIAL** — v0.9.3 inclui sondas e recuperação antitravamento dos inimigos e aliados; navegação complexa, 15 ondas e playtest pendentes |
| Etapa 3 — Economia e reforços | Especificada; propostas aguardam aprovação | **PARCIAL** — cabeça/armamento do esquadrão retrabalhados na v0.9.3; suporte ainda não está visualmente homologado |
| Etapa 4 — Mapas | **Especificada em 10/11/2026**; layout de cinco setores e arquitetura ainda sujeitos a aprovação | Não iniciada |
| Etapa 5 — HUD, áudio e UX | **Especificada em 10/11/2026**; propostas aguardam aprovação | **PARCIAL** — v0.9.1 retira crosshair/hit beep e adiciona som grave de fim de onda; validação auditiva pendente |
| Etapa 6 — desempenho e distribuição | **Especificada em 10/11/2026**; metas e gates pendentes de aprovação | **PARCIAL** — release [v0.9.1](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.1) e CI aprovados; benchmark/15 ondas pendentes |
| GDD consolidado | **GDD PRONTO PARA REVISÃO**; síntese documental das Etapas 0–6, aprovação pendente | Não aplicável |

**Último avanço de produto:** versão 0.9 compilada e publicada no GitHub Actions, com 19 arquivos GLB regenerados e sincronizados na main. A versão 0.8 foi executada pelo usuário até a preparação da onda 2; a 0.9 exige validação visual/jogabilidade no Windows. Etapa 6 especificada documentalmente; GDD mestre consolidado em 11/11/2026, pronto para revisão documental; conflitos C-01/C-02 e aprovações pendentes. Sem alteração de código nesta rodada documental.

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

## 13. Sprint 0.9.2 — Spawn seguro e integração real de ondas

**Auditoria de 0.9.1:** [CI comprovado](https://github.com/TPollTech/Frontline-Survival/actions/runs/42945928310): importação de GLBs, parser, teste de inicialização Godot, checagens estáticas, exportação Windows e publicação de release. **Isso não homologou visualmente** paleta de cores, mira ou rig; esses itens seguem PARCIAIS até novo teste do usuário.

**Problemas de código identificados:** no Campo de Testes, inimigos ainda surgiam aleatoriamente entre oito pontos, mesmo perto do jogador/lojas ou ocupados; e o CI não testava execução real de ondas. A 0.9.2 acrescenta verificação do mundo físico e integração de cenas reais.

| Item | Trabalho | Estado | Evidência / pendência |
| --- | --- | --- | --- |
| V092-01 | Selecionar ponto de spawn com mínimo 10 m do jogador, 4,75 m das lojas e raio físico 0,72 m | **PARCIAL** — código implementado | 100 escolhas em integração Godot e inspeção em gameplay real |
| V092-02 | Favorecer surgimento fora da direção de visão, sem previsibilidade total | **PARCIAL** — código implementado | Inspeção visual de spawns |
| V092-03 | Rejeitar todos os pontos inseguros e tentar novamente sem perder o número da onda | **PARCIAL** — código implementado | Verificar cenário de área ocupada e ausência de onda travada |
| V092-04 | Mover spawns para o ciclo físico do Godot | **CONCLUÍDO (CÓDIGO/CI)** | Parser, startup e smoke test aprovados no runner |
| V092-05 | Teste automático com 100 escolhas de spawn e duas ondas | **CONCLUÍDO (CI)** — [primeira integração aprovada](https://github.com/TPollTech/Frontline-Survival/actions/runs/42948387516), [cenários de borda aprovados](https://github.com/TPollTech/Frontline-Survival/actions/runs/42948609563) | Testes visuais e 15 ondas continuam pendentes |
| V092-06 | Verificar também modelo colorido e animação do esquadrão no CI | **CONCLUÍDO (CI)** | [Workflow 0.9.2 aprovado](https://github.com/TPollTech/Frontline-Survival/actions/runs/42949035024); material e 12 quadros de dois aliados checados; avaliação visual ainda pendente |
| V092-07 | Publicar executável 0.9.2 em Releases | **CONCLUÍDO (CI + RELEASES)** | [Download direto](https://github.com/TPollTech/Frontline-Survival/releases/download/v0.9.2/FrontlineSurvival-v0.9.2-Windows.zip), [release](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.2) com SHA-256 e [CI verde](https://github.com/TPollTech/Frontline-Survival/actions/runs/42949035024) |
| V092-08 | Validar 15 ondas no notebook real | **PENDENTE** | Critério de aceitação da Etapa 0 e Etapa 2 |

**Escopo fechado deste incremento:** não ampliar número de inimigos, não alterar a economia nem a curva de armas e não redesenhar o mapa. O Campo de Testes e a textura de asfalto permanecem iguais. A [Etapa 2 completa](docs/ETAPA_2_INIMIGOS_ONDAS.md) segue PARCIAL até IA/navegação avançada, playtests e métricas reais.

**Validação final do incremento 0.9.2 (CI):** integração com 100 escolhas, oito posições de borda, ausência de locais seguros, duas ondas reais, material COLOR_0, dois aliados e smoke test aprovado. [Cenários documentados](docs/TESTES_0_9_2.md). **A correção visual da 0.9.1 e a estabilidade de 15 ondas ainda não foram homologadas pelo jogador.**


## 14. Sprint 0.9.3 — correções visuais, foley e antitravamento

**Origem:** usuário observou um aliado com a cabeça aparentemente separada do corpo, armas com aparência de blocos e som de recarga repetitivo/agudo. Pediu também continuar a próxima frente da Etapa 2.

| Item | Mudança | Status |
| --- | --- | --- |
| V093-01 | Gola/neck mesh, HeadPivot do aliado com capacete e máscara presos ao mesmo eixo | **PARCIAL** — código e testes CI; falta inspeção de postura no Windows |
| V093-02 | Quatro texturas originais com projeção triplanar e paleta GLB | **CONCLUÍDO (GERAÇÃO/CI)**; qualidade visual ainda **PARCIAL** |
| V093-03 | Detalhes de geometria nas cinco armas; regeneração 19 GLBs | **CONCLUÍDO (GERAÇÃO/CI)**; qualidade visual ainda **PARCIAL** |
| V093-04 | Cinco WAVs de recarga por arma, sem apito genérico, volumes moderados | **CONCLUÍDO (GERAÇÃO/CI)**; conforto auditivo **PARCIAL** até teste |
| V093-05 | IA: sondar paredes e desviar lateralmente sem teleportar inimigos | **PARCIAL** — código integrado, precisa de teste de obstáculos |
| V093-06 | IA: detectar perseguição sem avanço e disparar recuperação | **PARCIAL** — código integrado, precisa de playtest |
| V093-07 | Aliados: desvio leve e recuperação ao seguir jogador/inimigos | **PARCIAL** — código integrado; teste em jogo pendente |
| V093-08 | Integridade: 100+ spawns, duas ondas, dois aliados, textura e áudio | **CONCLUÍDO (CI)** — [testes aprovados](https://github.com/TPollTech/Frontline-Survival/actions/runs/43009563242) |
| V093-09 | Release Windows v0.9.3 com ZIP/EXE/PCK/SHA-256 | **CONCLUÍDO (CI + RELEASES)** — [publicação verificada](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.3) |
| V093-10 | Inspeção visual e sessão real de 15 ondas | **PENDENTE** |

**Auditoria e proteção:** a 0.9.3 foi aplicada sobre a branch \`main\` atual do repositório, sem substituir o jogo pelo patch antigo feito a partir do 0.7. O código, os GLBs, os WAVs e as texturas são enviados ao GitHub; o pipeline exporta somente depois que os testes passam. **Etapas 1, 2 e 3 seguem parciais** até a homologação jogando.

[QA v0.9.3](docs/TESTES_0_9_3.md) · [Notas de release](docs/releases/v0.9.3.md).

## 15. Plano fechado proposto para o lançamento v1.0 (11/11/2026)

**Objetivo:** terminar um jogo Survival completo, não um projeto com atualizações infinitas. As ondas do modo clássico continuam ilimitadas; **o desenvolvimento da v1.0 termina quando os 12 gates de qualidade do GDD são cumpridos.**

### Documentos novos e sua função

| Documento | Função | Estado |
| --- | --- | --- |
| [Pesquisa de MW3 Survival 2011](docs/PESQUISA_MW3_SURVIVAL_2011.md) | Manual oficial, cobertura contemporânea e guias; fatos separados de propostas | **CONCLUÍDO (PESQUISA)** |
| [GDD mestre v1.0](docs/GDD_V1_0.md) | O que entra/não entra, começo/meio/fim da experiência, conteúdo e 12 gates de aceitação | **CONCLUÍDO (DOCUMENTAÇÃO); PROPOSTAS NÃO APROVADAS** |
| [Plano M0–M8](docs/PLANO_ENTREGA_V1_0.md) | Implementação sequenciada, dependências, aceitação e critérios para v1.0.0 | **CONCLUÍDO (DOCUMENTAÇÃO)** |
| [Backlog v1.1+](docs/BACKLOG_1_1_PLUS.md) | Expansões separadas para não atrasar 1.0 | **CONCLUÍDO (DOCUMENTAÇÃO)** |

### Limite de escopo proposto

- **Versão 1.0:** 1 mapa definitivo **Complexo Industrial**, mais Campo de Testes; cinco famílias de armas realmente distintas; inimigos básicos/corredor/fuzileiro/pesado; três lojas físicas; três apoios; ondas infinitas; duas dificuldades; recordes/patentes offline; Windows Releases.
- **Depois da 1.0:** novos mapas, helicópteros, cães/bombas, multiplayer, veículos, grandes árvores de acessórios e outros conteúdos não essenciais.
- **Não perder decisões estabelecidas:** solo offline, 75 s de preparação configurável 45–120, F nas lojas, sem crosshair 2D, asfalto do Campo de Testes preservado e reforços 3/4.

### Marcos de produção

| Ato | Marcos | Resultado |
| --- | --- | --- |
| Início | **M0–M2** | Estabilidade, armas/aliados/áudio aprovados; IA e ondas confiáveis |
| Meio | **M3–M5** | Economia/suporte, mapa definitivo, menus, XP/recordes/salvamento |
| Fim | **M6–M8** | Performance, RC com 12 gates de aceite e release estável v1.0.0 |

**Estado do jogo hoje:** versões 0.9.x ainda **PARCIAIS** nas Etapas 0–6. A pesquisa e o planejamento não significam implementação. Falta aceitar 10 propostas V1-P01–10, validar tabelas de balanceamento, finalizar layout e executar Windows QA (15 ondas no mínimo).

**Próxima sprint real recomendada:** **M0**, primeiro homologar v0.9.3 e corrigir armas, cabeça/mãos dos aliados, recargas e linha de visão antes de aumentar a complexidade dos mapas. **Próxima rodada documental:** números de balanceamento e critérios de progressão com simulação, mantendo propostas identificadas.


## 16. Sprint v0.9.11 — M0 QA e M2 diretor de ondas

**Base real auditada:** main já estava na v0.9.10, com alterações de modelagem/mira e áudio gravado em WAV PCM feitas posteriormente à v0.9.3. Esta sprint foi feita sobre esse estado, preservando modelos, gravações, scripts de áudio e demais alterações dos colaboradores.

**Referência histórica:** o Survival de MW3 (2011) usa ondas especiais cuja sequência muda por dificuldade/mapa. A distribuição abaixo é uma **regra original do Frontline**, não a alegação de uma sequência oficial do MW3. [Pesquisa](docs/PESQUISA_MW3_SURVIVAL_2011.md).

| ID | Entrega | Estado | Evidência |
|---|---|---|---|
| V0911-01 | Centralizar regras de quantidade e tipos em `wave_rules.gd` | **CONCLUÍDO (CI)** | Integração Godot e teste das regras |
| V0911-02 | Um pesado anunciado na onda 10 e um na 15; dois a partir da 20 nas ondas-marco | **PARCIAL (IMPLEMENTADO/CI)** | Simulação aprovada; avaliação real da curva pendente |
| V0911-03 | Aviso textual discreto antes de combates com pesados, sem novos apitos | **PARCIAL (IMPLEMENTADO/CI)** | Cena headless verifica o aviso na onda 10; teste visual pendente |
| V0911-04 | Testar composição de 50 ondas (limites de 55 por onda e 12 simultâneos) | **CONCLUÍDO (CI)** | 2.416 afirmações e 2.150 posições simuladas; **não** 50 ondas jogadas |
| V0911-05 | Manter teste integrado de duas ondas reais e verificar gatilho da onda 10 | **CONCLUÍDO (CI)** | 475+ verificações do runtime |
| V0911-06 | Preservar gravações de disparo/recarga, modelos e materiais da v0.9.10 | **CONCLUÍDO (REVISÃO DE ESCOPO)** | Nenhum WAV/GLB/material/script de áudio alterado nesta sprint |
| V0911-07 | ZIP Windows v0.9.11 em GitHub Releases | **AGUARDANDO PUBLICAÇÃO** | Confirmar CI verde e assets da release |
| V0911-08 | Jogar 15 ondas, ajustar balanceamento e avaliar FPS/áudio/rig no Windows | **PENDENTE** | Homologação real necessária |

**M0:** permanece **PARCIAL**; a QA automatizada cresceu, mas G1 e teste de 15 ondas no Windows ainda faltam.  
**M2 / Etapa 2:** permanece **PARCIAL**; composição de ondas-marco implementada, mas IA completa, navegação e balanceamento por mapa exigem trabalho futuro.  
**Versão 1.0:** não alterar a definição de pronto: G1–G12 e aceite do jogo real continuam obrigatórios.

[QA v0.9.11](docs/QA_V0_9_11.md) · [Notas de release](docs/releases/v0.9.11.md)

## 17. Prioridade M0/M1: Campo de Testes polido — v0.9.12 (11/11/2026)

**Decisão direta do usuário:** antes de ampliar mapas, ondas e spawns por helicópteros/transportes, terminar e homologar a sensação de jogar o **Campo de Testes**. Evidência real: usuário jogou **até a onda 10** e considera o loop funcional, mas apontou falta de corrida convincente, hitmarker, sangue, corpos, loot, indicador de dano mais orgânico e humanoides melhores.

**Estado atual:** a versão 0.9.11 ajustou composição de ondas; **não continuar expansão de ondas nesta fase**. A 0.9.12 é uma sprint de polimento, não conteúdo novo de mapa.

| ID | Alteração | Estado de implementação | Pendência |
|---|---|---|---|
| V0912-01 | Corrida tática: arma inclinada para baixo, transição e braço de apoio separado | **CONCLUÍDO (CÓDIGO/CI)** | Aprovar visual e feeling no Windows |
| V0912-02 | Hitmarker breve e discreto; cor diferenciada em headshot, **sem som** | **CONCLUÍDO (CÓDIGO/CI)** | Aprovar no Windows |
| V0912-03 | Sangue de impacto breve e com orçamento limitado | **CONCLUÍDO (CÓDIGO/CI)** | Aprovar visual e FPS |
| V0912-04 | Corpo no mapa até 17 s e máximo 12; desativar colisão ao morrer | **PARCIAL** — script e regressão CI | Verificar queda real, 17s, 12 corpos e FPS |
| V0912-05 | Armas dos inimigos recolhíveis por F e munição ocasional; máximo 18 itens, limpeza em 20s | **CONCLUÍDO (CÓDIGO/CI)** — coleta testada | Verificar UX/F junto às lojas e otimização |
| V0912-06 | Indicador de tiro substituído por quatro arcos vermelhos curvos | **CONCLUÍDO (CÓDIGO/CI)** | Aprovar forma e transparência no Windows |
| V0912-07 | Silhueta dos inimigos e aliados mais arredondada e arma deslocada à frente | **PARCIAL** — cápsulas e grip ajustados | Ainda precisa **rig humanoide real** e revisão visual |
| V0912-08 | Testes integrados: hitmarker, sprint, drops, sangue, corpos e 2 ondas; 50 composições sem jogar | **CONCLUÍDO (CI)** | 15 ondas reais ainda pendentes |
| V0912-09 | Exportar ZIP Windows v0.9.12 e publicar em GitHub Releases | **CONCLUÍDO (CI + RELEASES)** | [Build aprovado](https://github.com/TPollTech/Frontline-Survival/actions/runs/43077610098) e [ZIP verificado em Releases](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.12) |

**Mantidos:** Campo de Testes, asfalto, três estações por F, 75s entre ondas, sem crosshair permanente, sons WAV PCM da v0.9.10, reforços e waves atuais. **Sem novas fases, mapas, helicópteros ou caminhões nesta sprint.**

**Próximas decisões pós-polimento (registradas, NÃO implementadas):** soldados humanoides com esqueleto/rig, animações reais, queda física/ragdoll se desempenho permitir; mais tarde chegadas por transporte terrestre e aéreo e unidades blindadas especiais. A proposta de personagens CC0 (Quaternius) deve ser testada isoladamente no Godot 4.4.1 antes de substituir os NPCs.

**Ajuste adicional na v0.9.12:** munição caída é identificada pela arma de origem e não pode ser convertida silenciosamente para outra arma equipada; o prompt mostra classe e quantidade. Cenário positivo (mesma arma) e negativo (arma não possuída) integrados ao teste runtime. **A v0.9.12 foi publicada e teve CI verde**, mas FPS, aparência dos corpos, rig humanoide e dinâmica de corrida continuam **PARCIAIS** até teste no Windows. Não iniciar implementação de novos mapas/ondas/transportes nesta fase.

[Checklist do Campo de Testes](docs/M0_POLIMENTO_CAMPO_TESTES.md) • [QA 0.9.12](docs/QA_V0_9_12.md) • [Release notes](docs/releases/v0.9.12.md)


## 18. Protótipo visual v0.9.13 — primeiro soldado humanoide (Quaternius)

**Decisão do usuário (11/11/2026):** usar um modelo melhor do Quaternius e avaliar o resultado no Campo de Testes. **Sem expansão de mapas, ondas, helicópteros ou inimigos especiais** até a jogabilidade atual ficar polida.

**Referência externa confirmada:** [Quaternius Universal Base Characters — CC0](https://quaternius.com/packs/universalbasecharacters.html), um modelo rigged com 65 ossos. O GLB é uma versão reduzida do modelo CC0 [documentada aqui](docs/ASSET_QUATERNIUS_CC0.md); pesa cerca de 741 KB e preserva pesos de skinning. O pacote base **não contém clipes de animação**.

| ID | Incremento | Estado | Próxima verificação |
| --- | --- | --- | --- |
| V0913-01 | Adicionar um humanoide do Quaternius com malha e esqueleto completos | **CONCLUÍDO (ARQUIVO)** | Importação Godot e visual Windows |
| V0913-02 | Adaptar colete, capacete, visor e postura básica do rifle, mantendo identidade original | **PARCIAL** — implementação | Avaliação visual de mãos, cabeça, altura e aparência |
| V0913-03 | Animar pernas e braços com poses simples usando o esqueleto importado | **PARCIAL** — código experimental | Verificar caminhada/corrida/combate e FPS |
| V0913-04 | Trocar apenas o primeiro soldado comum de cada onda, com fallback ao modelo antigo | **PARCIAL** — implementação e comparação A/B | Verificar spawn e luta reais |
| V0913-05 | Preservar IA, collider, armas, áudio PCM, cadáveres e loot | **CONCLUÍDO (REVISÃO DE ESCOPO)** | Teste de duas ondas e 15 ondas reais |
| V0913-06 | Teste de rig/skeleton, ocultação do corpo antigo e presença da arma | **CONCLUÍDO (CI)** | [Build 0.9.13 aprovada](https://github.com/TPollTech/Frontline-Survival/actions/runs/43081848984), incluindo esqueleto e arma no runtime |
| V0913-07 | Release v0.9.13 Windows com protótipo em combate | **CONCLUÍDO (CI + RELEASES)** | [ZIP Windows publicado](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.13) e SHA-256 |
| V0913-08 | Avaliar Quaternius com clipes completos de animação idle/walk/run/fire/death | **PENDENTE** | Só depois de aprovação da malha e compatibilidade/licença |

**Critério de avançar:** o jogador aprova a anatomia e o desempenho do primeiro soldado antes de migrar aliados e todos os inimigos. **O teste de rig no CI não é aprovação visual.** Continuar mantendo o Campo de Testes e as regras atuais inalterados.

[Asset e licença CC0](docs/ASSET_QUATERNIUS_CC0.md) · [QA v0.9.13](docs/QA_V0_9_13.md) · [Release](docs/releases/v0.9.13.md)

## 9. Atualização de prioridade M0 — 11/11/2026

O [plano de polimento do Campo de Testes](docs/M0_POLIMENTO_CAMPO_TESTES.md) registra decisão posterior de **priorizar sensação de corrida, hitmarker contextual silencioso, sangue, corpos temporários, loot com F, arcos de dano e personagens mais naturais**, antes de mapa novo, veículos ou ampliação de ondas. A sessão real relatada alcançou a onda 10, **não** as 15 exigidas. A 0.9.12 registra código/CI de parte desse polimento; o aceite visual, a interação contextual F e benchmarks no Ryzen 5 7530U/8 GB seguem pendentes. Ver [registro de decisões](docs/REGISTRO_DECISOES.md) e [GDD mestre](docs/GDD_MESTRE.md). A proposta de lançamento 1.0 e V1-P01–V1-P10 permanecem sem aprovação formal. **GDD PRONTO PARA REVISÃO**, sem expandir escopo.

## 19. Correção de postura do humanoide — hotfix v0.9.14

**Feedback direto (11/11/2026):** screenshot da 0.9.13 revelou pose totalmente deformada, com braços verticalizados e malha torcendo. A qualidade visual da 0.9.13 foi **REPROVADA**, mesmo com CI verde. **Nunca marcar modelos/animadores como aceitos apenas porque 65 ossos existem.**

**Causa identificada:** o script de animação em `scripts/quaternius_soldier_visual.gd` substituía a rotação original de descanso de ossos importados por quaternions relativos (próximos à identidade) em vez de compor pequenas rotações sobre a base. Isso provocou a inversão/deformação visual.

| ID | Mudança | Estado |
| --- | --- | --- |
| V0914-01 | Capturar rotações originais do esqueleto do Quaternius | **CONCLUÍDO (CÓDIGO)** |
| V0914-02 | Aplicar deltas pequenos sobre a pose base de braços, pernas e coluna | **CONCLUÍDO (CÓDIGO)** |
| V0914-03 | Testar cabeça/quadril/pés, mãos abaixo da cabeça e desvios angulares de ossos | **CONCLUÍDO (CI)** após workflow verde |
| V0914-04 | Fallback no jogo se pose humana inválida | **CONCLUÍDO (CÓDIGO)** |
| V0914-05 | Exportar ZIP Windows v0.9.14 e publicar GitHub Release | **CONCLUÍDO (CI + RELEASES)** — [download](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.14) com checksum; [CI verde](https://github.com/TPollTech/Frontline-Survival/actions/runs/43086856738) |
| V0914-06 | Inspeção visual no Windows: postura, mãos, arma, pernas, movimento e FPS | **PENDENTE (JOGADOR)** |

**Decisão:** manter apenas um modelo Quaternius em teste por onda; não passar todos os inimigos/aliados para humanoides e não ampliar mapas/ondas até validar visualmente a 0.9.14. **A correção é de estrutura óssea, não uma promessa de animação profissional.**

[Diagnóstico e correções](docs/releases/v0.9.14.md) · [QA v0.9.14](docs/QA_V0_9_14.md)


## 20. Novas exigências do núcleo Survival — perks, attachments, 30s e combate (11/11/2026)

**Solicitação direta do usuário:** após observar MW3 (2011), o jogador quer perks compráveis, Última Chance/Last Stand, recompensas por metas, estatísticas no fim de cada onda, armas inicialmente sem attachment mas customizáveis na loja (Red Dot + Silenciador etc.), agachamento e deitar. Notou que o MW3 original tem **30 segundos de preparação**; foi confirmado em materiais de 2011.

**PRIORIDADE MANTIDA:** tudo será desenvolvido e homologado primeiro no **Campo de Testes**. Não iniciar mapas adicionais, reforços por helicóptero/camburão, novas ondas ou armas enquanto essa frente ainda for parcial. A versão executável permanece **v0.9.14**; este incremento foi **SOMENTE DOCUMENTAL**.

### Documentos desta pesquisa/planejamento

| Documento | Objetivo | Estado |
| --- | --- | --- |
| [MW3 Survival 2011: fatos e divergências](docs/PESQUISA_MW3_SURVIVAL_MECANICAS.md) | Fontes de 2011–2012, diferenças entre Last Stand e Self Revive, 30s, desafios e attachments | **CONCLUÍDO (PESQUISA)** |
| [Especificação do núcleo CT-01–CT-07](docs/NUCLEO_SURVIVAL_PERKS_ATTACHMENTS_MOVIMENTO.md) | Contratos de estatísticas, economia, perks, compra de acessórios, posturas e testes | **CONCLUÍDO (DOCUMENTAÇÃO)** |
| [GDD mestre v1.0](docs/GDD_V1_0.md) | Adendo §16 integra esses requisitos como bloqueantes do núcleo | **ATUALIZADO (DOCUMENTAÇÃO)** |
| [Registro de decisões](docs/REGISTRO_DECISOES.md) | D-017–D-024 e conflito histórico 75s/30s; sem inventar aprovação dos custos | **ATUALIZADO (DOCUMENTAÇÃO)** |
| [Etapa 3](docs/ETAPA_3_ECONOMIA_SUPORTE.md) | Desafios, perk e kit como componentes reais da economia | **ATUALIZADO (DOCUMENTAÇÃO)** |

### Matriz de desenvolvimento do Campo de Testes

| ID | Recurso | Estado atual | Próximo teste |
| --- | --- | --- | --- |
| CT-01 | **Resumo estatístico após onda**: kills, precisão, headshots, tempo, dano, dinheiro por fonte | **PENDENTE** | Contadores consistentes, shotgun sem precisão >100%, bônus uma vez, F e N não bloqueados |
| CT-01b | **30 s entre ondas** com 75 s preservado para quem já personalizou | **PENDENTE** — código tem padrão 75 e mínimo 45 | Migração do \`ConfigFile\`, 30/45/60/75/90/120, preparar corretamente |
| CT-02 | **Metas monetárias**: Quad Kill, Rampage, Killstreak, headshots; valores de referência $500 etc. | **PENDENTE** | Não duplicar créditos, distinguir mortes simultâneas de rápidas e 5 sem dano |
| CT-03 | **Agachar e deitar** com câmera e colisão, não só velocidade | **PARCIAL** — C/Ctrl reduzem velocidade; prone não existe | Colisor, teto, ADS, armas e hit registration |
| CT-04 | **Attachments compráveis para as cinco armas**: red dot e silenciador simultâneos, efeitos e modelos próprios | **PENDENTE** | Cada arma básica sem acessórios, compra/troca/loot, ADS e WAV apropriados |
| CT-05 | **Perks na estação de suporte**: benefício real, substituição de um ativo | **PENDENTE** | Compra, troca de efeito, sem stack ou débito duplicado |
| CT-06 | **Última Chance/Last Stand + Kit de Reanimação** (equipamento diferente de perk) | **PENDENTE** | Pistola ao cair, matar para levantar ou usar kit pré-comprado; treino/clássico separados |
| CT-07 | **Homologação prolongada no Campo de Testes** | **PENDENTE** | 15 ondas Windows reais, rig humanoide, compras, FPS/RAM e nenhuma regressão |

**Atenção:** uma lista antiga do MW3 Survival **não comprova silenciador à venda no original**. Silenciador para todas as nossas armas é funcionalidade própria aprovada como objetivo pelo usuário. **Tempos exatos, custos, percentuais e teclas propostas não são valores definitivamente aprovados**; após estudo de balanceamento, documentar versão real.

**Regra de escopo:** primeiro confirmar visualmente o humanoide corrigido da v0.9.14 (M0), então CT-01 e CT-02. A ordem acima é orientativa para implementação; manter controle de regressões a cada release. Não confundir documentação com entrega de gameplay.

[Plano M0–M8 atualizado](docs/PLANO_ENTREGA_V1_0.md) · [Pesquisa complementar](docs/PESQUISA_MW3_SURVIVAL_MECANICAS.md)


## 21. Sprint CT-01–CT-06 — núcleo Survival v0.9.15 (11/11/2026)

**Escopo pedido diretamente pelo jogador:** implementar agora perks compráveis, Última Chance/Last Stand, bônus de killstreak/quadkill, resumo de onda, intervalo 30s, attachments para as cinco armas e agachar/deitar. **Sem expandir mapa, onda, transporte ou número de NPCs**.

**Base:** v0.9.14. Mantidos áudio PCM gravado das versões Astra/Sol, materiais, HUD sem crosshair permanente e Quaternius de um inimigo por onda. A equipe ainda deve verificar se o novo boneco está visualmente correto; o antigo teste de ossos foi insuficiente para reprovar a aberração da v0.9.13.

| Item | Implementação no código | Validação |
|---|---|---|
| CT-01 | Preparação **30s padrão** (settings antigos preservados) e relatório da onda com tiros, precisão, headshots, dano, tempo e dinheiro discriminado | **IMPLEMENTADO (CÓDIGO)** → CI/Windows pendente |
| CT-02 | Motor de quatro desafios; duas metas por onda, +$500 por meta, event IDs e prevenção de recompensa duplicada | **IMPLEMENTADO (CÓDIGO)** → teste determinístico/CI pendente |
| CT-03 | Postura \`stand/crouch/prone\`, altura de câmera + cápsula e checagem de teto; C/Ctrl/Z | **IMPLEMENTADO (CÓDIGO)** → colisão real/câmera pendentes |
| CT-04 | **Red Dot, Holográfica, Silenciador e Compensador** na estação do Arsenal; peças 3D, compra por arma, scope + muzzle juntos | **IMPLEMENTADO (CÓDIGO)** → modelos/ADS/qualidade sonora pendentes |
| CT-05 | Cinco perks na estação de Suporte, **um por vez**, efeitos de reload/precisão/ADS/mobilidade/resistência | **IMPLEMENTADO (CÓDIGO)** → integrar testes de saldo/efeitos |
| CT-06 | **Última Chance:** estado ferido, pistola com 8 cartuchos, 10s para matar e recuperar; kit autorreanimação consumível separado | **IMPLEMENTADO (CÓDIGO)** → treino/clássico e edge cases no Windows pendentes |
| CT-07 | QA prolongado/visual (15 ondas, colisões, IA, som, FPS) | **PENDENTE (JOGO REAL)** |
| CT-08 | Teste de **renderização da malha Quaternius** via Xvfb e imagem gravada no repo | **IMPLEMENTADO (SCRIPT CI)** — aguarda imagem e revisão humana |
| CT-09 | Nova **GitHub Release v0.9.15** com ZIP/EXE/PCK/SHA-256 | **CONCLUÍDO (CI + RELEASES)** — [release](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.15), [CI aprovado](https://github.com/TPollTech/Frontline-Survival/actions/runs/43161283939) |

**Regras especiais:** desafio remunerado apenas uma vez por onda/ID; créditos de abates já pagos no momento da morte não são somados novamente no relatório. Shotgun = 1 tiro por trigger, não N pellets. Silenciador usa WAV gravado original via filtro passa-baixa — **não é uma nova gravação profissional de disparo suprimido**. O usuário deve avaliar a qualidade.

**Importante:** esses itens não passaram automaticamente de **implementado em código** a **concluído jogando**; todos os G1–G12 do GDD ainda se aplicam. Não declarar 1.0 enquanto visuais/armas/NPC/benchmark não estiverem aprovados.

[Notas v0.9.15](docs/releases/v0.9.15.md) • [QA v0.9.15](docs/QA_V0_9_15.md) • [Pesquisa MW3 original](docs/PESQUISA_MW3_SURVIVAL_MECANICAS.md)

**Homologação técnica da v0.9.15 — 12/11/2026:** CI de importação, teste de 50 composições, testes de recursos Survival, integração de duas ondas com NPCs, captura da malha do Quaternius em Godot/Xvfb, validação estática, exportação Windows e publicação ZIP + SHA256 **CONCLUÍDOS**. O workflow precisou de correção porque o `git stash --include-untracked` ocultava os pacotes antes da Release. **Status de jogabilidade continua PARCIAL**: confirmar no Windows Última Chance, perks, acessórios, postura deitada, precisão/relatório, gameplay de 15 ondas, aparência do humanoide e FPS real.


## 21. Sprint v0.9.16 — Polimento do Campo de Testes: IA tática e menus

**Decisão atual:** não ampliar mapas, ondas ou transporte; priorizar inimigos inteligentes, jogabilidade e apresentação no Campo de Testes. **Base preservada:** v0.9.15 (perks, attachments, Last Stand, 30 s padrão, precisão/metas, áudio PCM) e modelo humanoide A/B.

| ID | Mudança | Estado antes do QA | Aceitação |
| --- | --- | --- | --- |
| CT16-01 | IA de soldado comum escolhe cobertura real por raycast/collider | **IMPLEMENTADO / PARCIAL** | Cobertura validada no mapa e sem travamento |
| CT16-02 | Estados avançar, ir à cobertura, agachar/deitar, espiar, retornar | **IMPLEMENTADO / PARCIAL** | Observação em 10–15 ondas |
| CT16-03 | Carregadores finitos e WAVs de recarga por arma nos inimigos | **IMPLEMENTADO / PARCIAL** | CI + combate real sem tiros infinitos |
| CT16-04 | Runner e pesado com personalidade de ataque própria | **IMPLEMENTADO / PARCIAL** | Balanceamento sem IA uniforme |
| CT16-05 | Menu de configurações com Gráficos, Áudio, Controles, Jogabilidade | **IMPLEMENTADO / PARCIAL** | Navegação e salvamento confirmados |
| CT16-06 | Escala 3D e VSync, mouse invertido, opções de hitmarker/dano | **IMPLEMENTADO / PARCIAL** | Efeito real no jogo e persistência |
| CT16-07 | HUD, lojas, avisos, relatório e pausa com estilo uniforme | **IMPLEMENTADO / PARCIAL** | Capturas e aprovação visual |
| CT16-08 | Regressão por teste Godot + 50 composições simuladas | **CONCLUÍDO (CI)** | [CI 43166124429](https://github.com/TPollTech/Frontline-Survival/actions/runs/43166124429): 585 testes integrados, 50 composições, humanoide renderizado |
| CT16-09 | Release v0.9.16 para Windows (ZIP/EXE/PCK/sha256) | **CONCLUÍDO (CI + RELEASES)** | [v0.9.16](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.16), ZIP de 36,3 MB, checksum SHA256 |
| CT16-10 | Performance no Ryzen 5 7530U e 15 ondas de jogo real | **PENDENTE** | Não declarar finalizado sem isso |

**Critério de finalização:** IA tática, menus e HUD só passam a **CONCLUÍDO (JOGO)** depois do playtest. Os 12 gates da v1.0 seguem intactos. **Sem expansão** nesta rodada.

[Notas de release](docs/releases/v0.9.16.md) · [QA v0.9.16](docs/QA_V0_9_16.md)

**Fechamento técnico da sprint 0.9.16 (12/11/2026):** CI Windows/Ubuntu Godot aprovado, 585 verificações integradas, QA de 50 composições, recursos Survival, captura humanoide e release publicados. **Marcos M0/M2 seguem PARCIAIS** até o usuário testar IA, cobertura, menu, FPS e 15 ondas no Windows.

## 22. Backlog — IA militar completa

**Solicitação (12/11/2026):** evoluir os NPCs do comportamento tático inicial da v0.9.16 para uma **IA militar completa**, com sensação de soldados que observam, decidem e cooperam, e não somente correm em direção ao jogador.

**Estado:** **PENDENTE — PLANEJAMENTO/IMPLEMENTAÇÃO**. Não confundir com as melhorias básicas da v0.9.16. **Prioridade:** depois de estabilizar e validar a IA e os personagens do Campo de Testes; antes de expandir mapas/ondas.

### Critérios de escopo e aceitação

- **Navegação inteligente:** rotas confiáveis em torno de obstáculos, recuperação quando preso, avaliação de múltiplas coberturas e caminhos de retirada; adotar navegação/navmesh ou solução equivalente apenas se realmente necessária.
- **Combate tático:** alternância entre avançar, cobrir, espiar, recuar, flanquear, pressionar, suprimir, buscar ângulos de tiro e mudar de posição conforme a ameaça.
- **Coordenação de esquadrão:** papéis complementares (assalto, apoio, flanqueador, atirador), comunicação de alvos/última posição observada, evitando que todos executem a mesma decisão.
- **Percepção e memória:** visão com obstáculos, alcance e campo de visão, resposta contextual a disparos/sons, perda de contato e investigação sem rastreamento sobrenatural do jogador.
- **Recursos e posturas:** munição, recarga protegida, agachamento, posição deitada, mira e disparo coerentes com animação e colisão; evitar atirar através de paredes.
- **Personalidades e dificuldade:** runner, soldado comum, pesado/Juggernaut e aliados com decisões distintas, precisão/reação balanceadas e progressão de dificuldade sem trapaças.
- **Animações e apresentação:** transições naturais entre corrida, cobertura, recarga, mira, tiro, dano e morte, ligadas aos estados reais da IA.
- **Desempenho e QA:** decisões escalonadas e limites de consultas de física; verificar até 12 inimigos ativos e sessões de 15 ondas no Ryzen 5 7530U com 8 GB RAM, sem travamentos nem queda excessiva de FPS.

**Entrega:** dividir em pequenas etapas documentadas (percepção → navegação/cobertura → combate/flanqueio → coordenação → animações → balanceamento/QA), cada uma com testes, estados **PENDENTE / PARCIAL / CONCLUÍDO** e build Windows no GitHub Releases quando aprovada. **Não considerar “IA militar completa” concluída com os scripts táticos da v0.9.16.**
