# Frontline Survival — Etapa 2: Inimigos, IA e progressão de ondas

**Estado:** documento de planejamento v1.0 (10/11/2026). Propostas a revisar; nenhuma mecânica foi implementada nesta execução.  
**Base:** protótipo 0.7, scripts enemy.gd, main.gd e ally.gd, ROADMAP.md, REGISTRO_DECISOES.md.  
**Dependência de implementação:** primeiro concluir a Etapa 0 e validar no Godot; alinhar visuais e feedback com a Etapa 1.  
**Hardware de referência:** Ryzen 5 7530U, gráficos integrados, 8 GB de RAM, Godot Compatibility.

> Objetivo: cada onda exige novas decisões táticas, graças à composição e ao equipamento dos soldados, não apenas a barras de vida maiores. O jogo permanece original, sem copiar assets ou personagens do MW3.

## 1. Regras estabelecidas — preservar

- Survival FPS solo e offline com ondas sucessivas e potencialmente infinitas.
- Finalizar uma onda NÃO encerra a partida; inicia preparação, depois a próxima começa automaticamente.
- Preparação padrão de 75 segundos, ajustável de 45 a 120; tecla N antecipa apenas durante preparação.
- Campo de Testes permanente, textura de asfalto preservada e três estações físicas de compra acionadas por F (não há loja rápida pelo B).
- Treinamento com reanimação opcional mantém progresso; modo clássico termina somente quando o jogador morre.
- Esquadrão e ataque aéreo comprados em estação, depois acionados pelas teclas 3 e 4.
- Evolução do armamento inimigo por faixas de ondas, com mudanças perceptíveis na experiência de combate.
- Documentar, revisar e só então codificar; medir desempenho no notebook antes de aumentar carga gráfica/IA.

## 2. Diagnóstico da versão 0.7 — observado no código, NÃO testado no Godot

| Área | Implementação presente | Limitação a resolver |
| --- | --- | --- |
| Tipos | Soldado comum, corredor e pesado | Papéis táticos e silhuetas pouco distintos |
| Kits | Escopeta, SMG, fuzil e LMG | Diferenças atuais sobretudo numéricas/visuais |
| Onda | Total = mínimo de (5 + 2 × número da onda) e 55 | Quantidade aumenta, mas composição precisa ser melhor dirigida |
| Ativos | Teto de 12 NPCs vivos simultâneos | Não aumentar antes de medir CPU, RAM e FPS |
| Spawn | Oito pontos predefinidos nas bordas do campo | Falta distância/visibilidade/ocupação contextual |
| Movimento | Perseguição, strafe e desvio reativo a colisões | Pode travar em obstáculos; falta navegação por mapa |
| Tiro inimigo | Aplica dano se estiver em alcance e com linha de visão, respeitando um intervalo | Falta reação legível, precisão por classe e disparos em rajada |
| Pesados | Ondas múltiplas de cinco a partir da 10 e chance rara depois | Aviso, limite e contrajogo precisam ser definidos |
| Contagem | Avança quando sem spawns pendentes e sem inimigos vivos | Precisa ser robusta a remoções, mortes simultâneas e bugs |
| Recompensa | Concedida ao derrotar NPC; bônus e cura ao concluir onda | Balancear depois em conjunto com Etapa 3 |

**Não confundir descrição do código com teste aprovado.** Os dados de desempenho e jogabilidade no hardware-alvo continuam pendentes.

## 3. Arquétipos propostos de inimigos

| Papel | Armas | Identidade visual e sonora | Comportamento predominante | Resposta do jogador |
| --- | --- | --- | --- | --- |
| Escopeteiro | Escopeta | Colete leve, cano curto e disparo espaçado | Busca curta distância, aproxima por cobertura | Recuar e manter distância |
| Operador SMG | SMG | Silhueta compacta e rajadas rápidas | Avanço ágil, flancos curtos | Proteger os lados |
| Fuzileiro | Fuzil | Equipamento médio, mira visível | Pressão de média distância, pequenas pausas | Romper linha de visão |
| Corredor | Escopeta/SMG | Poucas proteções, corrida nítida | Fechar distância e expulsar de posição fixa | Priorizar alvo próximo |
| Metralhador pesado | LMG | Armadura grossa, passos lentos, fogo sustentado | Pressão frontal, mobilidade reduzida | Cobertura e foco de dano |
| Especial tático | A definir | Silhueta única e aviso anterior | Uma habilidade simples, se aprovada | Contrajogo explícito |

**Regra de escopo:** os três tipos existentes permanecem como base. Um arquétipo novo só entra depois de validar navegação, combate e desempenho. Classes não podem se diferenciar apenas por números de vida.

