# Pilotos de assets — revisão 00-24, 00-25, 00-27

24/11/2026. Preservados os recursos e código do gameplay existentes. Revisão anterior d4e9a126 com [Windows 45511716282](https://github.com/TPollTech/Frontline-Survival/actions/runs/45511716282) e [Studio 45511716406](https://github.com/TPollTech/Frontline-Survival/actions/runs/45511716406) aprovada. A main também continha a3ac48ad (sincronização de capturas), preservada.

## Piloto canônico 1 — objeto industrial

Balizador de proteção de área industrial, conceito genérico autoral, sem alegação de réplica, marca ou referência fotográfica analisada. Fonte editável: tools/asset_pipeline/parametric/pilot_object.py. Base 0,22 × 0,045 × 0,22 m, altura total 0,835 m; corpo torneado com perfil não trivial e faixa elevada. Três malhas, biblioteca PBR existente (texturas base color, ORM e normal), normais, UV e tangentes autorais. Pivô da raiz no chão; base com offset local de 0,0225 m; orientação canônica Y-up, direção da raiz -Z (referência de transform, não prova de orientação de uma forma rotacionalmente simétrica). Três LODs com 48/24/12 segmentos e distâncias propostas 0/15/35 m, orçamento provisório da categoria object. Colisor de caixa de 0,22 × 0,835 × 0,22 m separado do visual, centro 0,4175 m.

```sh
python -m tools.asset_pipeline.parametric.pilot_object /tmp/frontline-pilot REVISION
```

Gera GLB/glTF de cada LOD, report com SHA-256 e contrato, executa Audit estrito sobre cada exportação, verifica orçamento de triângulos por nível e slots por instância. CI gera duas cópias e compara diretórios byte a byte. Stage separado injeta exatamente os GLBs no Studio de QA, sem publicar no Pages de produção. O script Godot carrega os mesmos GLBs no mapa real em sessão isolada, mede atributos, contagem, dimensões e identidade do colisor e captura a câmera do jogador. Chromium confere o mesmo SHA-256, contagens, dimensões, normais e UVs e salva três capturas. Não substitui nenhuma geometria de produção. Troca de LOD durante a captura é controlada pelo teste, não ligada a distância no gameplay.

## Matriz de cobertura

pilot_coverage.py gera evidência a partir do catálogo vivo reconciliado: categorias existentes, IDs, arquivos GLB/glTF, amostras reais e um candidato por categoria. Inclui também categorias previstas nos BUDGETS sem asset existente. As amostras e os candidatos legados não equivalem a pilotos de fonte canônica nem aprovação visual. Categorias não geométricas (áudio, textura, material, shader, câmera, física) exigem verificações próprias; não inventar uma malha substituta para representá-las. Somente object possui o novo piloto canônico nesta rodada.

## Evidências e limites

[CI 45514843046](https://github.com/TPollTech/Frontline-Survival/actions/runs/45514843046): geração e reprodução estrita das seis exportações aprovadas; etapas Godot/Studio ainda em execução ao registrar. O primeiro workflow 45514798558 não iniciou por uso do contexto runner.temp no env do job; corrigido no commit beb9316a com GITHUB_ENV. Capturas automatizadas não equivalem a inspeção visual efetiva. Não houve integração permanente do piloto, homologação de aparência, benchmark no hardware-alvo ou cobertura de pilotos de todas as categorias. 00-24, 00-25 e 00-27 permanecem parciais. 


## Expansão de pilotos — revisão 00-27

O CI anterior [45514843046](https://github.com/TPollTech/Frontline-Survival/actions/runs/45514843046) terminou verde: balizador 876/444/228 triângulos, seis exports determinísticos, três GLBs importados/renderizados no Godot, três no Studio com hashes/dimensões/contagens coincidentes, colisor separado invariável; matriz de 20 categorias. Continua sem homologação visual manual ou integração permanente.

Fonte autoral dos novos conceitos: `tools/asset_pipeline/parametric/pilot_suite.py`. Preservados os assets atuais, o commit 3b920fe0 e a sincronização posterior c7e59e96. São pilotos técnicos preliminares, não réplicas de produtos comerciais ou modelos aprovados para gameplay. Sem pesquisa fotográfica ou revisão visual efetiva nesta rodada. Arma fictícia visual e carcaça de acessório são sólidos gráficos sem mecanismos funcionais.

| ID | Categoria | Conceito |
|---|---|---|
| qa:training_prop | weapon | Silhueta fictícia de treinamento |
| qa:optic_shell | accessory | Carcaça óptica opaca sem função |
| qa:glove | first_person | Luva com cinco dedos em nós independentes |
| qa:mannequin | character | Manequim vestido com membros separados |
| qa:shelter | structure | Abrigo industrial aberto |
| qa:supply_station | object | Terminal de suprimentos sem lógica de compra |
| qa:planter | environment | Floreira com volumes orgânicos |
| qa:terrain_tile | terrain | Módulo de terreno elevado |
| qa:yard_composition | map | Composição de pátio; não mapa completo nem export do cenário original |

A receita define envelopes físicos por componente e pivô local inferior, perfis chanfrados por extrusão, lofts elípticos de cinco seções com resolução decrescente, PBR base/ORM/normal, UVs, normais e tangentes. Cada piloto exporta três LODs GLB e glTF. Contrato de dimensão calculado a partir dos envelopes autorais, independentemente da malha exportada; direção -Z é uma referência de transformação, não homologação semântica. A luva e o manequim são estudos estáticos de partes articuláveis, não rig anatômico/IK. Não há proxy de colisão criado para as nove novas peças, troca por distância no jogo ou navegação; esses campos são explicitamente desconhecidos/não integrados. Orçamentos são por instância QA e provisórios, não medição de desempenho.

```sh
python -m tools.asset_pipeline.parametric.pilot_suite /tmp/frontline-suite REVISION
```

O workflow `asset-pilot-suite.yml` gera e compara duas cópias byte a byte, exige os contratos e budgets de todos os 54 exports, abre a cena real do Godot em sessão QA com a câmera nativa, posiciona cada GLB para enquadramento isolado e verifica SHA-256, triângulos, dimensões, atributos e clipping. Stage QA injeta os GLBs idênticos, sem publicar no Studio de produção. Playwright compara hashes, contagens e dimensões nos mesmos 27 GLBs, salva capturas por nível. A imagem gerada é evidência técnica, não revisão visual manual.

[CI 45516214029](https://github.com/TPollTech/Frontline-Survival/actions/runs/45516214029): geração estrita e comparação byte a byte concluídas com sucesso; renderização Godot/Studio em andamento no momento do registro. Não contar renders antes de verificar logs. Cobertura canônica total ainda não alcançada (veículo, efeito, colisão, geometria de biblioteca e categorias não geométricas, entre outras). Não substituir produção sem cumprir AGENTS.md. Sem benchmark em hardware-alvo e sem nova release homologada.


## Revisão de acabamento, cobertura geométrica e Studio QA

[CI 45516214029](https://github.com/TPollTech/Frontline-Survival/actions/runs/45516214029) confirmado: 27 GLBs aprovados em Godot e Chromium. Preservados 31a356bd e f9277909, sem substituir assets de produção.

Nova fonte `pilot_finish.py`: blocos com chanfros tridimensionais e topologia fechada (LOD0), anéis de loft com perfis específicos, texturas PBR de 128 px e nove variações cromáticas locais. Aplicada aos dez pilotos anteriores; não altera a biblioteca de materiais de produção. Quatro pilotos acrescentados: utility_cart (vehicle), signal_effect (effect, volume estático, não partícula), collision_proxy (collision, caixa autoral com Shape3D independente verificada na sessão QA), geometry_sample (geometry_library). Todos os 13 grupos de BUDGETS têm uma receita; 14 pilotos, incluindo dois object. O proxy de colisão mantém 12 triângulos invariáveis; não precisa de redução visual. A direção do nó não garante orientação semântica.

[CI do balizador 45516709723](https://github.com/TPollTech/Frontline-Survival/actions/runs/45516709723) aprovado: 924/460/244 triângulos, GLB/glTF reproduzíveis, 3/3 em Godot e Studio. [CI da suíte 45516709742](https://github.com/TPollTech/Frontline-Survival/actions/runs/45516709742) aprovado: 13 pilotos, 78 exports estritos, 39 GLBs renderizados no Godot e 39 no Studio com SHA-256, contagens e dimensões coincidentes. Somados: 84 exports, 42 GLBs. [CI 45517239959](https://github.com/TPollTech/Frontline-Survival/actions/runs/45517239959) aprovado para regressão técnica de produção.

### Inspeção efetiva de imagens

Artefatos 14977504595 (balizador, 907a608f), 14977717453 (baseline, 259485fb) e 14977888052 (suíte refinada, 907a608f) baixados e capturas LOD0 de Studio e Godot abertas para inspeção. Os chanfros e a diferenciação de cores são visíveis, mas os conceitos continuam estilizados e insuficientes para realismo de produção. Observações: interferência de superfícies na faixa do balizador no Studio; membros e cabeça separados no manequim; objetos de chão suspensos na captura QA; vista traseira do abrigo/pátio pouco informativa. As capturas não demonstram animações, anatomia profissional, materiais calibrados ou terreno contínuo.

Correções autorais: a7f78652 separa a faixa do corpo em três segmentos sem superfícies externas coincidentes e faz raycast de chão para o balizador. bfc367a8 altera encaixe de dedos, torso e cabeça, posição dos braços, proporção do relevo, raycast de chão em categorias apoiadas e enquadramento frontal oblíquo pela câmera nativa em sessão isolada. Comparação dimensional no espaço local do anchor. Os CIs [45517239918](https://github.com/TPollTech/Frontline-Survival/actions/runs/45517239918) e [45517239895](https://github.com/TPollTech/Frontline-Survival/actions/runs/45517239895) ainda não concluídos ao registrar. Não declarar correções visualmente aprovadas até conferir novas capturas.

### Publicação de QA separada

A rota prevista é /Frontline-Survival/qa/ e o catálogo contém exclusivamente pilotos, GLBs idênticos, capturas Godot com hash e link de volta ao Studio original. A publicação exige validação da suíte, do balizador e do Studio na própria subrota antes do deploy; valida o catálogo remoto, 14 pilotos/42 capturas, mesma revisão e ausência de IDs qa: no catálogo de produção. `coverage.html` e `native-evidence.json` usam o inventário real da mesma revisão para áudio, textura, câmera, material, shader e física; observações vazias ficam pendentes. Não confundir amostra nativa com novo piloto canônico. Arquivos originais de áudio e textura são copiados com verificação de hash; metadados de câmera, shader e consultas são reais do inventário.

[Pages 45516931730](https://github.com/TPollTech/Frontline-Survival/actions/runs/45516931730) falhou no estágio de publicação (variável de argumentos sombreada por dicionário de asset); e788e716 corrige a causa. [Pages 45517275068](https://github.com/TPollTech/Frontline-Survival/actions/runs/45517275068) pendente ao registrar. Não afirmar que a rota está publicada antes do teste pós-deploy. A geometria está coberta tecnicamente por categoria, mas evidências nativas, cobertura integral do catálogo, refinamento realista, inspeção de todas as perspectivas, produção e benchmark ainda incompletos. 00-27, 00-24 e 00-25 permanecem parciais.

Revalidação posterior: [CI 45517239895](https://github.com/TPollTech/Frontline-Survival/actions/runs/45517239895) aprovado (1116/556/292 triângulos, 3/3 Studio e Godot). Artefato 14978266452 baixado; capturas LOD0 abertas: interferência externa da faixa eliminada visualmente, colisor e chão verificados; a base fica parcialmente cortada no enquadramento Godot, portanto não homologar câmera/asset. Suíte 45517239918 aprovou a etapa de Godot; comparação final Studio em execução. Pages 45517275068 iniciou, sem deploy confirmado. Documentação apenas, sem novo CI para não interromper a publicação em andamento.


## Revisão artística com backend Blender — 00-27

Preservados fc02a43c e df34cf3c (sincronização de capturas), sem edição dos modelos de produção. CI [45517239918](https://github.com/TPollTech/Frontline-Survival/actions/runs/45517239918) terminou verde: 39/39 GLBs comparados Godot/Studio, somados ao balizador 3/3 no CI 45517239895. Artefato 14978058645 baixado e capturas LOD0 de estação, abrigo e veículo abertas em ambos os ambientes. Observação: estação sem detalhes de gabinete, abrigo com cobertura e painel traseiro lisos, veículo com pneus em volumes verticais e cabine sem vidros. Os objetos apoiados aparecem no chão, com melhor enquadramento do que a baseline anterior.

Referências visuais consultadas: [Rittal Outdoor Enclosure Solutions](https://www.rittal.com/us-en_US/Solutions/Rittal-Product-Solutions/outdoor-enclosure-solutions), [Outdoor Basic enclosure](https://www.rittal.com/com-en/products/PG20231215SCH101/PG20240221SCH003/PRO0258?variantId=9784540) e [foto CS Toptec](https://www.directindustry.com/prod/rittal/product-5066-2418845.html). Observadas projeção da cobertura, plinto, portas, dobradiças, puxadores e grelhas. Receitas fictícias originais; sem copiar imagens, logos ou CAD de terceiros. Essas referências orientam a estação e os detalhes industriais, não constituem estudo fotográfico completo de abrigo e veículo.

`pilot_art.py` usa BlenderBackend.bevel real nos corpos principais de estação, abrigo e veículo em LOD0 (três segmentos, limite angular), sem fallback silencioso. Detalhes adicionais por malhas autorais combinadas em grupos de material, mantendo o orçamento de slots. Porta, grelha com 7/4/2 lâminas, juntas e puxadores decorativos; cobertura em camadas e nervuras de abrigo; pneus por revolução com eixo horizontal e vidros opacos decorativos no veículo. Normais/UV/tangentes continuam no exporter canônico; contratos de dimensão e pivôs verificam a saída real. Texturas da suíte 256px, redução de variação e intensidade do normal map em metais pintados. Não há interior, rig, navegação, física de veículo ou lógica de suprimentos. O conjunto continua QA-only; os outros onze pilotos não receberam remodelagem geométrica nesta revisão (variações PBR da suíte afetam outros materiais).

[CI 45518029777](https://github.com/TPollTech/Frontline-Survival/actions/runs/45518029777): instalação do Blender, testes de arte, reprodução estrita e renderização Godot passaram; Studio em execução no momento do registro. CI 45518029702/45518109104 falharam porque a suíte genérica de testes do Windows não instala Blender; f03d30cb permite skip somente quando Blender ausente em fluxo não artístico; o CI artístico exige FRONTLINE_REQUIRE_BLENDER=1 e o gerador exige Blender sem fallback. Vidros ajustados ao envelope em 0aed750b. CI de revisão atual [45518280679](https://github.com/TPollTech/Frontline-Survival/actions/runs/45518280679), Windows [45518280471](https://github.com/TPollTech/Frontline-Survival/actions/runs/45518280471) ainda em validação.

### Publicação QA

[CI 45517275068](https://github.com/TPollTech/Frontline-Survival/actions/runs/45517275068): 14 pilotos, 42 capturas e 13 categorias geométricas staged; NATIVE_EVIDENCE_PASS áudio 3, câmera 3, material 2, física 3, shader 3, textura 3. Studio de produção 32 GLBs aprovado. A subrota QA falhou no carregamento: artefato 14979251478 baixado e pages-server.log confirma HTTP 404 em /Frontline-Survival/qa/studio-light.json. Correção ea41ceec inclui metadados HDRI junto à textura. Novo [Pages CI 45518280483](https://github.com/TPollTech/Frontline-Survival/actions/runs/45518280483) ainda sem confirmação de deploy. Não declarar a rota acessível até o teste pós-deploy. Mantida tarefa parcial: inspeção após alterações, qualidade artística, produção, rig e benchmark pendentes.


## Revisão de capturas Blender e rigging de mãos/personagem

Preservados 75100d0c e a sincronização posterior 0506899a. CIs [45518029777](https://github.com/TPollTech/Frontline-Survival/actions/runs/45518029777) e [45518280679](https://github.com/TPollTech/Frontline-Survival/actions/runs/45518280679) aprovados, cada um com 39 GLBs Godot/Studio. [45518280471](https://github.com/TPollTech/Frontline-Survival/actions/runs/45518280471) Windows aprovado, incluindo QA_ARSENAL_PASS. Balizador 45518280530 aprovado. Nenhum modelo de produção substituído.

Artefatos 14978468183 (3afe4f34) e 14978883219 (0aed750b) baixados e imagens LOD0 de estação/abrigo/veículo abertas no Studio e Godot; também mão e personagem da primeira revisão. Estação: puxador e ventilação discretamente visíveis na segunda versão, gabinete ainda genérico, vista Studio traseira. Abrigo: nervuras visíveis no Godot, cobertura básica. Veículo: vidros visíveis, aspecto de brinquedo, cabine voltada para +Z enquanto direção contratual é -Z; a primeira janela estava no lado interno entre carga e cabine. Corrigida a orientação no commit cd3047b4, para-brisa exterior e teste independente de posição frontal. Grelha escura e espaçamento da porta ajustados em c7f4d83e. Mão: dedos rígidos, pouca anatomia; manequim: volumes simplificados, sem deformação. Não homologar artisticamente nenhuma dessas capturas.

`pilot_anatomy.py` cria perfis longitudinais diferenciados, palma/cuff, dedos e polegar, torso, cabeça, braços e pernas; materiais QA coordenados. RigSpec real com hierarquia, bind frame comum, pesos normalizados e até dois ossos por vértice. Mão: 16 ossos (punho, palma, quatro cadeias de três, polegar de dois); personagem: 13 ossos (pelvis, spine, head, pares upper/lower de braços e pernas, pés). Os contratos de pivô passam a registrar rests dos ossos e o frame comum dos meshes. Seis LODs skinned, exportação GLB/glTF, teste Python de repouso e deslocamento de vértices/filhos com rotação de 25 graus. Ainda são cascas separadas; sem retopologia contínua, IK, limites anatômicos validados, captura de movimentos, animações de produção ou materiais fotogramétricos. Não afirmar anatomia realista final.

CI [45519310297](https://github.com/TPollTech/Frontline-Survival/actions/runs/45519310297): geração/reprodução estrita e renderização Godot aprovadas, Studio em execução ao registrar. Commit 16c90a73 acrescenta validação de Skeleton3D, parent/rest hierarchy (rest no export estático), arrays de índices/pesos, pesos mistos e deslocamento do filho real; screenshots posados e teste de seleção/rotação/reset de osso no Studio. O teste confirma controle de pose, não aprova anatomia nem deformação visual; capturas novas ainda não abertas. CI atual [45519577840](https://github.com/TPollTech/Frontline-Survival/actions/runs/45519577840) em validação, Windows [45519577861](https://github.com/TPollTech/Frontline-Survival/actions/runs/45519577861).

### Publicação

[45518280483](https://github.com/TPollTech/Frontline-Survival/actions/runs/45518280483) passou a geração isolada, permanece em teste de subrota antes do deploy; consulta pública não confirmou acesso. A geração contém o HDRI corrigido. Novo [45519577862](https://github.com/TPollTech/Frontline-Survival/actions/runs/45519577862) pendente. Não afirmar que /qa/ foi publicada. Preserve os gates. Tarefa 00-27 parcial, 00-24 e 00-25 parciais.


## Publicação confirmada e inspeção dos rigs — revisão 00-27

Preservados 2d4fe386 e 79023034 (sincronização de capturas). [Pages 45518280483](https://github.com/TPollTech/Frontline-Survival/actions/runs/45518280483) concluído com sucesso, incluindo PAGES_QA_DEPLOY_PASS https://tpolltech.github.io/Frontline-Survival/qa/ 14 e PAGES_DEPLOY_PASS da revisão 0aed750b0a910122d1ab660be4f30f89b5b4b516. Teste pós-deploy fez HTTP real no catálogo remoto, verificou 14 pilotos/42 capturas, mesma revisão, ausência de IDs QA no catálogo de produção. Tentativa independente de abrir URL com ferramenta web nesta sessão não retornou página; não afirmar navegação independente. [Pages 45519577862](https://github.com/TPollTech/Frontline-Survival/actions/runs/45519577862) ainda em teste de subrota quando registrado.

CIs [45519310297](https://github.com/TPollTech/Frontline-Survival/actions/runs/45519310297), [45519485851](https://github.com/TPollTech/Frontline-Survival/actions/runs/45519485851), [45519577840](https://github.com/TPollTech/Frontline-Survival/actions/runs/45519577840) aprovados, 39 GLBs Godot/Studio em cada suíte. [45519577861](https://github.com/TPollTech/Frontline-Survival/actions/runs/45519577861) Windows aprovado, QA_ARSENAL_PASS.

### Revisão efetiva de imagens e métricas

Artefatos baixados e capturas abertas: [14978838985](https://github.com/TPollTech/Frontline-Survival/actions/runs/45519310297/artifacts/14978838985) (repouso c7f4d83e); [14979024517](https://github.com/TPollTech/Frontline-Survival/actions/runs/45519485851/artifacts/14979024517) (repouso e pose 16c90a73); [14980500177](https://github.com/TPollTech/Frontline-Survival/actions/runs/45519577840/artifacts/14980500177) (veículo cd3047b4). LOD0 Godot e Studio inspecionados. A mão dobra o dedo central e o braço do personagem se desloca, verificável nas capturas; a dobra do dedo é discreta no Godot devido ao enquadramento. A luva mostra junção marcada entre punho e palma e polegar separado; ombros do manequim parecem separados, especialmente na pose. Personagem ainda sem anatomia detalhada, rosto, mãos integradas e retopologia contínua. Veículo corrigido: cabine e para-brisa voltados para câmera no Godot, carga atrás; ainda aparência de brinquedo. Não homologar artisticamente.

| Piloto (16c90a73) | Ossos | Triângulos LOD0/1/2 | Vértices renderizados com pesos mistos LOD0/1/2 | Deslocamento do filho em 25° |
|---|---:|---|---|---:|
| glove | 16 | 5056/1376/688 | 7488/2016/1008 | 0,0105276 m |
| mannequin | 13 | 4216/1176/616 | 2688/768/384 | 0,1294309 m |

Dados de godot-report.json e studio-report.json, conferidos no artefato 14979024517. Vértices renderizados podem repetir vértices fonte por UV/normais; deslocamento é do osso filho, não de toda a superfície. Seis poses (três LODs por piloto) passaram nos dois ambientes; não implica validação de todas as poses ou IK.

### Correções na fonte aa303b81

Punho mais estreito, sobreposição maior com palma, polegar aproximado, perfil superior do torso alargado, braços deslocados para dentro; pesos locais suavizados por smoothstep e mistura da manga superior com spine para reduzir separação aparente. As peças ainda são cascas distintas, não uma única superfície soldada. Câmera QA aproximada de glove/mannequin; não muda câmera de gameplay. Publicação inclui seis novas capturas posadas do Godot, separadas das 42 de repouso, com hash e contexto de pose; teste do Studio seleciona também captura em pose. Pós-deploy verifica posed_count=6. CI [45520645671](https://github.com/TPollTech/Frontline-Survival/actions/runs/45520645671) passou geração estrita/reprodução e estava instalando dependências do Studio; [45520645718](https://github.com/TPollTech/Frontline-Survival/actions/runs/45520645718) publicação pendente; [45520645649](https://github.com/TPollTech/Frontline-Survival/actions/runs/45520645649) Windows em validação. Sem nova inspeção visual após estas correções até os artefatos existirem. Produção não modificada por aa303b81. 00-24/25/27 permanecem parciais.


## Malha contínua experimental de luva — revisão 00-27

Preservados 567139ed e ac5f4561 (sincronização posterior de screenshots), sem alterar assets/cenas de produção. Os quatro CIs solicitados passaram: 45519577862 (Pages cd3047b4), 45520645671 (39 GLBs da suíte e seis poses), 45520645718 (Pages aa303b81) e 45520645649 (Windows, QA_ARSENAL_PASS). O teste pós-deploy do último Pages exige catálogo QA de 14 pilotos, 42 capturas em repouso e posed_count=6, confirmado no log PAGES_QA_DEPLOY_PASS. Rota https://tpolltech.github.io/Frontline-Survival/qa/. A tentativa independente de acesso web nesta sessão não retornou a página; confirmação é HTTP real executado pelo CI, não navegação independente.

### Inspeção real da revisão aa303b81

Baixado artefato [14981085072](https://github.com/TPollTech/Frontline-Survival/actions/runs/45520645671/artifacts/14981085072); abertas as oito capturas LOD0 de glove/mannequin em repouso e pose no Studio e Godot. Punho e palma parecem mais integrados, dedos ainda volumes escuros separados e polegar pouco anatômico; pose de dedo visível no Studio, discreta no Godot. Ombros do manequim menos destacados, mas torso, cabeça, membros e botas continuam estilizados e sem anatomia contínua. A imagem não comprova ausência de interpenetração. Não homologar esses modelos. CI aa303b81 confirma 16/13 ossos, seis poses e pesos normalizados; mão com 3456/768/384 vértices renderizados de pesos mistos, personagem 3072/768/384; deslocamento do osso filho de 0,0105276 m e 0,1294309 m respectivamente em 25 graus.

### Nova fonte canônica

Commit 73596b74, `continuous_glove.py`: substitui exclusivamente o piloto QA glove. Decisão de escopo: começar pela mão, não refazer o personagem junto. A nova superfície usa patches quadriculados autorais de punho/palma, quatro tiras para os dedos e tira oblíqua para o polegar, compartilhando índices nas junções. Duas faces e faixa lateral de contorno fecham uma única casca. Três resoluções autorais (não decimação cega), triangulação reproduzível, envelope-alvo original de 126 × 192 × 44 mm, ajuste afim explícito ao envelope e pivôs no mesmo frame. Verifica incidência de arestas, orientação fechada, volume positivo, componente único e característica de Euler 2. A topologia é uma retopologia procedural simplificada, não escaneamento nem malha de produção profissional. Sem checagem global de auto-interseção.

Rig 16 ossos, pesos regionais normalizados com transições suaves e zonas de falange; teste LBS em quatro movimentos por LOD (punho 20°, dedo central 45°, anelar 35°, polegar 25°), verifica vértices deslocados e razão de área de cada triângulo entre repouso/pose. Limites 0,025–8 são guardrails de degeneração grosseira, não critério anatômico; não comprovam ausência de interpenetração ou preservação visual de volume. Mantém teste de pose real de 25° no Godot e Studio. Atlas UV frente/verso/lateral, PBR 512px original (trama, painéis, costuras, roughness/ORM e normal map); sem fotografia, scan, referência de material calibrada ou IK. Uma superfície e um material, sem costura geométrica ou placa protetora separada. Personagem continua piloto skinned de cascas distintas. Nenhum asset de produção substituído.

Testes `tests/test_continuous_glove.py` verificam topologia, dimensões, LODs, atlas determinístico, ossos e pesos. Workflow [45525440788](https://github.com/TPollTech/Frontline-Survival/actions/runs/45525440788) em execução, [45525440954](https://github.com/TPollTech/Frontline-Survival/actions/runs/45525440954) publicação em validação e [45525440883](https://github.com/TPollTech/Frontline-Survival/actions/runs/45525440883) Windows em validação. Não afirmar aprovação da nova luva sem resultado dos testes e inspeção de capturas posteriores. 00-13/21/24/25/27 permanecem parciais.


## Topologia contínua do personagem e auditoria de contatos

Preservados 8a616862 e a sincronização posterior e3a72580. [Windows 45525440883](https://github.com/TPollTech/Frontline-Survival/actions/runs/45525440883) aprovado (QA_ARSENAL_PASS). [Suíte 45525440788](https://github.com/TPollTech/Frontline-Survival/actions/runs/45525440788) passou geração estrita/reprodução e renderização Godot, ainda na etapa Studio. Nenhum artefato da revisão 73596b74 disponível na consulta; não houve inspeção efetiva das novas capturas, nem correção de defeitos baseada nelas. [Pages 45525440954](https://github.com/TPollTech/Frontline-Survival/actions/runs/45525440954) em testes de subrota, sem novo deploy confirmado. A última publicação confirmada continua aa303b81 (45520645718), 14 pilotos e 48 capturas. Consulta independente à URL não retornou conteúdo nesta sessão.

Commit f9b972da: `continuous_character.py` cria uma superfície autoral de patches ramificados (tronco, cabeça, braços em A, pernas e botas), frente/verso e perímetro fechado, envelope-alvo 0,98 × 1,80 × 0,33 m; uma malha, 15 ossos, três LODs autorais, atlas PBR de 512px (vestimenta, cinto, botas e trama procedural). Pesos regionais normalizados com transições suaves. As mãos do personagem são simplificadas e não incorporam o piloto de luva. Sem referência fotográfica nova, face detalhada, rig de dedos no personagem, IK ou retopologia de scan. Trata-se de um estudo de malha conectada, não aprovação artística. O teste verifica componente único, orientação/volume, característica de Euler 2, dimensões, orçamento, quatro poses por LOD e pesos.

`intersection_audit.py` verifica contato entre triângulos não adjacentes, com broad phase por células/AABB e eixos separadores (incluindo eixos coplanares), tolerância 1e-8 m. Testes sintéticos incluem cruzamento, sobreposição coplanar, separação coplanar e paralela. Ambos os rigs contínuos registram contagem, exemplos e pares testados em repouso e quatro poses de cada LOD. Pares com vértice de índice compartilhado são excluídos; o método não cobre todas as interseções adjacentes, poses entre amostras, contato com outros objetos ou distorção anatômica. Resultados não são gate de aprovação: contatos registrados precisam ser revisados/corrigidos antes de homologar; ausência de contatos não equivale a prova global. A auditoria não substitui revisão dos materiais e capturas. Não foi possível ler contagens reais ainda (logs/artefatos não disponíveis). 

CI [45526099663](https://github.com/TPollTech/Frontline-Survival/actions/runs/45526099663) avançou após testes unitários para geração estrita e comparação reproduzível; Godot/Studio pendentes. [Pages 45526099772](https://github.com/TPollTech/Frontline-Survival/actions/runs/45526099772) e [Windows 45526099997](https://github.com/TPollTech/Frontline-Survival/actions/runs/45526099997) em validação. Alterações isoladas em fontes QA, testes e workflow; não substituem os assets de produção. Checklist 00-24/25/27 continua parcial.


## Inspeção dos dois rigs contínuos e correção de contatos

Preservados 7f55e051 e 5ba3a63b (sincronização posterior de capturas). CIs 45525440788, 45525440954, 45526099663, 45526099772 e 45526099997 aprovados. Pages 45526099772 confirmou PAGES_QA_DEPLOY_PASS e PAGES_DEPLOY_PASS da revisão f9b972da375ce6543e38b9cdda76a8d10345cb15 por HTTP real pós-deploy. Studio 14 pilotos, 42 capturas de repouso, seis posadas. Windows QA_ARSENAL_PASS. Balizador 45526099786 também aprovado.

Artefato [14983295868](https://github.com/TPollTech/Frontline-Survival/actions/runs/45526099663/artifacts/14983295868) baixado; abertas oito capturas reais LOD0 de glove/mannequin repouso/pose, Godot e Studio. Luva: superfície contínua, pontas muito afiladas, painel de aderência circular simplificado, costuras com contraste forte; personagem: membros conectados, sem rosto detalhado, aparência de manequim, dobra de ombro pouco natural. Não homologar artisticamente.

Contagens extraídas de pilot-report.json (exports GLB, por LOD, não de rig agregado final):

| piloto | LOD | triângulos | repouso | quatro poses em ordem de relatório |
|---|---:|---:|---:|---|
| glove | 0 | 2844 | 0 | 0/0/0/0 |
| glove | 1 | 1496 | 0 | 0/0/0/0 |
| glove | 2 | 660 | 0 | 0/0/0/0 |
| mannequin | 0 | 2676 | 0 | 2/0/0/0 |
| mannequin | 1 | 1556 | 0 | 2/0/0/0 |
| mannequin | 2 | 768 | 0 | 0/0/0/0 |

Luva poses wrist 20°, finger_1_j1 45°, finger_2_j0 35°, thumb_j0 25°. Personagem arm_0_upper 25°, arm_1_lower 45°, leg_0_lower 35°, head 20°. Pares de faces do personagem LOD0 (1995,1998), (1998,2018), LOD1 (1051,1054), (1054,1066). Contatos no ombro esquerdo. Localmente, extraídos POSITION, indices, JOINTS_0, WEIGHTS_0 e inverseBindMatrices dos GLBs reais; reconstruída malha por posições coincidentes e aplicada LBS de 25° em arm_0_upper; auditoria independente SAT reproduziu exatamente os pares acima. Redução de metade do peso de braço nas faixas mistas do ombro eliminou contatos 2/2/0 para 0/0/0 no teste local. A simulação não substitui validação da nova exportação, nem mede outros estados intermediários.

Commit 1aba84b9 aplica a redução na primeira faixa da manga, arredonda pontas dos dedos (taper final .48 em vez de .34), melhora atlas de aderência, costuras, trama e normal map da luva; atlas do personagem ganha bolsos frontais, zíper, proteção ocular opaca e detalhes de vestimenta. São detalhes procedurais, não fotogrametria nem geometria de rosto. Gate exige zero contatos não adjacentes em repouso e quatro poses por LOD para ambos os rigs; teste unitário exige o mesmo. Isso não elimina limitações anteriores do detector (faces adjacentes, contato contínuo, outras poses). Sem novos pilotos ou alterações de produção.

Nova suíte [45528961593](https://github.com/TPollTech/Frontline-Survival/actions/runs/45528961593), Pages [45528961601](https://github.com/TPollTech/Frontline-Survival/actions/runs/45528961601), Windows [45528961629](https://github.com/TPollTech/Frontline-Survival/actions/runs/45528961629) em execução. Não afirmar aprovação da nova geometria, materiais ou publicação antes de confirmar testes e inspeção. Último deploy confirmado f9b972da; não houve verificação independente da URL nesta sessão. 00-13/24/25/27 parciais.


## Correção do ombro confirmada, poses combinadas e frente do atlas

Preservados fa2b7063 e 604e1821 (sincronização posterior das capturas). CI [45528961593](https://github.com/TPollTech/Frontline-Survival/actions/runs/45528961593) aprovado; geração reproduzível, 39 GLBs em Godot e Studio. Windows [45528961629](https://github.com/TPollTech/Frontline-Survival/actions/runs/45528961629) aprovado. Balizador 45528961605 aprovado. Artefato [14982624984](https://github.com/TPollTech/Frontline-Survival/actions/runs/45528961593/artifacts/14982624984) baixado. Abertas oito capturas reais LOD0 em repouso/pose, Godot/Studio. Luva: pontas arredondadas, painel de aderência retangular arredondado com estrias visíveis, costuras discretas; polegar simplificado. Personagem: ombro sem a interpenetração detectada anteriormente nas amostras; aparência ainda de manequim, cabeça/mãos genéricas, roupa de baixa complexidade. Zíper e bolsos apareciam na vista Studio +Z enquanto o Godot mostrava a face sem detalhes pela frente -Z. Fonte corrigida f93d7076, troca as ilhas frontais/traseiras do atlas sem alterar geometria ou rig e adiciona teste do mapeamento pelo índice da camada. Nova imagem não inspecionada ainda.

Relatórios pilot-report.json dos GLBs da revisão 1aba84b9 confirmam zero contatos em todos os repousos e quatro poses individuais por LOD: glove 2844/1496/660 triângulos; mannequin 2676/1556/768. Os quatro contatos do ombro anteriormente registrados (2/2/0) foram eliminados. Não significa ausência de contatos entre faces adjacentes nem em todos os movimentos.

### Poses combinadas

Análise local independente dos GLBs corrigidos: extração POSITION/indices/JOINTS_0/WEIGHTS_0/inverseBindMatrices e hierarquia, solda analítica por posição coincidente, reconstrução LBS com rotações locais X e auditoria SAT não adjacente (tolerância 1e-8 m). Três cenários de cada rig, quatro frações (25%, 50%, 75%, 100%), três LODs: 72 amostras, zero contatos. Razões de área de faces observadas:

| modelo | LOD | amostras | contatos | razão mín–máx |
|---|---:|---:|---:|---|
| glove | 0 | 12 | 0 | 0.62524–1.99120 |
| glove | 1 | 12 | 0 | 0.62398–2.29154 |
| glove | 2 | 12 | 0 | 0.62114–2.47548 |
| mannequin | 0 | 12 | 0 | 0.71075–1.41033 |
| mannequin | 1 | 12 | 0 | 0.50032–1.50026 |
| mannequin | 2 | 12 | 0 | 0.74156–1.22090 |

50579e2e integra `combined_pose_audit.py` em ambas as receitas e testes: três combinações por rig, 12 amostras/LOD, exige deslocamento, razão de área finita de 0.025 a 8 e zero contatos não adjacentes. Reporta ângulos, fração, áreas e contatos. Os limites são guardrails de degeneração grosseira, não limites anatômicos. Testes de CPU, não captura da animação combinada dentro do jogo. O workflow disponibiliza artefato antecipado de capturas Godot e relatórios dos rigs antes do teste mais demorado do navegador. CI 45529409669 passou testes unitários e geração reproduzível, chegou à renderização Godot; nova revisão UV f93d7076 em validação. Nenhum modelo novo nem mudanças de produção.

Pages [45528961601](https://github.com/TPollTech/Frontline-Survival/actions/runs/45528961601) ainda em teste de subrota ao registrar; 45529409639 cancelado por revisão posterior, [45529734340](https://github.com/TPollTech/Frontline-Survival/actions/runs/45529734340) pendente. Última publicação confirmada f9b972da, 45526099772. Não afirmar publicação da revisão corrigida nem homologação artística sem evidência. 00-21/24/25/27 parciais.

## Reteste integrado da fundação

Base `7a1d0f05a6c313826ad718b58ddd51f91e154ab6`, sem mudanças de gameplay ou Actions. Linux, Blender 4.3.2, Godot 4.4.1 Compatibility/llvmpipe e Firefox 135 com WebGL. A revisão Windows 95c7ac8 continua sendo a fonte das medições do cenário representativo em Ryzen 5 7520U, com 960 intervalos e 207 transições/24 contatos. A comparação Git não mostrou mudanças em scripts de produção, cenas, projeto ou assets até a base deste reteste. O hardware-alvo e metas finais continuam em 10-08.

- **00-24 e 00-25:** 13 categorias cobertas pela suíte, 39 GLBs e 39 glTFs nas três resoluções, com export estrito, orçamento provisório e contratos de escala, orientação, pivôs e hierarquia. Comparação byte a byte em dois diretórios. Godot importou/renderizou 39 GLBs. Studio conciliou SHA-256, contagem e envelope dos mesmos 39 arquivos. A suíte negativa glTF passou 17/17 e o contrato de checkout/caminhos Windows 2/2 em Linux. O reteste nativo Windows permanece distinto.
- **00-26 e 00-27:** mecanismo de CI já aprovado historicamente. Conferidas lado a lado as 26 vistas LOD0 das 13 categorias de geometria no Godot e Studio. O carro de utilidade é exclusivo de QA. O inventário de produção reconciliou 86 amostras, seis capturas, câmeras, materiais/texturas, áudio, efeitos/shaders e consultas pelos respectivos verificadores e fluxos de inspeção, com as limitações existentes de shader e física. Não é homologação artística.
- **00-28:** índice 8/31/7 e 10/10 testes Node aprovados. NumPy 2.2.6, trimesh 4.11.1 e SciPy 1.15.3. Duas reconstruções idênticas entre si e aos 31 GLBs em produção. Inspecionadas seis imagens Godot entre as 18 poses capturadas, incluindo repouso, ADS, recarga e movimento da peça do sniper, e composições correspondentes no Studio. Os 31 GLBs só trazem POSITION/COLOR_0 e o material de produção solicita normal map. A falta de tangentes continua afetando esse canal; corrigir com revisão de materiais e reconstrução a partir da fonte, com inspeção comparativa. Parcial.
- **00-29:** nas composições capturadas e reconstruídas, passaram superfícies visíveis, triângulos e transforms para mãos em três estados, soldado, runner, heavy, aliado e equipamento Quaternius. No Blender, importar o GLB CC0 rastreado e salvar como fonte de trabalho gerou cena editável com 65 ossos, três malhas ligadas à armature e uma auxiliar. Preservar o GLB original como referência imutável e validar nova exportação antes de substituir em produção. A deformação skinned da pose Godot ainda não é reproduzida na composição do Studio. Parcial.
- **00-30:** o contrato de receitas passou 13/13 no modo headless previsto. Mapa, estações, ambiente, loot, torreta e objeto arremessável foram conferidos pelo inventário e por reconstrução e inspeção no Studio. Contatos e colisores independentes têm cobertura na 00-10 e no piloto de colisão. Duas alocações de 349.524 bytes foram reportadas ao encerrar a sonda isolada de receitas executada também em GLES3; a sonda não renderiza a partida e o aviso não apareceu nas saídas da captura real. Este caso permanece registrado para investigar o ciclo de recursos em 10-02. Nenhum veículo de produção foi criado.
