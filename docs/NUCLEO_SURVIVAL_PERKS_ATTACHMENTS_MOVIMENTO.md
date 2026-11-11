# Frente M0/M1/M3 — núcleo Survival fiel a MW3 (2011), no Campo de Testes

**Data:** 11/11/2026. **Tipo:** especificação de produto antes da implementação, não resultado de build.  
**Origem:** exigências do jogador: **perks, Última Chance/Last Stand, bônus em dinheiro, estatísticas no fim da onda, 30 segundos, attachments para todas as armas, agachar e deitar**.  
**Referências históricas e limites:** [Pesquisa MW3 — mecânicas](PESQUISA_MW3_SURVIVAL_MECANICAS.md).  
**Prioridade confirmada:** terminar e testar no **Campo de Testes**; não desenvolver mapas novos, entradas por helicóptero/caminhão ou outras ondas especiais agora.  
**Critério de escopo:** as funcionalidades acima são **requisitos pedidos pelo usuário**; valores monetários e efeitos específicos abaixo são **propostas de balanceamento**, não números já aprovados nem funcionalidades existentes.

## 1. Contrato do loop de 30 segundos e resumo de onda

- Após eliminar o último inimigo: estado \`COMBATE -> ONDA_FINALIZADA -> PREPARAÇÃO\`, sem reiniciar a partida.
- Proposta: intervalo entre ondas **30 segundos por padrão** (fidelidade ao MW3 2011), com opções no menu **30 / 45 / 60 / 75 / 90 / 120 segundos**. O usuário havia escolhido 75 s anteriormente: **não zerar as preferências já gravadas**. A mudança do valor padrão para *novas instalações* será aplicada em sprint de código separada, não nesta rodada.
- Preparação inicial é variável diferente do intervalo entre ondas (\`INITIAL_PREPARATION_SECONDS = 25\` atualmente); não alterar sem motivo.
- \`N\` antecipa a onda durante preparação. Pausar, menu de compras e sumário não podem reiniciar a contagem.
- Após o último inimigo: resumo de onda visível **3–5 segundos**, discreto; pode abrir detalhes durante a preparação por tecla opcional, sem bloquear lojas ou as 30 s.
- Princípio: se a janela de compras é curta, estações devem ser acessíveis e abertura/fechamento extremamente rápida.

### 1.1 Contrato de dados da onda

\`WaveStats\` deve guardar:
\`wave_number, started_at, ended_at, kills_player, assists, kills_allies, shots_fired, shots_hit, headshot_kills, headshot_hits, damage_taken_health, damage_taken_armor, money_from_kills, money_from_challenges, money_from_wave, money_spent, challenge_completions, reward_total\`.

Definições:
- **Precisão = 100 × tiros que acertaram ao menos um inimigo / disparos efetuados pelo jogador**. Um tiro de escopeta conta **uma vez**, mesmo que quatro pellets acertem. Não contar projéteis de aliados. Sem tiros, mostrar \`--\` (não 100%).
- **Headshots (abates)** só somam quando o tiro do jogador mata por dano de cabeça. \`headshot_hits\` pode ser registrado separadamente, mas não substitui abates.
- **Dano recebido** registra separadamente vida e colete e pode ser agregado na pontuação; qualquer acerto recebido zera sequência \`sem sofrer dano\`.
- **Economia** tem fontes diferentes; um inimigo morto por explosão/aliado não pode pagar o mesmo bônus duas vezes.
- **Duração** mede só combate (exclui preparação, pausa e tempo em menus pausados).
- **Resumo da onda** não deve bloquear o controle de \`F\` das lojas, a tecla \`N\` e os controles de pausa.

Exemplo de relatório (valores demonstrativos):
\`\`\`text
ONDA 08 CONCLUÍDA
Eliminações         18
Headshots            5
Precisão            63%
Duração            01:14
Dano recebido       24
--------------------------------
Abates             +$360
Desafios          +$1.000
Bônus de onda      +$240
TOTAL DA ONDA     +$1.600
PRÓXIMA ONDA EM 00:30
\`\`\`
Esses números são de *mockup*, não parâmetros oficiais de MW3 ou do projeto.

## 2. Desafios e bônus em dinheiro por desempenho

### 2.1 Motor de desafios

- Avaliar eventos de combate por \`event_id\`, \`enemy_id\`, \`killer\`, \`damage_source\` e \`time\` para distinguir quem matou, a causa e evitar contagem duplicada.
- Começar com **duas metas por onda**, sorteadas dentre as elegíveis (como relatado em guias MW3), selecionadas antes do início do combate.
- **Proposta de valores:** primeiro cumprimento por meta = **+$500**; segundo = **+$1.000**; limitar a segunda recompensa de cada meta por onda até testar a inflação da economia.
- Estatísticas continuam contabilizadas mesmo que a meta não tenha sido sorteada, mas só metas ativas pagam dinheiro.
- Mostrar aviso visual breve \`+500 RAMPAGE\`, sem som agudo, e registrar no resumo.
- Se o jogador falhar, não cobrar punição monetária. Saldo nunca fica negativo.

| Desafio | Critério operacional proposto | Observação |
| --- | --- | --- |
| **Rampage** | 4 inimigos eliminados em até 4 segundos | Meta temporal independente de Quadkill |
| **Killstreak** | 5 abates pessoais **sem receber nenhum acerto** | Dano no colete também reinicia |
| **Headshots** | 5 abates por tiro na cabeça na onda | Não confundir 5 impactos sem matar |
| **Quad Kill** | 4 inimigos mortos pelo **mesmo evento explosivo** ou um único disparo | Não pagar como Quadkill por quatro tiros em sequência |
| **Flash Kill** | 5 abates de inimigos atordoados | Só elegível quando flashbang estiver funcionando |
| **Knife Streak** | 3 abates com corpo a corpo | Só elegível com identificação correta da fonte de dano |

**Não ativar meta que não tem implementação:** a cada onda o sorteio é feito sobre um conjunto de desafios habilitados; a capacidade aumenta sem invalidar dados antigos.

### 2.2 Fórmula de encerramento (proposta própria)

\`wave_reward = base_wave + performance_bonus + challenge_bonus\`, enquanto recompensas dos kills já pagos durante o combate **não são pagas novamente**.

- \`base_wave\`: pequeno crescimento por onda, sem multiplicador exponencial.
- \`performance_bonus\`: combinação limitada por precisão, headshot, rapidez e dano sofrido; cada item deve aparecer no relatório.
- \`challenge_bonus\`: créditos por eventos confirmados, pagos uma vez por conclusão, sem duplicar.
- Não reproduzir cegamente as fórmulas de GameFAQs do MW3 2011: valores são relatos comunitários, não documentação de código.
- Simular 15 ondas com bom e mau desempenho; garantir que o jogador não compre todos os itens após duas ondas.

## 3. Perks compráveis — um por vez no núcleo

**Referência:** no MW3 Survival, perks são fornecidos por compras de suporte/caixas de benefício.  
**Frontline:** no primeiro incremento, abrir uma categoria *Perks* na **estação física de suporte** existente; comprar via F de perto, sem teleporte de caixa, caso o transporte ainda não esteja pronto.

| Perk próprio do Frontline (nome provisório) | Efeito proposto | Limites |
| --- | --- | --- |
| **Reação Rápida** | Reduz tempo de levantar arma/entrar em ADS | Não acelera disparo acima do rate da arma |
| **Mira Firme** | Reduz dispersão ao atirar sem ADS e o deslocamento do sway | Não remove recuo por completo |
| **Recarga Ágil** | Reduz tempo de recarga em cerca de 20% | Ajustar som/animação à duração real |
| **Mobilidade** | Move-se um pouco mais rápido durante ADS | Não torna LMG igual a pistola |
| **Resistência** | Pequena melhora na recuperação entre combates | Não substitui colete, compra de cura ou Self Revive |

**Regra inicial:** **um único perk ativo**, compra de outro **substitui** o anterior; mostrar o perk atual e avisar claramente antes de cobrar. Os efeitos desaparecem ao terminar a sessão clássica. Não salvar uma vantagem permanente via XP/patente.

**Valores de venda:** PENDENTES de balanceamento; os preços históricos de $3.000–$5.000 não fazem sentido automaticamente na economia atual do Campo de Testes (rifle $350, esquadrão $420). Preço só aprovado depois de simular progressão.

## 4. "Última Chance" (Last Stand) e kit de autorreanimação

Implementar como estados separados para não conflitar com o revive do **treino** atual.

### 4.1 Estados

\`VIVO -> FERIDO_ULTIMA_CHANCE -> RECUPERADO\` ou \`MORTO\`.

No primeiro dano fatal de uma partida clássica (proposta):
- Consome uma chance disponível e entra no chão com **pistola de emergência**, câmera baixa e movimento muito limitado;
- Janela sugerida **10 s** de sangramento; matar um inimigo nessa janela levanta o jogador com **35 HP**, 1 s de proteção contra dano e sem restaurar colete automaticamente;
- Se o jogador não matar ninguém, o **Kit de Reanimação** previamente comprado pode ser consumido para levantar; sem kit, encerra a sessão;
- Um Kit não serve como compra repetida automaticamente no estado ferido, exigindo posse anterior;
- Não permitir usar repetidamente a mesma eliminação ou efeito de explosão para obter recuperações infinitas;
- O treino, que já oferece revive manual após morrer, mantém seu comportamento separado; pode simular Última Chance sem perda de progresso.

**Last Stand ≠ Perk em uso:** a queda com pistola é uma mecânica de sobrevivência; Self Revive/Kit de Reanimação é um consumível comprável na **estação de equipamentos**, não ocupa o único slot de perk.

### 4.2 Colisões e edge cases

- Durante o estado ferido, hitbox/câmera acompanham o chão; sem arma primária, sprint, salto ou granada.
- Se não houver munição de pistola, oferecer uma quantidade limitada de emergência; bloquear exploração de munição infinita.
- Mata o último inimigo ao estar ferido: primeiro resolver recuperação, depois encerrar a onda; não iniciar próximo combate morto.
- Fim da janela e última bala no mesmo frame: resolução determinística (definir prioridade de sinais).
- Dano direto enquanto ferido (se permitido) acelera sangramento, mas nunca aplica duas mortes ou dois gastos do item.
- Compra no shop durante morte/queda proibida; log de compra precisa impedir débito indevido.

## 5. Attachments obrigatórios por arma (compras na estação de armas)

**Requisito do usuário:** as armas são compradas **SEM attachments** e depois tunadas; no lançamento do núcleo **todas as cinco famílias** precisam ter pelo menos miras e escolha de acessório de cano, com aparência e efeito real.

### 5.1 Slots

- **Mira:** sem mira adicional (ferro original) ou Red Dot/Holográfica, uma ativa por vez.
- **Cano:** sem acessório ou Silenciador/Compensador, um ativo por vez.
- **Empunhadura** (fase seguinte do mesmo subsistema): se suportada por cada arma, grip reduz recuo com pequena penalidade de movimento/tempo de ADS.
- No núcleo, permitir **Red Dot + Silenciador simultaneamente**; não fazer attachment substituir a mira da outra categoria.
- Cada arma tem suas **próprias** escolhas e compras. Trocar de fuzil para SMG não transfere mira nem custo; remover ou substituir acessório não cobra duas vezes por erro de UI.
- Arma apanhada no chão entra como **versão básica** sem attachments, salvo se o drop indicar explicitamente e de maneira validada acessórios equipados.

### 5.2 Matriz funcional de compatibilidade

| Arma | Mira Red Dot | Silenciador | Alternativa adicional |
| --- | --- | --- | --- |
| Pistola | Sim | Sim | Mira holográfica compacta |
| SMG | Sim | Sim | Grip/compensador |
| Fuzil | Sim | Sim | Holográfica, grip |
| Escopeta | Sim | Sim (execução original do Frontline) | Choke ou mira compacta |
| LMG | Sim | Sim (modelo de cano adequado) | Grip/compensador |

**Fidelidade:** os guias do Survival MW3 2011 listam red dot, holo, ACOG, grip e underbarrel; **não confirmam silenciador na loja original**. Silenciador e disponibilidade em todas as classes são **adições autorais pedidas pelo usuário**.

### 5.3 Qualidade técnica obrigatória

- Óptica tem modelo/retícula física, não só texto de "Red Dot"; ADS precisa alinhar câmera e centro da mira com o raycast, inclusive após correr e agachar/deitar.
- Silenciador tem malha correta na boca do cano, sem atravessar arma/mão ou sumir na vista em primeira pessoa.
- Som de arma com silenciador deve usar **WAV próprio** (não reaproveitar beep ou som sintetizado legado). Se não houver arquivo gravado compatível, não ativar áudio defeituoso na build.
- Silenciador altera comportamento: menor volume e alcance de detecção dos inimigos; pequeno custo de dano/velocidade conforme balanceamento — não ser só cosmético.
- Grip reduz recoil apenas na classe compatível; atributos são recalculados a partir da arma base + attachments, nunca acumulando o bônus a cada troca.
- Compra no terminal exige saldo/arma/patente; pós-venda confirma visual, save apenas do estado da sessão.

## 6. Agachar e deitar de verdade (movimento/colisão)

\`STANDING ↔ CROUCHING ↔ PRONE\`; \`FERIDO\` e \`MORTO\` são estados distintos com regras próprias.

**Situação atual:** segurar \`C\` ou \`Ctrl\` apenas muda a velocidade do jogador para 3 m/s. A altura da câmera e do \`CollisionShape3D\` não acompanha; isso NÃO é agachamento completo. Deitar não existe.

| Posição | Controle padrão proposto | Deslocamento | Regras |
| --- | --- | --- | --- |
| Em pé | Inicial; levantar ao liberar agachar ou pressionar tecla de alternância | Velocidade normal | Sprint, salto e ADS normais |
| Agachado | C ou Ctrl; modo hold/toggle configurável | Lentamente | Câmera/colisor realmente baixam, recoil menor; sem sprint |
| Deitado | **Z** alterna (proposta de atalho) | Rastejar bem devagar | Câmera/colisor baixos; sem sprint/salto; giro da arma e recoil limitados |

**Cuidado importante em Godot 3D:** não apenas fazer \`scale.y\` do nó do jogador. Usar state machine + suavização da altura do \`CapsuleShape3D\` e \`CollisionShape3D.position\`, câmera e origem do tiro. Antes de levantar, **consulta física de teto/obstáculo**; impedir ficar preso dentro da geometria. Evitar a transição deitado→em pé se não houver espaço. Acessórios devem funcionar em cada postura.

**Interação com lojas/loot:** câmera baixa não pode permitir pegar itens do outro lado de paredes. \`F\` só funciona à distância regulamentada e com colisão/visão válida. A postura não deve aumentar alcance de compra.

## 7. Ordem de execução (Campo de Testes)

| Sprint candidata | Entrega única | Dependências | Testes obrigatórios |
| --- | --- | --- | --- |
| CT-01 | **Relatório por onda e timer 30 s** | Estatísticas básicas e saldo, settings | 2 ondas reais + transição 30s; migração de settings; painel não bloqueia loja |
| CT-02 | **Contadores de desempenho e desafios** | CT-01, eventos de dano/abate com ID único | Killstreak, Rampage, Quad Kill separados; headshot/escopeta; anti-duplicidade; simular 15 ondas de créditos |
| CT-03 | **Agachamento e prone físicos** | Estado de player e colisão | Teto, passagem estreita, tiro/ADS em todas as posturas, revive |
| CT-04 | **Attachments: mira + silenciador nas 5 armas** | Modelos e ADS aprovados | 5×2 acessórios, compra/troca/loots, recoil/dano, áudio, 720p |
| CT-05 | **Perks + loja de suporte** | Economia CT-02 | Uma vantagem ativa, troca, compras, reload/ADS sincronizados |
| CT-06 | **Última Chance e Kit de Reanimação** | CT-03, modos de morte/treino | 10s sangramento, matar para levantar, kit comprado, esgotar chance, final de onda |
| CT-07 | **Balanceamento e validação longa** | CT-01 a CT-06 | 15 ondas Windows reais, 5 armas, perícias, perks, posição, 12 NPCs, FPS/memória |

**Bloqueio atual:** v0.9.14 corrigiu estrutura do soldado Quaternius, mas a postura/rig **ainda precisa de aprovação visual real**. Não converter os NPCs restantes enquanto houver deformações. Features CT-01/02 podem ser planejadas ou codificadas sem ampliar mapas/ondas, mas sua release precisa preservar a correção visual.

## 8. Critérios de pronto desta frente

- Jogador consegue escolher e comprar red dot/silenciador em **todas as cinco armas**, e cada attachment tem custo/efeito/representação, sem piscar ou desalinhar.
- **C/Ctrl agacham de verdade e Z permite deitar**, com câmera/colisor/tiro corretos e segurança no teto.
- Vantagens compráveis **alteram performance** e não se acumulam indevidamente.
- Última Chance/Kit funcionam no treino/clássico sem mortes ou compras duplicadas.
- Onda termina sem travar, relatório mostra as métricas corretas, desafios pagos uma vez, e preparação de **30 s por padrão em novas instalações**.
- Nada foi declarado aprovado apenas por passar no CI: requer Windows jogável, 15 ondas e medição no hardware-alvo.
- Nenhum novo mapa/transporte/helipouso ou aumento de quantidade de ondas até passar nesse núcleo.

## 9. Fora de escopo desta frente

- Helicópteros, caminhões, desembarque, novos mapas, aumento de inimigos simultâneos ou aumento do limite de 55 por onda.
- Ragdoll pesado/física realista para todos os corpos sem medir custo.
- Gunsmith de 20+ peças, perks empilhados, prestígio, multiplayer e microtransações.
- Reproduzir diretamente o HUD, nomes visuais, modelos, áudios ou arquivos internos de Call of Duty.

**Estado geral em 11/11/2026:** requisitos aceitos como intenção do jogador, proposta técnica documentada, **nenhum dos CT-01 a CT-07 implementado nesta rodada de documentação**.
