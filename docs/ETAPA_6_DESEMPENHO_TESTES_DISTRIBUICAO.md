# Frontline Survival — Etapa 6: desempenho, QA e distribuição Windows

**Estado:** especificação documental v1.0, 10/11/2026. **PROPOSTAS NÃO APROVADAS.** Nenhum benchmark ou teste de gameplay é comprovado por este documento.
**Referências:** [ROADMAP](../ROADMAP.md), [decisões](REGISTRO_DECISOES.md), [Etapa 0](ETAPA_0_ESTABILIZACAO.md), [Etapa 4](ETAPA_4_MAPAS_ARQUITETURA.md), [Etapa 5](ETAPA_5_HUD_AUDIO_ACESSIBILIDADE.md), [Build Windows](BUILD_WINDOWS.md).

## 1. Requisitos estabelecidos e evidências disponíveis
- Jogo **solo offline** em Godot 4, alvo **Ryzen 5 7530U, Radeon integrada, 8 GB RAM**, renderer Compatibility; Campo de Testes permanente, incluindo o asfalto.
- Ondas contínuas, preparação padrão **75 segundos**, compras nas estações com **F**, suporte comprado e ativado por atalhos; HUD discreto, sem tutorial permanente.
- GitHub Releases é o canal oficial de ZIP Windows versionado; não sobrescrever releases existentes; uma versão só pode ser anunciada como disponível depois de conferir o asset remoto.
- O CI da v0.9.0 compilou/exportou e publicou um ZIP. **Isso não comprova qualidade visual, FPS, estabilidade nem 15 ondas jogadas.** A captura do usuário mostrou arma branca e aliados com geometria/pose defeituosas; essas falhas são **bloqueantes visuais ainda não validadas como corrigidas**. Não usar FPS instantâneo da captura como benchmark.
- Problemas relatados a rastrear: materiais das armas brancos, aliados mal articulados, apitos repetitivos na transição de onda, mira física desalinhada e preferência explícita do jogador por **remover a crosshair**. A documentação anterior da Etapa 5 que exige retícula deve ser revisada antes de qualquer implementação; não reintroduzi-la como requisito.

## 2. Orçamento de desempenho (E6-P01 — proposta)
| Cenário no notebook-alvo | Meta provisória | Medição obrigatória |
| --- | --- | --- |
| Campo de Testes vazio, 1280×720 baixo | 60 FPS desejáveis | FPS médio, 1% low, CPU/GPU, RAM |
| Ondas 5, 10 e 15 em combate | **30 FPS como piso proposto**, 60 desejáveis | Amostra de 3 minutos por cenário, frametime e picos |
| 12 inimigos + 2 aliados + 1 suporte | Sem travadas recorrentes acima de 100 ms | p95/p99 frametime, instâncias, draw calls |
| Preparação e loja física | Sem queda ou bloqueio de input | Tempo de resposta de F, Esc e compra |
| Sessão prolongada de 15 ondas | Sem crescimento contínuo de RAM/instâncias | RAM inicial/final, nós vivos, vazamentos |

**Método:** notebook na tomada, perfil de energia documentado, mesma resolução e preset, fechar tarefas externas, aquecer 2 minutos; repetir três vezes cada cenário. Registrar mínimo, média, 1% low e p95/p99 de frametime com ferramentas Godot/Windows. Não atribuir números sem medições. **Critério de aceite proposto:** piso sustentado de 30 FPS no cenário crítico; picos isolados devem ser diagnosticados e não escondidos na média. Validar o teto de 12 inimigos da Etapa 2 antes de aumentá-lo.

## 3. Diagnóstico e prioridades de otimização (E6-P02)
1. Instrumentar CPU física/IA, render, quantidade de objetos e áudio, sem mexer no gameplay durante a medição de referência.
2. Se CPU limitar: reduzir buscas de alvos por quadro, cachear alvos, distribuir cálculos de IA no tempo, pooling de efeitos, liberar instâncias temporárias.
3. Se GPU limitar: revisar quantidade de materiais/superfícies e transparências, luzes dinâmicas, sombras, partículas, LOD e oclusão por setor; preservar legibilidade e identidade visual.
4. Se RAM limitar: auditar importação de GLB/texturas, streaming/ciclo de vida de mapas e áudio; não descarregar recurso ainda referenciado.
5. Reexecutar a matriz após **cada** otimização, com comparação antes/depois e rollback se causar regressão.
6. Não mascarar defeitos visuais (armas brancas/aliados deformados) com redução de qualidade; corrigir material, malha e rig separadamente.