## 4. Progressão proposta de composição

A transição armamentista em faixas é uma decisão já estabelecida; percentuais e ondas especiais abaixo são hipóteses de balanceamento, NÃO aprovações.

| Ondas | Composição inicial sugerida | Novidade e intenção |
| --- | --- | --- |
| 1–3 | 100% escopeta, soldados básicos | Ensinar mira, compras e posicionamento |
| 4–6 | Predomínio SMG (70–100%); restante escopeta a calibrar | Introduzir ameaça de maior cadência |
| 7–9 | SMG/escopeta e alguns corredores, até ~20% | Pressão em flancos e aproximação |
| 10 | Mistura + um pesado anunciado | Primeira onda marco; contrajogo legível |
| 11–14 | Fuzis predominantes (~70–85%), SMGs ocasionais | Combate em média distância |
| 15 | Fuzis + um pesado anunciado | Segundo pico, sem excesso de ativos |
| 16–19 | Fuzis e LMGs (alvo inicial 65/35) | Supressão e movimento entre coberturas |
| 20 | Fuzis/LMGs + pesado | Onda marco; nunca um encerramento |
| 21+ | Rotação de composições entre kits existentes | Diversidade antes de aumentar vida ou dano |

**Quantidade de inimigos:** manter até prova em contrário a fórmula da 0.7 (onda 1 = 7; 4 = 13; 10 = 25; 15 = 35; 20 = 45; teto 55) e no máximo 12 simultâneos. Entram gradualmente, não todos de uma vez. Ajustes futuros devem considerar a duração real de cada onda e o custo de munição.

**Diretriz de progressão:** não aumentar quantidade, vida, dano e precisão simultaneamente. Modificar um ou dois eixos por faixa e documentar impacto no jogador.

## 5. Diretor de ondas: estados e invariantes propostos

Fluxo pretendido:

    MENU -> PREPARAÇÃO INICIAL (25 s no campo atual)
         -> ANÚNCIO -> COMBATE -> CONCLUÍDA
         -> PREPARAÇÃO (75 s padrão) -> ANÚNCIO -> COMBATE -> ...
                 Durante combate: morte treino -> reanimação -> combate
                 Durante combate: morte clássica -> tela de fim de jogo

**Invariantes obrigatórias:**

1. O número da onda só incrementa uma vez por início autorizado.
2. O total pendente de spawn nunca fica negativo.
3. O contador de vivos equivale a inimigos vivos rastreados, não apenas a um número presumido.
4. Derrota do mesmo NPC causa no máximo uma recompensa e um decremento.
5. Conclusão só ocorre com fila de spawn vazia E zero inimigos vivos; ela só é processada uma vez.
6. Em pausa, jogo não continua progredindo, gerando inimigos ou consumindo duração de suporte.
7. Durante preparação, lojas, armas e suporte continuam acessíveis, sem reset do inventário.
8. N durante combate não pula ondas. N durante preparação antecipa uma única vez.
9. Reinício do Campo de Testes e reanimação não devem deixar NPCs órfãos nem contadores fantasmas.

### Spawn em grupos

**Proposta:** fila com pequenas entradas de 2–4 inimigos, espaçadas e respeitando o teto de ativos. Não instanciar uma multidão no mesmo quadro. Comparar a distribuição com o spawn individual da versão atual antes de alterar o código.

## 6. Regras para spawn justo

Para cada mapa, propor pontos com ID, setor, navegação válida, saída e proximidade das lojas. O seletor deverá:

1. Rejeitar posições dentro de paredes/objetos e pontos ocupados por outros soldados ou aliados.
2. Rejeitar posição muito próxima do jogador; **raio inicial sugerido: 10 m**, a validar no Campo de Testes.
3. Preferir pontos fora da linha de visão direta quando existirem alternativas; evitar inimigo materializando na frente da câmera.
4. Evitar entrar no raio imediato de uma estação, especialmente durante preparação.
5. Se não houver spawn válido, aguardar pequeno intervalo e tentar outro; emitir aviso interno de QA após repetidas falhas, sem criar loop infinito.
6. Não permitir spawn de inimigo sem caminho possível até a zona de combate.
7. Nos mapas multissetoriais futuros, permitir diferentes grupos de spawn por setor, mas com a mesma máquina de estados de ondas.

**Teste proposto:** pelo menos 100 escolhas de spawn em várias posições do jogador, com checagem de colisão, ocupação e distância. Esses testes ainda não foram executados.

## 7. IA leve e confiável para a GPU integrada

### 7A — Estados básicos (prioridade)

    ENTRAR -> AVANÇAR -> PROCURAR VISÃO -> ATACAR
                  |-> DESVIAR -> RETOMAR AVANÇO
         ATACAR -> REPOSICIONAR -> ATACAR
         QUALQUER ESTADO -> RECEBER DANO -> CONTINUAR / MORRER

