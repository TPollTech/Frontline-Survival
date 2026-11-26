# 02-01 — execução do padrão híbrido no pistol de produção

26/11/2026. Escopo exclusivo: **02-01 — Desenvolver um padrão híbrido de modelagem 3D**. Base preservada: `4f3eefcec318acc5c1145ca14cefeb64d6e5385f`. O padrão normativo está em [PADRAO_ARTISTICO_3D.md](PADRAO_ARTISTICO_3D.md); este relatório registra a demonstração no asset de produção `weapon:pistol` no Asset Studio e no Godot. Nenhum outro ID foi promovido. Auditorias anteriores (rifle, texturas isoladas, fundação) foram preservadas sem reescrita.

## Ambiente realmente executado

| Item | Valor |
|---|---|
| Sistema | Windows, checkout local `C:\Projetos git\Frontline-Survival` |
| Python | 3.11.9 em venv temporário |
| Dependências fixadas do repositório | numpy 2.2.6, trimesh 4.11.1, scipy 1.15.3, Pillow 12.3.0 |
| Node / Playwright / Three.js | Node 24.13.1, Playwright 1.51.1, Three.js 0.170.0 |
| Navegador | Chromium headless com SwiftShader WebGL2 (`--use-angle=swiftshader --enable-unsafe-swiftshader`) |
| Godot | 4.4.1-stable official (49a5bc7b6), Compatibility/OpenGL 3.3, AMD Radeon iGPU |
| CI | **não disparado** — GitHub Actions sem cota; entrega com `[skip ci]` |
| Exportação Windows | **bloqueada** — templates de exportação 4.4.1 ausentes no perfil; ver limites |

## Alterações no projeto

| Arquivo | Natureza |
|---|---|
| `tools/build_weapons.py` | Fonte canônica única: novo `hybrid_pistol_grip()` usando `OrganicLoft`/`LoftSection`/`build_organic` da biblioteca central; `Gun.add_parametric()` converte a IR sem reprocessar vértices e recusa malha aberta/volume ≤ 0; CLI `--only`/`--out` para gerar um asset e comparar duas gerações fora do checkout. Nenhuma outra receita de arma alterada. |
| `assets/models/pistol.glb`, `pistol_body.glb`, `pistol_action.glb`, `pistol_mag.glb` | Reexportados da fonte acima. O punho é a única mudança de geometria. |
| `tests/test_hybrid_grip.py` | Regressão focal: loft da biblioteca, solidez, grupos, contatos frame/heel, envelope, orçamento, atributos NORMAL/TANGENT e determinismo. |
| `tools/asset_studio/hybrid_pistol_capture.mjs` | Captura focal do Studio real para este ID (vistas + wireframe/sólido, hash do arquivo carregado, bloqueio de rede externa). |
| `docs/qa/02-01/` | Capturas, folhas comparativas, relatórios do Studio e `validate_gltf`, métricas e hashes. |

## Comandos e resultados

Todos os comandos abaixo foram executados nesta revisão; caminhos temporários fora do checkout.

```text
python tools/build_weapons.py --only pistol --out <tmp-a>      -> 47 peças, 139884 bytes
python tools/build_weapons.py --only pistol --out <tmp-b>      -> idêntico
sha256 (4 GLBs)                                                 -> 4/4 idênticos entre gerações
python -m tools.asset_pipeline.validate_gltf --root <tmp-a> \
  --file pistol.glb --category weapon --output ...             -> pass_with_unknowns; 0 erros, 0 avisos
python -m unittest discover -s tests -p test_hybrid_grip.py    -> 6 testes OK
python -m unittest discover -s tests -p test_weapon_surface_integrity.py -> 7 testes OK
python -m unittest discover -s tests -p test_sniper_sight_geometry.py    -> 3 testes OK
python -m unittest discover -s tests -p test_validate_gltf.py            -> 17 testes OK
python tools/asset_studio/prepare.py <stage>                    -> STUDIO_STAGE_PASS 52 assets/100 recursos
node hybrid_pistol_capture.mjs (porta 8811)                    -> 6 capturas, 0 requisições externas, 0 erros
godot --path . --editor --import                                -> importação OK (OpenGL 3.3)
godot --path . --script res://tests/tmp_pistol_capture.gd       -> QA_02_01_PISTOL_PASS (3 poses 1280x720)
```

Os testes Python não estavam disponíveis no Python do sistema (trimesh ausente); a venv temporária foi criada apenas com as versões já fixadas pelos workflows do repositório. Nenhum runner ou instalador novo foi adicionado ao projeto.

### Números medidos

| Métrica | HEAD | Entregue |
|---|---:|---:|
| Peças / grupos | 47 / 23-22-2 | 47 / 23-22-2 |
| Vértices / triângulos | 1498 / 2812 | 2068 / 3952 |
| Punho (vértices / triângulos) | 32 / 60 | 602 / 1200 |
| AABB X × Y × Z (m) | 0,1188 × 0,3875 × 0,3965 | 0,1188 × 0,3875 × 0,3930 |
| Contato punho↔frame / punho↔heel | sim / sim | sim / sim |
| Triângulos / teto LOD0 weapon | 15,6% | 22,0% (3952/18000) |
| Slots de material | 1 | 1 |
| Atributos | POSITION, COLOR_0, NORMAL, TANGENT | idem |

