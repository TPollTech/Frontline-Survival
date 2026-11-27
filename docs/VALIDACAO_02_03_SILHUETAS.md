# 02-03 — Auditoria de proporções e silhuetas

26/11/2026. Escopo exclusivo 02-03. Base técnica 163f755cf619713418e20e1a4442c05dc262d867, 02-01 e 02-02 já concluídos na main. Consultados [AGENTS](../AGENTS.md), [critérios](CRITERIOS_ACEITE_1_0.md), [especificação](ASSET_STUDIO_SPEC.md), [padrão híbrido](PADRAO_ARTISTICO_3D.md), [relatório 02-02](VALIDACAO_02_02_ARSENAL_HIBRIDO.md) e tests/test_hybrid_arsenal.py. Estado: parcial; nenhuma nova remodelagem publicada.

## Evidência visual e vínculo com a revisão atual

Abertas e inspecionadas as duas folhas PNG reais arquivadas em docs/qa/02-02/ (sheet-after-1.png, blob 9d8badb7cdc0b3aa8487eed2ec9cdd5fde90a55b; sheet-after-2.png, blob 9defac219e185a6abab0ef2df915d3b75a010726). Cada folha possui quatro linhas de seis vistas (perspectiva, direita, esquerda, superior, frontal, traseira). São 48 vistas históricas efetivamente observadas nesta sessão, não uma nova execução do navegador. [Página de evidência](qa/02-02/arsenal.html).

Recuperados os oito GLBs merged da revisão acima pelo GitHub em base64, decodificados e calculados SHA-256 no ambiente JavaScript (autoteste do algoritmo com vetor abc aprovado). 8/8 hashes coincidem com [after-report.json](qa/02-02/after-report.json). Conferidos limites min/max do accessor POSITION e contagem do accessor de índices do mesh exportado. Esta verificação não mede dimensões no mundo, não reexecuta o gerador nem verifica todas as variantes. As folhas compostas foram abertas, mas seus quadros individuais não foram reconciliados por hash de imagem nesta sessão. O PNG godot-arsenal.png não retornou conteúdo pelo conector (zero bytes recebidos), portanto não foi inspecionado novamente. O relatório histórico registra 24 poses reais; não atribuir esse teste a esta execução.

| ID | AABB XYZ local do GLB (m, convenção do projeto) | Triângulos | SHA-256 confere |
|---|---|---:|---|
| pistol | 0.11880 × 0.38750 × 0.39300 | 3952 | sim |
| smg | 0.28000 × 0.64150 × 1.27850 | 4796 | sim |
| rifle | 0.18650 × 0.64166 × 1.73350 | 6914 | sim |
| shotgun | 0.23400 × 0.46651 × 1.97750 | 6472 | sim |
| lmg | 0.42987 × 0.78000 × 1.98550 | 5244 | sim |
| sniper | 0.35325 × 0.62234 × 2.31250 | 4500 | sim |
| bolt_sniper | 0.29050 × 0.51850 × 2.38600 | 5228 | sim |
| sentinela | 0.16825 × 0.38000 × 1.78750 | 4316 | sim |

## Diagnóstico artístico por família

Observações qualitativas nas folhas do Studio, sob iluminação neutra e enquadramento independente por asset. Não tratar as imagens como fotografias em escala comparável entre linhas ou como avaliação da aparência final em FPS.

| Asset | Observação e direção de refinamento visual |
|---|---|
| pistol | Volumes arredondados com aparência de brinquedo; diferenciar planos e transições externas, revisar a relação visual altura/comprimento. |
| smg | Corpo volumoso e transições muito abruptas para as extremidades; harmonizar leitura da silhueta. |
| rifle | Transições entre volumes claros e escuros muito marcadas; suavizar visualmente a continuidade e reduzir aparência de primitivas justapostas. |
| shotgun | Perfil lateral muito uniforme, com volumes longos pouco diferenciados; trabalhar ritmo visual e transições. |
| lmg | Blocos externos muito simplificados e arredondamentos homogêneos; reforçar identidade visual de classe sem copiar um modelo real. |
| sniper | Perfil longo e pouco diferenciado; revisar contraste de massas e continuidade visual da mobília. |
| bolt_sniper | Aparência alongada, volumes com pouca variação e transições marcadas; melhorar coesão da silhueta autoral. |
| sentinela | Volumes predominantemente cilíndricos e simplificados; reforçar linguagem de design original, planos e transições. |

