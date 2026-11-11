# Frontline Survival — Histórico de versões

## 0.9.3 — Suporte articulado, materiais, foley e IA local

**Estado:** implementação submetida aos testes do Godot; apresentação de armas/aliados e IA permanecem **PARCIAIS** até validação jogando.

- Cabeça e capacete dos aliados presos ao mesmo pivô, com pescoço e gola conectando a silhueta do torso. Este item responde ao efeito de cabeça solta da captura.
- Metal e polímero com mapas de textura/normal procedurais originais, projeção triplanar e paleta GLB preservada.
- Mais pequenos detalhes nas cinco classes de armas; peças ainda estilizadas e econômicas para GPU integrada.
- Recargas mecânicas originais separadas por arma (pistola, SMG, fuzil, escopeta, LMG), com menor volume.
- Etapa 2: sondas leves de obstáculos e recuperação de perseguição quando NPCs ou aliados ficam presos; sem teleportes.
- Gerador determinístico em Python, exportação automática Windows e sincronização de GLBs, texturas e WAVs na branch main.
- Testes estáticos e de duas ondas ampliados com checagens de sons, materiais, cabeça dos aliados e resistência básica de integração.

**CI/Release:** [v0.9.3](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.3). A existência da Release com ZIP e SHA-256 confirma exportação; o teste real no Windows continua necessário.

---

## 0.9.2 — Spawn seguro e teste integrado de ondas

**Estado:** melhoria implementada; homologação em jogo **PARCIAL**. Integração headless verifica o fluxo de duas ondas e pelo menos 100 escolhas de spawn; teste prolongado de 15 ondas permanece pendente.

- **Etapa 2B:** seletor reutilizável de spawns, respeitando distância mínima de 10m do jogador, 4,75m das estações e raio de ocupação física de 0,72m. Os números são provisórios para Campo de Testes.
- Preferência suave por entradas fora da direção de visão do jogador, sem tornar spawn totalmente previsível.
- Se o ponto não for seguro, não cria NPC: aguarda 0,6s e tenta novamente. Log de advertência após tentativas recorrentes; sem descartar inimigos da fila.
- Geração de inimigos movida do processamento de quadros para **_physics_process**, necessário para consultar o espaço de colisão de maneira correta.
- **Etapa 2A / QA:** cenário automatizado `tests/runtime_wave_qa.gd` no GitHub Actions carrega a cena, inicia partidas, examina os pontos de entrada e verifica duas transições de onda com mortes reais dos NPCs e contadores coerentes.
- Nenhuma alteração gráfica em armas ou soldados neste incremento: os defeitos/ajustes visuais da v0.9.1 ainda precisam de avaliação do jogador.