Hashes entregues: ver `docs/qa/02-01/metrics.json` e `docs/qa/02-01/validate-gltf-weapon.json`.

## Inspeção visual efetiva

**Asset Studio (WebGL real).** O Studio foi montado com os recursos reais da revisão e aberto por Playwright. O painel confirmou o arquivo `assets/models/pistol.glb`, SHA-256 `a9823dd41d4adc91206d2cd3d3f2cbfa90ffd4651b032ea8ec535ef9d1a3bcdd`, 2068 vértices/3952 triângulos, 1 material/slot e AABB 0,1188 × 0,3875 × 0,393. Vistas perspectiva, frontal, direita, superior, wireframe e sólido comparadas antes/depois em [comparativa.html](qa/02-01/comparativa.html). Observações: o punho deixou de ser uma caixa octogonal facetada visível e passou a uma superfície contínua com palm swell e backstrap arredondado; as serrilhas continuam assentadas; não há peça solta nem transparência.

**Godot 4.4.1 Compatibility.** `scenes/main.tscn` real, câmera do jogador, 1280×720, renderer opengl3. Poses repouso, ADS e recarga a 50% capturadas antes/depois em [godot.html](qa/02-01/godot.html). Observações: sem fresta entre punho e frame/base do carregador, sem peça flutuante e sem recorte relevante da arma; mira e empunhadura preservadas; recarga continua separando o carregador. As capturas foram abertas e conferidas nesta sessão; a folha comparativa e os recortes fazem parte da entrega.

Inspeção: agente Buffy, 26/11/2026, sobre as capturas desta revisão (não sobre evidência histórica). Nenhuma correção adicional foi necessária após a inspeção; a correção de proporções de silhueta pertence ao 02-03 e está registrada como débito.

## Limites e débitos

- Demonstra o padrão em **um** asset de produção. As oito armas permanecem em **02-02**; proporções/silhuetas em **02-03**; materiais PBR autorais em **02-04**; texturas/normal maps próprios em **02-05**.
- Nenhuma homologação dimensional: o viewmodel usa escala de apresentação 0,95 em `player.gd`; a razão com a referência GLOCK G19 não atende à tolerância de 5% e está atribuída ao 02-03.
- Não foram autorados LOD1/LOD2 nem colisores para o punho; o teto de 18000 triângulos é provisório e não substitui o benchmark do 10-08.
- A revisão cobre repouso, ADS e recarga do pistol; não cobre demais armas, acessórios, mãos/rig, troca de arma ou gameplay.
- **ZIP Windows não gerado**: o binário de exportação 4.4.1 não está instalado no perfil (erro “No export template found”) e o CI está sem cota. A entrega não afirma executável validado; isso permanece no 10-10.
- Nenhuma execução de CI, benchmark ou Blender nesta sessão.

## Verificações pós-commit (`edc903b`)

| Verificação | Resultado |
|---|---|
| `node --test tests/test_arsenal_sources.mjs` | 9/10 — cobertura 8/31/7, índice determinístico e rejeições OK; a CLI de proveniência falhou |
| `python -m unittest tests/test_live_catalog.py` | 19/19 OK |
| `validate_gltf` em produção (32 GLBs) | 32/32 `pass_with_unknowns`, 0 erros; pistol sem avisos, 3952 triângulos |
| Regeração do painel (`tools/generate_checklist_panel.py`) | idêntica; arquivo sem diff após o commit |
| `git rev-parse origin/main` | `edc903b32cfb1a2eb12246982df9eb8c6de3634c`, igual ao HEAD local |

A CLI `arsenal_sources.mjs` falha neste checkout Windows ao comparar blobs: `core.autocrlf=true` faz arquivos de texto do worktree (por exemplo `scripts/weapon_materials.gd`) terem CRLF, enquanto o blob do HEAD é LF; o erro é “Source/output drift from HEAD”. O mesmo efeito já impede `build_manifest.mjs` de comparar o manifesto nesse checkout. As nove verificações de `collectArsenal` passam e o problema é de ambiente, não do asset; a execução canônica permanece em Linux/CI. Nenhum ajuste de EOL ou do repositório foi feito neste ID.

O script de captura Godot (`res://tests/tmp_pistol_capture.gd`) foi uma sonda temporária na worktree isolada e não foi integrado, para não criar runner redundante; o script de captura do Studio foi integrado por ser reutilizável. A worktree foi removida após as capturas.

## Decisão

Os portões do 02-01 (referências, escala declarada, silhueta, detalhes, materiais, exportação determinística, verificações focadas, Studio real, inspeção, Godot real, registro de evidências) foram demonstrados no pistol de produção. **02-01 aceito** com os débitos acima atribuídos a IDs posteriores. Nenhum outro ID promovido.
