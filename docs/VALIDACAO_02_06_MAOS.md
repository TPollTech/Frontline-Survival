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

## Segunda execução — receitas orgânicas candidatas

Base a2fecf22cbe5feb16e8e652b900c8f86639d3f83; a main já continha 02-05 concluído, preservado nesta entrega. O diagnóstico anterior não foi reexecutado. A biblioteca existente foi recuperada e os blobs Git locais conferidos exatamente: model.py 06713595b8709a822f1f103177b57f7d047662a2 e organic.py 32cef7ff8b0e7fc97d558daa18f7eca8cddae0fc. Nenhuma alteração nessas fontes.

Implementado `tools/asset_pipeline/parametric/fps_hand_geometry.py` (blob 3e7bc0ad0aff322798c5d749d4c675fc2e6059f3) sobre OrganicLoft e MeshSpec, sem novo algoritmo de loft. Receitas editáveis: palma assimétrica espelhável, reforço dorsal achatado, cinco larguras distintas dos dedos/polegar e dois segmentos afunilados por dedo, manga com seções assimétricas e punho. Eixo local Y, sobreposição visual prevista nas extremidades dos segmentos; não modifica pivôs, hierarquias ou animações existentes. Parâmetros autorais iniciais no espaço de apresentação, não dimensões antropométricas homologadas. A ordem/espelhamento dos dedos e encaixes precisa ser conferida antes da integração.

Testes em Python 3.13.5 com os dois arquivos canônicos acima em diretório temporário e imports por namespaces, sem checkout completo. `python -m unittest discover -s tests -p test_fps_hand_geometry.py -v`: 6/6 OK (0,199 s). Arquivo de teste blob 1ffe957953739a340b3499620c367e001f77eaa0. Cobertura: topologia fechada/volume positivo e valores finitos; espelhamento da palma; cinco larguras distintas e afunilamento distal; envelope da palma/painel; determinismo e teto candidato de 4000 triângulos por braço de referência; rejeição de entradas inválidas.

Verificação adicional com trimesh 4.11.1 e NumPy 2.3.5: as 15 peças de referência (palma 720 triângulos, painel 360, dez segmentos de 192 cada, três mangas/punho de 320 cada) têm 2010 vértices e 3960 triângulos no total. 15/15 watertight, winding consistente e área mínima positiva; menor área 5,748e-7. A segunda palma também passou no teste de espelhamento e topologia. Comprimentos de referência arredondados para o teste, não medição das poses reais. O teto é escolha provisória para o candidato, não benchmark do hardware-alvo.

Foi gerada e aberta uma folha local com nove peças isoladas, sombreamento por face no Matplotlib. Observados volumes achatados da palma/painel, segmentos afunilados e mangas de seção variável; ainda existem tampas planas e facetas visíveis na visualização sem normais suavizadas. Não foi apresentada mão montada, textura final, rig ou animação FPS. A folha não é captura do Asset Studio ou Godot e não comprova anatomia final. As receitas candidatas ainda não são consumidas pelo runtime nem pelo catálogo.

Ambiente verificado nesta execução: Python e Chromium disponíveis, Godot/Godot4/Blender/Firefox ausentes do PATH, busca local não encontrou executável Godot, git ls-remote falhou por DNS. Nenhuma alteração em player.gd, character_geometry.gd, model_surface.gd, GLBs, materiais, gameplay ou rig. Para encerrar 02-06, integrar as receitas à fonte canônica do runtime sem criar um segundo modelo de preview, revisar volumes, costuras e UV/tangentes, preservar os contratos de pivôs, executar a inspeção FPS e Studio em repouso/ADS/recarga e transições, corrigir os defeitos observados. 02-07/02-08 permanecem independentes. Nenhuma Action ou instalador. Estado parcial.

## Terceira execução — integração candidata no viewmodel

