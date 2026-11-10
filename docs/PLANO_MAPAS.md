# Plano de mapas — Frontline Survival

## 0. Mapa permanente de testes

**ID:** `campo_de_testes`

O mapa industrial atual e o **laboratorio permanente** do jogo. Ele deve continuar disponivel quando os mapas novos existirem. Objetivos: testar armas, mira, IA, compras, torretas, dano, audio, iluminacao e FPS em cada atualizacao. A textura do asfalto atual deve ser preservada como referencia de qualidade.

> Situacao na 0.4: o codigo do mapa ainda esta em `scripts/main.gd`. A separacao em cenas individuais fica para a fase de multiplos mapas. Nao se deve afirmar que ja existe selecao de mapas.

## 1. Primeiro mapa definitivo: Complexo Industrial

Mapa de tamanho medio, com rotas circulares e varios setores conectados:

- **Patio central:** combate aberto, boas linhas de visao e risco de cerco.
- **Galpao de cargas:** cobertura, corredores, dois acessos e pontos de flanqueamento.
- **Administracao:** salas, escadarias, passarela superior e janelas.
- **Deposito de combustivel:** espacos apertados, explosivos no mapa e entrada lateral.
- **Area externa:** zona com mais distancia de tiro e rotas alternativas.

Tres estacoes de compra em posicoes estrategicas; rotas alternativas entre elas; pontos de surgimento dos inimigos fora do campo visual imediato. Os setores nao precisam de telas de carregamento: sao partes de um mesmo mapa.

## 2. Outros mapas (ideias futuras)

- **Bairro abandonado:** ruas, lojas, interiores e pracas; combate urbano.
- **Base na montanha:** torres, trilhas, bunkers e diferentes alturas.
- **Porto:** conteineres, guindastes e armazens com cobertura variada.

## 3. Requisitos antes de criar o primeiro mapa definitivo

1. Entrada e saida da partida pelo menu.
2. HUD e configuracoes de audio funcionais.
3. Armas, recarga e compras sem bugs impeditivos.
4. IA sem travamentos frequentes em obstaculos.
5. Perfil de desempenho no Ryzen 5 7530U durante ondas com 12 inimigos.
6. Separacao de dados/instancias de mapa, regras de onda e gerenciador de menu.
7. Definicao de pacotes de modelos 3D e materiais com licencas apropriadas.

## 4. Objetivo de arquitetura

Cada mapa devera ter uma cena propria, com grupos/locais de spawn, estacoes de compra, zonas, navegacao de IA, limites e metadados (nome, descricao, dificuldade). A progressao de ondas, jogador, equipamentos e recordes devera funcionar independentemente do mapa.

## 5. Aprovacoes de experiencia (0.4)

- A preparacao entre ondas e configuravel (75 segundos por padrao), independente do mapa.
- Mapas novos precisam respeitar as mesmas regras de economia, HUD, lojas e descanso entre ondas.
- O Campo de Testes deve continuar disponivel para calibrar FPS, armas e inimigos.