- **Alcance por arma:** escopeteiro aproxima; SMG tenta curta/média; fuzileiro mantém média; pesado pressiona devagar.
- **Linha de visão:** dano jamais atravessa contêiner ou parede. Inimigo perde contato quando o jogador some da vista.
- **Última posição vista:** por intervalo curto, o inimigo pode investigar a área sem saber instantaneamente onde o jogador está.
- **Tempo de reação:** antes do primeiro disparo após encontrar o jogador, gesto/arma apontada com pequena janela de resposta; número concreto depende de testes.
- **Precisão por classe:** rajadas e chance de erro/espalhamento coerentes com distância. Não usar dano instantâneo infalível ao entrar no alcance.
- **Stagger:** reação de impacto não deve permitir travar permanentemente um pesado ou fuzileiro.

### 7B — Navegação e anti-travamento

- Avaliar NavigationAgent3D e regiões de navegação por mapa; usar solução simples inicialmente no Campo de Testes.
- Detectar falta de avanço pela distância percorrida ao longo do tempo, não só por colisões.
- Recuperar recalculando destino/rota, tentando waypoint alternativo ou voltando a uma posição conhecida válida.
- Não teletransportar NPC diante da câmera como solução de dificuldade.
- Escalonar recálculo de rotas entre NPCs, para evitar picos de CPU quando 12 estiverem ativos.
- NPC preso deve gerar log de teste e ter caminho de recuperação; não pode bloquear eternamente o fim da onda.

### 7C — Trabalho de grupo (depois)

Definir pequenas equipes com papéis simples (aproximação, cobertura, flanco curto). Nenhuma IA de aprendizado é necessária. Limitar quantidade de soldados tomando exatamente o mesmo caminho, mantendo oportunidades de defesa e fuga para o jogador.

## 8. Justiça e leitura do combate

- **Silhueta:** jogador reconhece a ameaça pelo armamento, equipamento, postura e som, sem depender só de cores.
- **Dano recebido:** indicar direção de ameaça sem obscurecer a tela; coordenação com Etapa 5 (HUD).
- **Primeira ameaça:** inimigo não pode surgir e causar dano no mesmo instante sem aviso.
- **Dano por arma:** escopeta de alto impacto e curto alcance; SMG rajadas e menor alcance; fuzil controle em média distância; LMG supressão lenta e visível.
- **Pesados:** anunciar chegada, movimento lento e vulnerabilidade clara; sem invencibilidade ou poder de matar sem tempo de reação.
- **Aliados:** distinguir por silhueta/marcação, não prejudicar o contador nem duplicar recompensas.
- **Morte de NPC:** animação e remoção não podem atrasar o reconhecimento de fim de onda.

## 9. Performance e orçamento

**Limite inicial:** até 12 inimigos ativos, além de suporte já existente. Este valor é provisório, só pode subir após benchmark no notebook real.

- Usar geometria enxuta, níveis de detalhe e quantidade controlada de materiais em NPCs.
- Reduzir custo de animação de NPCs distantes quando seguro, mantendo estado lógico.
- Reusar efeitos, limitar vozes de áudio e partículas; evitar iluminação dinâmica intensa a cada tiro.
- Processos de percepção/navegação podem atualizar por intervalos distribuídos, não tudo por frame.
- Medir FPS, RAM e quantidade de NPCs nas ondas 1, 5, 10, 15, além de cenário com torretas e aliados. Metas de 30 FPS em 720p e desejo de 60 FPS não são resultados comprovados.

## 10. Entregas de implementação futuras — NÃO executar neste ciclo

| Marco | Dependência | Escopo | Aceite |
| --- | --- | --- | --- |
| 2A — Diretor robusto | Etapa 0 validada | Máquina de estados, fila e contagem segura | 15 ondas sem game over indevido nem duplo spawn |
| 2B — Spawn contextual | 2A | Validação de ocupação, distância e saída | 100 spawns de teste sem nascer em colisões |
| 2C — IA básica confiável | 2B | Visão, objetivos, recuperação e reposicionamento | Inimigos não ficam presos sistematicamente |
| 2D — Classes e armamento | 2C + Etapa 1 | Silhuetas, kits, áudio e comportamentos distintos | Diferenças claras nas ondas 1/4/7/11/16 |
| 2E — Ondas marco | 2D e Etapa 3 parcial | Pesados anunciados e curva ajustada | Ondas 10/15/20 difíceis, mas vencíveis |
| 2F — Regressão longa | 2A–2E | 20+ ondas, reforços, mortes e compras | Nenhum P0; FPS/ram documentados |

