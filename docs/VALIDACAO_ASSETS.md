# Validação técnica de assets — 00-23 a 00-26

24/11/2026. Validador de leitura dos arquivos originais, sem modificar fontes, modelos ou gameplay. Catálogo vivo determina os GLBs/glTFs; o manifesto histórico permanece imutável. Preservado o commit 0305d713 de sincronização de assets.

## Comandos

```sh
python -m unittest discover -s tests -p 'test_validate_gltf.py' -v
python -m tools.asset_pipeline.validate_gltf --output /tmp/production-report.json
python -m tools.asset_pipeline.parametric.export_fixture /tmp/frontline-fixture REVISION
python -m tools.asset_pipeline.validate_gltf --root /tmp/frontline-fixture --source-root . --strict --category object --contract tools/asset_pipeline/parametric/export_fixture_contract.json --file asset.glb --file asset.gltf --output /tmp/fixture-report.json
```

O modo padrão registra avisos de legado e retorna erro para falhas impeditivas. --audit-only permite gerar evidência mesmo quando o arquivo falha; CI exige reconciliação posterior sem falhas impeditivas. --strict exige fonte rastreada, normais, materiais e limites provisórios; não afirma homologação visual. --contract informa unidade, eixo, dimensões, pivôs locais e uma direção de referência de nó; fixture demonstra contrato positivo e erros de dimensão, pivô e direção. Não inferir contratos de arquivos legados.

## Escopo dos verificadores

- GLB v2 header, chunks, tamanhos, buffers e strides; glTF JSON e URIs locais/base64. Atributos finitos, índices, contagem, bounds de POSITION, degeneração, normais unitárias e oposição ao winding, tangentes, UVs e canais exigidos pelo material; PBR e referências/texturas. Assinatura e MIME de imagem não equivalem à decodificação completa.
- Matriz afim/TRS, singularidade, quaternion, hierarquia acíclica e pai único, roots, referências de skin/animation, AABB de vértices em repouso com transforms de mundo, escala, pivôs e direção quando há contrato autoral. Não valida dimensões físicas sem contrato nem deformações dinâmicas. Normais globalmente invertidas, UV overlap e distorção, extensões/sparse, shaders e topologias não triangulares não são integralmente validados.
- Proveniência por SHA-256 de fonte, limites provisórios LOD0 e slots por arquivo/categoria. Variantes de arsenal não são somadas como se fossem instâncias simultâneas; não equivale a orçamento da composição real, benchmark ou aprovação dos LODs.
- Godot 4.4.1: GLTFDocument carrega os originais e mede triângulos. FileAccess.get_sha256 mede os bytes independentes. reconcile_validation.py exige mesma revisão, cobertura, hash e contagem quando ambas conhecidas. Registra desconhecidos e avisos; erros estáticos, importações inválidas, referências literais faltantes e divergências impedem o CI. O teste adicional da fixture confirma skin, tangentes, UV, material e juntas em GLB e glTF.
- Workflow .github/workflows/asset-validation.yml executa testes, gera dois bundles idênticos, valida contrato da fixture, reproduz relatório de produção byte a byte e publica relatórios/logs inclusive em falha. Não substitui Studio/renderização manual; aprovação visual sempre false.

## Evidências

