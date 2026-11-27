# 02-08 — Diagnóstico focal dos encaixes visuais

26/11/2026. Base `063e73e265ebef98edc1a41b38b690c33c5f4869`. Consultados AGENTS.md, checklist, critérios de aceite, especificação, padrão artístico, relatórios 02-06 e 02-07. Não reexecutadas auditorias de geometria/IK/poses anteriores. Escopo: composição virtual FPS, não modificar armas físicas, regras de combate ou demais IDs.

## Contratos e lacunas atuais

Fonte `scripts/player.gd`, blob 16b9a1673d5bd2059acca254d2cd1d670753f8e4. A montagem usa ombro, cotovelo, pulso, palma e juntas digitais, com malhas locais do 02-06. O 02-07 tem solucionador candidato, não integrado. Há sete famílias com mão de apoio e uma (pistola) com braço principal apenas. Os offsets de apoio têm seis chaves explícitas e fallback para sentinela. Há seis chaves de referência para carregadores removíveis de armas longas e caminho separado para o pump da escopeta. Não tratar existência de referência como comprovação de contato. O repouso, ADS, recarga e troca de todas as oito famílias ainda precisam de inspeção da composição atual; capturas anteriores foram realizadas em outras revisões e não homologam os encaixes atuais. Não modificar a pistola ou Sentinela apenas com base em ausência de chave ou de braço adicional: requer direção visual e validação no jogo.

Na animação, a referência de apoio é transformada ao espaço de Hands, mas o deslocamento usa support_palm_rest (centro na montagem inicial). As rotações animadas posteriores do cotovelo/pulso e do SupportArm alteram o centro da palma, embora não sejam consideradas nesse cálculo. O lerp de posição também introduz diferença temporal; não confundir esse efeito intencional com o desvio geométrico. Na fase em que o alvo visual deve ser alcançado, medir o centro efetivo depois das rotações. Uma compensação candidata é resolver, no mesmo referencial pai, a diferença entre a referência interpolada desejada e o centro atual relativo ao nó de apoio, preservando a orientação. Reaproveitar as transformações canônicas já disponíveis em rig.py e a futura integração IK, não criar uma biblioteca duplicada.

## Verificação matemática nova

Executada em JavaScript sobre as expressões atuais do código, em memória, sem Godot. Reconstrução da cadeia de apoio genérico, removido o deslocamento longitudinal comum; excluído o caso particular da escopeta. Aplicadas as rotações-alvo locais do cotovelo, pulso e SupportArm com a compensação inicial do pulso. Não são frames do jogo, nem medidas de distância às superfícies. Não simulados lerp, timing, colisões, IK ou contatos dos dedos.

| Caso representativo | Diferença entre centro animado e repouso (unidades de jogo) |
|---|---:|
| Neutro | 2,50e-17 |
| Amostra de recarga | 0,0486621 |
| Amostra de inclinação durante recarga | 0,0256380 |
| Amostra de corrida | 0,0480988 |

Grade de 21 valores de mag_out e 11 de reload_tilt em [0,1], rotação de SupportArm zero, demais entradas zero: 231 combinações. Alvo de translação sintético variável, sem medir ponto em GLB. Comparada a translação pela referência de repouso com a translação pelo centro animado reconstruído. Maior erro algébrico da primeira: 0,0498490632; maior erro residual da candidata: 1,39e-17. A candidata demonstra uma identidade de transformação, não desempenho, contato ou melhoria visual. A combinação dos parâmetros não representa necessariamente uma fase alcançável do animador. Não substituir o lerp ou a orientação automaticamente; a ordem de atualização e a transição precisam ser observadas e validadas.

## Pendências e ambiente

