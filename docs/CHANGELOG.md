# Frontline Survival — Histórico de versões

## 0.9 — Correção visual de armas e empunhadura (em validação)

**Estado inicial:** implementação no código e gerador de modelos, aguardando conclusão de CI e testes visuais no Windows. **Etapa 1: PARCIAL. Etapa 2 (representação dos soldados): PARCIAL.** Não considerar aprovado apenas por compilar.

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