[CI 45511716190](https://github.com/TPollTech/Frontline-Survival/actions/runs/45511716190), revisão d4e9a126: 17/17 testes; 2/2 exportações estritas aprovadas; 32 GLBs auditados, 31 com aviso NORMAL_MISSING e 1 sem aviso, mas com desconhecidos; zero erros estáticos impeditivos. Godot importou 32/32; 32/32 contagens coincidentes e hash independente, zero hard_failures. Fixture GLB/glTF também importada com verificação de atributos. A falta de normais autorais em 31 arquivos pode impactar sombreamento, mas não é diagnóstico visual de todos os defeitos. Corrigir fontes durante a migração, sem modificar silenciosamente binários.

CI anterior [45504785180](https://github.com/TPollTech/Frontline-Survival/actions/runs/45504785180): 86 amostras runtime, 32 GLBs e cinco capturas, inspeção e ZIP offline aprovados. [45504785421](https://github.com/TPollTech/Frontline-Survival/actions/runs/45504785421) corrigiu a falha histórica do arsenal, oito armas aprovadas (249 verificações individuais; uma verificação adicional da cobertura do registro). A revisão 0305d713 mudou modelos depois desse CI. Novo Windows [45511716282](https://github.com/TPollTech/Frontline-Survival/actions/runs/45511716282) e Studio [45511716406](https://github.com/TPollTech/Frontline-Survival/actions/runs/45511716406) ainda em validação ao registrar. Não se declara nova release ou homologação artística.

00-23 e 00-26: fundações técnicas concluídas no escopo suportado. 00-24 e 00-25: parciais até contratos físicos/semânticos de produção, orçamentos agregados e benchmark. As tarefas de migração, cobertura de composições e homologação não são promovidas.


## Primeiro piloto canônico

[Windows 45511716282](https://github.com/TPollTech/Frontline-Survival/actions/runs/45511716282) e [Studio 45511716406](https://github.com/TPollTech/Frontline-Survival/actions/runs/45511716406) concluídos com sucesso. O primeiro piloto autoral, com contrato físico e orçamento agregado por instância/LOD, foi acrescentado; consulte [PILOTOS_ASSETS.md](PILOTOS_ASSETS.md). A validação estrita das seis exportações e a reprodução byte a byte passaram no CI 45514843046; execução Godot/Studio pendente ao registrar.


## Expansão 00-27

O CI 45514843046 concluiu balizador 3/3 Godot/Studio, colisor invariável e equivalência de hashes, triângulos e dimensões. Nove novos conceitos em piloto_suite.py validaram seis exports estritos por asset, com contrato físico baseado em envelopes autorais e budget por LOD no CI 45516214029; Godot/Studio ainda em validação. Ver [PILOTOS_ASSETS.md](PILOTOS_ASSETS.md). Sem alteração dos modelos de produção.


## Revisão de acabamento e cobertura

CIs 45516709723/45516709742 aprovados: 84 exports determinísticos, 42 GLBs conferidos Godot/Studio, 14 pilotos em 13 categorias geométricas. Inspeção real de capturas LOD0 revelou sobreposição, encaixes e posicionamento inadequados; correções posteriores em revalidação. Ver [PILOTOS_ASSETS.md](PILOTOS_ASSETS.md). Sem homologação artística.


## Revisão artística Blender

14 pilotos / 13 categorias geométricas, 42 GLBs aprovados na revisão bfc367a8; nova arte de três pilotos via BlenderBackend, contratos e reprodução em revalidação. Publicação QA corrigida após HTTP 404 de metadados HDRI. Evidências, referências e limites em [PILOTOS_ASSETS.md](PILOTOS_ASSETS.md).


## Rigging dos pilotos

CIs 45518029777 e 45518280679 aprovados. Artefatos inspecionados de estação, abrigo e veículo; correções de orientação e novas cadeias de ossos skinned nos pilotos glove/mannequin. Geração estrita e importação Godot na revisão c7f4d83e passaram; validação de poses e publicação em andamento. Ver [PILOTOS_ASSETS.md](PILOTOS_ASSETS.md).


## Publicação e poses

Pages 45518280483 publicou QA 0aed750b com HTTP pós-deploy confirmado. CIs 45519485851/45519577840 aprovaram seis LODs skinned e controles de pose em Godot/Studio. Capturas inspecionadas, orientação do veículo confirmada; refinamento de encaixes e pesos em aa303b81 ainda em revalidação. Ver [PILOTOS_ASSETS.md](PILOTOS_ASSETS.md).


## Superfície contínua QA

CI 45520645718 confirmou 42 capturas em repouso e seis posadas publicadas. Revisão real de imagens aa303b81; nova luva com superfície fechada única, atlas UV/PBR e testes de deformação em 73596b74, CI 45525440788 em execução. Ver [PILOTOS_ASSETS.md](PILOTOS_ASSETS.md). Sem homologação artística.


## Contatos e personagem contínuo

45525440788 passou geração e Godot, Studio pendente; 45525440883 Windows aprovado. f9b972da cria personagem contínuo e auditoria determinística de contatos não adjacentes em repouso e poses nos dois rigs. Testes unitários passaram; exportação e resultados de contatos em 45526099663 pendentes. Sem aprovação visual. Ver [PILOTOS_ASSETS.md](PILOTOS_ASSETS.md).


## Contatos dos rigs contínuos e revisão visual

45526099663/45526099772 aprovados, capturas reais abertas. Repouso zero contatos; luva zero em quatro poses nos três LODs, personagem 2/2/0 no ombro. Simulação independente dos GLBs confirmou correção 0/0/0; 1aba84b9 aplica pesos e gate, refina pontas e materiais. CI 45528961593 em validação. Ver [PILOTOS_ASSETS.md](PILOTOS_ASSETS.md).


## Confirmação dos rigs corrigidos

45528961593 e Windows 45528961629 aprovados; capturas reais 1aba84b9 inspecionadas. Zero contatos em repouso e quatro poses por LOD dos dois rigs; 72 amostras combinadas dos GLBs aprovadas em análise independente. 50579e2e incorpora os testes; f93d7076 corrige orientação UV frontal. Publicação atual e inspeção posterior pendentes. Ver [PILOTOS_ASSETS.md](PILOTOS_ASSETS.md).


## LOD real de barricadas — 00-10

CI 45534922543 aprovado, 36 transições/rays, quatro bloqueadores independentes, três capturas reais inspecionadas. Ver [relatório](LOD_COLISOES_RUNTIME.md). Sem homologação de desempenho.
