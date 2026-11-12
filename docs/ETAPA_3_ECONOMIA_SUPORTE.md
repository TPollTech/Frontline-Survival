# Frontline Survival — Etapa 3: economia, estações e suporte tático

**Estado:** especificação de pré-produção v1.0, 10/11/2026. **Não aprovada para implementação.**  
**Base verificada:** protótipo 0.7 em scripts/main.gd, scripts/player.gd e scripts/ally.gd; ROADMAP.md; Etapas 0–2; registro de decisões.  
**Meta:** fazer cada compra ter utilidade, custo e contrajogo, sem criar bloqueios de progressão ou desequilíbrio nas ondas infinitas.

## 1. Restrições estabelecidas

- Survival solo offline, ondas contínuas, preparação padrão de 75 segundos entre ondas (configurável 45–120).
- Três estações físicas: armas, equipamentos e suporte. Interação apenas com F na proximidade, sem arsenal global no B.
- Teclas 1/2 alternam arma principal/pistola; G usa granada; 3 chama esquadrão previamente comprado; 4 aciona ataque aéreo previamente comprado.
- HUD discreto; crédito, vida, colete, munição, onda e recursos comprados precisam ser legíveis.
- Campo de Testes permanece disponível; capital de treinamento atual de $1.200 não deve ser confundido com economia aprovada para os mapas finais.
- Hardware-alvo Ryzen 5 7530U, 8 GB RAM, Godot Compatibility. Não ampliar efeitos, NPCs ou torretas sem medir desempenho.

## 2. Inventário fiel ao código 0.7 (implementado, não validado em sessão real)

| Estação | Produto | Preço atual | Efeito presente |
| --- | --- | ---: | --- |
| Armas | SMG | $180 | Equipa arma; propriedade registrada no jogador |
| Armas | Fuzil | $350 | Equipa arma |
| Armas | Escopeta | $450 | Equipa arma |
| Armas | LMG | $650 | Equipa arma |
| Equipamentos | Repor munição | $80 | Recarrega reservas pelo método do jogador |
| Equipamentos | +50 colete | $130 | Aumenta proteção |
| Equipamentos | +50 vida | $90 | Cura |
| Equipamentos | +2 granadas | $100 | Adiciona granadas |
| Equipamentos | Melhoria de dano (+24%) | $220 | Incrementa contador global até 3; comportamento por arma precisa revisão |
| Suporte | Torreta automática | $300 | Instância imediata à frente do jogador; duração descrita de 115 s |
| Suporte | Esquadrão de 2 soldados | $420 | Compra token; ativa com 3; até 6 aliados simultâneos |
| Suporte | Ataque aéreo | $420 | Compra token; ativa com 4 apenas durante combate; marcador por 1 s |

**Economia de ondas atual:** recompensa por eliminação depende da classe (base soldado 55, corredor 78, pesado 160), acrescida de até $80 conforme a onda; bônus ao terminar = $60 + $20 × número da onda; +$12 por headshot; cura de 15 de vida ao concluir. A onda tem min(5 + 2 × onda, 55) inimigos e teto de 12 simultâneos. São valores do código, não equilíbrio aprovado.

**Riscos concretos encontrados na leitura:**

1. O preço do upgrade é $220 por nível, mas a variável de upgrades é global; a estrutura por arma existe e requer regra consistente antes de expandir personalização.
2. A compra de torreta instancia imediatamente, sem seleção/validação explícita de posição livre; pode colidir com parede, loja ou NPC.
3. A descrição de reposição de munição não esclarece quantas armas/munições são atendidas; a regra deve ser exibida na loja.
4. O texto de falta de granadas manda comprar no SUPORTE, mas o item está na estação EQUIPAMENTOS; corrigir apenas quando a etapa for implementada.
5. O contador de alvos atingidos pelo ataque aéreo incrementa por inimigo na área, não por morte confirmada; o texto de HUD deve refletir impactos, não abates.
6. Compra e uso de reforços devem impedir consumo de token quando a ação falha por posicionamento inválido ou limite.
7. A renda de abates cresce por onda; sem telemetria de compras, a economia pode se tornar abundante demais e eliminar escolhas.

