# Frontline Survival — Etapa 0: Estabilização e Qualidade

**Estado:** especificação de planejamento; nenhuma tarefa aqui é considerada testada.  
**Data:** 10/11/2026  
**Base:** protótipo 0.7, branch main.  
**Prioridade:** P0.  
**Documento pai:** [ROADMAP.md](../ROADMAP.md).

> Esta etapa NÃO adiciona mecânicas. Seu propósito é garantir que o jogo já existente seja jogável de ponta a ponta no notebook-alvo antes de expandir o escopo.

## 1. Resultado esperado

A versão 0.7 deverá ser capaz de iniciar, combater, comprar, receber reforços, avançar ondas e terminar (somente quando apropriado), sem regressões críticas. O Campo de Testes permanece como laboratório permanente.

### Regras já aprovadas — NÃO reabrir nesta etapa

- Survival solo e offline, em Godot 4 e renderizador Compatibility.
- Ryzen 5 7530U, Radeon integrada e 8 GB de RAM como referência real de teste.
- Ondas sucessivas; última eliminação inicia preparação; após o intervalo, a próxima onda inicia sem intervenção.
- Preparação padrão de 75 segundos (ajustável de 45 a 120) e tecla N opcional para antecipar.
- Estações físicas para armas, equipamentos e suporte com interação por F; sem loja global pela tecla B.
- Campo de Testes com textura de asfalto preservada; capital inicial de teste de $1.200.
- Reanimação opcional no modo de testes, preservando dinheiro, armas e onda; modo clássico de uma vida.
- HUD essencial, configurações de áudio persistentes, esquadrão na tecla 3 e suporte aéreo na tecla 4.

## 2. O que já existe e o que ainda NÃO foi validado

O README e os scripts descrevem armas, inimigos, compras, menus, apoio e progressão, mas **o código em repositório não prova por si só que esses sistemas funcionam em execução**. Os testes anteriores foram majoritariamente estáticos. Não marcar qualquer checklist como concluído sem teste no Godot.

## 3. Plano de execução

### 0A — Inicialização e diagnóstico (bloqueante)

| ID | Verificação | Resultado esperado | Estado |
| --- | --- | --- | --- |
| QA-001 | Clonar/importar project.godot em pasta limpa | Projeto importa GLBs e WAVs sem arquivos ausentes | Pendente |
| QA-002 | Executar a cena principal com F5 | Menu inicial aparece, sem tela preta | Pendente |
| QA-003 | Examinar Debugger e Output | Nenhum erro de parser, referência inválida ou exceção crítica | Pendente |
| QA-004 | Iniciar, pausar, retomar e reiniciar | Árvore de cena, câmera e captura do mouse em estado correto | Pendente |
| QA-005 | Abrir no notebook-alvo em 1280×720 | Jogo aceita teclado/mouse e renderizador Compatibility | Pendente |

### 0B — Combate e controles (P0)

| ID | Ação | Resultado esperado | Estado |
| --- | --- | --- | --- |
| QA-010 | Atirar com mouse esquerdo | Munição diminui, disparo acerta, áudio/efeito correspondem | Pendente |
| QA-011 | Mirar, recarregar, trocar arma e disparar novamente | Sem travar tiro, câmera ou munição | Pendente |
| QA-012 | Comprar SMG, fuzil, escopeta e LMG | Inventário atualiza, arma aparece e funciona | Pendente |
| QA-013 | Disparar até esgotar carregador/reserva | Sem números negativos, sem tiro gratuito | Pendente |
| QA-014 | Testar granada, corpo a corpo e headshot | Dano e recompensa coerentes; sem fechar partida | Pendente |
| QA-015 | Abrir loja com F próximo e tentar fora de alcance | Interação contextual; B não abre loja | Pendente |

### 0C — Onda, dinheiro e estados da partida (P0 máximo)

