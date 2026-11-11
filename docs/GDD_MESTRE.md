# Frontline Survival — GDD mestre (pré-produção)

**Versão documental:** 1.0 — 11/11/2026. **Estado: GDD PRONTO PARA REVISÃO**, não aprovado para implementação. Documento de síntese; especificações detalhadas continuam nas Etapas 0–6. Nenhum teste ou implementação é comprovado por este GDD.

## 1. Visão e limites do jogo base
FPS 3D **solo offline** em Godot 4, renderizador Compatibility, com identidade própria. Inspiração no ritmo de Survival militar, sem copiar marcas, mapas, personagens, modelos ou áudio. Hardware de referência: **Ryzen 5 7530U, Radeon integrada, 8 GB RAM**.

**Início:** menu → seleção de modo e, quando implementado, mapa → partida. **Meio:** ondas sem limite final, combate, créditos, três estações físicas e preparação. **Fim de uma partida:** morte no modo clássico → resultado/recorde local → reiniciar ou menu; **não** há última onda ou campanha. Treino admite reanimação opcional com preservação de estado. O **Campo de Testes** e seu asfalto permanecem como laboratório; **um** mapa definitivo multissetorial (Complexo Industrial) é **proposta P-021**, não decisão aprovada.

## 2. Contrato de jogabilidade — estabelecido
- Matar o último inimigo inicia **preparação**, nunca game over; próxima onda começa automaticamente. Intervalo padrão **75 s**, configurável 45–120 s; **N** antecipa apenas durante preparação.
- **F** interage nas três estações próximas (armas, equipamentos, suporte); **B não abre loja global**. Suporte é comprado antes de ser acionado.
- Controles de referência: mouse esquerdo atira; direito ADS; **R** recarrega; **1/2** armas; **E** corpo a corpo; **G** granada; **3** esquadrão comprado; **4** ataque aéreo comprado. Validar foco de input em loja/pausa.
- HUD **discreto**: vida, colete, munição, créditos, onda, restantes e avisos contextuais. **Sem crosshair 2D padrão** (D-016); ADS usa alinhamento físico da arma. Som configurável e sem clipping.
- Campo de Testes com reanimação opcional; clássico encerra por morte. Sem online, coop, campanha ou microtransações no jogo base.

## 3. Especificações em proposta (não aprovadas)
| Sistema | Desenho proposto | Fonte / decisão pendente |
| --- | --- | --- |
| FPS e armas | Cinco famílias (pistola, SMG, fuzil, escopeta, LMG); recuo, dispersão, rig leve, efeitos contidos, modelos originais | [Etapa 1](ETAPA_1_FPS_ARMAS.md), P-003–P-006 |
| IA e ondas | Papéis diferenciados, kits por faixa de onda, navegação anti-trava, spawn contextual; teto inicial de 12 NPCs até benchmark | [Etapa 2](ETAPA_2_INIMIGOS_ONDAS.md), P-009–P-012 |
| Economia | Recompensa por abate/onda, escolhas entre arma, sobrevivência e suporte; compra atômica, sem débito em falha; capital do clássico a testar | [Etapa 3](ETAPA_3_ECONOMIA_SUPORTE.md), P-013–P-018 |
| Reforços | Torreta com posicionamento válido, esquadrão temporário, ataque aéreo com aviso e consumo só em ação válida | [Etapa 3](ETAPA_3_ECONOMIA_SUPORTE.md), E3-P04–P06 |
| Mapa definitivo | Complexo Industrial com cinco setores, rotas alternativas, lojas acessíveis em 75 s, duas alturas no máximo; cenas independentes | [Etapa 4](ETAPA_4_MAPAS_ARQUITETURA.md), P-019–P-022 |
| Interface/áudio | Estados de menu, escala HUD, buses de volume, acessibilidade, recordes locais separados por modo/mapa | [Etapa 5](ETAPA_5_HUD_AUDIO_ACESSIBILIDADE.md), P-023–P-025 |
| Desempenho/QA | 720p baixo: piso proposto de 30 FPS, 60 desejáveis; três medições; 15 ondas, 30 min, Windows real e gates de release | [Etapa 6](ETAPA_6_DESEMPENHO_TESTES_DISTRIBUICAO.md), P-026–P-029 |