## 3. Princípios de economia propostos

**P-013 — Economia sem softlock:** o jogador deve conseguir enfrentar ao menos as primeiras ondas com a pistola inicial e munição disponível, sem precisar comprar algo impossível. Falta de créditos não pode bloquear início de onda.

**P-014 — Três decisões de compra:** (a) aumentar poder de fogo, (b) recuperar sobrevivência, (c) adquirir suporte temporário. Os três devem competir por recursos de modo significativo.

**P-015 — Separar treino e Survival:** manter $1.200 no Campo de Testes; **proposta** de saldo inicial de $0–$300 no modo clássico, decidido após simulações e testes reais. Não alterar o valor do treino.

**P-016 — Sem escalada descontrolada:** preços estáveis inicialmente; não indexar automaticamente preços à onda. Se a renda se tornar excessiva, testar custo de munição, limites de recursos e escolhas de oportunidade antes de inflação arbitrária.

**P-017 — Compras transacionais:** validar saldo, limite, estoque lógico e local antes de debitar; aplicar efeito uma única vez; mostrar erro e preservar créditos em caso de falha.

**P-018 — Clareza da interface:** cada item mostra nome, preço, efeito exato, limite, duração/quantidade e estado (comprar/equipar/indisponível). O jogador nunca deve perder créditos sem confirmação visual.

### Hipótese de equilíbrio

A economia deve ser calibrada em sessões de ondas 1–5, 6–10, 11–15 e 16–20, medindo créditos recebidos, gastos por categoria, estoque de munição, vida restante e mortes. **Não definir preços finais só pela leitura das constantes.** Usar pelo menos três estratégias de teste: ofensiva (arma primeiro), defensiva (colete/vida), suporte (torreta/esquadrão).

## 4. Contrato de estações físicas

**Interação:** F próximo da estação abre/fecha painel; compras por botões e teclado 1–5; controles de combate travados enquanto a loja está aberta, sem pausar ondas automaticamente. A interface não pode ser aberta fora do raio, nem mudar de estação remotamente por abas.

**Estados:** FECHADA → ABERTA → VALIDANDO_COMPRA → SUCESSO/ERRO → ABERTA → FECHADA. Se começar uma onda, o painel pode ser fechado com aviso contextual; sem compra parcial.

**Verificações antes de debitar:** jogador vivo, estação alcançável, produto disponível, saldo suficiente, limite de compra, limite de entidades, destino válido para posicionamento e modo de jogo. Rejeições não alteram saldo, tokens ou inventário.

**Comportamento de arma já possuída:** equipar sem pagar novamente. Compras de munição, cura e colete não devem cobrar se não acrescentarem nada; mostrar capacidade máxima.

**UI proposta:** uma coluna de itens com preço e ícone simples; painel lateral curto de efeito/duração; saldo sempre visível; compra confirmada em menos de dois segundos sem bloquear câmera depois do fechamento. Navegável por mouse e teclado, com foco perceptível.

## 5. Regras de equipamentos e inventário (propostas)

| Recurso | Proposta | Regra de proteção |
| --- | --- | --- |
| Munição | Repor reservas das armas possuídas até limites próprios | Não cobrar se todas as reservas já estão cheias |
| Vida | Cura +50 até vida máxima | Não cobrar com vida cheia |
| Colete | Adicionar até +50, respeitando capacidade máxima | Não cobrar com colete cheio |
| Granadas | +2, limite de inventário a decidir | Não cobrar se não couberem duas; exibir quantidade atual |
| Upgrade | Máximo 3 níveis, com +24% por nível como base atual | Decidir se é global ou por arma; evitar dupla contagem |
| Arma principal | Uma principal equipada e pistola secundária | Troca entre armas compradas sem custo duplicado |
| Recursos de suporte | Tokens persistem na partida até uso válido | Não consumir em comando inválido |

**Mina terrestre:** prevista no ROADMAP, mas não existe na loja 0.7; **proposta para pós-estabilização**, sujeita a custo de IA/física e clareza de colocação. Não tratá-la como implementada.

## 6. Suporte tático — comportamento proposto

### 6.1 Torreta

