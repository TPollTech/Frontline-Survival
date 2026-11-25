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


### Revalidação da revisão 828426a — 25/11/2026

A revisão remota permanece 828426a, preservada. Foram realizadas dez verificações estáticas/numéricas independentes em JavaScript sobre os arquivos reais dessa revisão: correspondência de caps object com BUDGETS; parâmetros originais dos postes em comparação com 70f1f91c; restauração das malhas; quatro posições previstas; ausência de criação/mutação de colisor no helper; contagem de triângulos das receitas (cilindro usa contagens históricas, não nova medição); modelo numérico do seletor com os quatro estados iniciais e nove distâncias; geometria da trajetória de câmera nas quatro âncoras; troca somente de mesh no registro; alinhamento de escopo entre QA, CI, inventário e Studio. 10/10 aprovadas; não são execução de GDScript nem de física. Totais previstos continuam 49.248/10.584/4.128 triângulos.

A consulta de status combinado retornou lista vazia, e a consulta de workflows associada ao commit não retornou execuções (essa consulta é limitada a eventos de pull request; não comprova ausência de execução push). A página pública e a API de Actions não ficaram acessíveis. Git ls-remote falhou por DNS e Godot/Blender não foram encontrados no ambiente. Não foi possível obter o ID da execução atual nem baixar/inspecionar as novas capturas. Ausência de resultado não significa falha ou sucesso do CI. Sem evidência visual, nenhuma outra família foi ampliada e não se identificou correção de código justificada nesta revisão. Necessário ID/link da execução push correspondente a 828426a e seus artefatos de Godot/Studio, ou execução verificável no ambiente com engine. Hardware-alvo continua sem benchmark. Alteração exclusivamente documental, sem novo build; 00-10 permanece parcial.


## Execução independente do Actions — 25/11/2026

Base 1bcf176 preservada. Cota do Actions esgotada conforme responsável; nenhum workflow disparado. Clone local continua bloqueado por DNS, sem binário Godot/Blender. Não foi feita ampliação de famílias nem alteração visual ou física. Os resultados anteriores de 171 checks continuam válidos apenas para as quatro famílias naquela revisão; os 207 previstos ainda não foram medidos.

Novo runner `tools/asset_pipeline/world_lod_local.py` executa localmente o teste de orçamento, importação e QA renderizado já existente (Godot 4.4.1, Compatibility), em checkout limpo e pasta nova externa ao repositório. Mantém logs de versão, orçamento, importação e Godot; configura XDG_DATA_HOME e, no Windows, APPDATA/LOCALAPPDATA para perfil temporário (isolamento ainda não exercitado na engine). Não executa CI. Exige o marcador WORLD_LOD_PASS 207, retorno zero, ausência dos erros de script previstos e HEAD/checkout inalterados; confere 23 assemblies, 207 linhas, 86 peças, oito bloqueadores e 15 não bloqueantes, sequência de níveis, limites, invariância de colisor/ray registrada, totais esperados 49.248/10.584/4.128 e cabeçalhos das 30 capturas 1280x720. O modo verify-only verifica consistência de arquivos, não autenticidade/proveniência ou inspeção visual. Hardware e visual_reviewed permanecem false. Sem prova de FPS/VRAM ou contato CharacterBody3D. O runner usa o QA real existente, não geometria substituta.

Testes realmente executados: Python 3.13.5, 11/11 regressões com fixtures sintéticas (test_world_lod_local.py), compilação sintática dos dois arquivos. Fixtures validam aceitação de relatório consistente e rejeição de cobertura incompleta, família errada, caminho duplicado, triângulos/LOD errados, alterações de colisor/ray, falsa aprovação de hardware e cabeçalho/captura ausente. Os PNGs sintéticos são apenas cabeçalhos, não renders. O runner completo, orçamento real, integração Godot e Studio ainda não executados. O runner não substitui inspeção de imagens nem benchmark.

No Windows, na raiz do clone atualizado, com Python 3.10+ e Godot 4.4.1 (caminho exemplificativo, ajustar ao executável real):

```powershell
python -m unittest discover -s tests -p test_world_lod_local.py -v
python tools/asset_pipeline/world_lod_local.py "$env:TEMP\frontline-lod-qa-01" --godot "C:\Godot\Godot_v4.4.1-stable_win64_console.exe"
```

No Linux com display:

```sh
python tools/asset_pipeline/world_lod_local.py /tmp/frontline-lod-qa-01 --godot godot
```

