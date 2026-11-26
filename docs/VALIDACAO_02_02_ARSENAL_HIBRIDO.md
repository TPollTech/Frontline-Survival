# 02-02 — Remodelar completamente o arsenal

26/11/2026. Base: `403fc35` (main, 02-01 concluído) + alterações desta entrega. Fonte canônica
editável: `tools/build_weapons.py`. Biblioteca central: `tools/asset_pipeline/parametric/organic.py`.
Complementa [padrão artístico híbrido](PADRAO_ARTISTICO_3D.md), [especificação do Studio](ASSET_STUDIO_SPEC.md)
e [critérios de aceite](CRITERIOS_ACEITE_1_0.md). Não promove homologação artística nem substitui o
portão de 13 passos; proporções, PBR, texturas e mãos continuam em 02-03 a 02-08.

## Escopo executado

As oito armas de produção foram remodeladas na fonte canônica aplicando a **regra híbrida** provada em
02-01: volumes maquinados (receiver, trilhos, canos, miras, carregadores, mobília pequena) permanecem nas
primitivas paramétricas; as superfícies orgânicas/esculpidas passam a ser geradas pela biblioteca central
(`OrganicLoft`) e convertidas para trimesh dentro da mesma assembleia, sem prévia paralela.

| Arma | Peças substituídas por `OrganicLoft` | Peças maquinadas preservadas |
|---|---|---|
| `weapon:pistol` | `grip` (receita 02-01, inalterada) | slide, slide_top, frame, dust_cover, sights, guarda |
| `weapon:smg` | `pistol_grip`, `foregrip` | receiver, handguard, coronha dobrável, óptica |
| `weapon:rifle` | `wood_stock`, `grip` | receiver, top_cover, wrist, butt_plate, handguards, ferrolho |
| `weapon:shotgun` | `pump_action`, `solid_stock`, `vertical_grip`, `pistol_grip` | receiver, canos, ribs, rubber_butt, mira |
| `weapon:lmg` | `heavy_stock`, `pistol_grip` | receiver, cooling_shroud, drum, bipé, óptica |
| `weapon:sniper` | `precision_stock`, `pistol_grip` | receiver, handguard free-float, cano, miras |
| `weapon:bolt_sniper` | `stock_body`, `cheek_rest`, `grip_stock` | receiver de aço, forearm, cano, miras, ferrolho |
| `weapon:sentinela` | `heavy_stock`, `lower_handguard`, `grip` | receiver tubular, cano, miras |

Contratos preservados: nomes de peça consumidos pelo código, agrupamento `body/mag/action` (23/22/2 na
pistola; 38/2/1 SMG; 39/2/1 rifle; 25/0/10 shotgun; 46/2/1 LMG; 33/2/1 sniper; 24/2/3 VLR-8; 11/1/1
Sentinela), pivôs, estados de animação, colisão independente e o envelope externo de cada arma.

## Extensão necessária da biblioteca central

`OrganicLoft` só gerava anéis elípticos: punhos funcionam, coronhas viram tubo. Foi adicionado
`section_power` (expoente de superelipse, `2 ≤ p ≤ 16`, padrão `2.0` = elipse histórica, resultado
byte-idêntico ao anterior). Com `p ≈ 3.2–3.6` a seção é um retângulo arredondado — lados planos e cantos
com filete — que é o que mobília maquinada/moldada exige, sem inventar geometria por peça. Teste dedicado:
`tests/test_parametric_organic.py::test_loft_superellipse_section` (fechado, determinístico, nunca excede a
caixa do anel, volume maior que a elipse inscrita).

Os helpers `hybrid_loft` (eixos Y/Z), `hybrid_grip` e `hybrid_stock` ficam em `tools/build_weapons.py` e
mantêm o mesmo `pos`/`angles` da peça substituída. `hybrid_stock` usa seções inscritas no envelope
(`≤ 0,5 · largura/altura`) e reproduz o *drop* da culatra via deslocamento de centro, para que sola,
chapa de recuo e punho continuem encontrando a superfície contra a qual foram modelados.

