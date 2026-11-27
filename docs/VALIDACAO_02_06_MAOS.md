# 02-06 — Diagnóstico de mãos, dedos, luvas e antebraços

26/11/2026. Base 8ce71a5226694483f3894521b47e39bba41f669e. Escopo exclusivo 02-06; preservar 02-03, 02-04, 02-05, 02-07 e 02-08. Consultados AGENTS.md, checklist, critérios, especificação e padrão artístico. Estado parcial: diagnóstico, não remodelagem homologada.

## Fonte canônica e contratos atuais

A geometria FPS é criada em `scripts/player.gd` (_add_first_person_arm, _arm_link, _arm_capsule_link, _arm_piece), com `scripts/character_geometry.gd` e `scripts/model_surface.gd`. Os três blobs são idênticos nas revisões 3461e5ba191fa46f861d17a34690a7816465d3ef, 823c26df6311e18f497ab4786ce7fb51b0714ed6 e 8ce71a5226694483f3894521b47e39bba41f669e: respectivamente 9659ccd4f91b6ddc807a8ea25ece69e5e51a16c6, 8d8e00541e554fb3cfe72bd4f27f34e996938d0e e 7eee9a911789586a299ebc26b1ffc78196396986. A equivalência é de fontes, não de todos os estados de runtime.

A montagem cria 15 instâncias de malha por braço: três mangas/punho, palma em cápsula achatada, painel dorsal em esfera achatada, oito cápsulas dos quatro dedos e duas do polegar. 13 nós de articulação locais por braço (ombro, cotovelo, pulso, oito dos dedos e dois do polegar); não é um skeleton skinned. A pistola instancia apenas o braço principal; o nó SupportArm existe, mas fica sem geometria. As demais famílias instanciam ambos os braços. Não mudar esse comportamento nesta etapa sem revalidação de estados/encaixes (02-08). As posições, nomes, hierarquias, rotação do pulso de apoio e arrays de articulações são contratos do runtime. Preservar as rotinas de animação, inclusive recarga, corrida e retorno das mãos. Anatomia de rig/IK e pesos contínuos pertencem ao 02-07.

## Inspeção de evidências existentes

Abertas nesta sessão as folhas reais [02-03 Godot](qa/02-03/godot-comparacao.jpg), blob 5cfa2b6866033c64a73c8db096cfe87423037d77, e [02-04 materiais](qa/02-04/materiais.jpg), blob a37b421128beb2c27fd7640ad2501e182372889a. Observadas as mãos e mangas visíveis nos estados arquivados de repouso, ADS e recarga: silhueta arredondada, volume simplificado da luva e mangas verdes com pouca definição. A resolução reduzida das folhas e a oclusão pelo viewmodel não permitem inspecionar individualmente as falanges ou certificar deformações e contatos. Não houve nova captura. Não atribuir as execuções históricas a esta sessão.

## Verificação numérica focal da fonte das mangas

Reproduzidas as expressões da receita sleeve em Python/NumPy (oito seções, 16 lados, triangulação e tampas), para cinco comprimentos derivados das coordenadas da montagem real: dois trechos do braço principal, dois do apoio genérico (sem o caso específico do pump) e punho. Cada reconstrução tem 128 vértices, 252 triângulos e 378 arestas; todas as arestas com incidência dois e orientações opostas, área mínima positiva e volume orientado negativo na convenção matemática de mão direita (winding horário adotado pelo Godot). Resultados:

| Caso | Comprimento do eixo local | Área mínima de triângulo | Resultado |
|---|---:|---:|---|
| Principal, braço | 0.416893 | 0.000071320 | OK |
| Principal, antebraço | 0.392556 | 0.000050323 | OK |
| Apoio genérico, braço | 0.480521 | 0.000071320 | OK |
| Apoio genérico, antebraço | 0.410967 | 0.000050323 | OK |
| Punho | 0.104848 | 0.000048739 | OK |

5/5 reconstruções numéricas passaram. Isso não executa SurfaceTool, não demonstra normais geradas, não valida colisões, poses ou importação. A receita atual não atribui UVs nem tangentes às mangas. Os comprimentos são derivados do espaço de apresentação do jogo, não medidas anatômicas de uma pessoa.

## Próximas alterações de produção

- Substituir a palma arredondada por volume assimétrico com transições da região tenar, base dos dedos e punho, reutilizando a biblioteca canônica; não duplicar modelos somente para o Studio.
- Diferenciar espessuras e volumes de cada dedo, polegar e articulação; preservar pivôs e testar continuidade das silhuetas em extensão/flexão. A montagem usa duas cápsulas por dedo, com raio compartilhado entre os quatro dedos; não tratar os dois segmentos visuais como comprovação de anatomia ou rig completo.
- Refinar painel dorsal, costuras e transições da luva; manter orçamento de superfície e materiais compartilhados. Usar referências autorais/licenciadas de anatomia e luvas; não foram obtidas referências anatômicas externas nesta sessão.
- Preservar a topologia fechada das mangas e acrescentar perfil anatômico, UV/tangentes coerentes e detalhes de tecido quando necessários. Reutilizar os materiais e mapas existentes onde aplicável; não integrar o 02-05 por este ID.
- Executar o portão obrigatório no Studio e no Godot sob iluminação normal e distância de jogo, inspecionar mãos e antebraços em repouso, ADS, recarga e transições com a animação em execução. Registrar comparação antes/depois e limitações. Não aceitar 02-07/02-08 por consequência.

## Ambiente e decisão

Verificação local: Chromium e Python 3 com trimesh 4.11.1 disponíveis; Godot, Godot4 e Blender ausentes do PATH; git ls-remote falhou por DNS para github.com; /mnt/data sem checkout. Nenhuma nova geometria, alteração de rig, textura de produção, GLB, shader, gameplay ou runner foi publicada. Sem Actions ou instaladores. Não promover o 02-06 sem remodelagem e inspeção FPS real.