Usar pasta nova a cada execução; se Linux sem display, executar sob xvfb-run. Para conferir arquivos coletados sem executar engine, acrescentar --verify-only ao comando. Enviar local-summary.json, world-lod-report.json, logs e PNGs reais para inspeção; o perfil temporário não é necessário. Depois validar inventário/Studio e benchmark no Ryzen 5 7530U/iGPU/8GB. Sem homologação, build ou ZIP. Estado 00-10 parcial; não alterar outros IDs.


## Validação local renderizada no Windows — 25/11/2026

Revisão de referência `56ee143d0fb039bc5357776282e0c8d9eec87fa2`. O clone da main não ficou disponível via Git devido ao DNS. O teste usou uma cópia isolada do baseline ancestral 62c8837 com os recursos de jogo e dependências do QA atualizados pelo comparativo do GitHub. Os blobs recuperados foram conferidos pelos respectivos hashes. Esta cópia de QA não corresponde a um checkout integral da revisão.

Godot 4.7.2 stable no Windows, Compatibility/OpenGL 3.3, AMD Radeon integrada no Ryzen 5 7520U. Foi usado o QA renderizado existente diretamente após a importação, pois o runner completo exige Godot 4.4.1. Testes de orçamento Python: 2/2 aprovados. Godot: `WORLD_LOD_PASS 207`. O modo `--verify-only` do runner aceitou o relatório e os 30 PNGs. O ensaio percorreu 23 conjuntos, 86 peças, oito bloqueadores independentes e 15 conjuntos não bloqueantes. Os totais medidos foram 49.248 / 10.584 / 4.128 triângulos nos três níveis. Os quatro postes passaram nas nove transições cada e nos limites de 1.632 / 360 / 144 triângulos por conjunto.

Foram abertas as seis imagens dos postes. No comparativo com câmera fixa, a haste e a luminária permanecem visíveis nos três níveis, com mudança discreta no contorno da carcaça no LOD2. A captura distante sofre oclusão parcial e serve para conferir a luminária, com visibilidade limitada da haste. A sequência fixa usa o seletor com distâncias sintéticas e não cobre popping em movimento.

Sem alteração funcional e sem disparo de Actions. A tarefa permanece parcial: falta verificar Godot 4.4.1 e Asset Studio para esta revisão, ampliar a cobertura a outras famílias e medir desempenho no Ryzen 5 7530U com 8 GB. Sem novo executável ou ZIP de distribuição nesta atualização documental.

## Validação local no Godot 4.4.1 — 25/11/2026

Base `4b603e425fa12f6cf035cff6d508c5449905a481`, com `56ee143d` e alterações posteriores preservadas. Git e Godot disponíveis no Linux. Renderização Compatibility/OpenGL 4.5 com Mesa llvmpipe em Xorg, por software. Sem disparo de Actions.

- Na main de referência e novamente pelo runner corrigido (`284b36f`), o Godot 4.4.1 retornou `WORLD_LOD_PASS 207`. No mapa real foram verificados 23 conjuntos, 86 peças, oito bloqueadores invariáveis e 15 conjuntos não bloqueantes. Os níveis somaram 49.248 / 10.584 / 4.128 triângulos. Cada poste manteve três peças, 1.632 / 360 / 144 triângulos e a política não bloqueante.
- A importação em clone limpo reescreveu metadados `.import` versionados e gerou arquivos `.uid`. O runner agora importa um snapshot temporário da revisão Git e preserva a verificação de integridade do checkout original. A execução completa passou com o checkout limpo e verificou os cabeçalhos dos 30 PNGs de 1.280 × 720. Testes Python de orçamento e verificador: 13/13.
- Inspeção de seis capturas dos postes no Linux. Em câmera fixa, a luminária e a parte visível da haste permanecem nos três níveis. A 31,2 m, a haste fica parcialmente ocluída e a luminária ocupa poucos pixels. As capturas fixas usam distância sintética para acionar o seletor. A análise não cobre popping durante movimento ou contato do personagem.
- O inventário Godot aprovou 86 amostras e capturou cinco vistas nativas. O Asset Studio foi montado com o inventário da revisão correta. Seus 19 testes de catálogo passaram. Em Node, o payload de composições conferiu com o SHA-256 do catálogo e com o inventário exportado, incluindo os 23 conjuntos e os quatro postes. O Chromium headless encerrou a página durante o carregamento e o Chromium completo não conseguiu abrir um socket local. A navegação e a inspeção WebGL seguem pendentes.

A tarefa segue parcial. A cobertura das demais famílias e o benchmark de FPS, frame time e memória no Ryzen 5 7530U com GPU integrada e 8 GB continuam pendentes. A medição de triângulos é por recurso, sem inferência de ganho de desempenho.


## Preparação do benchmark isolado — 25/11/2026

