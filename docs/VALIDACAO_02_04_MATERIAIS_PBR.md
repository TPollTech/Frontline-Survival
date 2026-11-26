# 02-04 — Materiais PBR de produção: diagnóstico e perfis candidatos

26/11/2026. Base a56f1091ff137a20ef6f3e968e77c674f33d6bd6. Escopo exclusivo 02-04; 02-03 segue parcial, não promover outros IDs. [Critério de aceite](CRITERIOS_ACEITE_1_0.md): aplicar materiais de produção por superfície e verificar aparência no Godot sob iluminação normal. Estado parcial; os perfis candidatos não são aplicados nem homologados.

## Caminho efetivo de material

- tools/asset_pipeline/parametric/pbr.py já contém MaterialLibrary, PBRMaterial e seis presets técnicos, geração determinística, cores lineares, PNGs sRGB/lineares e ORM. Não duplicar essa biblioteca nem modificar os presets históricos.
- tools/build_weapons.py, blob d753c7ab9096cfbc7fdf1acf0a1394fb0b94648f: Gun.add atribui cores de face a partir de MAT; Gun.save concatena as geometrias no merged e em cada grupo body/mag/action. A identidade visual de superfície não se torna material PBR distinto no export atual.
- O after-report.json de 02-02 registra nas oito armas uma instância de malha, um material/slot e zero texturas embutidas por GLB merged. São dados históricos, não nova renderização; a equivalência dos oito GLBs já foi conferida no 02-03.
- scripts/weapon_materials.gd, blob 47ad7823f3d7e2dbd4e727bf041ba369db6b211e: dois StandardMaterial3D com metallic 0.48/0.06, roughness 0.59/0.86 e normal_scale 0.38/0.24 (metal/polímero); um override por nó, escolhido por substrings de nome. Não distinguir material pelo nome do grupo nem pela cor: as cores black, tan e darktan aparecem em superfícies de naturezas distintas. Madeira, borracha e metal pintado não têm perfis próprios nessa implementação. Triplanar e opacidade atuais devem ser preservados onde pertinentes.
- scripts/player.gd, enemy.gd, ally.gd e loot_pickup.gd usam o mesmo serviço de acabamento. Corrigir apenas o jogador deixaria NPCs, aliados e pickups inconsistentes. O inventário runtime usa get_active_material(i), adequado para medir materiais efetivos por superfície. O Studio runtime-composition.js já lê metallic/roughness escalares e triplanar; packing de texturas metallic/roughness permanece explicitamente limitado.

## Perfis escalares candidatos

Arquivo [production_surface_profiles.json](../tools/asset_pipeline/parametric/production_surface_profiles.json). Seis classes opacas, valores lineares iniciais de direção artística (não parâmetros medidos de materiais específicos). Metal exposto e latão: resposta metálica; metal pintado, madeira, polímero e borracha: dielétricos. Manter cor de vértice autoral sem multiplicação dupla. Não inferir material de uma cor escura nem transformar recessos automaticamente em transparência. Ópticas e efeitos com requisitos especiais continuam fora desse conjunto opaco. Texturas próprias, UV e mapas finais são 02-05.

Verificação real em Python local, arquivo com SHA-256 90436eb97b08ea4bd02b257d498f44c934f1a15cafd1acc3ab3db6506e5228f1 e blob Git 29350aa5cf025a2ca53a2331c9d67962b0486074: 9/9 verificações passaram (schema/workflow, seis IDs esperados, chaves e fatores finitos entre 0 e 1, metalicidade coerente com classe, seis rugosidades distintas, até oito perfis, opacidade, associação explícita, status candidato/política de textura). Isto valida apenas os dados, não importação, material real, quantidade efetiva de slots ou aparência. Nenhum runner novo. O arquivo ainda não é consumido pelo gerador nem pela engine.

## Integração necessária, após correções de silhueta pertinentes

1. Usar os perfis como ponto de partida para PBRMaterial da biblioteca existente; registrar identidade semântica explícita por superfície na fonte canônica antes da concatenação. Preservar as mesmas malhas e grupos; consolidar por material e grupo quando possível. Manter teto provisório de oito slots, medir os slots/draw calls de cada variante e o conjunto real, não presumir custo a partir dos seis perfis.
2. Exportar materiais glTF metallicRoughness com IDs estáveis, cor de vértice corretamente interpretada e normais/tangentes preservadas. Não substituir a geometria, não editar manualmente GLB nem baseline. Regenerar as 31 variantes e conciliar o catálogo real.
3. Adaptar o serviço de material existente para respeitar a identidade de cada superfície e não sobrescrever todos os materiais com um único override; preservar normal/albedo triplanares existentes quando apropriados. Usar os mesmos materiais efetivos no jogador, inimigos, aliados e pickups. Texturas novas e ORM autoral ficam em 02-05.
4. Verificar determinismo, importação, integridade geométrica, estados e orçamentos. Inspecionar as oito armas no Studio e Godot em repouso, ADS e recarga sob luz normal; comparar superfícies metálicas e dielétricas e registrar capturas reais, resultados e limites. Não promover 02-03/05 ou demais IDs.

## Ambiente e decisão

Verificação local nesta execução: /mnt/data sem checkout, Chromium encontrado, Godot/godot4/Blender/Firefox ausentes do PATH; git ls-remote falhou por resolução DNS. O conector GitHub funcionou. Nenhuma nova renderização, aplicação de perfil ao asset, modificação de fonte de geometria, GLB, shader, textura, gameplay, CI ou ZIP. A preparação de dados não encerra o critério de aceite. 02-04 permanece parcial.
