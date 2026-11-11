# M0 — Campo de Testes: polimento antes de ampliar o Survival

**Direção atualizada pelo usuário em 11/11/2026.** O núcleo do Campo de Testes já chegou à onda 10 em sessão real Windows. Isto é evidência parcial de funcionamento, **não** teste de 15 ondas nem aprovação da arte.

## Decisão de prioridade

Até o Campo de Testes ficar convincente e estável, **não abrir novos mapas, não acrescentar mais faixas de ondas, não introduzir helicópteros/caminhões nem aumentar o número de inimigos especiais**. A prioridade imediata é sensação de FPS, personagens, feedback de acerto, morte e loot, testando um incremento por vez em GitHub Releases.

As decisões de lançamento 1.0 continuam propostas; este direcionamento atualiza a **ordem de execução** e não muda as regras essenciais (75s entre ondas, F nas lojas, sem crosshair estática, modo offline, asfalto).

## Feedback real mais recente

- O Campo de Testes foi jogado até a **onda 10**, e a progressão está funcionando segundo o relato.
- A corrida parece apenas uma caminhada acelerada.
- Falta um **hitmarker discreto sem som**, exibido SOMENTE quando o tiro acerta.
- Faltam efeitos de sangue quando o alvo é atingido.
- Cadáveres desaparecem imediatamente; devem permanecer no chão por um período e sumir para não pesar.
- Inimigos devem deixar armas e, ocasionalmente, munição; F pega o item sem substituir as compras das estações.
- O indicador vermelho de direção do tiro parece uma barra reta/quadrada; substituir por arco curvo e arredondado.
- Modelos de soldados continuam geométricos demais; arma está no centro do corpo, empunhadura ainda carece de realismo.
- Futuro: inimigos chegando de transportes terrestres, helicóptero e blindados mais fortes; **adiar até polimento do campo de testes**.

## Entrega v0.9.12 (polimento M0 + M1)

| Item | Implementação | Status |
|---|---|---|
| Sprint tático | Arma desce/inclina, sway mais forte, transição suavizada, mão de apoio afasta, tiro bloqueado durante corrida | **CONCLUÍDO (CÓDIGO + CI)** — validar sensação no Windows |
| Hitmarker | Quatro traços mínimos, branco no acerto e âmbar no headshot; duração 160 ms; sem mira permanente nem efeito sonoro | **CONCLUÍDO (CÓDIGO + CI)** — avaliar tamanho |
| Sangue nos impactos | Gotículas escuras discretas, temporárias e limitadas a 14 efeitos ativos | **CONCLUÍDO (CÓDIGO + CI)** — avaliar aparência real |
| Corpos após morte | Permanecem até 17 s, colisão desligada, limite de 12 corpos; desaparecimento automático | **CONCLUÍDO (CÓDIGO + CI)** — observar queda e chão |
| Armas/munição no chão | Arma separada do NPC; 32% de chance de caixa de munição; F para recolher; itens de 20 s e limite 18 | **CONCLUÍDO (CÓDIGO + CI)** — avaliar UX/colisão |
| Arcos de dano | Quatro indicadores curvos, somente quando atingido e temporários | **CONCLUÍDO (CÓDIGO + CI)** — avaliar geometria real |
| Silhueta humana | Coletes/ombros arredondados via cápsulas e rifle mais à frente dos braços | **PARCIAL** — ainda são personagens procedurais, não rig humanoide profissional |
| Entradas de caminhão/helicóptero | Ideia registrada, **não codificada** | **ADIADO por decisão do usuário** |
| Novos mapas e composição de ondas | Nenhuma expansão nesta sprint | **ADIADO por decisão do usuário** |

**Observação de QA:** o teste de Godot pode comprovar que o hitmarker aparece ao emitir um acerto, que os pickups são coletados e que o cadáver não some de imediato, mas **não consegue garantir qualidade de animação, imagem ou sensação de som no Windows**.

## Migração futura para personagens realmente humanoides

A substituição de uma boneca de primitivas por humanoides precisa de **modelo com rig/esqueleto e animações compatíveis**. Avaliar um pequeno protótipo isolado primeiro:

- [Quaternius — Universal Base Characters](https://quaternius.com/packs/universalbasecharacters.html): base humanoide CC0, com rigs.
- [Quaternius — Universal Animation Library](https://quaternius.itch.io/universal-animation-library): caminhada, sprint, combate, recarga e morte, CC0.
- Confirmar a licença exata do arquivo baixado e testar importação/retarget no **Godot 4.4.1**. Um projeto de IK que depende de Godot 4.6+ não deve ser copiado diretamente para a base atual.
- Ajustar roupa/equipamento militar próprio, escalas, hitboxes, LOD e grip das armas; avaliar FPS com 12 inimigos.
- Só substituir os NPCs antigos quando essa implementação renderizar bem e passar nos testes.

**Não baixamos nem incorporamos modelos externos na v0.9.12**; os modelos e sons atuais foram preservados. A arquitetura de IA, loja e ondas fica intacta.

## Condições para retomar expansão

Antes de produzir Complexo Industrial, helicópteros ou mais ondas:
1. Sprint e ADS aprovados no jogo real.
2. Soldados com arma nas mãos, sem cabeça solta, com animação de morte aceitável.
3. Acertos, sangue, corpos e coleta funcionando confortavelmente.
4. Início, duas lojas, reforços, ao menos 10 ondas e teste prolongado de 15 ondas sem regressões.
5. FPS medido com corpos/loot ativos dentro do orçamento de GPU e RAM.

Enquanto esses pontos não forem validados, os itens novos permanecem **PARCIAIS** para jogabilidade, mesmo que o CI passe.