## Defeitos encontrados na inspeção e corrigidos na fonte

1. **Primeira revisão** — o pump da escopeta usava seções de até `0,78 · altura`, ultrapassando o envelope
   e engolindo tubo-carregador/cano na vista frontal; as coronhas usavam `waist = 0,40–0,48`, encolhendo a
   culatra e criando efeito "cogumelo" contra as borrachas/placas de recuo (LMG, sniper, VLR-8).
2. **Correção** — seções reinscritas no envelope (`0,80–1,00`), power 3,6 nas coronhas e 3,2 no pump.
3. **Segunda revisão** — as coronhas ficaram retas ("tubo"), perdendo o *drop* da fonte original.
4. **Correção final** — curva de centro `-0,12 h` (punho) a `+0,16 h` (culatra), restaurando o caimento do
   dorso sem mover planos de encaixe. Cada correção foi seguida de rebuild, recaptura e nova inspeção.

## Medições dos GLBs entregues

Três builds completos em sequência produziram os 31 GLBs byte a byte idênticos entre si e iguais aos de
`assets/models/` (`cmp` arquivo a arquivo, zero divergência). Todos fechados (`is_watertight`) e com volume
positivo; `validate_gltf` sem erros/avisos nos 31 arquivos.

| Arma | Triângulos (antes → depois) | AABB medida (X × Y × Z, m) | Desvio máx. de bounds |
|---|---:|---|---:|
| pistol | 3952 → 3952 | 0,1188 × 0,3875 × 0,3930 | 0,0 mm |
| smg | 2516 → 4796 | 0,2800 × 0,6415 × 1,2785 | 0,0 mm |
| rifle | 4634 → 6914 | 0,1865 × 0,6417 × 1,7335 | 0,0 mm |
| shotgun | 2104 → 6472 | 0,2340 × 0,4665 × 1,9775 | 0,6 mm |
| lmg | 2964 → 5244 | 0,4299 × 0,7800 × 1,9855 | 0,0 mm |
| sniper | 2220 → 4500 | 0,3532 × 0,6223 × 2,3125 | 0,0 mm |
| bolt_sniper | 1808 → 5228 | 0,2905 × 0,5185 × 2,3860 | 0,0 mm |
| sentinela | 896 → 4316 | 0,1683 × 0,3800 × 1,7875 | 1,1 mm |

Maior arma: 6914 triângulos = 38,4% do teto provisório LOD0 de 18 000. Prisma de contato medido por
distância vértice-a-vértice contra o HEAD: todas as peças esculpidas ficaram **mais próximas** dos vizinhos
(por exemplo `sniper/precision_stock` 26,6 mm → 8,4 mm; `lmg/heavy_stock` 30,2 mm → 4,5 mm;
`shotgun/vertical_grip` 65,1 mm → 1,7 mm), ou seja, nenhuma peça se soltou. Envelope idêntico é o contrato
de integração (enquadramento do viewmodel, recorte de parede, alinhamento de miras) e agora é garantido por
`tests/test_hybrid_arsenal.py`.

## Verificações executadas

| Verificação | Resultado |
|---|---|
| `tests.test_hybrid_arsenal` | 4/4 (peças esculpidas presentes, sólidos fechados, envelope ≤ 2 mm, teto de triângulos) |
| `tests.test_hybrid_grip` | 6/6 |
| `tests.test_parametric_organic` | 15/15 (2 skipped por backend Blender ausente), inclui superelipse |
| `tests.test_parametric_library/advanced/export` | verdes |
| `tests.test_weapon_surface_integrity` | 7/7 |
| `tests.test_live_catalog` / `test_validate_gltf` | 19/19 e 17/17 |
| `tests.test_arsenal_qa_contract`, `test_player_weapon_contract`, `test_sniper_sight_geometry` | verdes |
| `tools.asset_pipeline.validate_gltf assets/models/*.glb` | 31/31 sem erros ou avisos |
| `tools.asset_pipeline.live_catalog` | `LIVE_CATALOG_PASS`, 52 assets, 8 armas, 100 recursos |
| Determinismo | 31/31 idênticos entre builds e iguais à árvore |