## 11. Matriz de testes de aceitação

| ID | Teste | Falha bloqueante |
| --- | --- | --- |
| E2-01 | Onda 1 termina e prepara onda 2 | Fim de jogo ao concluir onda |
| E2-02 | N funciona só na preparação | Pula ondas durante combate |
| E2-03 | Ondas 1–15 e posteriormente 20+ | Contadores travados/reset espontâneo |
| E2-04 | Spawn perto de paredes, lojas e jogador | NPC dentro de objeto/jogador |
| E2-05 | 100 spawns com posições variadas | Ponto inválido recorrente |
| E2-06 | Linha de visão bloqueada por contêiner | Dano atravessa obstáculo |
| E2-07 | Perseguir player atrás de obstáculos | NPC preso e onda interminável |
| E2-08 | Ondas 1, 4, 7, 10, 11, 15, 16, 20 | Mesmos kits/táticas em todas |
| E2-09 | Múltiplos tiros letais simultâneos | Recompensa ou contagem dupla |
| E2-10 | Morte em treino e em clássico | Progresso perdido indevidamente |
| E2-11 | Compras F + aliados 3 + ataque 4 | Onda ou câmera quebra ao usar suporte |
| E2-12 | 12 inimigos e suporte em 720p | Degradação contínua de FPS/RAM |

**Evidência mínima para cada execução real:** versão/commit, build do Godot, cenário e onda, configuração gráfica, passos, resultado, erro/captura se houver e FPS observado. Nenhum teste desta tabela está marcado como concluído.

## 12. Critérios de encerramento da Etapa 2

- [ ] Etapa 0 concluída com partida real até onda 15 sem defeitos P0. — **PENDENTE**: Etapa 0 ainda requer 15 ondas reais.
- [ ] Contadores, fila e eventos de morte consistentes durante 20+ ondas. — **PENDENTE**: faltam 20+ ondas completas em jogo real.
- [ ] Inimigos não aparecem dentro de paredes ou jogador. — **PARCIAL**: 100 amostras de spawn em CI; jogo real ainda precisa validação.
- [ ] Perseguição, reação, linha de visão e tiro respeitam colisões. — **PARCIAL**: IA básica com LOS/colisão; IA militar completa pendente.
- [x] Kits variam de forma clara e as ondas marco são anunciadas. — **CONCLUÍDO (CÓDIGO/CI)**: kits e marcos configurados e simulados em CI.
- [ ] Nenhum NPC preso permanentemente impede a conclusão de onda. — **PARCIAL**: sondas anti-trava; faltam testes longos de NPCs presos.
- [x] Reanimação, modos de morte, compras e reforços preservados. — **CONCLUÍDO (CÓDIGO/CI)**: reanimação, compras e suporte preservados no CI.
- [ ] Custo medido no Ryzen 5 7530U/8 GB, em 720p, comparado à Etapa 0. — **PENDENTE**: consumo e FPS reais do Ryzen 5 7530U não medidos.

## 13. Decisões pendentes de aprovação

| Referência | Proposta | Situação |
| --- | --- | --- |
| E2-P01 | Manter fórmula de quantidade da 0.7 até testes | Pendente |
| E2-P02 | Manter teto de 12 ativos até benchmark | Pendente |
| E2-P03 | Composição da tabela de faixas | Pendente |
| E2-P04 | Pesado anunciado nas ondas 10/15/20 | Pendente |
| E2-P05 | Navegação por regiões nos mapas multissetoriais | Pendente |
| E2-P06 | Cobertura simples antes de IA de grupos | Pendente |
| E2-P07 | Nova classe especial tática | Fora do núcleo inicial; avaliar depois |
| E2-P08 | Tempo mínimo de reação ao primeiro tiro | Depende de playtest |

**Fora de escopo agora:** novos mapas implementados, helicópteros pilotáveis, destruição física extensa, multiplayer, chefes não aprovados, IA de aprendizagem, visual de alta fidelidade que prejudique hardware-alvo.

---

**Próxima lacuna recomendada no planejamento:** Etapa 3 — economia, estações e suporte tático, usando a tabela de ondas como referência. **Nenhum script, asset ou cena foi alterado nesta rodada.**

---

## Auditoria de progresso — 12/11/2026

Checklist desta etapa sincronizada com o CI da v0.9.17: **2 critérios concluídos no código/CI, 3 parciais e 3 pendentes**. O diretor de ondas já funciona, simula 50 composições e faz duas transições no CI; **não prova 20 ondas reais, IA militar completa ou FPS do hardware-alvo**. [Auditoria central](AUDITORIA_CHECKLISTS_2026_11_12.md).