## Dependências e portão de alteração

O padrão já registra uma referência dimensional para a pistola e informa que a geometria estilizada não atende à tolerância de 5%; não reclassificar como aprovada. Nesta sessão não foram obtidas nem inspecionadas referências específicas novas para as oito famílias; preservar a autoria dos modelos fictícios e usar referências de linguagem visual licenciadas e proporções autorais documentadas. Não derivar medidas físicas de uma imagem sem escala confiável.

O teste tests/test_hybrid_arsenal.py congela os envelopes anteriores dentro de 2 mm; scripts/player.gd aplica perfil de apresentação e usa a geometria nas composições de FPS. Alterar o envelope ou fazer escala uniforme indiscriminada pode invalidar enquadramento, estados e encaixes. Refinar primeiro as relações visuais dentro do envelope atual quando possível. Se o desenho autoral exigir alteração de envelope, revisar explicitamente o contrato afetado, sem relaxar tolerâncias só para fazer testes passarem, e revalidar as composições reais. Não mudar o gameplay, PBR global ou mãos nesta tarefa.

Para aceite, registrar referências e alvos de proporção por asset, corrigir a fonte canônica tools/build_weapons.py, exportar e verificar determinismo e contratos, repetir as vistas coerentes do Studio e as poses de repouso/ADS/recarga no Godot; comparar antes/depois com enquadramento equivalente e registrar observações. Preservar 31 variantes e IDs, não introduzir modelos paralelos. O 02-03 não encerra 02-04 a 02-08.

## Ambiente e decisão

Verificação local nesta execução: /mnt/data sem checkout, Chromium presente, Godot/godot4/Blender ausentes do PATH, git ls-remote falhou por DNS. Sem acesso ao checkout Windows que produziu 02-02 nesta sessão. Nenhuma alteração de fonte, GLB, material, teste ou jogo; sem nova renderização/CI/ZIP. Não repetir a auditoria binária já aprovada, mas executar os testes afetados após correções. Estado parcial: diagnóstico e conciliação realizados; referências, alterações e inspeção pós-alteração permanecem necessárias.

## Refinamento de contornos e revalidação

Base 1d4e6d5. A comparação autoral usou as folhas e os oito GLBs originais de 02-02, com SHA-256 reconciliado na revisão base. A primeira rodada preservou os limites de apresentação e trabalhou as transições de contorno dentro dos envelopes históricos. Os alvos foram seção mais plana na empunhadura da pistola, perfil mais anguloso no punho dianteiro da SMG, transição mais estreita na coronha do rifle e da shotgun, seção mais plana na coronha da LMG, pescoço mais definido no sniper, perfil mais arredondado na madeira do bolt sniper e planos mais marcados no guarda-mão da Sentinela. Os alvos são autorais e relativos à geometria de 02-02.

A fonte canônica `tools/build_weapons.py` regenerou 31 variantes, 19 com hashes novos. Duas gerações produziram bytes idênticos entre si. Passaram os quatro testes de arsenal híbrido, os três de geometria das miras, a suíte de integridade de superfícies (sete verificações, incluindo as três de miras) e dois testes do contrato de captura. As oito armas passaram o limite de 2 mm de variação de envelope e conservaram a contagem de triângulos.

- Firefox 135 em Linux com WebGL abriu os oito GLBs de produção e capturou 48 vistas. Os oito SHA-256 observados no Studio coincidiram com os arquivos regenerados. Foram inspecionadas as comparações em perspectiva, direita, superior e frontal. As alterações são localizadas e mantêm a leitura das famílias. Nas folhas, as primeiras quatro colunas são da 02-02 e as últimas quatro da revisão nova. [Pistola, SMG, rifle e shotgun](qa/02-03/studio-comparacao-1.jpg) · [LMG, sniper, bolt sniper e Sentinela](qa/02-03/studio-comparacao-2.jpg).
- Godot 4.7.2 Compatibility, Mesa llvmpipe em Linux, abriu a cena real com 24 poses por revisão. A lista de poses, os FOVs e as posições dos viewmodels coincidiram antes e depois. A inspeção da folha mostrou as miras nas mesmas posições em ADS e preservou a leitura do conjunto durante as poses de recarga. Na folha estão repouso, ADS e recarga em cada metade, antes à esquerda e depois à direita. [Comparação no Godot](qa/02-03/godot-comparacao.jpg).

