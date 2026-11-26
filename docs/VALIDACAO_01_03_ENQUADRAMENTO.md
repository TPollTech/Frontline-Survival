# 01-03 — Enquadramento das oito armas

26/11/2026. Revisão consultada: fc39a1a3aa8eedaa6998cb08ad8c0870e9bb498f. Escopo exclusivo 01-03. Critério normativo: conferir oito armas em repouso, ADS e recarga sem corte ou enquadramento indevido na resolução suportada.

## Evidência e metodologia

Inventário real Windows/Godot 4.4.1, revisão 95c7ac8c0b32c7c5723ab33cb7a2d4dd29d52968, arquivo evidence.zip/inventory/runtime_inventory.json, SHA-256 51f663f01b7dc142de276d92e8a7046c094c3cb758e6979b8a3d74358e5ad4bb, igual ao manifesto sha256.json do ZIP. Sem failures registrados. Selecionadas as 24 amostras fps_ com optic e muzzle vazios, três estados por arma. Análise NumPy dos buffers reais position: base64 decodificado, tamanho e SHA-256 de cada atributo conferidos com o inventário, contagem igual à superfície. Apenas malhas visíveis sob Viewmodel/body, Viewmodel/mag e Viewmodel/action, excluindo mãos, acessórios e efeitos. Matrizes world em coluna; câmera ativa invertida, aplicação da transformação da malha, profundidade -z, perspectiva vertical keep_height, viewport 1280x720, focal em pixels 360/tan(FOV/2). Coordenadas x=640+focal*x/depth, y=360-focal*y/depth. Não é rasterização nem mede oclusão. Contagens de vértices fora do retângulo não são percentuais da área visível. Recorte de coronha/carregador pode ser normal.

## Resultados da projeção (captura histórica)

| Arma | Pose | Distância mínima ao near plane (m) | Limites projetados x_min,y_min,x_max,y_max (px) | Vértices fora / total |
|---|---|---:|---|---:|
| pistol | hip | 0.5893 | 743.2,430.2,859.2,729.8 | 10/1498 |
| pistol | ads | 0.4493 | 572.9,359.4,707.1,881.4 | 212/1498 |
| pistol | reload | 0.5960 | 759.9,456.0,887.8,997.6 | 105/1498 |
| smg | hip | 0.3788 | 723.3,390.2,1103.8,803.1 | 24/1336 |
| smg | ads | 0.2088 | 321.2,301.2,958.8,1154.9 | 146/1336 |
| smg | reload | 0.3740 | 733.9,419.5,1149.9,918.1 | 112/1336 |
| rifle | hip | 0.3693 | 735.1,431.7,1034.5,789.8 | 24/2459 |
| rifle | ads | 0.1993 | 521.5,360.0,758.5,871.8 | 24/2459 |
| rifle | reload | 0.3671 | 747.9,435.2,1078.0,889.3 | 720/2459 |
| shotgun | hip | 0.2065 | 721.9,420.7,1322.5,1143.1 | 48/1120 |
| shotgun | ads | 0.1000 | 335.5,354.4,944.5,1383.2 | 30/1120 |
| shotgun | reload | 0.2037 | 734.6,418.5,1398.3,1308.2 | 56/1120 |
| lmg | hip | 0.2362 | 689.4,410.6,1301.4,1027.4 | 46/1576 |
| lmg | ads | 0.1000 | 193.0,299.2,1087.0,1633.6 | 128/1576 |
| lmg | reload | 0.2298 | 681.4,423.7,1385.4,1191.0 | 138/1576 |
| sentinela | hip | 0.4683 | 728.3,428.6,951.1,714.9 | 0/472 |
| sentinela | ads | 0.2983 | 559.9,360.0,720.1,735.9 | 4/472 |
| sentinela | reload | 0.4695 | 740.8,430.1,976.9,783.8 | 27/472 |
| sniper | hip | 0.2250 | 699.8,404.1,1279.7,1098.1 | 64/1180 |
| sniper | ads | 0.1000 | 324.5,355.1,955.5,1612.5 | 76/1180 |
| sniper | reload | 0.2221 | 692.4,396.5,1349.1,1244.8 | 127/1180 |
| bolt_sniper | hip | 0.1862 | 708.1,401.5,1381.4,1185.1 | 72/960 |
| bolt_sniper | ads | 0.1000 | 335.0,360.0,945.0,1546.7 | 70/960 |
| bolt_sniper | reload | 0.1839 | 718.3,391.5,1459.3,1365.3 | 144/960 |

24/24 poses sem vértice das armas atrás do plano próximo; margem mínima arredondada 0,1000 m. 23/24 poses com vértices fora da tela, principalmente abaixo e, em alguns casos, à direita; apenas Sentinela hip totalmente dentro. Não inferir defeito/aceite pelo bounding box isolado. Priorizar revisão visual de escopeta, LMG e VLR-8 nos recortes laterais e rifle na recarga. Inspecionadas duas imagens reais anteriores do ZIP, com hashes conferidos: views/fps.png (pistola em primeira pessoa, recorte inferior da empunhadura) e inventory/fps_rifle_ads.png (rifle com óptica, retículo central e coronha/antebraços recortados inferiormente). A segunda imagem não equivale à amostra básica de iron sight usada na tabela. Nenhuma captura atual nem animação completa inspecionada.

## Equivalência e decisão

Diff remoto 95c7ac8..fc39a1a3aa8eedaa6998cb08ad8c0870e9bb498f confirma revisão ancestral e nenhum arquivo em scripts/, scenes/, project.godot ou tests/viewmodel_framing_qa.gd alterado. scripts/player.gd blob 9659ccd4f91b6ddc807a8ea25ece69e5e51a16c6; tests/viewmodel_framing_qa.gd blob 4aa8c1c3c430d823c1d85c7bafcddfa310c68451 idêntico nas duas revisões. O teste existente verifica âncora, margem near, centralização e recarga intermediária e salva uma folha 8x3 no OpenGL. Não foi executado nesta sessão. A comparação também registra 31 GLBs modificados, incluindo novos atributos de normais/tangentes; não presumir equivalência integral de geometria para todos os arquivos nem renderização atual a partir da captura antiga. Os seis GLBs de sniper já tiveram posições/índices/cores/hierarquia conciliados em VALIDACAO_01_01_SNIPERS.md. O reteste de fundação registra paridade representativa, não a inspeção das 24 poses da 01-03.

Godot não encontrado no container desta sessão. Não alterar enquadramento por hipótese, não exigir enquadramento integral das armas e não publicar correção visual não testada. Manter 01-03 parcial até executar o teste existente e inspecionar as 24 posições atuais, incluindo recarga em movimento. Nenhum gameplay, GLB, instalador, runner ou workflow alterado. Nenhum Actions disparado. Entrega exclusivamente documental, sem export Windows novo.