| ID | Ação | Resultado esperado | Estado |
| --- | --- | --- | --- |
| QA-020 | Eliminar sete inimigos da onda 1 | Inicia preparação para onda 2; NÃO mostra Fim de Jogo | Pendente |
| QA-021 | Aguardar intervalo sem apertar N | Onda 2 começa automaticamente ao chegar a zero | Pendente |
| QA-022 | Comprar durante a preparação | Tempo/estado preservados, próxima onda mantém a compra | Pendente |
| QA-023 | Apertar N durante preparação | Inicia onda antecipadamente uma vez, sem duplicar spawns | Pendente |
| QA-024 | Apertar N durante combate | Não altera indevidamente a onda | Pendente |
| QA-025 | Completar ondas 1 a 15 em uma única sessão | Progressão sem reset espontâneo, contador travado ou game over indevido | Pendente |
| QA-026 | Morrer em modo treino | Reaparece conservando onda, arma, créditos e recordes da sessão | Pendente |
| QA-027 | Morrer em modo clássico | Fim de jogo apenas após morte, com reinício controlado | Pendente |
| QA-028 | Último inimigo preso ou fora da área útil | Situação detectável e reproduzível; não deixar onda permanentemente sem solução | Pendente |

### 0D — Reforços, interface e persistência (P0/P1)

| ID | Ação | Resultado esperado | Estado |
| --- | --- | --- | --- |
| QA-030 | Comprar e chamar esquadrão com 3 | Débito/estoque corretos, aliados aparecem e atuam | Pendente |
| QA-031 | Comprar e ativar ataque aéreo com 4 | Recurso consumido uma única vez; alvo e impacto coerentes | Pendente |
| QA-032 | Testar torreta durante e entre ondas | Não esgota duração antes de iniciar combate sem justificativa | Pendente |
| QA-033 | Alterar áudio geral, tiros e UI para 0/baixo/médio | Sem áudio estourado e controles efetivos | Pendente |
| QA-034 | Fechar e reabrir o jogo | Configurações persistem, sem corromper configuração | Pendente |
| QA-035 | Usar mouse em lojas, pausa e configurações | Cliques não atiram por trás do menu; Esc não quebra captura | Pendente |
| QA-036 | Conferir HUD em 720p | Vida, colete, munição, dinheiro, onda e inimigos legíveis; sem texto de controle permanente | Pendente |

## 4. Roteiro obrigatório de partida de 15 ondas

1. Abrir o jogo do zero, anotar versão, modo escolhido e configurações.
2. Iniciar no Campo de Testes e registrar capital inicial.
3. Antes da primeira onda, comprar pelo menos uma arma na estação física com F.
4. Finalizar onda 1 e anotar o comportamento da transição para preparação.
5. Durante a preparação, comprar munição ou equipamento; não usar N em pelo menos uma transição.
6. Nas ondas seguintes, testar N em outra preparação e conferir a ausência de spawns duplicados.
7. Nas ondas 4 e 11, observar mudança dos kits de armas dos inimigos.
8. Testar uma torreta, um esquadrão e um ataque aéreo, se os créditos obtidos permitirem.
9. Em um ciclo separado, testar morte no modo treino e no modo clássico.
10. Alcançar onda 15 e registrar bugs, FPS, RAM e situações de IA presa. Repetir os casos que falharam antes de fechar a etapa.

**Observação:** não é suficiente "chegar na onda 15" se a câmera, as lojas ou os reforços quebrarem durante a sessão.

## 5. Desempenho — protocolo de medição

**Não inventar FPS:** o desempenho só é aprovado mediante teste real no notebook. Medir com o equipamento ligado na tomada, plano de energia anotado, resolução registrada e apps pesados em segundo plano fechados, mas sem alterar a configuração de forma não documentada.

Registrar FPS observado, pior queda perceptível, RAM do processo/sistema, temperatura caso haja ferramenta disponível e número de inimigos simultâneos em:

- Menu inicial / Campo de Testes vazio.
- Onda 1, onda 5, onda 10 e onda 15.
- Combate com ao menos 10 inimigos ativos, se a progressão permitir.
- Combate com torreta + esquadrão + efeitos, quando viável.

**Meta de produto, não resultado medido:** piso desejado de 30 FPS em 720p baixo durante o combate; buscar 60 FPS nas situações comuns. Travamentos, queda progressiva a cada onda e encerramento por falta de memória são bloqueantes, mesmo que a média pareça aceitável.

### Modelo de registro

| Cenário | Resolução | FPS observado | RAM observada | Inimigos | Erros / notas |
| --- | --- | --- | --- | --- | --- |
| Menu | — | Não medido | Não medido | 0 | Pendente |
| Onda 1 | — | Não medido | Não medido | — | Pendente |
| Onda 5 | — | Não medido | Não medido | — | Pendente |
| Onda 10 | — | Não medido | Não medido | — | Pendente |
| Onda 15 | — | Não medido | Não medido | — | Pendente |
| Efeitos + reforços | — | Não medido | Não medido | — | Pendente |