- Compra na estação de suporte, com pré-visualização de local e confirmação antes do débito (proposta).
- Manter inicialmente **até 2 torretas ativas**, como no código. Duração de 115 s é valor de referência a testar, não definitivo.
- Posicionamento exige piso livre, sem parede, NPC ou bloqueio de loja. Se inválido, informar motivo e não cobrar.
- Adquirir alvo hostil em linha de visão; não atravessar obstáculos; informar visualmente atividade, dano e término.
- Onda encerrada não deve renovar duração nem deixar torreta imortal; definir se o temporizador pausa durante a preparação (proposta: não pausa, mas só depois de medir custo/benefício).
- Evitar explosões, rastros e sons exagerados; limitar disparos e efeitos no hardware-alvo.

### 6.2 Esquadrão aliado

- Compra de **1 token = 2 soldados**; tecla 3 consome somente quando a chamada for válida.
- Manter limite atual de **6 aliados simultâneos**; impedir que a compra seja desperdiçada por limite ou spawn obstruído.
- Duração atual de cada aliado: 160 s no código, a validar com os 75 s de preparação.
- IA de apoio: acompanhar jogador ou alvo hostil acessível, priorizar hostis próximos, sem bloquear portas/lojas. Não exigir comandos complexos na primeira versão.
- Identificação azul e silhueta própria; evitar confusão com inimigos.
- Não contar aliados no total de inimigos vivos; abates por aliados devem respeitar recompensa única do inimigo.

### 6.3 Ataque aéreo

- Compra token na estação; tecla 4 apenas em combate, após mirar área válida.
- Código atual: marcador por aproximadamente 1 s; dano em raio de 13 m, escala até 275 na origem. Esses números são base de teste.
- Proposta: prévia curta e visível do alvo, aviso antes do impacto e confirmação de posição dentro da área jogável.
- Não gastar token se não houver alvo válido; não atingir jogador por comportamento surpresa sem indicação clara.
- Contar separadamente **alvos atingidos** e **eliminações**; não anunciar morte de quem apenas sofreu dano.
- Aguardar teste de explosões múltiplas e de compatibilidade com reforços, sem criar efeitos pesados.

## 7. Matriz de integração com ondas e modos

| Situação | Comportamento exigido/proposto |
| --- | --- |
| Preparação de 75 s | Jogador anda, recarrega e compra; tokens podem ser guardados |
| N antecipa onda | Loja fecha com segurança, saldo/inventário preservados |
| Combate com loja aberta | Onda continua; interface não pode bloquear o jogador permanentemente |
| F fora do alcance | Não abre loja; nenhuma transação |
| Morte no treino | Manter créditos, armas e tokens; reanimação não duplica compras |
| Morte clássica | Fim de partida, compras e suporte desativados |
| Reinício | Zerar estado da partida nova conforme modo, sem carregar tokens antigos |
| Mudança de mapa | Mesmas regras de economia e suporte; posições de loja são do mapa |
| Onda 10/15/20 | Recursos precisam ter custo-benefício sem eliminar toda a ameaça automaticamente |

## 8. Critérios de aceitação e testes futuros