**Valores numéricos do protótipo não são balanceamento aprovado:** treino $1.200, preços e recompensas, fórmula de quantidade de inimigos e duração de suportes devem ser aferidos em sessão real. Não alterar por inferência.

## 4. Dependências e implantação futura — sem execução autorizada
1. **0:** baseline Godot/Windows, regressão P0, 15 ondas e métricas; corrigir defeitos bloqueantes.
2. **1 + 2:** vertical slice de arma/ADS e inimigo/onda, mantendo transições; testar qualidade visual e custo de IA.
3. **3:** transações, munição, economia e suporte; medir 10–20 ondas e evitar softlock.
4. **4:** blockout do Complexo Industrial, navegação, spawns, lojas e MapLoader; manter Campo de Testes.
5. **5:** UX/HUD/áudio, menus e estatísticas; não reintroduzir crosshair.
6. **6:** profiling e otimização orientados por medição; QA Windows, empacotamento e release apenas após gates.

Cada incremento futuro: aprovação explícita → branch de implementação → alteração isolada → CI → execução real no notebook → evidência de QA → revisão/merge. CI verde **não** substitui inspeção visual, FPS medido nem sessão de 15 ondas.

## 5. Auditoria de coerência — conflitos e correções documentais pendentes
| ID | Divergência | Interpretação prevalente / ação antes de implementar |
| --- | --- | --- |
| C-01 | [Etapa 5](ETAPA_5_HUD_AUDIO_ACESSIBILIDADE.md) fala em retícula/hit marker; D-016 e Etapa 6 exigem retirar crosshair | **D-016 prevalece:** não usar retícula 2D fixa; revisar feedback de acerto para não recriar crosshair sem aprovação. |
| C-02 | [Plano histórico de mapas](PLANO_MAPAS.md) cita depósito de combustível e área externa; Etapa 4 propõe oficina e perímetro | **Etapa 4 é proposta mais recente**, mas nomes/layout precisam de aprovação; não fundir setores por suposição. |
| C-03 | Etapa 2 sugere inimigos especiais e ondas marco; Etapa 6 impõe limite de hardware | Nenhuma nova classe/teto acima de 12 antes de benchmark e validação da IA. |
| C-04 | Treino possui $1.200 e clássico não tem saldo final aprovado | Não usar capital de treino como padrão do clássico; balancear antes de fixar preços. |
| C-05 | Roadmap mistura histórico de protótipos 0.7–0.9.2 e tarefas futuras | **Implementado/CI, testado no Windows e aprovado** são estados diferentes; verificar evidência por versão. |
| C-06 | Jogo de ondas infinitas versus exigência de início/meio/fim | O fim é **da sessão por morte**, não fim da progressão de ondas. |

## 6. Checklist de consistência para revisão do GDD
- [x] Visão, público/hardware, modo offline e identidade original definidos.
- [x] Loop, preparação 75 s, estações F, controles e HUD preservados.
- [x] Treino versus clássico e fim da sessão diferenciados.
- [x] Armas, IA, economia, reforços, mapas, UX e desempenho têm documento de origem.
- [x] Propostas e decisões estabelecidas separadas; nenhuma proposta promovida automaticamente.
- [x] Ordem de dependências, testes, gates e limites de expansão registrados.
- [x] Conflitos transversais identificados sem ocultá-los.
- [ ] Aprovar/rejeitar propostas P-001–P-029 e decisões específicas E2/E3/M4/E5/E6.
- [ ] Resolver C-01 e C-02 nos documentos-fonte após decisão, antes de implementar.
- [ ] Executar testes reais, benchmark e regressão; **não fazem parte da conclusão documental**.

**GDD PRONTO PARA REVISÃO** significa que a síntese documental das Etapas 0–6 está disponível para análise; **não significa GDD aprovado, código concluído, jogo testado ou release estável**. Próximas execuções: verificar novas decisões e mudanças remotas; não criar documentos ou commits repetidos sem lacuna real.

## 7. Expansões (fora do jogo base)
Novos mapas urbanos/montanha/porto, coop, campanha, clima dinâmico, chefes adicionais, veículos, perks extensos e ranking online. Exigem planejamento e aprovação próprios, sem comprometer o núcleo solo.
