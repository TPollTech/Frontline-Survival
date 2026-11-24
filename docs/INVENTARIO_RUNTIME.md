# Inventário runtime — QA de cenas reais

Complemento ao inventário estático e contrato v1. A rotina de QA instancia a cena real e usa as receitas existentes, sem editar scripts do jogo nem gerar modelos substitutos. O workflow independente roda Godot 4.4.1/OpenGL3 via Xvfb e publica JSON, logs e quatro screenshots. Não publica release nem altera a baseline. O perfil de dados da execução CI é isolado.

## Cobertura planejada da captura

- Mapa e menu: cena de entrada, três estações, câmera briefing, luz/ambiente, todas as hierarquias de nós; transformações locais e globais em metros, matrizes coluna-major.
- Oito armas: repouso, ADS e recarga; óticas e acessórios suportados amostrados individualmente, não produto cartesiano. Montagem real, materiais efetivos, mãos e colisão do player.
- Inimigos de três tipos, classes de armamento usuais, aliado, humanoide experimental explicitamente habilitado apenas no QA, torreta, oito pickups de arma, munição, granada e efeitos de granada/sangue/evento visual de disparo.
- Registros de cada nó e hierarquia, malha e bounds locais, superfícies e contagem de vértices/índices/triângulos quando disponível, normais/UVs, material efetivo e texturas, shapes, layers, câmeras, luz, ossos e poses.

Não é captura de todos os estados de uma partida, nem exportador geométrico para o Studio. Não grava buffers completos de geometria, índices LOD ou shaders completos; consultas físicas, marcador/impacto aéreo, traçador inimigo e combinações não amostradas ainda precisam de evidência. Nenhum campo ausente deve ser inventado. O manifesto continua estático e só será promovido após conciliação dos resultados efetivos.

## Execução

Workflow: Asset inventory runtime evidence (.github/workflows/asset-inventory.yml). No checkout, após importação do Godot, definir FRONTLINE_INVENTORY_DIR para um diretório de QA isolado; executar `godot --path . --rendering-driver opengl3 --script res://tools/asset_pipeline/runtime/inventory_qa.gd` e `python docs/qa/verify_runtime_inventory.py <diretorio>/runtime_inventory.json`. Preferir perfil de usuário temporário (XDG_DATA_HOME no Linux); nenhum teste deve operar sobre partida pessoal. O verificador rejeita amostras faltantes, nós órfãos, transformações não finitas, superfícies vazias e falha de rig. Capturas geradas não equivalem a inspeção visual.

Estado desta entrega: implementação publicada para execução remota, não afirmar resultado antes de confirmar CI. Godot ausente e GitHub sem DNS no container local. A falha do arsenal do workflow principal não foi corrigida. A tarefa de inventário permanece parcial até execução e conciliação verificadas. 
