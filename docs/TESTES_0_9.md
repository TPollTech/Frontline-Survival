# Frontline Survival 0.9 — Guia de validação visual e build Windows

**Escopo:** correção da orientação das faces dos GLBs, escala/posição das armas, mãos do jogador, empunhadura de inimigos e aliados.  
**Estado:** testes de jogo pendentes; compilação automatizada não substitui teste no Windows.  
**Origem do feedback:** screenshot do usuário da versão 0.8 no Campo de Testes, preparação para a onda 2. Na captura, o HUD indica 138 FPS naquele instante; **não** é benchmark sustentado nem prova de 15 ondas.

## O que corrigir e por quê

1. **Face winding:** o gerador de malhas criava laterais e tampas dos blocos chanfrados com normal apontando para dentro. A renderização do Godot ocultava superfícies externas por backface culling, gerando aparência vazada/incompleta. Inverter as faces e corrigir as superfícies anelares da boca é a correção de causa raiz. Regenerar **19 arquivos GLB** (5 armas completas e 14 partes).
2. **Enquadramento em FPS:** modelos longos (escopeta, rifle e LMG) alcançavam o plano próximo da câmera; aplicar escala por classe e deslocamento para frente, com foco na escopeta reportada.
3. **Mãos do jogador:** os punhos agora dependem de pontos sugeridos de gatilho e guarda-mão próprios de cada classe. Não é rig profissional nem captura de movimento.
4. **Soldados e aliados:** centralizar a arma, alinhar flash à boca e orientar ombros/cotovelos a dois pontos de empunhadura em cada quadro. Trata-se de IK leve procedural; testar estabilidade ao caminhar, mirar, ser atingido e cair.
5. **Compatibilidade:** preservar ondas contínuas, asfalto original, compras por F, N opcional entre ondas, HUD e suporte.

## Roteiro de validação pelo executável

| ID | Ação | Resultado esperado | Situação |
| --- | --- | --- | --- |
| V09-01 | Abrir FrontlineSurvival.exe e iniciar partida | Sem editor Godot, sem tela preta nem fechamento | Pendente de teste do usuário |
| V09-02 | Selecionar escopeta e girar câmera | Arma opaca/inteira, sem lados ausentes | Pendente |
| V09-03 | Mirar com escopeta e correr/andar | Sem peça da coronha cortando a câmera | Pendente |
| V09-04 | Comprar SMG, rifle e LMG, trocar entre elas | Silhueta/material visível e distintas | Pendente |
| V09-05 | Atirar, recarregar e alternar armas | Carregador, ferrolho/pump continuam encaixados | Pendente |
| V09-06 | Observar mão direita e esquerda ao atirar | Duas mãos próximas de gatilho/guarda-mão, sem flutuação evidente | Pendente |
| V09-07 | Aproximar-se de soldado escopeteiro/SMG | Arma voltada para frente e entre as mãos | Pendente |
| V09-08 | Observar soldado em movimento e disparo | Braços acompanham arma sem atravessar torso | Pendente |
| V09-09 | Chamar esquadrão (3) | Aliados usam rifle com postura corrigida | Pendente |
| V09-10 | Testar morte, acerto e movimento de braços | Nenhuma regressão relevante de animação | Pendente |
| V09-11 | Eliminar todos na onda 1 | Preparação de 75 s e próxima onda, nunca game over | Pendente na 0.9 |
| V09-12 | Testar até onda 5, medir FPS com inimigos e aliados | Sessão sem travamento e taxa registrada | Pendente |
| V09-13 | Testar até onda 15 com compras/torretas | Fluxo de ondas e memória estáveis | Pendente |
| V09-14 | Conferir Campo de Testes | Asfalto e estações nas posições anteriores | Pendente |

## Evidências técnicas separadas dos testes visuais

- **Fonte alterada:** scripts/player.gd, scripts/enemy.gd, scripts/ally.gd, tools/build_weapons.py e verificador estático.
- **Modelos binários:** reconstruídos a partir do gerador corrigido pelo workflow Windows. O pipeline também tenta sincronizar os novos GLBs com main, sem desconsiderar a possibilidade de falta de permissão.
- **Validação em CI:** importação Godot 4.4.1, teste de inicialização headless e verificação de integridade, depois exportação Windows.
- **Validação visual:** só pode ser feita após jogar e observar a arma do jogador e os soldados. CI aprovado não confirma pose perfeita.

## Definição de estados

- **CONCLUÍDO (CI):** comprovadamente gerado/importado/exportado sem falhas no workflow; não equivale a jogabilidade aprovada.
- **PARCIAL:** código implementado e/ou build feita, mas visual/física/performance requer validação.
- **CONCLUÍDO (JOGO):** usuário testa casos centrais da funcionalidade e aprova o comportamento.
- **PENDENTE:** não implementado ou não testado.

**Próxima decisão de produção:** revisar feedback da 0.9, ajustar alinhamento se necessário e só depois elevar qualidade do rig/animações de maneira mais ampla.