## 6. Classificação de defeitos

- **P0 / bloqueante:** jogo não abre, não atira, trava, perde progressão sem comando, termina ao concluir onda, impossibilita comprar/recarregar, erro crítico de script ou memória.
- **P1 / alta:** efeito sonoro excessivo, câmera inconsistente, compra falha ocasional, IA frequente presa, FPS abaixo do piso-alvo nos testes definidos.
- **P2 / refinamento:** animação pouco realista, HUD desalinhado sem bloquear jogo, cosméticos e melhorias visuais.

**Modelo do bug:** ID, versão/commit, Godot usado, plataforma, modo, onda, passos de reprodução, resultado esperado, resultado real, trecho do Debugger/Output, severidade, vídeo ou captura quando possível.

## 7. Estratégia de correção — somente após a evidência

1. Reproduzir e registrar.
2. Corrigir um defeito por vez em branch específica.
3. Executar verificação estática, teste do sistema atingido e regressão mínima do loop das ondas.
4. Não refatorar grandes módulos no mesmo commit de uma correção urgente, salvo necessidade demonstrada.
5. Atualizar registro de teste com commit e resultado; não marcar "passou" por inspeção de código apenas.

**Proposta técnica (ainda não aprovada):** separar gradualmente o script principal em controladores de ondas, economia, HUD e suporte, mas só depois de estabilizar o comportamento atual. A refatoração não deve mudar regras da partida.

## 8. Critérios de aceite da Etapa 0

- [x] Projeto abre no Godot sem erros críticos. — **CONCLUÍDO (CÓDIGO/CI)**: importação e CI Godot 4.4.1 aprovados.
- [x] Disparo, mira, recarga, compras e controles básicos funcionam. — **CONCLUÍDO (CÓDIGO/CI)**: disparo, lojas, recarga e controles exercitados no CI.
- [ ] Avanço de 15 ondas sem término indevido nem contador travado. — **PENDENTE**: faltam 15 ondas reais homologadas.
- [x] Modo treino e modo clássico se comportam conforme suas regras. — **CONCLUÍDO (CÓDIGO/CI)**: treino e clássico implementados e cobertos pela integração.
- [x] Reforços ativam e são consumidos corretamente. — **CONCLUÍDO (CÓDIGO/CI)**: reforços/tokens integrados nos testes.
- [ ] Configurações de áudio e tela persistem após reinício. — **PARCIAL**: persistência por ConfigFile; falta teste após reinício no Windows.
- [ ] HUD e menus não interferem no combate. — **PARCIAL**: menus passaram CI; visual v0.9.17 carece de aprovação.
- [ ] Medições de FPS e memória do notebook foram registradas. — **PENDENTE**: FPS e RAM do notebook não medidos formalmente.
- [ ] Nenhum P0 aberto; pendências P1 conhecidas e documentadas. — **PENDENTE**: restam pendências de 15 ondas e QA visual.

## 9. Decisões versus propostas

| Item | Situação |
| --- | --- |
| Regras de onda, compras F, mapa de testes, 75s e reanimação opcional | **Decisão já estabelecida** |
| Fazer testes reais no Ryzen 5 7530U / 8 GB | **Necessidade obrigatória para aceitar** |
| Matriz de QA e relatório por bug | **Proposta de processo neste documento** |
| Refatorar main.gd em módulos | **Proposta técnica — depende de QA** |
| Alterar preços, armas, mapas ou IA | **Fora de escopo da Etapa 0** |

**Próxima ação:** executar o checklist real e preencher os resultados. Em paralelo, pode-se aprovar o desenho da Etapa 1, sem implementá-lo antes de cumprir os critérios desta etapa.

---

## Auditoria de progresso — 12/11/2026

Checklist desta etapa sincronizada com o CI da v0.9.17: **4 critérios concluídos em código/CI, 2 parciais e 3 pendentes**. O jogo passa no Godot, tem partida/armas/lojas e testes de estados, mas a **Etapa 0 não está concluída** porque faltam 15 ondas reais, benchmark do notebook e aprovação do HUD da v0.9.17. [Auditoria central](AUDITORIA_CHECKLISTS_2026_11_12.md).
