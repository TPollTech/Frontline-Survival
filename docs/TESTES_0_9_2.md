# Frontline Survival v0.9.2 — Matriz de testes e regressão

**Origem:** pedido de auditoria da v0.9.1 e implementação da próxima parte do ROADMAP.  
**Escopo:** spawn contextual (Etapa 2B), contagem e transição de ondas (2A), materiais do jogador e animação de aliados (regressão v0.9.1).  
**Nota:** CI executa em ambiente Godot Linux headless; a release é para Windows e não equivale a teste de 15 ondas no notebook.

| ID | Cenário | Evidência técnica | Situação |
| --- | --- | --- | --- |
| 092-01 | 100 escolhas de spawn no Campo de Testes | `tests/runtime_wave_qa.gd` testa distância do jogador e das lojas | **CONCLUÍDO (CI)** |
| 092-02 | Jogador simulado junto de cada entrada do mapa | Teste de oito posições críticas e exclusão de distância | **CONCLUÍDO (CI)** |
| 092-03 | Todos os pontos próximos de uma loja / jogador | Teste de situação sem escolha válida, sem criar NPC | **CONCLUÍDO (CI)** |
| 092-04 | Cena real + duas ondas completas | Instancia NPCs e contabiliza abates, fila, vivos e preparação | **CONCLUÍDO (CI)** |
| 092-05 | Paleta importada da arma inicial | Runtime testa material que habilita cores COLOR_0 | **CONCLUÍDO (CI)**, visual ainda pendente |
| 092-06 | Dois soldados aliados | Instancia equipe e processa 12 quadros de animação | **CONCLUÍDO (CI)**, pose visual ainda pendente |
| 092-07 | GitHub Release Windows | ZIP, EXE, PCK e SHA256 publicados após CI verde | **A confirmar na release v0.9.2** |
| 092-08 | Jogar 15 ondas com compras e reforços | Sessão completa com queda de FPS e RAM | **PENDENTE** |
| 092-09 | Spawn justo durante combate real | Jogar perto das bordas e estações com 12 inimigos ativos | **PENDENTE** |
| 092-10 | Ausência de regressões da 0.9.1 | Cores das cinco armas, mira sem crosshair, aliados e sons | **PENDENTE** |

**Regras de interpretação:** `CONCLUÍDO (CI)` significa checagem reproduzível aprovada no runner; `PARCIAL` significa código implementado sem homologação de jogabilidade; `PENDENTE` não pode ser marcado como aprovado automaticamente. Defeitos observados no Windows entram como novos itens com captura/etapa para correção.

[ROADMAP](../ROADMAP.md) · [Documentação da Etapa 2](ETAPA_2_INIMIGOS_ONDAS.md) · [Releases](https://github.com/TPollTech/Frontline-Survival/releases)
