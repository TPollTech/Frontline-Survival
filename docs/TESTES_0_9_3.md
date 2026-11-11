# Frontline Survival v0.9.3 — Checklist de regressão

**Contexto:** screenshot do suporte com a cabeça destacada; armas anteriormente brancas, agora coloridas porém muito geométricas; som de recarga genérico e agudo. Próxima frente do ROADMAP: obstáculos/IA.

| ID | Verificação | Estado |
| --- | --- | --- |
| 093-01 | Arquivos gerados: 4 texturas PNG e 5 WAVs de recarga por classe | **CONCLUÍDO (CI)** após job verde |
| 093-02 | GLBs do armamento recompilados com novos detalhes | **CONCLUÍDO (CI)** após job verde |
| 093-03 | Cabeça/capacete/máscara no mesmo pivô e gola sobreposta ao torso | **PARCIAL**: estrutura implementada, confirmar visual |
| 093-04 | Armas usam textura de metal/polímero e continuam coloridas | **PARCIAL**: script e importação validados, confirmar no jogo |
| 093-05 | Recarregar cada uma das cinco armas reproduz seu WAV mecânico | **PARCIAL**: arquivos e seleção implementados, ouvir no jogo |
| 093-06 | Inimigos tentam contornar obstáculos ao perseguir | **PARCIAL**: sondas e desvio; faltam testes práticos com caixas/contêineres |
| 093-07 | Soldados bloqueados acionam recuperação após progresso insuficiente | **PARCIAL**: algoritmo integrado; avaliar em combate real |
| 093-08 | Aliados contornam obstáculos e continuam usando armas | **PARCIAL**: comportamento implementado; observação em jogo pendente |
| 093-09 | Spawns e duas ondas automatizadas, com dois aliados | **CONCLUÍDO (CI)** após job verde |
| 093-10 | 15 ondas completas, compras, morte, revive, FPS e sons confortáveis | **PENDENTE** |
| 093-11 | ZIP Windows com EXE/PCK em Releases, SHA-256 | **CONCLUÍDO (CI+RELEASES)** após publicação |

**Observação:** a Etapa 2 ainda NÃO está 100% concluída; o mapa futuro exigirá navegação de setores/escadas e testes específicos. Medidas de FPS da captura do usuário são pontuais, não benchmark.
