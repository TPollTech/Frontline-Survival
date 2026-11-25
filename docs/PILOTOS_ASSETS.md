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
