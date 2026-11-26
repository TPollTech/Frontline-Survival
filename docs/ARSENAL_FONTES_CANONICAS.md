# 00-28 — Migração do arsenal e acessórios para fontes canônicas

Data: 25/11/2026. Base preservada: [4b732acb](https://github.com/TPollTech/Frontline-Survival/commit/4b732acb701303bb412f1a45d7b16034cc438d94). Estado: **parcial**. Escopo exclusivamente 00-28; nenhum recurso visual ou script de gameplay substituído.

## Primeira fase: indexar as fontes que já produzem os recursos reais

- Oito IDs de armas do dicionário WEAPONS correspondem aos oito IDs históricos do manifesto; 31 GLBs (8 merged, 8 body, 8 action, 7 mag). Shotgun não possui mag separado, por contrato preexistente.
- Fonte editável existente: tools/build_weapons.py. O novo índice liga cada ID e cada variante à função geradora, ao caminho original e ao Git blob SHA-1 atual. Não existe novo modelo de preview, mudança de escala ou substituição de GLB.
- Sete acessórios (red_dot, holo, scope4, scope_2x, scope_4x, suppressor, compensator) permanecem nos procedimentos reais de scripts/player.gd, incluindo as dependências de montagem e material. Não inventar GLB independente para esses acessórios. Compatibilidade, estado e transformações específicas de cada arma continuam na engine.
- Seis arquivos fonte/dependências são vinculados por hash. A baseline histórica não foi editada. A comparação GitHub entre 5b47000 e 4b732acb retornou 136 caminhos modificados, dos quais 12 GLBs de armas; os 12 blobs atuais foram consultados individualmente. Os outros 19 GLBs do arsenal mantêm identificadores históricos segundo a comparação, não foram baixados individualmente nesta etapa.

## Ferramentas

`tools/asset_pipeline/arsenal_sources.mjs` exporta o coletor de contratos e uma CLI em Node 22. A CLI calcula hashes Git de arquivos reais, verifica o conjunto rastreado, rejeita divergência de HEAD, fontes e variantes faltantes ou IDs extras, e gera JSON fora do checkout. A extração das declarações GDScript e Python é heurística, não um parser semântico. Não prova cobertura dinâmica arbitrária.

```sh
node --test tests/test_arsenal_sources.mjs
node tools/asset_pipeline/arsenal_sources.mjs /tmp/arsenal-source-index.json
node tools/asset_pipeline/arsenal_sources.mjs /tmp/arsenal-reproduction.json --rebuild python
```

O terceiro comando executa a receita existente duas vezes em diretórios temporários distintos, nunca sobre assets de produção. Exige dependências Python previamente instaladas; compara os conjuntos de saídas e hashes Git blob com os originais e entre as duas execuções. Divergência falha o comando e é registrada. O workflow Arsenal source provenance roda a regressão/CLI no push e permite a tentativa opcional de reprodução manual com versões candidatas explícitas (não afirmadas como ambiente original).

## Evidências e limites

- 9/9 verificações da função collectArsenal passaram no runtime JavaScript conectado ao GitHub, usando manifesto e fontes reais da revisão base, mais os hashes da comparação acima: cobertura 8/31/7, repetição determinística, ausência de output, output extra, ausência de fonte, ausência de receita, mudança de acessório, papel de variante incorreto, ausência de promoção visual. A primeira tentativa falhou por incluir weapon_id na extração do guard; o limite de palavra foi corrigido e os nove testes passaram.
- O arquivo Node de regressão inclui uma décima verificação de CLI; suíte Node em checkout e execução do novo workflow ainda não confirmadas. Rebuild de produção, Godot, Blender, Studio e capturas novas não foram executados neste ambiente (DNS bloqueou clone; Godot/Blender ausentes). Não confundir hash/registro com igualdade geométrica comprovada.
- Commits: b33ca5a (coletor), 2f0def3 (proteção de proveniência), dfcd26e (regressões), 4b7be8e (CI). Nenhuma alteração de GLB, texturas, gameplay, versão de jogo ou pacote Windows.
- Faltam: confirmar CI e reprodução determinística efetiva dos 31 GLBs; migrar receitas legadas ao motor central ou adaptador validado; incorporar índice gerado ao catálogo vivo/Studio sem duplicar geometria; comprovar composições reais dos sete acessórios, materiais, transforms e paridade no Godot; inspeção visual individual em repouso, ADS, recarga e acessórios, orçamento/benchmark e homologação. Não remover legado antes da paridade.

Não declarar concluída a tarefa 00-28.


## 00-28 — Diagnóstico do canal normal e candidato isolado (25/11/2026)

Base 2957adf4776e4756284d3210ac9606a35a91fe8d. Preservado o reteste integrado 7a1d0f (índice 8/31/7, 10 testes Node, duas reconstruções idênticas, capturas reais de repouso/ADS/recarga; ver PILOTOS_ASSETS.md). Não repetir esses testes como se novos fossem.

- Lidos os GLBs reais rifle, rifle_body, rifle_action e rifle_mag pela API GitHub em base64 e interpretado o JSON dos arquivos binários. Respectivamente 2.459/1.363/32/1.064 vértices e 4.634/2.574/60/2.000 triângulos; cada arquivo contém POSITION e COLOR_0, sem NORMAL, TANGENT ou TEXCOORD_0. Os 31 arquivos sem normal já estão registrados no reteste integrado. Não alegar nova leitura integral dos 31: a tentativa de lote excedeu o limite de chamadas.
- tools/build_weapons.py exporta com trimesh.Scene.export(file_type='glb') sem solicitar normais explicitamente. scripts/weapon_materials.gd usa StandardMaterial3D com normal_enabled=true, normal textures reais e uv1_triplanar=true, aplicada por player, enemy e loot_pickup. O triplanar é intencional, sem atlas UV.
- Fonte oficial Godot 4.4.1-stable: modules/gltf/gltf_document.cpp (trecho de importação de malhas, linhas 3527–3571): force_generate_tangents exige triângulos, NORMAL e ausência de TANGENT; sem TEXCOORD_0 gera uma base tangente auxiliar a partir da normal. editor/import/3d/resource_importer_scene.cpp define meshes/ensure_tangents=true por padrão. Os dois sidecars rifle consultados não estão disponíveis no Git, então confirmar a configuração efetiva após importação. drivers/gles3/rasterizer_scene_gles3.cpp, linha 296, emite aviso quando uses_tangent e atributo ausente. scene/resources/material.cpp, linhas 1282–1324 e 1621–1630, calcula TANGENT e BINORMAL para projeção triplanar e amostra NORMAL_MAP nas três direções. Logo, o aviso não demonstra sozinho que o normal map inteiro deixou de funcionar. Eliminar o aviso não é evidência de paridade visual.
- O Studio atual (tools/asset_studio/runtime-composition.js) aproxima apenas albedo triplanar e atribui normalMap=null quando triplanar. A equivalência do canal normal ainda requer implementação e comparação real, independentemente do atributo da malha. Não desabilitar normal_enabled, trocar textura ou inventar UV/tangente sem significado só para calar aviso.
- Candidato no próprio gerador canônico: `--candidate-normals EMPTY_DIRECTORY`, exigindo diretório vazio fora do checkout, solicita exportação explícita das normais das malhas já geradas, exige shape correto, valores finitos e unitários, mantém a montagem de grupos merged/body/action/mag, coordenadas, cores e faces na fonte. Caminho padrão usa a chamada de exportação anterior exatamente, sem mudar assets de produção. Nenhum novo instalador, runner, arquivo GLB ou shader alterado. Candidato não integrado: verificar se a versão fixada de trimesh aceita a opção e gera NORMAL, validar duas gerações, comparar atributos originais (posições/índices/cores, hierarquia, bounds), importar com ensure_tangents, medir presença/validade dos atributos no Godot, observar a renderização em repouso/ADS/recarga e comparar material triplanar no Studio. Não substituir produção nem regenerar baseline antes de confirmar reprodução e aparência.
- Ambiente desta execução: chamadas de Python/container falharam (ClientError), portanto não foi possível executar o gerador candidato, Node, Godot, Firefox, testes de importação ou export Windows. A verificação desta entrega é estática do patch e leitura dos quatro GLBs reais; não é novo teste de engine. Preservar 00-28 parcial até a correção efetiva em produção e paridade representativa. O candidato é uma opção temporária para revisão de fonte, não uma nova rotina de QA.

Referências técnicas: [importador glTF](https://github.com/godotengine/godot/blob/4.4.1-stable/modules/gltf/gltf_document.cpp#L3527-L3571), [importação de cena](https://github.com/godotengine/godot/blob/4.4.1-stable/editor/import/3d/resource_importer_scene.cpp), [material triplanar](https://github.com/godotengine/godot/blob/4.4.1-stable/scene/resources/material.cpp#L1282-L1324), [aviso Compatibility](https://github.com/godotengine/godot/blob/4.4.1-stable/drivers/gles3/rasterizer_scene_gles3.cpp#L296-L300).