Estado parcial. O refinamento local preserva o envelope de apresentação. Ainda falta sanar a divergência da pistola com a referência dimensional do padrão artístico e validar alvos dimensionais específicos para as demais famílias.

## Conciliação geométrica após integração PBR — 26/11/2026

Comparados os 31 GLBs reais de `3461e5ba191fa46f861d17a34690a7816465d3ef` (refinamento de contornos 02-03) e `d47784b905ccb3422a7a251f402e8e320fd6caf1` (main atual). Os 62 arquivos foram recuperados por SHA de revisão via GitHub, decodificados e lidos em memória. Verificados cabeçalho GLB 2.0, tamanho, malha única, ausência de transformações locais explícitas e accessors de posições e índices. Para cada triângulo, os três vértices float32 foram canonicalizados por rotação cíclica, sem inverter winding; ordenação do multiconjunto preserva multiplicidade e ignora a reorganização das primitivas por material. Comparação exata, sem tolerância ou arredondamento das coordenadas.

| Família | Triângulos merged | Triângulos body/action/mag | Slots merged antes/depois | Geometria exata |
|---|---:|---|---|---|
| pistol | 3952 | 2412 / 1420 / 120 | 1 / 2 | 4/4 |
| smg | 4796 | 4616 / 60 / 120 | 1 / 5 | 4/4 |
| rifle | 6914 | 4854 / 60 / 2000 | 1 / 3 | 4/4 |
| shotgun | 6472 | 4924 / 1548 / inexistente | 1 / 4 | 3/3 |
| lmg | 5244 | 5024 / 60 / 160 | 1 / 4 | 4/4 |
| sniper | 4500 | 4320 / 60 / 120 | 1 / 4 | 4/4 |
| bolt_sniper | 5228 | 4964 / 144 / 120 | 1 / 3 | 4/4 |
| sentinela | 4316 | 4220 / 36 / 60 | 1 / 2 | 4/4 |

31/31 multiconjuntos de triângulos orientados exatamente iguais, 31/31 contagens de vértices iguais. A integração PBR não alterou os contornos e grupos geométricos homologados anteriormente. Os 41.422 triângulos das oito versões merged foram comparados, além das variantes de grupos (representações alternativas; não somar como carga simultânea). Isso permite reutilizar a evidência de geometria de 3461e5b, não equivale a nova renderização nem a equivalência de materiais, normais, tangentes, cores ou poses em execução. Não foram verificadas dimensões contra novas referências, nem alteradas fontes ou GLBs nesta sessão.

Ambiente verificado: Chromium presente; Godot, Godot4, Blender e Firefox ausentes do PATH; /mnt/data sem checkout; git ls-remote falhou por DNS. Não foi possível executar o portão de renderização. Permanecem abertas as referências dimensionais e a divergência da pistola já registrada; 02-03 continua parcial. Nenhuma alteração no 02-04 ou 02-05, nenhuma Action ou instalador.

## Comparação dimensional externa

Base ec99f6f. A AABB local dos oito GLBs completos foi medida pela união dos limites POSITION de suas primitivas, em milímetros. Os modelos do jogo são autorais. As referências abaixo servem para conferir ordens de grandeza e orientar proporções externas. As configurações foram escolhidas por classe e pela silhueta geral. Para as sete armas longas, a comparação externa se limita ao comprimento total. Ela não define tolerância para altura ou largura, que continuam registradas para acompanhamento.