Base f1ca06c05f49653b6c13b635a4a14741a2a537ff preservada. Os resultados reais anteriores de 207/207 e seis capturas de postes permanecem válidos no escopo registrado; não foram repetidos. Neste ambiente, Git falha por DNS, Godot e Blender não estão disponíveis (consultas de executáveis e git ls-remote), logo nenhuma nova renderização, cobertura geométrica ou medição de desempenho foi feita.

Novo modo opcional `--benchmark` do runner existente, com snapshot Git, perfil de QA isolado e Godot 4.4.1. Não executa novamente os 207 checks. `world_lod_benchmark.gd` usa a cena real, câmera nativa, 1280 × 720, VSync desabilitado (verifica o estado retornado pela API, não o driver), sem limite de FPS; gameplay congelado, HUD/viewmodel ocultos. Percurso quadrado dentro do mapa, quatro lados de 60 passos, mesmas poses nas quatro passagens A/B/B/A (LOD0 fixo e seletor normal). Cada passagem aquece 240 frames e registra outros 240, 960 intervalos no total; delta simulado de 1/60 s para o seletor (não tempo real de gameplay). O baseline fixa malhas e estado do seletor somente no processo QA, sem alterar o jogo. Saída bruta: intervalos entre frame_post_draw (não timestamps de GPU), triângulos registrados (não triângulos enviados à GPU), CPU/GPU/SO/versão, RAM física informada pelo SO, memória estática do motor e monitor de memória de vídeo quando disponível (não RSS/VRAM medidos externamente). Relatório Python valida ordem, amostras e variação e resume FPS derivado, média, mediana, p95 e p99 de frame time. Sem aprovação automática de hardware, nem equivalência a partida completa.

Teste realmente executado em Python 3.13.5 no container: 8/8 testes sintéticos novos do analisador (incluindo percentis, baseline, amostras, valores não finitos e rejeição de falsa aprovação). O teste não mede desempenho. Os blobs do analisador e seus testes são conferidos contra os hashes dos arquivos testados antes de publicar. Não houve execução do script GDScript, importação ou do runner completo nesta sessão; integração e comportamento do benchmark ainda precisam de prova real.

Comando na raiz de um checkout limpo, Windows (ajustar caminho real do Godot):
```powershell
$destino = "$env:TEMP\frontline-lod-bench-$(Get-Date -Format yyyyMMdd-HHmmss)"
python tools/asset_pipeline/world_lod_local.py "$destino" --godot "C:\Godot\Godot_v4.4.1-stable_win64_console.exe" --benchmark
```
No Linux com display: `python tools/asset_pipeline/world_lod_local.py /tmp/frontline-lod-bench-01 --godot godot --benchmark`. Usar pasta nova; não compartilhar o perfil temporário. Coletar world-lod-benchmark.json, benchmark-summary.json e logs, verificar hardware/driver, temperatura/carga e repetir em condições comparáveis. A medição no Ryzen 5 7530U/iGPU/8 GB, validação WebGL, ampliação de famílias, contato do personagem e popping durante movimento continuam pendentes. Sem CI, build ou ZIP. Estado 00-10 parcial.

## Execução do benchmark e contato do jogador — 25/11/2026

Base remota `b6f1d43d6541dda192cd314786333541e9f39900` conferida, com `f1ca06c` ancestral. O importador headless do Godot 4.4.1 retornou falhas de textura do backend dummy e, em uma tentativa, encerrou com sinal 11. O runner passou a importar o snapshot usando o mesmo OpenGL Compatibility do ensaio, com áudio dummy nas duas fases. A importação neste Linux ainda registrou avisos de Vulkan indisponível, mas concluiu em OpenGL e carregou a cena real.

