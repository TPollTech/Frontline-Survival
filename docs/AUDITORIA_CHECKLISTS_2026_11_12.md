# Auditoria dos checklists — Frontline Survival

**Data:** 12/11/2026 · **Referência:** branch `main`, release `v0.9.17` · **Objetivo:** sincronizar o ROADMAP e os documentos ETAPA_0–ETAPA_6 com o que realmente existe no código e foi verificado.

## Convenção de status (não confundir implementação com aprovação do jogo)

- `[x] CONCLUÍDO (CÓDIGO/CI)`: requisito delimitado e implementado, com evidência no código, teste automatizado ou release. **Não significa que a etapa completa está concluída.**
- `[ ] PARCIAL`: há código, UI ou especificação funcionando em parte, mas falta um subrequisito ou validação manual/visual.
- `[ ] PENDENTE`: não foi implementado, ainda não foi medido ou falta evidência necessária.
- `CONCLUÍDO (JOGO)`: somente depois de teste reproduzível de aceitação no Windows, especialmente em visual/áudio, 15 ondas e hardware-alvo.

## 1. Resultado da auditoria

| Seção | Concluídos | Parciais | Pendentes | Status global |
| --- | ---: | ---: | ---: | --- |
| ROADMAP — implementações Etapas 0–6 | 13 | 20 | 11 | **PARCIAL** |
| ROADMAP — backlog de expansões | 0 | 0 | 6 | **PENDENTE** |
| Etapa 0 — checklist de aceite | 4 | 2 | 3 | **PARCIAL** |
| Etapa 1 — checklist de aceite | 2 | 4 | 4 | **PARCIAL** |
| Etapa 2 — checklist de aceite | 2 | 3 | 3 | **PARCIAL** |
| Etapa 3 — matriz de 18 testes | 0 | 11 | 7 | **PARCIAL** |
| Etapa 4 — matriz de 18 testes | 0 | 8 | 10 | **PARCIAL / MAPA NÃO INICIADO** |
| Etapa 5 — matriz de 18 testes | 3 | 11 | 4 | **PARCIAL** |
| Etapa 6 — matriz de 18 testes | 1 | 12 | 5 | **PARCIAL** |

**Como ler:** as matrizes de teste das Etapas 3–6 não são idênticas às listas de implementação. Documentos dessas etapas ganharam uma seção separada com `[x]` nas entregas de código já realizadas.

## 2. O que comprovadamente funciona no código/CI

- Godot 4.4.1, parser e startup headless; scripts, ativos e GLBs importados no pipeline.
- **595 asserções de integração** (duas transições de onda e 100 amostras de spawn) e **2.416 de composição** (50 variações; 2.150 inimigos planejados, 16 pesados de ondas-marco).
- **23 asserções de mecânicas Survival:** desafios, precisão, Last Stand, perks e acessórios; lojas físicas, suporte e posturas também aparecem na integração.
- Cinco classes de armas com características distintas, attachment por arma, mira e disparo, recarga em WAV, feedback de hit/headshot.
- Três lojas físicas, loop de ondas contínuo, 30 segundos padrão de preparação e antecipação por `N`.
- Menu principal, pausa e quatro categorias de configurações persistentes; HUD reduzido na 0.9.17.
- Limite de NPCs, corpos, loot e efeitos temporários, para evitar crescimento descontrolado de instâncias.
- ZIP Windows `FrontlineSurvival-v0.9.17-Windows.zip`, EXE/PCK e arquivo SHA-256 publicados no GitHub Releases.

## 3. Itens que NÃO devem ser marcados concluídos sem mais trabalho

- **Etapa 0:** não há 15 ondas reais documentadas; falta comprovar estabilidade prolongada. Usuário relatou chegar à onda 10 em teste anterior.
- **Etapa 1:** modelos de mãos/rig e empunhadura ainda são rudimentares; a mira Red Dot da v0.9.17 precisa aprovação visual, e clipping/áudio não foram homologados.
- **Etapa 2:** IA usa coberturas/recarga/posturas básicas, mas não constitui uma IA militar completa; rotas, flanqueamento e 20 ondas continuam pendentes.
- **Etapa 3:** valores econômicos carecem de balanceamento; a rotina atual pode cobrar cura com vida cheia e munição cheia, não valida completamente a posição da torreta nem o alvo do ataque aéreo. O contador do ataque aéreo pode contabilizar acertos como eliminações.
- **Etapa 4:** só existe o Campo de Testes; cinco setores, Complexo Industrial, seletor e recordes por mapa estão pendentes.
- **Etapa 5:** menus/alertas e HUD existem, mas faltam testes em 720p/900p/1080p, escala própria do HUD, revisão de som e aprovação do layout.
- **Etapa 6:** não há benchmark reproduzível de CPU/GPU/RAM/FPS no Ryzen 5 7530U (8 GB), nem sessão homologada de 15 ondas/30 minutos.

## 4. Portões de qualidade

| Gate | Estado | Evidência |
| --- | --- | --- |
| A — Godot, importação, testes automatizados | **CONCLUÍDO (CI)** | [Workflow v0.9.17](https://github.com/TPollTech/Frontline-Survival/actions/runs/43171938905) |
| B — visual/áudio/jogabilidade no Windows | **PARCIAL** | Capturas e defeitos relatados; última correção 0.9.17 requer novo teste |
| C — 15 ondas, 30 minutos e FPS/RAM | **PENDENTE** | Sem relatório completo no notebook |
| D — ZIP Windows com versão imutável e SHA-256 | **CONCLUÍDO (RELEASE)** | [GitHub Releases v0.9.17](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.17) |

## 5. Documentos sincronizados

- [ROADMAP principal](../ROADMAP.md) — checklist original marcado linha a linha com status.
- [Etapa 0](ETAPA_0_ESTABILIZACAO.md), [Etapa 1](ETAPA_1_FPS_ARMAS.md) e [Etapa 2](ETAPA_2_INIMIGOS_ONDAS.md) — checklists de aceitação com caixas marcadas onde há CI.
- [Etapa 3](ETAPA_3_ECONOMIA_SUPORTE.md), [Etapa 4](ETAPA_4_MAPAS_ARQUITETURA.md), [Etapa 5](ETAPA_5_HUD_AUDIO_ACESSIBILIDADE.md) e [Etapa 6](ETAPA_6_DESEMPENHO_TESTES_DISTRIBUICAO.md) — matriz de casos com coluna de status + checklist de implementação.
- [QA 0.9.17](QA_V0_9_17.md) — exportação/releases e verificações de integração atualizadas; inspeção visual continua pendente.

**Regra permanente:** a cada sprint, atualizar as caixas **na seção de origem** e o registro de evidência; não acumular apenas uma nova tabela no final do ROADMAP. Evitar mudar um item para `[x]` quando apenas uma parte do critério está implementada.
