# 00-31 — Composição canônica de terreno, arquitetura e mapa

Data 25/11/2026; base preservada 5039de822a1137cf7c72d1d48b31a61fc24e2bb8. Estado parcial. GitHub Actions sem cota: [skip ci], nenhum workflow disparado.

## Implementação

`scripts/campo_de_testes_layout.gd` é a fonte editável de distribuição do Campo de Testes existente: terreno, quatro paredes, quatro contêineres, quatro barricadas, três estações, quatro pares de tambores, quatro postes, nove pinturas de pista, três fachadas (oito peças cada) e posição do letreiro. As 33 peças decorativas são geradas pelas fórmulas anteriores. Coordenadas Godot em metros, +Y para cima. `main.gd` consome a receita nas funções _create_world e _add_depot_decor; mantém ordem de montagem, geometria, texturas, RNG dos sacos, materiais, LOD, interações e colisores. Não alterar terreno, navegação, ponto inicial ou câmera. Não criar outros mapas nem alterar a cena de entrada scenes/main.tscn.

O catálogo vivo vincula a família histórica map:campo_de_testes à receita, ao montador e à cena, com fingerprints e grupos de composição; não altera o manifesto de baseline nem cria geometria de preview. A amostra map_briefing continua sendo fonte de malhas e transforms reais no Studio. Nenhuma nova captura foi gerada; não confundir metadados de fonte com reconstrução atual homologada. 23 conjuntos LOD, 86 peças LOD e 207 transições continuam previstos, sem alterar a tarefa 00-10. Há 13 bloqueadores estáticos do mapa previstos (solo, quatro paredes, quatro contêineres, quatro barricadas), dos quais oito pertencem ao registro LOD.

## Evidências

12/12 verificações estáticas V8 aprovadas sobre as fontes reais e a proposta: reconstrução textual reversível do main inteiro a partir da nova receita; terreno/material, quatro paredes, contêineres, barricadas e lojas; fórmulas de decoração; ordem dos pares de tambores, postes e letreiro; helpers físicos/LOD preservados; receita sem criação de geometria/RNG; vínculo real catálogo/cena; contagem prevista de bloqueadores e assemblies. Não são testes GDScript executados, nem prova de paridade de runtime. Nova regressão Python em tests/test_live_catalog.py (fingerprints, determinismo, ausência de preview duplicado, falhas por grupo ou referência de cena ausentes). Novo QA headless em tools/asset_pipeline/runtime/map_layout_qa.gd valida objetos estáticos e shapes reais, materiais do terreno, lojas, ordem dos 23 assemblies, posição inicial e briefing. Ambos adicionados, não executados nesta sessão. Python 3.13.5 disponível, git ls-remote falhou por DNS e Godot/Blender não encontrados. Sem renderização/inspeção nova, benchmark, release ou ZIP.

## Validação local pendente

```sh
python -m unittest discover -s tests -p test_live_catalog.py -v
godot --headless --editor --import --path .
godot --headless --path . --script res://tools/asset_pipeline/runtime/map_layout_qa.gd
```

Executar em perfil QA isolado (ver runner world_lod_local.py para configuração de perfil Windows/Linux), inventário com renderização, gerar catálogo e Studio da mesma revisão e comparar buffers, transforms, material e câmera com a baseline anterior. Verificar 13 bloqueadores, 23 assemblies e navegação no mapa real; testar partida e benchmark no hardware-alvo. Capturas antigas não homologam a nova revisão. Mantém 00-31 parcial até paridade de runtime, visual e desempenho. Escopo fechado: não alterar os demais estados.
