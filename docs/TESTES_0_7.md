# Roteiro de testes — Frontline Survival 0.7

## 1. Inicialização e estabilidade

- [ ] Importar `project.godot` no editor Godot 4.x Standard.
- [ ] Aguardar a importação de GLBs e dos cinco WAVs.
- [ ] Executar pelo F5: menu inicial e configurações aparecem sem tela preta ou erro.
- [ ] Verificar a aba **Depurador → Erros**: se existir erro, copiar a mensagem e o número da linha.

## 2. Armas e animação

- [ ] Iniciar no Campo de Testes com $1.200.
- [ ] Atirar com o mouse esquerdo e mirar com o direito.
- [ ] Observar se o clarão é pequeno e a arma recua.
- [ ] Comprar SMG ou fuzil na estação ARMAS com F.
- [ ] Pressionar R com um carregador parcialmente vazio. A arma deve inclinar; o carregador deve descer e voltar, e o mecanismo se mover perto do fim.
- [ ] Comprar metralhadora leve ($650): girar/baixar o conjunto durante recarga deve mostrar o tambor, e não simplesmente ocultar a arma.
- [ ] Testar a escopeta (R): o pump é animado, não há carregador destacável.
- [ ] Testar 1/2, corrida, mira e golpe de E; nada deve travar o disparo.
- [ ] Testar volume reduzido no menu e confirmar se permanece depois de reiniciar.

## 3. Inimigos e aliados

- [ ] Na onda 1, confirmar soldados com escopeta e articulação de pernas, em vez de membros girando no próprio centro.
- [ ] Dar tiros não letais e observar a reação corporal curta do alvo.
- [ ] Derrubar um soldado e confirmar queda + remoção após instantes, sem encerrar a partida.
- [ ] Na onda 4, confirmar a chegada de inimigos com submetralhadoras; na 11, fuzis.
- [ ] Comprar esquadrão na estação SUPORTE e usar tecla 3, observando dois soldados com identificação azul.
- [ ] Comprar ataque aéreo e acionar com tecla 4.

## 4. Progressão (regressão importante)

- [ ] Matar os sete inimigos da primeira onda.
- [ ] Ver **Preparação — Onda 2** com 01:15, não **Fim de Jogo**.
- [ ] Comprar equipamentos durante os 75 s.
- [ ] Esperar até zero e confirmar a segunda onda iniciando automaticamente.
- [ ] No Campo de Testes, deixar a vida chegar a zero e confirmar reaparecimento sem perder armas/dinheiro/onda.
- [ ] Não existe loja pelo B; F somente funciona próximo às estações.

## 5. Desempenho

- [ ] Com a opção FPS ligada, registrar FPS médios e mínimos aproximados no início.
- [ ] Repetir com dez ou mais inimigos ativos, duas torretas e dois aliados.
- [ ] Se cair demais, testar primeiro 720p em janela e desativar efeitos de tela cheia pesados. Não aumentar o número de NPCs antes de medir.

## Se aparecer erro

Copie **o texto exato da mensagem**, o nome do script, a linha e explique em que momento ocorreu (ex.: `R` recarregando a SMG, ou passagem da onda 1 para 2). Se for erro na importação de `.glb`, salve também as primeiras linhas da aba **Saída** do Godot.

Teste realizado neste ambiente: **estrutura, integridade do ZIP (após empacotar), arquivos GLB, contagem de faces, WAVs, picos de áudio, invariantes de ondas/compras e textura do asfalto**. Teste de execução do motor Godot: **pendente**.
