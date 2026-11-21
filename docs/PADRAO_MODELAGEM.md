# Padrão de modelagem do Frontline Survival

Use metros e modele no espaço local da peça. No Godot, Y aponta para cima e a frente da arma segue −Z. Separe malha visual, colisão e pivôs animados. Armeiros, personagens e cenário podem combinar malhas autorais em GLB com peças dimensionadas pelo código.

## Peças reutilizáveis

Use `ModelSurface.body(dimensions, profile)` com três dimensões positivas e constantes. O perfil MACHINED produz faces mais planas e quinas estreitas, MOLDED arredonda a transição, e PADDED dá mais volume a tecido e acolchoamento. A função gera normais analíticas, UV por face e dois níveis de detalhe na mesma superfície. Peças com as mesmas dimensões e perfil compartilham a malha. Aplique cor e material na instância.

Use GLB para silhuetas assimétricas, anatomia, dobras e mecanismos exclusivos. Preserve a origem, os encaixes e as peças móveis na exportação. Mantenha geometria plana para pintura no chão e colisões simples para navegação. Em modelos novos, confira a escala junto ao personagem e a leitura da silhueta nas distâncias de jogo.

## Aceitação

Confira poses em primeira pessoa, NPCs e peças de cenário no renderizador Compatibility. Valide os encaixes durante recarga e mira, as colisões do mapa e a partida exportada. Meça FPS no hardware-alvo antes de aumentar a densidade das malhas.