**Release e CI: CONCLUÍDOS** — [v0.9.2](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.2) com ZIP Windows e SHA-256, [workflow 42949035024 aprovado](https://github.com/TPollTech/Frontline-Survival/actions/runs/42949035024), incluindo material das armas, aliados, duas ondas e 100+ escolhas seguras. **Status de gameplay: PARCIAL** até sessão real e feedback.

---

## 0.9.1 — Paleta de armas, aliados, mira real e som de onda (em validação)

**Origem:** na v0.9.0, uma captura real mostrou armas brancas, aliados com poses deformadas e mira desalinhada; houve relato de apitos irritantes. O trabalho da 0.9.1 implementa correções, mas **não está homologado visualmente** até teste em Windows.

**Alterações de código:**
- GLBs armazenam cores no atributo `COLOR_0`. Novo material Godot configura `vertex_color_use_as_albedo`, usado por jogador, inimigos e aliados. Corrige o problema de cores que persistiu após inverter as faces da v0.9.0.
- Criada uma solução compartilhada para braços com geometria de dois segmentos e cotovelos posicionados segundo comprimento de braço e distância até a empunhadura. Reduz poses invertidas de soldados e aliados.
- Colete, mochila e ombreiras dos aliados receberam proporções menores para uma silhueta mais limpa.
- Retirados a crosshair 2D e o hitmarker sonoro agudo; tiro na cabeça continua recompensado pelo texto/créditos.
- Ao mirar, o visor/ferrolho frontal da arma é alinhado ao eixo central da câmera; as ópticas do fuzil/SMG/LMG têm abertura e poste 3D, sem disco opaco.
- Aplicação do recuo deslocada para **depois do raycast**, mantendo o primeiro tiro no ponto de mira antes da subida da câmera.
- Fim de onda recebe dois toques graves suaves sintetizados no próprio jogo; volume do efeito de compra reduzido.
- Preservados Campo de Testes, textura do asfalto, compras por F, intervalo padrão de 75 segundos, ondas contínuas, modos treino/clássico e reforços.

**Etapas do ROADMAP:** Etapa 1 (armas/mira), Etapa 2 (representação dos aliados e inimigos) e Etapa 5 (HUD e áudio) **PARCIAIS** até validação jogando. Etapa 0 (estabilidade) também **PARCIAL**; sessão de 15 ondas ainda pendente.

**QA:** [TESTES_0_9_1.md](TESTES_0_9_1.md). **Exportação: CONCLUÍDA (CI + RELEASES)** — [compilação aprovada](https://github.com/TPollTech/Frontline-Survival/actions/runs/42945928310), ZIP Windows + SHA-256 publicados na [release v0.9.1](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.1). **Visual, mira, sons e aliados: PARCIAIS**, aguardando teste no Windows real.

---

## 0.9 — Correção visual de armas e empunhadura (em validação)

**Estado de entrega:** **CI CONCLUÍDO** na [execução Windows 0.9](https://github.com/TPollTech/Frontline-Survival/actions/runs/42941790033): modelos regenerados, importação Godot 4.4.1, smoke test headless, integridade estática, exportação e artifact ZIP aprovados. Os 19 GLBs corrigidos foram [commitados no GitHub](https://github.com/TPollTech/Frontline-Survival/commit/680a86643ac51841cbe835d8dd8e194b4079c8f7). **Etapas 1 e 2: PARCIAIS**, pois visual, animação e jogabilidade real ainda precisam de aprovação do jogador.

**Correções:**
- Corrigida a orientação invertida das faces dos blocos chanfrados e dos anéis da boca do cano no gerador 3D: faces antes ocultas pelo backface culling devem voltar a aparecer.
- Regeneração integral das cinco armas e dos seus subconjuntos GLB, preservando geometria original de baixo custo e as funcionalidades de recarga.
- Armas longas com escala e profundidade adaptadas para evitar que a coronha ultrapasse o plano próximo da câmera, especialmente a escopeta.
- Mãos do jogador referenciadas ao gatilho e ao guarda-mão de cada classe, acompanhando a posição e escala do modelo.
- Armas de inimigos e aliados centralizadas, clarão alinhado ao cano e braços posicionados por duas metas de empunhadura com cálculo leve por quadro.
- Verificador estático com guarda de orientação externa de faces e presença das novas rotinas de empunhadura.

**Preservado:** Campo de Testes, textura original do asfalto, ondas contínuas, intervalo padrão de 75 s, lojas físicas via F, aliados, ataque aéreo, HUD e controles.

**Avaliação obrigatória:** [TESTES_0_9.md](TESTES_0_9.md): verificar armas opacas e inteiras, recarga e transições, duas mãos realmente sobre a arma, aliados/inimigos em movimento e disparo, ondas 1–5 e performance.

**Evidência de base:** o jogador executou a 0.8 no Windows e enviou captura da preparação para a onda 2, com 138 FPS naquele momento. Esse valor não é um benchmark de sessão prolongada e não homologa a 0.9.

---

## 0.8 — Feedback tático e pipeline Windows (em validação)

**Status técnico:** recursos implementados e exportados com êxito pelo Godot 4.4.1 no GitHub Actions; importação, smoke test headless e integridade estática aprovados. **Etapas 1 e 5: PARCIAIS (teste real pendente). Etapa 0: PARCIAL (CI aprovado, sessão de 15 ondas pendente). Exportação Windows: CONCLUÍDA (CI).** [Execução validada](https://github.com/TPollTech/Frontline-Survival/actions/runs/42936566841).

### Entregas neste incremento
- Indicadores de direção do tiro recebido: frente, direita, trás e esquerda, temporários, sem ocupar permanentemente o HUD.
- O inimigo informa sua posição ao causar dano; aviso só aparece se o ataque efetivamente causar dano.
- Headshot realça por instantes a retícula em âmbar; o bônus existente permanece.
- Mira ADS com deslocamento mais cauteloso e redução moderada do recuo.
- Retícula com expansão dinâmica conforme dispersão das rajadas e retorno ao centro.
- Atualização da identificação de versão no jogo.
- Novo workflow de importação, verificação estática e exportação do Windows em GitHub Actions.
- Instruções de teste sem abrir o Godot em [BUILD_WINDOWS.md](BUILD_WINDOWS.md).

### Preservado
- Ondas contínuas, preparação de 75 s com N opcional, Campo de Testes e asfalto original.
- Estações físicas com F, sem loja global no B.
- Treino com reanimação, suporte com 3/4, 1/2 para armas, menus e áudio ajustável.
- A própria versão 0.7 anterior continua registrada no histórico do GitHub.

### Ainda NÃO concluído
- Teste completo de 15 ondas no notebook e medições de FPS/RAM.
- Rig de mãos profissional, revisão de todas as armas e IA avançada.
- Avaliação do funcionamento no Windows real e eventuais correções depois do feedback.
- Etapas 0–6 do GDD como um todo.

### Lista curta de testes para a versão 0.8
1. Iniciar pelo EXE, sem Godot, abrir menus/pausa.
2. Tomar tiros de frente, dos lados e de trás; conferir indicador correto e temporário.
3. Fazer headshot; verificar flash âmbar e recompensa.
4. Comprar fuzil, usar F na loja, mirar e disparar sem travar controles.
5. Completar onda 1, aguardar 75 segundos e avançar à onda 2.
6. Testar apoio com 3/4 e reanimação no modo de treino.
7. Registrar erro, vídeo, FPS e RAM em eventual falha.

## 0.7 — Armas modulares e soldados articulados

- Cinco classes de armas com corpos/magazines/mecanismos GLB originais.
- Recargas e animações procedurais, braços em primeira pessoa.
- Soldados inimigos e aliados articulados.
- Efeitos curtos de tiro, traços e impactos com transparência.
- Verificador estático e roteiro de testes.

**Observação:** versões em pré-produção têm status explícito. A existência de um arquivo EXE não prova que uma etapa foi validada 100%.