| ID | Cenário | Resultado esperado | Situação atual |
| --- | --- | --- | --- |
| E3-01 | Comprar sem saldo | Compra rejeitada, saldo inalterado | **PARCIAL** — código/CI parcial; falta aceite completo |
| E3-02 | Comprar arma já possuída | Equipa gratuitamente | **PARCIAL** — código/CI parcial; falta aceite completo |
| E3-03 | Comprar cura com vida cheia | Sem débito, mensagem explicativa | **PENDENTE** — cobrança de cura com vida cheia ainda não é rejeitada |
| E3-04 | Comprar munição com reservas cheias | Sem débito, limites respeitados | **PENDENTE** — cobrança de munição cheia ainda não é rejeitada |
| E3-05 | Comprar upgrade no nível 3 | Rejeita sem cobrança | **PARCIAL** — código/CI parcial; falta aceite completo |
| E3-06 | Colocar torreta em parede ou NPC | Rejeita sem cobrança nem instância | **PENDENTE** — posicionamento de torreta não valida paredes/NPC |
| E3-07 | Tentar terceira torreta | Rejeita e mantém saldo | **PARCIAL** — código/CI parcial; falta aceite completo |
| E3-08 | Chamar esquadrão com 6 aliados | Não consome token | **PARCIAL** — código/CI parcial; falta aceite completo |
| E3-09 | Chamar ataque fora de combate | Não consome token | **PARCIAL** — código/CI parcial; falta aceite completo |
| E3-10 | Acionar ataque em alvo inválido | Não consome token | **PENDENTE** — token aéreo consumido antes de validar destino |
| E3-11 | Comprar durante preparação e antecipar N | Estado íntegro, loja fechada | **PARCIAL** — código/CI parcial; falta aceite completo |
| E3-12 | Morte e reanimação de treino | Saldo, armas, tokens preservados | **PARCIAL** — código/CI parcial; falta aceite completo |
| E3-13 | Morte clássica | Sem compras após game over | **PARCIAL** — código/CI parcial; falta aceite completo |
| E3-14 | Aliado mata último inimigo | Contador zera uma vez, onda conclui | **PARCIAL** — código/CI parcial; falta aceite completo |
| E3-15 | Ataque aéreo atinge mas não mata | HUD não registra eliminação falsa | **PENDENTE** — contador de alvos atingidos pode ser confundido com eliminações |
| E3-16 | Comprar e ativar suporte em ondas 5,10,15 | Sem perda de FPS inaceitável | **PENDENTE** — benchmark de suporte não realizado |
| E3-17 | Sessão longa de 20 ondas | Economia não bloqueia progresso nem elimina escolhas | **PENDENTE** — 20 ondas reais não testadas |
| E3-18 | Usar mouse e teclado nas três estações | Foco, saldo, feedback e fechamento corretos | **PARCIAL** — código/CI parcial; falta aceite completo |

**Nenhum teste foi executado neste ciclo.** Registrar build, commit, FPS/ram e resultados antes de aprovar a implementação.

## 9. Implementação futura em incrementos independentes

1. **3A — Contrato de transação e limites:** separar validação, débito e efeito; testes E3-01 a E3-05. Depende da Etapa 0.
2. **3B — Interface física e feedback:** comparação, navegação e mensagens; E3-11, E3-18.
3. **3C — Inventário e upgrades:** corrigir consistência entre upgrades globais/por arma, capacidades e compra útil.
4. **3D — Torreta e esquadrão:** posicionamento válido, duração, limite e IA de apoio; E3-06 a E3-08.
5. **3E — Ataque aéreo:** alvo válido, marcador, token e contabilização; E3-09, E3-10, E3-15.
6. **3F — Balanceamento:** comparar três estratégias de gasto ao longo de 20 ondas; E3-16 e E3-17. Depende da Etapa 2 validada.

## 10. Decisões pendentes

| Código | Decisão | Padrão provisório |
| --- | --- | --- |
| E3-P01 | Créditos iniciais no Survival clássico | $0–$300 para testar; manter $1.200 no treino |
| E3-P02 | Upgrade global ou por arma | Decidir antes de alterar lógica |
| E3-P03 | Limite de granadas e capacidades | Definir com base em sessões reais |
| E3-P04 | Torreta consome duração na preparação | Proposta: sim, mas requer balanceamento |
| E3-P05 | Esquadrão dura 160 s | Preservar temporariamente e medir |
| E3-P06 | Ataque aéreo tem dano ao jogador | Proposta: sem fogo amigo na versão base |
| E3-P07 | Preços e recompensas definitivos | Só após 10–20 ondas de teste |
| E3-P08 | Mina terrestre | Adiar até núcleo estável |

**Fora de escopo nesta etapa:** veículos, comandos complexos de esquadrão, árvore de perks, loot boxes, compras com dinheiro real, multiplayer e inventário persistente entre partidas.

---

**Resultado desta rodada:** Etapa 3 documentada; nenhuma alteração de código, cena ou asset. Próxima lacuna recomendada: Etapa 4 — especificação de arquitetura de mapas multissetoriais, rotas, navegação e spawn, mantendo o Campo de Testes.


---

## 11. Revisão de escopo — requisitos novos do núcleo (11/11/2026)

