# Revisão estática 0.6

## Itens revisados

- Preservada a cena principal, o Campo de Testes, o ciclo de ondas, o modo reanimação e os ajustes de som.
- Removido o tratamento de `KEY_B` para loja rápida; compras apenas pelo `KEY_F` nas estações correspondentes.
- A tecla F não dispara e E agora aplica golpe corpo a corpo; 3/4 ativam suporte comprado.
- Lista de lojas contém metralhadora leve, três opções de suporte e cinco opções de equipamentos.
- Armas disponíveis têm GLB original importável (`pistol`, `smg`, `rifle`, `shotgun`, `lmg`), com script-fonte gerador.
- Onda e arsenal dos inimigos variam conforme progressão em função explícita.
- Testar a importação GLB, efeitos e execução da IA no Godot 4 no notebook; ambiente atual não possui binário do motor.

## Roteiro rápido de teste no notebook

1. F5, iniciar, testar tiro na pistola (sem bola amarela) e golpe E.
2. Comprar metralhadora na estação de ARMA com F. Conferir 75 balas e animação/clarão.
3. Comprar reforços na estação SUPORTE com F; conferir 3 com aliados e 4 com ataque em área.
4. Limpar ondas 1–3; a 4ª deve usar SMG; a 11ª deve usar fuzis.
5. Morrer em modo de treinamento; reviver mantendo a onda e o saldo.
6. Abrir Esc, alterar volumes; conferir que os ajustes persistem.
7. Medir FPS quando houver 12 inimigos e 2 aliados; objetivo é fluidez sem sobrecarregar a GPU integrada.
