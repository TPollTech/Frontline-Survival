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