- Checkout limpo `f94ab18`: 207/207 transições e raios, 23 conjuntos, 86 peças, 30 PNGs verificados pelo runner. A cápsula real do jogador fez 24/24 varreduras com `CharacterBody3D.test_move`, uma por nível em cada um dos oito bloqueadores. A identidade do corpo interceptado e a distância percorrida permaneceram dentro da tolerância de 2 mm. A varredura testa contato horizontal sem deslocar o jogador.
- Inspeção de 15 imagens fixas, três níveis nas cinco famílias. Os sacos ficam mais facetados no LOD2 e a base da estação perde arredondamento. Tambor, lateral do contêiner e poste permanecem reconhecíveis nos ângulos capturados. A inspeção usa o seletor a distâncias sintéticas, sem ensaio de popping em movimento.
- Benchmark na base `b6f1d43`, cena real com Godot 4.4.1 Compatibility, AMD EPYC 9V45 e Mesa llvmpipe Linux. As gerações e a análise dos 960 intervalos passaram. Na sequência A/B/B/A, as médias por passagem foram 59,17 / 45,14 / 43,60 / 57,37 ms. O seletor reduziu a geometria registrada de 49.248 para uma média de 11.712 triângulos, 76,2% abaixo do LOD0 fixo neste percurso. O driver Linux advertiu que não podia alterar VSync. A medição caracteriza o ensaio em software e o perfil de geometria, sem estimativa para a iGPU alvo.
- Python: 21/21 testes de LOD e benchmark, 19/19 de catálogo. No Godot, inventário reconciliado de 86 amostras e cinco vistas nativas capturadas na revisão `b6f1d43`. O Studio local foi montado com 225 buffers e 86 composições. Chromium inicializou WebGL2 em um smoke test mínimo, mas encerrou a aba ao carregar módulos do Studio. A suíte de reconstrução no browser continua bloqueada neste ambiente.

A 00-10 permanece parcial. A cobertura física aumentou para os bloqueadores registrados. Novas famílias e geometrias, popping durante movimento, WebGL no Asset Studio e benchmark no Ryzen 5 7530U/iGPU/8 GB permanecem em aberto. Execução local sem GitHub Actions.


## Preparação da captura de transições em movimento — 25/11/2026

Base e11c2be9147fbab9d147960db886fa471bff6154 preservada (inclui 00-32). Sem repetir 207/207 transições, 24/24 contatos, benchmark A/B/B/A ou inventário anteriores. Neste container Python 3.13.5, Chromium e Xvfb disponíveis; Godot ausente no PATH, git ls-remote falhou por DNS. Sem checkout integral, inventário/Studio atuais, nova renderização ou hardware-alvo.

Novo modo independente `--motion` no runner: usa o mesmo snapshot e perfil isolado do benchmark, sem disparar workflows. Cena real, câmera nativa à altura de 1,65 m, gameplay congelado e HUD/viewmodel ocultos. Reaproveita o percurso quadrado do benchmark, agora com 110 passos por lado (44 m), delta simulado 0,1 s, 4 m/s equivalentes e 441 amostras incluindo fechamento. O seletor de produção é chamado pelo tick normal na posição real da câmera, sem forçar distância de seleção; as capturas ocorrem fora da janela de medição A/B. Registra caminhos de 23 assemblies, posição da câmera, níveis e nome de PNG por frame. Verificador Python exige 441 imagens (cabeçalhos PNG 1280x720, não decodificação), trajetória, famílias e caminhos únicos, níveis válidos e mudanças adjacentes em ambos sentidos de ambos limiares na sequência agregada. Não garante visibilidade de todos os objetos, ausência de popping entre frames, fidelidade visual, navegação do jogador ou FPS. A velocidade e a cadência são simuladas, não tempo real. Não alterar meshes, colisores, LOD de produção ou benchmark existente.

10/10 testes sintéticos novos executados em Python 3.13.5, inclusive percurso fechado, amostra ausente, posição incorreta, caminho inválido, salto de nível, falta de transições, duplicidade, PNG inválido e falsa aprovação. Os PNGs das fixtures são somente cabeçalhos; não são imagens reais. Hashes dos dois arquivos Python testados conferidos antes da publicação. GDScript e runner integrado ainda não executados; coleta/inspeção de frames reais continua pendente.

Windows, na raiz de checkout limpo e atualizado, ajuste o executável:
```powershell
$destino = "$env:TEMP\frontline-lod-motion-$(Get-Date -Format yyyyMMdd-HHmmss)"
python tools/asset_pipeline/world_lod_local.py "$destino" --godot "C:\Godot\Godot_v4.4.1-stable_win64_console.exe" --motion
```
Linux com display: `python tools/asset_pipeline/world_lod_local.py /tmp/frontline-lod-motion-01 --godot godot --motion`. A pasta nova deve ter espaço para 441 PNGs. Revisar world-lod-motion.json, motion-summary.json, logs e a sequência real; por exemplo, com FFmpeg instalado, executar dentro da pasta de evidências: `ffmpeg -framerate 10 -i motion-%04d.png -c:v libx264 -pix_fmt yuv420p motion.mp4`. A reprodução em 10 FPS representa o delta simulado, não a taxa de renderização. Se houver oclusão, complementar com trajetórias específicas antes de julgar a qualidade. WebGL do Studio, ampliação de famílias aplicáveis, inspeção de popping e benchmark no Ryzen 5 7530U/iGPU/8 GB continuam pendentes. Sem release ou ZIP; 00-10 parcial.
