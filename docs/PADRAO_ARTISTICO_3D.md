# Padrão artístico híbrido 3D — 02-01

26/11/2026. Estado: definição documental, demonstração de produção pendente. Base técnica: 98e1390059d7d1d30c26fcc480015e59ca7de9af. Complementa [especificação](ASSET_STUDIO_SPEC.md), [contrato v1](ARQUITETURA_ASSET_PIPELINE.md), [guia operacional](GUIA_PIPELINE_3D.md) e [critério de aceite](CRITERIOS_ACEITE_1_0.md). Não substitui o portão de 13 passos nem promove homologação artística.

## Direção artística

Realismo militar contemporâneo, proporções críveis, materiais distinguíveis e desgaste localizado. Usar Modern Warfare como referência de linguagem visual de FPS, não como fonte de geometria, texturas ou marcas. Para cada asset, registrar referências visuais efetivamente consultadas, vistas, origem/licença, dimensões de referência e incertezas. Preferir fotos próprias/licenciadas, referências de superfícies e desenhos autorais; não reproduzir conteúdo proprietário. As referências específicas do piloto ainda devem ser reunidas e inspecionadas.

Priorizar nesta ordem: silhueta e escala, contatos e volumes, material e iluminação, microdetalhes. Evitar aparência de blocos, bordas infinitamente agudas, detalhes flutuantes, ruído uniforme, brilho plástico indiscriminado e desgaste aleatório. Criar variações deliberadas e reproduzíveis.

## Rotas de autoria

| Família | Geometria principal | Complemento |
|---|---|---|
| Armas, acessórios, veículos | Hard surface: perfis, extrusão, loft, bevel e topologia personalizada | Blender para curvas/booleanas complexas, UV, bake e refinamento |
| Mãos, soldados, roupas | Topologia orgânica e deformável | Blender para retopologia, rig, pesos e detalhes; manter interfaces da engine |
| Objetos e estações | Receitas paramétricas reutilizáveis | Detalhes hard surface e materiais por função |
| Cenário e estruturas | Módulos parametrizados, composição real Godot | Formas orgânicas e variação controlada de materiais |
| Efeitos e runtime | Fonte canônica existente na engine | Captura real no Studio; explicitar limites de shaders |

Usar tools/asset_pipeline/parametric/ (advanced, organic, shading, pbr, rig, lod, exporter, backend Blender) quando adequado. Não duplicar fontes ou migrar em massa nesta etapa. Arsenal atual: tools/build_weapons.py; personagens: scripts/character_geometry.gd; mundo: scripts/world_asset_geometry.gd, model_surface.gd e consumidores. Fonte editável única por ID; outputs, dependências, revisão, hashes, licença e parâmetros rastreáveis. Studio usa GLB original ou composição real capturada, nunca malha ilustrativa paralela. Preservar IDs e manifesto de baseline.

## Escala, formas e acabamento

- Metro, +Y para cima, frente declarada por asset, câmera Godot -Z; converter Blender uma vez pelo contrato v1. Não compensar proporção física escalando o viewmodel. Registrar AABB medida, dimensões esperadas e justificativa de estilização. Definir tolerância por referência antes de modelar; meta inicial de desvio dimensional até 5% quando existir referência confiável, não aplicável a medidas desconhecidas.
- Geometria primária define silhueta e volumes; geometria secundária define recortes e junções visíveis; detalhes terciários pequenos passam para normal/roughness quando não afetam a silhueta ou animação. Bevel proporcional ao tamanho e processo de fabricação, sem arredondar todas as bordas igualmente.
- Contatos e pivôs existentes, encaixes, estados de animação, colisão independente e nomes consumidos pelo código são contratos de integração. Testar separação indevida, clipping e deformações nas poses efetivas; não alterar gameplay para mascarar modelo.
- UVs, winding, normais, tangentes e materiais coerentes. PBR: base color sRGB, normal/ORM lineares (R AO, G roughness, B metallic), normal tangent-space +Y. Metal exposto com resposta metálica; pintura, polímero, madeira e tecido dielétricos. Diferenciar brilho por superfície, evitar iluminação pintada no albedo; desgaste nas zonas de uso e contato. Transparência somente justificada. Texturas próprias/licenciadas, sem referências ausentes.
- LOD e slots conforme BUDGETS do guia: weapon 18000/7000/1800 triângulos LOD0/1/2 e 8 slots; valores são tetos provisórios, não alvo obrigatório. Não inventar LOD quando inaplicável; registrar exceção. Preservar Compatibility e reservar benchmark integral ao 10-08.

## Piloto escolhido — rifle de produção existente

Fonte: tools/build_weapons.py, função rifle(), exportação g.save('rifle'). Auditoria textual na base acima identificou receptor chanfrado, tampa de perfil com seções e nervuras, coronha e guarda-mão de madeira, carregador curvo e materiais nomeados receiver, walnut, walnut_dark e steel. Isto comprova estruturas existentes na fonte, não sua qualidade visual. O [reteste integrado da fundação](AUDITORIA_HOMOLOGACAO_PIPELINE.md#encerramento-de-00-28-e-00-34) registra rifle real em repouso, ADS e recarga e comparação de relevo triplanar; não comprova o novo padrão.

Demonstrar o padrão neste mesmo ID de produção: reunir referências autorais/licenciadas e medir a silhueta; estabelecer ficha de proporções, detalhes e materiais; corrigir apenas a fonte se a inspeção mostrar necessidade; verificar exportação e catálogo real. Abrir o rifle em seis vistas e perspectiva do Studio, comparar no Godot em repouso, ADS e recarga sob iluminação de jogo. Preservar poses, encaixes e funcionamento. Se não houver mudança necessária, documentar por evidência cada requisito atendido pelo asset atual. Não introduzir fixture QA-only como substituto de produção.

## Ficha de aprovação por asset

Registrar ID e revisão; referências e licenças; dimensões e tolerâncias; fonte e backend; materiais/canais; triângulos e slots medidos; colisões/LOD; resultados automáticos focados; capturas Studio e Godot da revisão; plataforma/versões, câmera, iluminação, poses, observações e decisão por critério.

| Portão | Evidência exigida |
|---|---|
| Silhueta/escala | Vistas ortográficas e perspectiva, dimensões conferidas |
| Geometria/contatos | Sem peças soltas indevidas, clipping relevante ou defeitos de superfície nas poses aplicáveis |
| Materiais | Canais coerentes, superfícies distinguíveis, sem transparências ou artefatos indevidos |
| Integração | Mesmos recursos reais no Studio/Godot, contratos preservados, verificações focadas aprovadas |
| Inspeção | Capturas efetivamente observadas e decisão registrada; diferenças de renderizador explícitas |

Aceite 02-01 requer todos os portões demonstrados em um asset de produção, além desta definição. Remodelagem das oito armas, materiais e texturas completos, mãos/rig e mundo pertencem aos IDs 02-02 a 02-10. Nenhum desses IDs é promovido aqui.

## Evidências e limites desta revisão

Leitura remota de AGENTS.md, checklist, critérios, especificação, guia, arquitetura, auditoria integrada, tools/build_weapons.py, arsenal_sources.mjs e lod.py. Conferência documental de caminhos, critérios e preservação dos IDs. Sem execução nova de Godot, WebGL, Blender ou exportação; nenhuma alteração de malha, material, gameplay ou catálogo. Sem aprovação visual ou nova captura. Estado 02-01 permanece parcial; a demonstração no rifle de produção é o próximo passo obrigatório.
