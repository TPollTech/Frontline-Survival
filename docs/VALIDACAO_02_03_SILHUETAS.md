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
