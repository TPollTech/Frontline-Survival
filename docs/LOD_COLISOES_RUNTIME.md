# 00-10 — LOD e colisões independentes no mapa real

## Escopo e revisão

Base anterior 40ad8f13 preservada; main inicial ff5d2fd3. Implementação 8e5a757a, sem alterar gameplay de combate, rigs QA ou outras tarefas. Os quatro CIs solicitados 45528961601, 45529409669, 45529734363 e 45529734340 estão verdes; pós-deploy confirmou publicação f93d7076 com 14 pilotos. Nenhuma alteração de estado em tarefas fora de 00-10.

A biblioteca paramétrica mantém BUDGETS de 13 categorias, colisores box/sphere/capsule/convex/concave estático e validação independente. Os limites por categoria são provisórios por instância; categorias não geométricas não recebem budgets de triângulos. Integração incremental na família de barricadas do mapa campo_de_testes, sem alterar os bloqueadores existentes nem adicionar assets. scripts/model_surface.gd oferece body_lods() usando amostras exatas da geometria existente, index buffers compactados e cache compartilhado; body() e LOD nativo legado permanecem intactos para outros consumidores. scripts/world_lod.gd registra assemblies, verifica hierarquia visual simples, três meshes, orçamento por assembly, AABB com tolerância de 5% e existência de BoxShape3D independente. O loop do jogo consulta a câmera ativa a cada 0,2s; distâncias nominais 0/12/30m, margem 1m. Altera apenas part.mesh. Mantém materiais, transforms, shape/RID, layer/mask. Falha de registro mantém LOD0 e bloqueador. A política é distância do centro do bloqueador, não screen-space error. O recurso LOD0 explícito não usa o LOD nativo adicional do mesh legado; custo real depende da câmera e driver.

## Evidência real

[CI 45534922543](https://github.com/TPollTech/Frontline-Survival/actions/runs/45534922543) aprovado na revisão 8e5a757a. Fixture neutra: 9 transições e rays, colisor invariável. Teste Python confirma correspondência dos limites structure com BUDGETS. Teste Godot 4.4.1 Compatibility/OpenGL3 sob Xvfb (Ubuntu runner): cena main.tscn real, câmera nativa do jogador, HUD/viewmodel ocultados para inspeção; sem fixture visual substituta. Quatro barricadas, nove distâncias por barricada (4,12,13.2,30,31.2,30,28.8,12,10.8m); 36 checks, todos aprovados. Sequência 0,0,1,1,2,2,1,1,0. Ray mask 1 interceptou o mesmo corpo e mesma face a cada troca; identidade Shape3D, RID, dimensões, transforms, máscara/camada, materiais e transform visual comparados. Não é ensaio de movimento do CharacterBody3D nem benchmark de frame time.

| assembly | sacos | LOD0 | LOD1 | LOD2 | materiais | colisores |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 8 | 3456 | 864 | 384 | 8 | 1 |
| 1 | 8 | 3456 | 864 | 384 | 8 | 1 |
| 2 | 6 | 2592 | 648 | 288 | 6 | 1 |
| 3 | 6 | 2592 | 648 | 288 | 6 | 1 |
| Total (mesmo nível) | 28 | 12096 | 3024 | 1344 | 28 | 4 |

Cap structure por assembly 20000/8000/2000 triângulos, 8 slots, 24 colisores. Os bloqueadores são caixas analíticas, zero triângulos proxy. 75% e 88,8889% de redução teórica agregada LOD1/2 relativamente a LOD0; não equivale a ganho de FPS nem melhoria medida contra o LOD automático anterior. 

Artefato [14987221247](https://github.com/TPollTech/Frontline-Survival/actions/runs/45534922543/artifacts/14987221247) baixado; world-lod-report.json contém 36 linhas e quatro assemblies. Abertas as três capturas PNG 1280x720 barricade-lod0/1/2. Primeira barricada ao centro visível a 4/13,2/31,2m, mesma posição e silhueta geral, sem desaparecimento grosseiro nas imagens. LOD2 distante é pequeno demais para homologar detalhe fino; as capturas não medem popping durante movimento. Visual dos sacos já existente continua estilizado; sem remodelagem artística. Build Windows [45534922509](https://github.com/TPollTech/Frontline-Survival/actions/runs/45534922509) ainda em execução ao registrar. 

## Limites

Não temos acesso ao Ryzen 5 7530U iGPU 8GB; nenhuma medição FPS/VRAM/frame time no hardware-alvo. As outras famílias conservam LOD legado/nativo e colisões existentes; migração por categorias pertence às tarefas futuras. Não afirmar cobertura integral ou homologação no hardware. 00-10 continua parcial até os requisitos restantes serem comprovados. Nenhum novo piloto.