**Falha pré-existente, não mascarada**: `tests.test_sniper_contract::test_model_generator_exports_sniper_with_mechanical_parts`
exige a string literal `shotgun();lmg();sniper()` no gerador. Essa chamada foi substituída pelo bloco
`RECIPES`/`--only` antes desta entrega; o teste falha igualmente num worktree limpo em `403fc35`
(reproduzido nesta sessão). Não foi alterado para não enfraquecer a suíte dentro deste ID.

## Inspeção real — Asset Studio (WebGL)

Staging oficial (`tools.asset_studio.prepare`) servido em loopback, sem CDN. `before` = GLBs de `403fc35`
em worktree separado; `after` = GLBs desta revisão. O Studio valida SHA-256 do catálogo e **recusou** o
staging quando os GLBs foram substituídos sem restage (`Falha: Hash divergente`), o que confirma que a
inspeção usou os arquivos reais.

- 8 armas × 6 vistas (perspectiva, direita, esquerda, superior, frontal, traseira) = 48 capturas da revisão
  entregue; 16 capturas do estado anterior nas vistas comparáveis.
- `after-report.json` / `before-report.json`: `external: []`, `errors: []`, hash por arma registrado.
- Inspeção adicional no navegador compartilhado com zoom de 3× sobre `weapon:shotgun` (direita e esquerda):
  emenda pump↔receiver encostada, sem fresta; coronha encontrando a chapa de recuo; nenhuma peça flutuante.
- Página de evidência: [qa/02-02/arsenal.html](qa/02-02/arsenal.html) (comparativo, 6 vistas, recortes 2×,
  métricas e as 24 poses do Godot).

## Inspeção real — Godot

Godot **4.7.2.stable** (única build disponível neste ambiente; 02-01 foi inspecionado em 4.4.1), renderizador
Compatibility, OpenGL 3.3 Core, AMD Radeon iGPU, 1280×720. Cópia isolada do projeto em diretório temporário
para não sujar o checkout; `--import` concluído antes da captura.

`tests/arsenal_viewmodel_qa.gd` instancia a cena real de jogo, percorre as oito armas e captura repouso, ADS
e recarga na viewport real (24 células, `docs/qa/02-02/godot-arsenal.png`, posições de viewmodel e FOV em
`godot-arsenal.json`, log em `godot-log.txt`). Resultado: armas na mão do jogador, miras alinhadas no ADS,
recarga com a arma girada e carregador destacado, sem peças soltas, frestas ou transparências.

O `project.godot` do checkout foi reescrito automaticamente para `4.7` ao abrir o editor nesta máquina; a
alteração **não** foi incluída no commit (o projeto continua declarando 4.0/GL Compatibility).

## Bloqueios e limites declarados

- Proporções estilizadas e conferência dimensional contra referências seguem em **02-03**; nenhuma
  homologação artística é declarada aqui.
- Materiais PBR de produção e texturas/normal maps autorais: **02-04 / 02-05**. O que foi visto é o
  StandardMaterial3D atual do jogo com projeção triplanar.
- Mãos, dedos, luvas e encaixe de empunhadura: **02-06 / 02-08**.
- ZIP Windows não gerado: templates de exportação ausentes nesta máquina; CI segue sem cota (`[skip ci]`).
- Sem benchmark de hardware-alvo (pertence a **10-08**).
- A inspeção Godot rodou em 4.7.2, não na 4.4.1 da entrega anterior; a diferença de versão está registrada.