## 4. Matriz de testes integrada (E6-P03 — todos pendentes)
| ID | Teste | Aceite proposto |
| --- | --- | --- |
| Q6-01 | Inicialização offline em Windows limpo sem editor | EXE/PCK abrem sem dependência de Godot instalado |
| Q6-02 | Campo de Testes e asfalto | Geometria, colisão e textura preservadas |
| Q6-03 | Armas 1ª pessoa, 5 categorias | Materiais corretos, sem branco inesperado, clipping ou peças ausentes |
| Q6-04 | ADS sem crosshair | Alça/massa ou óptica alinhadas ao centro balístico; disparos coerentes |
| Q6-05 | Aliados invocados e inimigos | Anatomia/empunhadura sem braços invertidos, mãos flutuantes ou arma deslocada |
| Q6-06 | F em 3 estações, saldo insuficiente | Transações corretas, sem compra remota nem débito indevido |
| Q6-07 | 3/4 suporte comprado; G granada | Tokens, ativação e consumo corretos |
| Q6-08 | Onda 1 até 15 sem interrupção | Contadores, spawn e transições corretos, sem softlock |
| Q6-09 | Preparação 75 s e tecla N | Contagem correta, sem ondas duplicadas |
| Q6-10 | Morte clássica e reanimação no treino | Resultados e progresso separados |
| Q6-11 | Pausa, configurações e reinício | Áudio, mouse e controles persistentes e coerentes |
| Q6-12 | Transição sonora de onda | Sem apitos irritantes/repetição; alerta visual funciona com áudio desligado |
| Q6-13 | FPS e memória em ondas 5/10/15 | Métricas registradas, sem degradação contínua |
| Q6-14 | HUD em 720p/900p/1080p | Legível, sem crosshair, sem cortar elementos |
| Q6-15 | Complexo Industrial, quando aprovado e existente | Todas as rotas, estações, IA e setores acessíveis |
| Q6-16 | Arquivo ZIP da release | SHA-256 bate; EXE/PCK presentes; download público funciona |
| Q6-17 | Teste de regressão de assets | Materiais de GLB e poses verificados em screenshot real, não só headless |
| Q6-18 | 30 minutos de jogo após 15 ondas | Sem travamento, vazamento ou queda persistente não explicada |

**Evidência por teste:** build SHA/tag, máquina, resolução/preset, passos, resultado observado, logs, captura e reteste após correção. “Passou no CI” é uma categoria distinta de “passou no notebook”.

## 5. Classificação e portões de entrega (E6-P04)
- **P0:** crash, não inicia, loop quebrado, corrupção de save, bloqueio de compra/onda, perda de controle ou falha grave de gameplay. Não publicar como versão estável.
- **P1:** arma inteiramente branca, aliados visualmente quebrados, ADS desalinhado, alerta sonoro irritante recorrente ou FPS abaixo do piso proposto. Pode existir apenas como **pré-release de teste com aviso explícito**; nunca chamar de correção validada.
- **P2:** polimento de VFX, pequenas animações e melhorias cosméticas. Documentar e priorizar sem bloquear testes do núcleo.
- **Gate A — CI:** importação Godot, análise de scripts, smoke headless, exportação Windows e ZIP/sha256 aprovados.
- **Gate B — execução Windows:** abrir jogo, conferir armas, aliados, áudio, ADS e compra; capturas reais.
- **Gate C — regressão longa:** 15 ondas, sessão de 30 min, benchmarks e ausência de P0; avaliar P1 antes de chamar de estável.
- **Gate D — publicação:** incrementar versão, notas de release com limitações, tag imutável, ZIP+SHA, conferir asset remoto e registrar link. **O workflow existente pode automatizar Gate A/D; não automatiza B/C.**

## 6. Plano de implementação futura e dependências (não executar nesta rodada)
| Ordem | Tarefa futura | Dependência | Entregável e aceite |
| --- | --- | --- | --- |
| 6A | Baseline e coleta de métricas | Etapa 0, build reproduzível | Planilha/log de 3 repetições por cenário |
| 6B | Corrigir P1 visuais/ADS/áudio relatados | Etapas 1, 2, 5 | Capturas e testes Q6-03/04/05/12 |
| 6C | Otimizar gargalo comprovado | 6A, limite IA E2 | Comparativo antes/depois sem regressão |
| 6D | Regressão de 15 ondas e 30 min | 6B/6C, E3 | Q6-06 a Q6-13 registrados |
| 6E | Validar mapa multissetores | Aprovação e entrega E4 | Q6-15 + desempenho por setor |
| 6F | Checklist de release estável | Gates A–C e QA | Publicação versionada, notas e SHA-256 |

**Início/meio/fim do jogo base:** menu e escolha de modo/mapa → sobrevivência sem última onda, compras e preparação → morte no modo clássico e resultado local. Escopo inicial proposto: Campo de Testes + **um** mapa definitivo, não campanha. Mapas extras, coop e progressão online ficam para expansões.

## 7. Decisões pendentes
- **E6-P01:** aceitar 30 FPS piso em 720p baixo, 60 desejáveis, e três repetições por cenário?
- **E6-P02:** aprovar a ordem de otimização baseada em profiling, sem elevar o teto de inimigos antes da medição?
- **E6-P03:** aceitar 18 testes e exigência de execução real no notebook antes de “estável”?
- **E6-P04:** aceitar gates A–D e tratamento de P1 como pré-release somente?
- **Conflito resolvido como requisito do jogador:** retirar crosshair; a Etapa 5 anterior descreve retícula e precisa de ajuste documental antes da implementação. A geometria ADS permanece hipótese técnica a validar.

**Coerência:** preserva E0 (regressão), E1 (armas/ADS), E2 (IA e limite), E3 (economia), E4 (setores) e E5 (UX/áudio), sem presumir aprovação das propostas. **Próxima lacuna:** consolidar GDD mestre, separar decisões estabelecidas/propostas e revisar consistência transversal. Nenhuma modificação de código, cenas, assets ou configurações executáveis nesta rodada.