Chromium, Node e Python presentes; command -v godot godot4 godot-mono blender sem resultado; git ls-remote falhou por resolução DNS de github.com. Sem checkout funcional. Nenhuma nova renderização, alteração de modelo, socket, rig, animação ou gameplay. Não publicar correções de encaixe como homologadas sem a câmera FPS e Studio. Em ambiente funcional, integrar a compensação somente quando o erro visual for confirmado, comparar poses e transições nas oito famílias, avaliar afastamento/interpenetração das palmas/dedos e a continuidade da mão de apoio no contato desejado. Manter os refinamentos 02-06 e as dependências dimensionais 02-03/rig 02-07 independentes. Sem Actions, instaladores ou alteração de outros IDs. Estado parcial.

## Compensação integrada em 27/11/2026

No animador FPS, a translação da mão de apoio passou a considerar a posição da palma após as rotações do ombro, cotovelo e pulso. A correção usa o mesmo centro da malha e os alvos já usados pelo animador, preservando a interpolação temporal. A pistola não tem articulação de apoio e fica fora do cálculo.

No Godot 4.5.2 Compatibility, Windows e AMD Radeon integrada, a sonda mediu a posição real da palma contra os alvos do animador em 61 poses de recarga por arma longa (427 no total). Com a interpolação saturada para isolar o erro geométrico, o desvio máximo caiu de 0,04984907 para 0,00000056 unidade de jogo. O QA do arsenal passou nas oito armas (249 verificações). Os testes Python de mãos e IK passaram (6/6 e 7/7).

Foram renderizadas 24 poses FPS por revisão, em repouso, mira e recarga. Na comparação de recarga inspecionada, a mão de apoio da escopeta está visível junto ao guarda-mão. As outras armas longas ocultam parte do contato com o carregador pelo ângulo e pelo limite inferior da câmera. A pistola mantém a mesma pose visível. [Comparação no Godot a 1280 × 720](qa/02-08/recarga-antes-depois.jpg).

O 02-08 segue parcial. Faltam inspeção de contato dos dedos e das transições em movimento, inclusive troca de arma, e inspeção da composição atual no Asset Studio. O teste por poses isolou o erro de translação e não mediu a distância aos polígonos nem o desvio com a interpolação em tempo real.

## Encaixe durante a interpolação — 27/11/2026

Base `a6df74d`. A compensação da palma é aplicada depois da interpolação de translação, no mesmo quadro das rotações do braço. A mão de apoio da escopeta acompanha a posição efetiva do guarda-mão deslizante, que já é animado separadamente. O alcance ao carregador e o deslocamento de corrida e granada continuam interpolados. O deslocamento acumulado é zerado ao reconstruir o viewmodel na troca. As 231 amostras matemáticas anteriores serviram de base e não foram repetidas.

Antes da solicitação de usar somente a página publicada para a inspeção visual restante, a cena principal foi executada no Godot 4.5.2 Compatibility, Windows e AMD Radeon integrada, a 1280 × 720. O animador de produção recebeu incrementos de 1/60 s. Em 130 passos de recarga da escopeta, o maior desvio entre o centro da palma e o ponto do guarda-mão caiu de 0,00854343 para 0,00000039 unidade de jogo. A métrica mede dois pontos, sem verificar interseção de superfícies ou curvatura dos dedos.

A comparação FPS é composta de seis quadros por família e por revisão, em repouso, mira, dois momentos da recarga e duas fases da troca. A escopeta mantém a mão junto ao guarda-mão nas poses observadas. Em várias famílias, o carregador e os dedos saem do enquadramento durante a recarga. Na troca, a arma sai pelo limite inferior da câmera e a seguinte reaparece. A sequência confirma o fluxo de troca amostrado e não resolve a inspeção dos dedos ocultos. [Oito famílias no Godot](qa/02-08/fps-oito-familias.jpg) · [Escopeta antes e depois](qa/02-08/pump-antes-depois.jpg).

O [Asset Studio publicado](https://tpolltech.github.io/Frontline-Survival/) identificou a revisão `828426a`, anterior a esta alteração. O catálogo público tem 24 poses estáticas das oito famílias, em repouso, mira e recarga, sem amostras de troca. O 02-08 permanece parcial. A página pública não demonstra contato dos dedos e deformações em movimento na revisão entregue.