| Asset | Modelo digital Z × Y × X (mm) | Referência de comprimento | Razão digital/referência |
|---|---|---|---:|
| pistol | 393 × 387,5 × 118,8 | [G19 Gen5](https://us.glock.com/en/products/law-enforcement/pistols/g19-gen5), 185 mm | 2,12 |
| smg | 1.278,5 × 641,5 × 280 | [SCAR-SC](https://fnherstal.com/app/uploads/technical-data-fn-scar-sc-2.pdf), 653 mm com coronha estendida, proxy para silhueta compacta | 1,96 |
| rifle | 1.733,5 × 641,66 × 186,5 | [SCAR-L Mk2 STD](https://fnherstal.com/app/uploads/technical-data-fn-scar-l-mk2-2.pdf), 903 mm com coronha estendida | 1,92 |
| shotgun | 1.977,5 × 466,51 × 234 | [Mossberg 590A1 50774](https://resources.mossberg.com/hubfs/press_releases/Mossberg-Introduces-7-Shot-Versions-of-590A1-and-590-PR-1-4-2016-FINAL.pdf), 39,5 pol. = 1.003,3 mm | 1,97 |
| lmg | 1.985,5 × 780 × 429,87 | [MINIMI 5.56 Mk3](https://fnherstal.com/app/uploads/sites/2/technical-data-fn-minimi-556-mk3.pdf), 939 mm com coronha estendida | 2,11 |
| sniper | 2.312,5 × 622,34 × 353,25 | [Springfield M1A Loaded MA9222](https://www.springfield-armory.com/m1a-series-rifles/m1a-loaded-rifles/m1a-loaded-308-rifle/), 44,33 pol. = 1.125,98 mm | 2,05 |
| bolt_sniper | 2.386 × 518,5 × 290,5 | [Sako TRG 42 A1](https://media.sako.global/image/upload/v1691732877/TRG_22_42_A1_instruction_manual_v1.9_gc6vrx.pdf), 1.204 mm, extremo superior do intervalo publicado | 1,98 |
| sentinela | 1.787,5 × 380 × 168,25 | [Auto-Ordnance M1 Carbine](https://www.auto-ordnance.com/PDF/Guns-CLASSIC2020.pdf), 35,75 pol. = 908,05 mm | 1,97 |

Na pistola, os 387,5 mm de altura correspondem a 3,03 vezes os 128 mm da referência com carregador. A razão altura/comprimento é 98,6% no GLB e 69,2% na referência. Logo, a escala uniforme conservaria a divergência de proporção. A largura externa total do GLB e a largura de armação de 34 mm da referência têm pontos de medição diferentes.

O ajuste de geometria segue aberto. O envelope é consumido pelo enquadramento, pelas poses e pelo encaixe das mãos. A correção precisa validar a pistola na fonte e reavaliar seus pontos de referência visuais no jogador, inimigos e itens coletáveis, com novas capturas antes de promover a 02-03. Esta comparação não alterou modelos ou arquivos de jogo.

## Ambiente de geração restaurado

Windows x64, Python 3.11. Com NumPy 2.2.6, trimesh 4.11.1 e SciPy 1.15.3 obtidos do PyPI e usados em pasta isolada, `python tools/build_weapons.py --out <diretório-temporário>` exportou 31 GLBs das oito famílias. SciPy é usado indiretamente na conversão de cores de faces para vértices no trimesh. Versões registradas em `tools/requirements-arsenal.txt`.

Esta execução confirma o funcionamento do gerador canônico com a fonte atual. Os arquivos gerados foram gravados fora do repositório. A correção dimensional e a homologação visual continuam abertas.

## Ensaio dimensional no Windows — 27/11/2026

Base `541ba01ba4b70240df38f42da00647ce40a69553`. As receitas canônicas geraram 31 GLBs em isolamento. O ensaio levou o comprimento das oito famílias aos alvos da tabela anterior e ajustou também a altura da pistola. Os comprimentos foram medidos na geometria antes da gravação. A largura da pistola e as demais proporções exigem revisão de seções e interfaces. Nenhuma receita candidata foi integrada.

Godot 4.7.2 oficial, Compatibility/OpenGL 3.3, Windows x64 e RTX 4060, viewport de 1280 × 720, cena real e oito famílias em repouso, ADS e quadro intermediário de recarga. O script de captura existente produziu 24 quadros por revisão. Na [comparação inspecionada](qa/02-03/godot-ensaio-dimensional-windows.jpg), a base está à esquerda e o ensaio à direita. A escala isolada deslocou as miras em relação ao alvo e deixou a mão de apoio visivelmente fora do guarda-mão, especialmente no rifle e na escopeta. O êxito do script indica geração das imagens. A inspeção rejeitou a substituição dos modelos.

Prioridade alta no 02-03. A próxima correção precisa levar os pontos de mira, apoios e pivôs para o mesmo espaço dos modelos redimensionados, preservando os contratos das poses publicadas. O aceite exige inspeção de todas as famílias no Studio e no Godot, com recarga em movimento, e conferência das composições de mundo atingidas. O ensaio não cobriu Studio, movimento contínuo nem jogo exportado. O editor usado é 4.7.2 e os templates Windows locais identificados são 4.7.1. Nenhum ZIP foi gerado.