O gerador `python -m tools.asset_pipeline.bake_fps_hands` mantém as receitas Python como fonte canônica e exporta as malhas locais. O runtime ajusta o comprimento no eixo Y por segmento, inverte o winding para a convenção do Godot e suaviza as normais. As posições dos pivôs, a hierarquia de articulações e as rotinas de animação foram mantidas. A exportação Windows inclui o JSON requerido pelo runtime.

Receitas orgânicas integradas ao viewmodel FPS com pivôs e animações preservados. Seis testes passaram e 18 poses foram renderizadas e revisadas no Godot 4.7.2 em Windows. A oclusão dos dedos limita a revisão. Inspeção das deformações durante as transições, integração e inspeção no Asset Studio e exportação Windows permanecem abertas.

Validação em cópia isolada, com o blob de player.gd igual ao da main antes da intervenção e os GLBs da cópia de teste anterior. O teste exercitou a câmera do jogador em repouso, ADS e amostras de recarga, compatibilidade OpenGL, AMD Radeon. A [captura e o candidato](https://chatgpt.com/library?file_id=libfile_272e329589748191a9a8a20243fa697f&account_id=personal) correspondem a essa execução. Templates de exportação Windows ausentes. Estado parcial.

## Quarta execução — verificação dos templates integrados

Base `a3bed9d1b9f77e806a2a9cca802bfdd8f9e5602e`. Escopo 02-06, preservando os seis testes e as 18 poses da terceira execução; não repetidos. Recuperado o JSON de produção `assets/models/fps_hand_templates.json` (blob b1e17f16d1b341240add1154690c4ef3df0c5136), o consumidor `scripts/fps_hand_mesh.gd` (1cc13d9224c8674afc8c7320dff95e13626eb9e7) e a montagem `scripts/player.gd` (16b9a1673d5bd2059acca254d2cd1d670753f8e4). Verificação numérica em JavaScript, em memória, com os dados reais do JSON: reconstrução do vértice (x, y + comprimento * coeficiente, z), conforme consumidor. Sem reconstruir uma versão paralela do modelo, sem executar Godot.

18 casos para os 16 templates: duas palmas, painel, dois comprimentos de braço, dois de antebraço, punho e dez segmentos digitais. Os comprimentos foram calculados das expressões atuais de player.gd para braço principal e apoio genérico (não o caso particular da escopeta). O braço de apoio usa 0,4805205511; a primeira avaliação de 0,4075536774 foi descartada e o caso corrigido foi efetivamente reexecutado. Resultado final 18/18: índices válidos, coordenadas finitas, todas as arestas com duas incidências de orientação oposta, área mínima positiva (mínimo global 5,7482523984e-7), volume orientado positivo na convenção dos templates. A inversão de winding está explícita no consumidor Godot, não foi executada nesta sessão.

Teste adicional de continuidade geométrica: soma de ângulos sólidos dos triângulos em torno de cada extremo do eixo local dos quinze casos de segmentos alongados, normalizada por 4*pi. 30/30 pontos (Y = +/- comprimento/2) internos às respectivas peças, desvio máximo da unidade inferior a 1e-7. Isso sustenta a sobreposição local no eixo dos segmentos, mas não comprova ausência de clipping ou deformação visível durante as animações.

Para as palmas, os quatro centros de pivô dos dedos e o do polegar foram transformados ao espaço local pela inversa da rotação X de pi/2 da palma. 8/10 pontos internos; dedo 0 da mão principal direita e dedo 3 da mão de apoio esquerda externos (ângulo sólido normalizado aproximadamente zero). Demais pontos aproximadamente um. Centro externo não prova descontinuidade, pois o volume do segmento pode intersectar a palma; inspecionar a união e a flexão reais antes de alterar a geometria. O consumidor gera normais, mas não UV/tangentes; revisão de acabamento e integração/inspeção no Studio permanecem abertas. Não confundir esses testes numéricos com execução de SurfaceTool, captura ou revisão de deformações no FPS.

Ambiente verificado nesta execução: Chromium e Node disponíveis; Godot/Godot4/Godot Mono, Blender e Firefox ausentes do PATH; git ls-remote falhou por resolução DNS para github.com. Sem checkout funcional do jogo. Não foi alterado nenhum modelo, pivô, rig, animação, material ou outro ID; sem Actions ou instaladores. Estado parcial.

## Quinta execução — continuidade local dos dois dedos investigados

Base `7c6199301abd8434b7f9f0af3720038cbbca93bf`. Sem repetir os seis testes das receitas, as 18 poses históricas, as 18 reconstruções ou os 30 extremos de eixo da quarta execução. Os mesmos blobs de player.gd (16b9a1673d5bd2059acca254d2cd1d670753f8e4) e fps_hand_templates.json (b1e17f16d1b341240add1154690c4ef3df0c5136) foram usados.

Verificação numérica em JavaScript sobre os dados reais do template: para cada um dos dois segmentos proximais investigados, reconstruídos os vértices com o comprimento determinado pelo código, aplicada a rotação de menor arco de +Y para o vetor do segmento, translação para seu centro, rotação X do pivô e translação para a raiz do dedo. Transformação inversa para o espaço local da palma. Para cada vértice resultante, calculado o número de winding por soma de ângulos sólidos dos triângulos da palma; considerado interno se o desvio da unidade for inferior a 1e-7.

| Mão / dedo | Intervalo de rotação X (rad) | Amostras uniformes, inclusive extremos | Vértices internos por amostra (mín–máx) | Amostras com sobreposição |
|---|---|---:|---:|---:|
| Principal direita / 0 | 0 a 0,38 | 39 | 4–5 | 39/39 |
| Apoio esquerda / 3 | 0 a 0,34 | 39 | 1–2 | 39/39 |

Intervalos incluem a pose inicial zero e os extremos dos alvos de flexão do código para esses dedos, considerando mag_out e melee_punch entre zero e um. A existência de vértices estritamente internos é evidência de interseção volumétrica local nas amostras, não mede volume de interseção, nem garante ausência de abertura em toda a junção ou entre amostras. Não foram simulados frames reais, colisões, deformações de pele ou renderização. Não há justificativa nesta evidência para deslocar os pivôs automaticamente. A continuidade visual durante animações e inspeção no Asset Studio continuam abertas.

Verificação local nesta sessão: command -v godot godot4 blender sem resultado; git ls-remote para o repositório falhou por resolução DNS. Sem execução do Godot/Studio. Nenhuma alteração de geometria, rig, pivôs, animações ou materiais; sem Actions ou instaladores. Estado parcial.

## Sexta execução — transições renderizadas em FPS

Godot 4.7.2 Compatibility com AMD Radeon em Windows, em cópia de teste isolada. Os scripts de montagem e consumo das mãos correspondem aos blobs da main. O JSON de teste tem origem no conteúdo textual retornado pelo conector, com blob local distinto do blob remoto. Os GLBs da cópia de teste são de uma revisão anterior. Nenhuma auditoria numérica foi refeita.

A cena principal foi aberta e o animador de produção avançou em 61 passos por arma, com o tempo de recarga aplicado diretamente. A folha registra 0%, 25%, 50%, 75% e retorno ao repouso em três linhas: rifle, escopeta e pistola. Recargas de rifle, escopeta e pistola amostradas na câmera FPS real no Godot 4.7.2 em Windows. A mão de apoio do rifle volta ao guarda-mão, mas o enquadramento encobre as duas junções investigadas. Inspeção próxima e no Asset Studio abertas. A folha permite observar o deslocamento macro, mas a oclusão pelo equipamento e o corte inferior impedem inspecionar abertura, clipping ou acabamento das articulações. Nenhuma alteração de malha ou pivô justificada por esta amostra. [Captura](<https://chatgpt.com/library?file_id=libfile_888b14762cb48191896b94ed2b511ea9&account_id=personal>). Estado parcial.