**Nota de precedência:** a frase anterior "árvore de perks fora de escopo" se referia a uma **árvore extensa**. O usuário agora requer explicitamente **perks compráveis simples** no Campo de Testes, sem árvore, e extras de sobrevivência. Essa mudança **não** autoriza expansão de mapa, helicóptero ou multiplayer.

### Economia, metas e painel de fim de onda

- Fontes de dinheiro separadas: recompensa por NPC, bônus por onda, bônus de precisão/tempo/headshot/dano e desafios especiais.
- Dados da onda: disparos, tiros que acertam, headshots que matam, dano tomado por vida/colete, abates e tempo de combate.
- Recompensas sugeridas como referência: primeiro cumprimento da meta +$500, repetição +$1000 por meta elegível/onda, limitadas até validar economia. O MW3 histórico sorteava metas da onda; no Frontline escolher duas elegíveis por onda.
- **Quad Kill ≠ Rampage:** quatro inimigos mortos por um único evento ≠ quatro abates rápidos com tiros diferentes. Killstreak sem receber dano é uma terceira métrica, não sinônimo.
- Ao matar último NPC: gerar resumo e detalhar créditos, sem pagar duas vezes o dinheiro dos kills já recompensados.
- Preparação após onda: atualmente 75 s configurado; **30 s é o padrão original confirmado e a proposta para novos jogos Frontline**, com presets maiores e preservação de settings atuais.

### Lojas e perks

- **Arsenal:** anexos compráveis para **cada uma das cinco classes**; arma comprada começa sem attachment, red dot e silenciador independentes e cumulativos.
- **Equipamentos:** Kit de Reanimação consumível comprado, separado do estado Última Chance.
- **Suporte:** perks próprios com um ativo por vez; substituir perk anterior sem benefícios empilhados.
- Toda compra desconta apenas após validação da entrega. Mudança de arma não clona attachment ou compra.
- O silenciador para todas as armas é uma decisão própria do Frontline; não atribuir esse item à loja original de MW3 sem fonte.

### Dependências de código

\`WaveStats\` centraliza contagem; \`ChallengeEngine\` monitora eventos uma única vez; \`MoneyLedger\` reconcilia saldo e relatório; \`PerkInventory\`/arma controla vantagens e slots; \`DownedState\` e \`PostureController\` mantêm transições físicas de acordo com o modo de jogo.

**Estado:** propostas arquiteturais e requisitos do usuário documentados; **PENDENTE DE IMPLEMENTAÇÃO** nesta etapa.  
[Design detalhado](NUCLEO_SURVIVAL_PERKS_ATTACHMENTS_MOVIMENTO.md) · [Pesquisa histórica](PESQUISA_MW3_SURVIVAL_MECANICAS.md)


---

## Auditoria de execução — 12/11/2026 (base v0.9.17)

**Quadro atualizado após o documento histórico.** Critérios: **0 concluídos em CI; 11 parciais; 7 pendentes**. **A Etapa 3 ainda NÃO está completamente concluída.**

### Entregas já implementadas

- [x] Três lojas físicas por F e compras implementadas — **CONCLUÍDO (CÓDIGO/CI)**
- [x] Perks, Last Stand, attachments e resumo financeiro de ondas integrados ao jogo — **CONCLUÍDO (CÓDIGO/CI)**

### Itens parciais

- [ ] Torretas, esquadrão e ataque aéreo funcionam em código; casos-limite e posicionamento incompletos — **PARCIAL**
- [ ] Interface de loja usa mouse; navegação por teclado/comparação ainda requer trabalho — **PARCIAL**

### Pendências de execução ou validação

- [ ] Bloquear compras inválidas de cura/munição e corrigir validação do alvo aéreo — **PENDENTE**
- [ ] Equilibrar economia/suporte com 10–20 ondas reais — **PENDENTE**

**Evidências:** [Godot CI da v0.9.17](https://github.com/TPollTech/Frontline-Survival/actions/runs/43171938905) · [Release Windows v0.9.17](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.17) · [Auditoria central](AUDITORIA_CHECKLISTS_2026_11_12.md). Teste CI não substitui validação real no notebook.
