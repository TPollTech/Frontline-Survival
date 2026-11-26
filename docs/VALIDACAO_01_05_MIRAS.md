# 01-05 — Alinhamento das miras e lunetas

26/11/2026. Revisão consultada: 9ebd7ec2b183c72400f5d6fd16dd1c51c5d9d361. Escopo exclusivo 01-05. Critério: conferir alinhamento de todas as miras e lunetas e combinações compatíveis na câmera real.

## Implementação e cobertura

scripts/player.gd (blob 9659ccd4f91b6ddc807a8ea25ece69e5e51a16c6): install_attachment, get_sight_height, get_visual_sight_point e get_viewmodel_rest_pose. O teste existente tests/sight_alignment_qa.gd (blob fbff43d231d2e06e595feb2758cbdfbbee787c85) prevê 25 combinações de arma/óptica em ADS, testa marcadores e emissores com FOV do cenário 60/76/100 e arma 76, salva folha de 25 vistas físicas (antes do overlay Sentinela). Não foi executado nesta sessão: godot/godot4 ausentes do PATH. Não substituir sua execução por cálculo. As snipers aceitam 2x e upgrade 4x, sem red_dot/holo; Sentinela aceita red_dot/holo/scope4; demais aceitam red_dot/holo. Não foram testadas rejeições de instalação ou combinações simultâneas de muzzle neste ensaio.

## Nova conciliação numérica

Inventário Godot 4.4.1 Windows histórico, evidence.zip/inventory/runtime_inventory.json, revisão 95c7ac8c0b32c7c5723ab33cb7a2d4dd29d52968, SHA-256 51f663f01b7dc142de276d92e8a7046c094c3cb758e6979b8a3d74358e5ad4bb confirmado contra sha256.json. Lista failures vazia. Python/NumPy executados. Selecionadas 25 amostras fps_ com pose ads, sem muzzle instalado. Usada Camera3D ativa e matriz world em coluna. Para 17 acessórios, exatamente um Optic_EmissiveReticle visível por amostra; centro dado pela translação world real. Para oito miras originais, marcador definido no código (0, altura, z) transformado pela matriz world do nó body, que inclui escala e profundidade do modelo. Não confundir marcador com vértice observado. Projeção perspectiva 1280x720, focal vertical 360/tan(FOV/2) com FOV real da captura, posição relativa à câmera calculada por inversa da matriz world. Base 76, multiplicadores ADS existentes. Todos os 25 pontos à frente do near plane. Desvio do centro: 17/17 emissores 0 px; 8/8 marcadores abaixo de 0,00005 px, máximo 0,00004847684823191647 px (pistola). Tolerância do teste existente: 0,5 px.

| Arma | Miras verificadas | Desvio marcador original (px) |
|---|---|---:|
| pistol | original, red_dot, holo | 0,00004848 |
| smg | original, red_dot, holo | 0,00001365 |
| rifle | original, red_dot, holo | 0,00001462 |
| shotgun | original, red_dot, holo | 0,00002472 |
| lmg | original, red_dot, holo | 0,00003093 |
| sentinela | original, red_dot, holo, scope4 | 0,00004304 |
| sniper | original, scope_2x, scope_4x | 0,00004520 |
| bolt_sniper | original, scope_2x, scope_4x | 0,00001294 |

Verificação adicional de abertura geométrica dos acessórios: 125 superfícies visíveis de MeshInstance3D descendentes de Attachment_Optic_, excluído o próprio emissor e superfícies com albedo alpha inferior a 0,999. 30 buffers únicos position/index decodificados, tamanho e SHA-256 conferidos para cada atributo, índices em intervalo. Transformação para espaço da câmera e interseção bilateral Moller-Trumbore da linha central (0,0,-1) com triângulos, entre near plane e centro do emissor menos 1e-5 m; tolerância baricêntrica 1e-8 e determinante 1e-12. Zero interseções nesse intervalo. Não é teste físico de disparo, rasterização ou oclusão completa: malhas do corpo, mãos, lentes transparentes e shaders não avaliados nessa sonda. Nenhuma conclusão sobre montagem artística, retículo atrás de geometria da arma ou overlay durante gameplay.

Inspecionada imagem real histórica inventory/fps_rifle_ads.png, 1280x720, SHA-256 3fab6db550d24b6a17a5f255073ea5b37bf88a2cdb0558bd761b78fb1238a7f5 conferido contra manifesto: emissor centralizado dentro da abertura da óptica do rifle. Não há folha sight_alignment.png nesse ZIP. Não declarar inspeção de todas as combinações nem captura atual.

## Equivalência e decisão

Comparação remota 95c7ac8..9ebd7ec2b183c72400f5d6fd16dd1c51c5d9d361 confirma ancestralidade e ausência de mudanças em scripts/, scenes/, project.godot ou tests/sight_alignment_qa.gd. Os GLBs foram alterados durante homologação da fundação (normais/tangentes); não atribuir imagens antigas à revisão atual. Código de configuração e projeção permanece pertinente, mas 01-05 ainda requer teste existente em Godot com combinações atuais e inspeção de todas as miras/lunetas na câmera, incluindo overlay Sentinela e ausência de obstrução indevida pelo modelo. Não foi detectada necessidade de alterar código neste escopo numérico. Manter parcial. Nenhuma execução GDScript/WebGL, nova captura, build Windows, alteração de gameplay/modelos/runner/workflow ou Actions nesta sessão. Entrega documental, fundação 34/34 preservada.
