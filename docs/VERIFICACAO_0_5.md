# Testes de aceite — Frontline Survival 0.5

O que verificar no Godot ao executar no notebook:

1. Tela inicial abre e permite iniciar partida e ajustar configuracoes em 1280x720 (pode rolar o menu Configuracoes).
2. Antes da primeira onda, o HUD mostra "Preparacao / Onda 01" e contagem de 25 segundos.
3. Durante preparacao B abre o menu de compras, que exibe 3 abas e $1200. Comprando SMG, dinheiro diminui $180 e arma fica equipada.
4. Menu de compra aceita botoes do mouse; ao fechar o menu, mouse volta a controlar a camera.
5. Eliminados os 7 inimigos da onda 1, entra na preparacao da onda 2 (75s) **sem** aparecer "Fim de jogo".
6. Com o contador zerando, inicia automaticamente onda 2 sem recarregar cena. O dinheiro / arma comprada permanecem.
7. Com modo treino ligado, receber dano ate zerar vida reanima e restaura vida; nao perde onda, arma, kills, dinheiro. A protecao impede dano por 5s.
8. Desligando reanimacao nas Configuracoes, o modo classico mostra "Fim de Jogo" somente ao morrer.
9. HUD nao mostra texto fixo com teclas de atirar/mirar. E visivel apenas quando proximo de loja; B durante preparacao.
10. A textura de asfalto e os containers nao foram substituidos.
11. Observar FPS com 8-12 inimigos e salvar erros exatos do Depurador se existirem.

Esse roteiro nao substitui o teste de execucao: a maquina que preparou o projeto nao tem Godot instalado.
