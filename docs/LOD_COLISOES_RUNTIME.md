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


## Ampliação incremental — revisão 3f50aa13

Preservados 5ce2a54f, f883a42d e alterações posteriores. CIs solicitados 45537702060, 45537701973, 45536901686 aprovados; 45537701896 e 45537701885 cancelados, substituídos por revisão a9e86d65 com Studio 45538009975, Windows 45538010101 e Pages 45538010122 aprovados. Escopo exclusivo 00-10.

12f775ae generaliza o registro de assemblies com três níveis por peça, materiais/transformações invariáveis, limites canônicos structure/object verificados por teste Python. Reforços laterais dos quatro contêineres usam a geometria ModelSurface existente e o BoxShape3D preexistente; não remalha corpo/nervuras restantes. Oito tambores mantêm as quatro peças cilíndricas com parâmetros originais e tesselações menores (24/12 segmentos); três estações mantêm as duas peças ModelSurface e a interação/posição existente. Tambores/estações eram decorativos sem bloqueador: não criar colisão nova. Preservadas as quatro barricadas e os respectivos bloqueadores. Distâncias 0/12/30 m, histerese 1 m, atualização 0,2 s; sem screen-space error. Registro usa arrays por peça e tolerância AABB de 5%. Catálogo registra hashes por peça e nível, incluindo multiplicidade, e política existing_box/nonblocking. Nenhum modelo substituto, nenhum novo piloto.

CI inicial 45542136438 e inventário 45542136270 falharam por inferência de tipos de baseline/hit no script QA; 3f50aa13 corrigiu explicitamente Dictionary. [45542221025](https://github.com/TPollTech/Frontline-Survival/actions/runs/45542221025) aprovado: nove transições na fixture e 171 verificações de distância/histerese/triângulos/transformações/materiais/rays no mapa real (19 x 9), oito bloqueadores BoxShape3D invariáveis (72 verificações) e 11 conjuntos com ray sem colisão (99 verificações). Teste roda Godot 4.4.1 Compatibility/OpenGL3 sob Xvfb, câmera real do jogador, HUD/viewmodel ocultados. Ray não é ensaio de contato do CharacterBody3D. Artefato [14989992033](https://github.com/TPollTech/Frontline-Survival/actions/runs/45542221025/artifacts/14989992033) baixado: 171 linhas, 19 assemblies; abertas 12 capturas reais, quatro famílias/3 distâncias. LOD distante pequeno e alguns objetos ocluídos (especialmente contêiner e tambor), sem concluir equivalência visual integral. 1efc8cf4 acrescenta comparação com câmera fixa real na mesma posição, aciona seletor por distância sintética exclusivamente em QA; [45542462884](https://github.com/TPollTech/Frontline-Survival/actions/runs/45542462884) em execução ao registrar.

| Família | Conjuntos | Peças | Bloqueadores | LOD0 | LOD1 | LOD2 |
|---|---:|---:|---:|---:|---:|---:|
| barricada | 4 | 28 | 4 | 12096 | 3024 | 1344 |
| reforços | 4 | 8 | 4 | 3456 | 864 | 384 |
| tambores | 8 | 32 | 0 | 24576 | 4608 | 1536 |
| estações | 3 | 6 | 0 | 2592 | 648 | 288 |
| total | 19 | 74 | 8 | 42720 | 9144 | 3552 |

Métricas do JSON, agregadas para todos no mesmo nível: redução teórica de 78,6%/91,7% vs LOD0; não FPS, nem comparação com o LOD automático anterior. Cada estrutura e objeto respeita seu orçamento por conjunto. [Inventário 45542221048](https://github.com/TPollTech/Frontline-Survival/actions/runs/45542221048) aprovado; artefato 14990006864 baixado, 19 conjuntos e 57 níveis, 185 buffers procedurais, 219 portáveis, 86 amostras. Studio 45542221085 em validação; Windows 45542221077 cancelado após QA_ARSENAL_PASS, substituído por 45542462863. Nova publicação 45542462915 não confirmada. Demais famílias permanecem sem migração; hardware Ryzen 5 7530U/8GB indisponível, sem benchmark de FPS/VRAM/frame time. 00-10 permanece parcial, nenhuma outra tarefa promovida.


### Revisão de câmera fixa confirmada

[45542462884](https://github.com/TPollTech/Frontline-Survival/actions/runs/45542462884) aprovado, 171 verificações repetidas; inventário 45542462819 aprovado. Artefato [14989089738](https://github.com/TPollTech/Frontline-Survival/actions/runs/45542462884/artifacts/14989089738) baixado e 12 imagens de câmera fixa abertas: uma por nível em cada família. Barricadas apresentam redução perceptível de arredondamento no LOD2; contêiner mantém corpo e nervuras (apenas reforços laterais migrados, pouco visíveis de frente); tambores mantêm silhueta e anéis, estação mostra facetas nos níveis inferiores quando vista de perto. Não há desaparecimento grosseiro nas imagens. Capturas fixas foram feitas a 4 m, com distância sintética passada ao seletor apenas em QA; não são a distância normal de uso de LOD2. Não medem popping em movimento. Nenhuma alteração de gameplay adicional. 00-10 parcial por cobertura das demais famílias e benchmark indisponível.


## Ampliação para postes de iluminação — 25/11/2026

Base 70f1f91c (inclui a57fa2c e a sincronização posterior de capturas) preservada. Escopo somente 00-10. `_add_light_post` usa a fonte visual já existente para poste cilíndrico, carcaça e lente (mesmas dimensões, cores, transforms e materiais); três níveis reutilizam cylinder_lods/body_lods, categoria object, âncora no poste. Sem adicionar corpo, shape, luz ou interação. Falha de registro restaura as malhas originais. Demais famílias preservadas.

Metas derivadas das contagens das receitas já medidas, ainda não observadas nesta revisão: quatro novos conjuntos, 12 peças, 1632/360/144 triângulos por conjunto (caps object 8000/2800/700, 4 slots, 8 colisores); totais previstos 23 conjuntos, 86 peças, 8 bloqueadores e 15 não bloqueantes, 69 níveis e 49.248/10.584/4.128 triângulos agregados. Não é medição de FPS. QA Godot exige 207 transições/rays, composição dos cinco grupos de famílias, contratos dos postes, 15 capturas por distância e 15 fixas; inventário e teste browser exigem 23 conjuntos, quatro postes; browser confere política, partes e triângulos por nível. A verificação estática da proposta em V8 passou 8/8 (parâmetros originais, ausência de novo colisor, fallback, caps, aritmética, QA, alinhamento catálogo/browser e cobertura de capturas). Não equivale a executar GDScript, Godot, Studio ou a inspecionar PNGs. Clone local falhou por DNS; Godot e Blender não encontrados. CI desta revisão, inspeção visual e benchmark do Ryzen 5 7530U/iGPU/8GB ainda pendentes. Sem release ou ZIP. Não promover estado de nenhuma outra tarefa.
