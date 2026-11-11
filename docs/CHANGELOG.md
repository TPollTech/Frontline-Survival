# Frontline Survival — Histórico de versões

## 0.8 — Feedback tático e pipeline Windows (em validação)

**Status técnico:** recursos implementados no código, ainda exigem validação do workflow Godot e teste real no Windows. **Etapas 1 e 5: PARCIAIS. Etapa 0: EM TESTES.**

### Entregas neste incremento
- Indicadores de direção do tiro recebido: frente, direita, trás e esquerda, temporários, sem ocupar permanentemente o HUD.
- O inimigo informa sua posição ao causar dano; aviso só aparece se o ataque efetivamente causar dano.
- Headshot realça por instantes a retícula em âmbar; o bônus existente permanece.
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
