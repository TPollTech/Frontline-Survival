# 01-06 — Integridade visual das peças

26/11/2026. Base 2a9a97900bafd11c81cee2831987854512fd50d1. Escopo exclusivo 01-06. Critério: inspecionar armas/partes móveis em estados relevantes e corrigir transparências, sobreposições ou peças soltas indevidas.

## Arquivos atuais

Leitura dos oito GLBs completos diretamente pela API GitHub em base64, validação GLB 2.0/chunks e accessors POSITION/COLOR_0/índices em V8. Posições finitas, índices válidos, alpha integral quando presente, área de cada triângulo superior a 1e-12 m², zero faces duplicadas por assinatura de posições arredondadas a 1e-7 m independentemente da ordem, cada aresta indexada presente duas vezes com orientações opostas. Verificações de topologia não equivalem a ausência de interseções ou peças desconectadas espacialmente.

| GLB | Vértices | Triângulos | Blob Git |
|---|---:|---:|---|
| pistol | 1498 | 2812 | 9c4d400dd6a7224380b25b17fbe678d5e46140ab |
| smg | 1336 | 2516 | e0a94cbf5c09b267ed926898c7021333ef6a2b8d |
| rifle | 2459 | 4634 | 20497430e50b2a1333377a4443a60128d83d110b |
| shotgun | 1120 | 2104 | b6a21fe35e6e55e316d468d7647b9b8b4948b671 |
| lmg | 1576 | 2964 | e97d5cadb6b1257dde95b973771902de66bb8f84 |
| sentinela | 472 | 896 | d672fe0f3f7ab0c293f6ef3ee9f7deec2daa148d |
| sniper | 1180 | 2220 | 8abe49549fd2e659369975889e8fe8e70ec5f5d2 |
| bolt_sniper | 960 | 1808 | 9228554f776c28ce4c472be4b9c92c8bd7b5a8ec |

Total 10.601 vértices, 19.954 triângulos; todos os oito passaram nas verificações descritas. Não foram medidas interpenetrações não coincidentes ou contato entre sólidos. A tentativa adicional de conciliar as 23 partes atuais com os oito GLBs completos foi interrompida pelo limite de chamadas Code Mode, sem resultado integral retornado. Não declarar 31/31 testados nesta sessão.

## Captura anterior real

Python/NumPy, evidence.zip/inventory/runtime_inventory.json, revisão 95c7ac8c0b32c7c5723ab33cb7a2d4dd29d52968, SHA-256 51f663f01b7dc142de276d92e8a7046c094c3cb758e6979b8a3d74358e5ad4bb conferido contra manifesto sha256.json. 57 amostras fps_, 164 registros de superfícies visíveis em Viewmodel/body, action, mag (57/57/50; escopeta sem mag separado), 23 buffers únicos. Decodificados position/index/color quando presente, conferidos tamanhos e hashes, contagens de vértices e triângulos, índices e posições finitas. Materiais efetivos todos com transparency=0 e alpha=1; cores de vértices, quando presentes, alpha=1. 140.574 instâncias de triângulos nas poses; aplicação das matrizes world em coluna, coordenadas arredondadas a 1e-6 m, assinatura de triângulos independente da ordem. Zero duplicatas pelas assinaturas dentro de cada pose, zero coincidências entre os três grupos. Não mede sobreposição parcial ou interferência volumétrica. Entre as superfícies de acessórios visíveis, 13 registros ópticos têm transparency=1 e albedo alpha=0,16, coerentes com lente intencional; demais 142 registros de ópticas e 16 de muzzle opacos. Não alterar lentes nem encaixes intencionais para satisfazer métrica.

Três imagens reais históricas abertas e inspecionadas, hashes conferidos: views/fps.png (pistola, 5f8a0ab5a603efa97baa9281d7702505543f7829cf2c10dfda6d3ce59ca03537), inventory/fps_rifle_ads.png (3fab6db550d24b6a17a5f255073ea5b37bf88a2cdb0558bd761b78fb1238a7f5), inventory/enemy_rifle.png (72a927622af3c44e97772ead40040004b9f20973c8aff91826f5b66bd2b49c3a). Corpos aparecem sólidos nas áreas visíveis, sem transparência evidente nessas três imagens; não permitem concluir sobre partes ocultas, qualidade artística ou animações. Comparação Git 95c7ac8..2a9a97900bafd11c81cee2831987854512fd50d1: ancestral, scripts/, scenes/ e project.godot inalterados, 31 GLBs modificados; não atribuir captura antiga à revisão atual.

## Decisão

docs/releases/v0.9.33.md registra reparo dos contatos de SMG/LMG, rifle, escopeta e ópticas, preservando encaixes e transparências intencionais. Gerador canônico tools/build_weapons.py já valida sólidos (volume, orientação, faces, alpha, duplicatas) e scripts/weapon_materials.gd aplica material opaco. Não foi encontrada falha nas verificações executadas que justifique editar modelos. Godot/godot4 não localizado no PATH; não houve execução atual do jogo, teste de recarga animada, geração de novos GLBs ou captura atual. Manter 01-06 parcial: conferir partes atuais e inspeção das oito armas em estados relevantes, incluindo interpenetrações e peças soltas, com testes existentes de enquadramento/miras/poses de ação. Não repetir fundação nem publicar alterações não testadas. Nenhum código, modelo, workflow, instalador ou runner alterado. Entrega documental, sem export Windows ou Actions.
