# 00-30 — Fontes canônicas de objetos, estruturas e ambiente

Data 25/11/2026. Base preservada: 18b08b1d1f22feedddc17ddc262ac4344a41442c. Estado parcial. GitHub Actions sem cota, não disparar workflows; commits com [skip ci].

## Migração efetiva
A biblioteca de produção `scripts/world_asset_geometry.gd` oferece seis receitas: box, machined, world_box, cylinder, depot_environment e depot_sun. Usa ModelSurface existente e primitivas Godot com os mesmos parâmetros. Cinco famílias históricas ligadas ao catálogo vivo: map:campo_de_testes, environment:lighting, object:loot, object:turret, object:grenade. Quatro scripts consumidores: main.gd, loot_pickup.gd, turret.gd e frag_grenade.gd. A fonte canônica de montagem permanece nos scripts consumidores; a biblioteca não é um novo modelo de preview. Catálogo inclui fingerprint da receita atual, dependências, funções e aprovação falsa, preserva baseline e contrato anterior de personagens.

A regra do box sólido e decoração fina (<0,035 m) foi preservada; malhas MACHINED usam o cache ModelSurface existente. Cilindros mantêm tesselação nativa ou ajustes do consumidor. Ambiente e luz direcional preservam exatamente as atribuições anteriores. Não alterar materiais específicos, transforms, ordem de inserção dos nós, colisores, RNG, interações, física, efeitos ou gameplay. Seis funções de montagem (contêiner, barricada, tambor, decoração, poste, estação) permanecem textualmente iguais; não ampliar os 23 conjuntos LOD previstos nem promover 00-10. A composição/terreno/mapas completos será tratada em 00-31; efeitos/colisões procedurais em 00-32.

O inventário histórico não contém família vehicle em produção. O veículo utility_cart da suíte canônica é QA-only (PILOTOS_ASSETS.md), com validações anteriores documentadas, não substitui um recurso em jogo. Não inventar veículos de produção, não ativar piloto e não criar mecânica de veículo neste escopo. Nova descoberta integral do checkout e confirmação de runtime permanecem pendentes.

## Evidências
12/12 verificações estáticas em V8 sobre as fontes reais da base e alterações propostas: receita de ambiente/luz exata, distribuição do mapa, regra box/colisores, cilindro/transform/material, seis montagens e LOD intactos, equivalência textual reversível do loot e torreta, física/efeitos/visual do objeto arremessável preservados, cinco IDs e chamadas, vínculo no catálogo sem preview duplicado, contrato de personagens intacto e ausência de categoria vehicle na baseline. Não são execução GDScript, Python ou Godot.

Novos testes: regressão de catálogo em tests/test_live_catalog.py e contrato headless de 13 verificações em tools/asset_pipeline/runtime/world_asset_geometry_qa.gd. Não executados neste ambiente. Comandos locais previstos:

```sh
python -m unittest discover -s tests -p 'test_live_catalog.py' -v
godot --headless --editor --import --path .
godot --headless --path . --script res://tools/asset_pipeline/runtime/world_asset_geometry_qa.gd
```

Depois, executar inventário, QA LOD e Studio no mesmo commit, comparar buffers, transforms, materiais, câmera, luz, colisores e capturas reais. Não há novas capturas inspecionadas, benchmark, release ou ZIP Windows. Sem CI conforme solicitação. A migração de receitas existentes não comprova equivalência artística ou desempenho; execução/importação dos scripts, testes Python, Godot, Studio, migração mais ampla para biblioteca paramétrica central e homologação permanecem pendentes. Não marcar concluída.
