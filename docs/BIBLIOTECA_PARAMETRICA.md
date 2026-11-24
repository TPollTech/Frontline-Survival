# Biblioteca paramétrica — fundação v1

Escopo: API central executável em Python, IR imutável, geração básica e adaptador Blender real opcional. Não substituir modelos legados antes dos pilotos e do Studio. Esta etapa não encerra geometrias avançadas, materiais PBR completos, rigging, colisões, LOD, exportação GLB nem homologação artística.

| Módulo | Responsabilidade |
|---|---|
| model.py | MeshSpec, MaterialSpec (fatores básicos), NodeSpec, SceneSpec, Transform, IDs, referências, ciclos, bounds, SHA-256 da IR |
| recipes.py | Receitas Box/Cylinder em metros, protocolo GeometryBackend, PythonBackend com topologia fechada e orientação |
| blender_backend.py | Processo opcional isolado, timeout, JSON, validação de entrada/saída, avaliação de malha |
| blender_bridge.py | bpy real, conversão (x,-z,y), unidades métricas, triangulação avaliada, bevel técnico por ângulo |
| tests/test_parametric_library.py | Testes de contrato e integração real Blender sobre fixtures neutras |

Arquivos em tools/asset_pipeline/parametric/. Python >=3.10, sem dependência externa para a base; CI 3.11. Blender é opcional no desenvolvimento; `FRONTLINE_BLENDER` permite indicar executável. Não há download implícito na biblioteca. A instalação CI usa o pacote do Ubuntu 22.04 e registra a versão real; não é lockfile de Blender, portanto reprodutibilidade binária entre versões ainda não garantida.

Exemplo a partir da raiz:

```python
from tools.asset_pipeline.parametric import Box, PythonBackend, NodeSpec, SceneSpec, Transform
mesh = PythonBackend().build(Box("fixture", (1.0, 2.0, 3.0)))
scene = SceneSpec("technical_fixture", (mesh,), (), (
    NodeSpec("root"),
    NodeSpec("part", mesh.id, "root", local=Transform.translation((0, 1, 0))),
))
print(scene.world_bounds(), scene.sha256())
```

A IR usa metros, +Y cima, sistema destro, matrizes coluna-major e composição pai * local. Triângulos CCW; rejeita faces degeneradas, duplicatas, vértices não referenciados, IDs duplicados, referências inexistentes e ciclos. Transform aceita bases afins de determinante positivo; reflexões e degeneração são rejeitadas nesta versão. Origem do nó é seu pivô. Bounds são medidos a partir dos vértices; nenhuma recentralização automática. MaterialSpec contém fatores básicos, sem textura/UV/tangente nesta fase. Serialização JSON estável por IDs, não promessa de GLB determinístico. O backend Blender opera na malha local, preserva ID e converte de volta; hierarquia e materiais ficam na IR original. A conversão é uma rotação própria e os testes usam fixture assimétrica deslocada. Bevel técnico é uma capacidade inicial, não implementação completa da tarefa seguinte.

Comandos:
```sh
python -m unittest discover -s tests -p 'test_parametric_library.py' -v
FRONTLINE_REQUIRE_BLENDER=1 python -m unittest discover -s tests -p 'test_parametric_library.py' -v
```

O workflow Parametric library QA valida baseline, manifesto, Python e Blender real (sem skip na segunda execução). Nenhum novo asset de gameplay, export ou versão do jogo; não há preview inventado. Godot e Asset Studio não são aplicáveis à homologação de modelos nesta entrega de biblioteca isolada; o Studio ainda não existe. Testes remotos pendentes de confirmação no momento do commit inicial. A regressão preexistente do arsenal não é corrigida aqui.

## Evidência CI — 24/11/2026

[Run 45442588521](https://github.com/TPollTech/Frontline-Survival/actions/runs/45442588521), commit `de6bbab5177999e73cba5b60455c93d7308bc7ab`. Verificação estática, manifesto e testes da fundação Python concluídos com sucesso no CI. Instalação/testes do backend Blender ainda não confirmados. Conferidos os 90 hashes da baseline (60 recursos + 30 fontes/configurações); todos preservados. Sem Studio ou mudança de modelos/partida; não publicar ZIP como homologado. Logs completos do job serão disponíveis no link do Actions quando concluído.

## Encerramento validado — 24/11/2026

[Run 45442588521](https://github.com/TPollTech/Frontline-Survival/actions/runs/45442588521) concluído com sucesso no commit `de6bbab5177999e73cba5b60455c93d7308bc7ab`. Logs conferidos: Python sem Blender: 20 testes aprovados, 2 skips esperados; com Blender 3.0.1 (pacote 3.0.1+dfsg-7), FRONTLINE_REQUIRE_BLENDER=1: 22/22 testes aprovados, zero skips, em 2,046 s. Os testes de integração test_asymmetric_roundtrip e test_actual_blender_bevel foram executados de fato. Inventário estático e 18 testes do manifesto aprovados. [Artefato de log](https://github.com/TPollTech/Frontline-Survival/actions/runs/45442588521/artifacts/14945545304) e [evidência persistente](qa/parametric_foundation_evidence.json). Os 90 hashes de recursos e fontes/configurações da baseline foram reconferidos na main sem divergências. Nenhum script de gameplay ou asset alterado.

**Fundação concluída:** API, IR, geração básica e backend opcional real foram implementados e testados. Não significa geometrias avançadas completas nem homologação de assets. A versão testada do Blender é 3.0.1; compatibilidade com outras versões e fixação de dependências deverão ser validadas na evolução do pipeline. Nenhum modelo de produção foi modificado, portanto o portão visual de novos modelos não se aplica a esta entrega de biblioteca; Studio permanece inexistente. O workflow Windows [45442587247](https://github.com/TPollTech/Frontline-Survival/actions/runs/45442587247) falhou: Arsenal QA - isolated individual tests of all eight weapons. Sem ZIP novo aprovado.

## Geometrias avançadas — implementação

`advanced.py` acrescenta receitas imutáveis `Extrusion(id, profile_xz, height_m, y_min_m)` e `Revolution(id, profile_ry, segments)`, disponíveis no PythonBackend.build e BlenderBackend.build (roundtrip real). Extrusão ao longo de +Y, perfil simples convexo ou côncavo em XZ, fechamento implícito, ear clipping determinístico e tampas orientadas. Revolução completa em torno de Y de seção fechada (raio, altura), perfis escalonados e anéis ocos, vértices únicos no eixo, fechamento sem seam duplicada. Entradas autointersectantes, repetidas, colineares, degeneradas, raios negativos e combinações de eixo não suportadas são rejeitadas. Furos no perfil de extrusão e revolução parcial não são suportados nesta API inicial; usar CSG quando aplicável.

`BlenderBackend.boolean(id, left, right, operation, right_transform=...)`: union/difference/intersection por modificador Blender solver EXACT, entradas fechadas orientadas e transform da segunda malha no frame canônico. Resultado vazio ou inválido gera BlenderError. `bevel(mesh, width_m, segments, angle_rad=...)`: bevel por ângulo, clamp overlap do Blender, de 1 a 8 segmentos; largura efetiva pode ser limitada. Não há fallback silencioso. CSG exige Blender. Validação de bordas e volume não certifica ausência de toda autointerseção interna. UVs, normais, materiais por face, curvas e LOD são tarefas distintas.

Testes analíticos em peças neutras: volume e bounds de extrusão côncava, cone, revolução sólida/oca/escalonada, determinismo e entradas inválidas; volumes de união/interseção/diferença de blocos sobrepostos, interseção vazia, bevel segmentado e roundtrip real. Executar `python -m unittest discover -s tests -p 'test_parametric*.py' -v`. CI repete a suíte da fundação e exige Blender real. Nenhum asset de produção/exportado ou script de gameplay modificado; sem aprovação visual no Studio ou Godot. Resultados da ampliação pendentes na publicação inicial.

### Correção da primeira execução — 24/11/2026

[CI 45448151957](https://github.com/TPollTech/Frontline-Survival/actions/runs/45448151957), commit 83edef1: suite Python sem Blender aprovada (38 casos, 6 skips esperados); Blender 3.0.1 real: 37/38 casos aprovados, falha em test_boolean_volumes (subcaso intersection). O log mostra que bpy usa INTERSECT, não INTERSECTION. União, diferença, bevel, extrusão/revolução e roundtrip passaram. A aprovação anterior do teste de interseção vazia era insuficiente: aceitava qualquer BlenderError, inclusive a falha de enum. Corrigido o mapa de operações explícito e o teste exige agora a mensagem de resultado efetivamente vazio retornado pela avaliação. Acrescentados casos de sólidos disjuntos e cavidade interna, com volumes e bounds analíticos. Nenhum asset de produção modificado. Revalidação CI obrigatória antes de marcar concluído.

### Segunda correção de CSG — 24/11/2026

[CI 45448536284](https://github.com/TPollTech/Frontline-Survival/actions/runs/45448536284), commit 4b3602f: 39/40 testes com Blender real, uma falha no subcaso intersection de test_boolean_volumes. O enum foi corrigido, a interseção vazia genuína, sólidos separados e cavidade interna passaram. O novo erro é ValueError: degenerate triangle no resultado avaliado. Implementada normalização coplanar com BMesh dissolve_limit (tolerância angular 1e-6 rad) antes e depois do CSG, sem merge-by-distance, sem desabilitar verificações de MeshSpec. Não aplicada em roundtrip simples ou bevel. Adicionado teste de interseção com limites, volume, oito vértices e doze triângulos. Requer nova execução real; não presumir aprovação. O workflow Windows 45448536286 também falhou; nenhum novo executável homologado.

### Terceira correção — saneamento restrito ao CSG

[Run 45451680377](https://github.com/TPollTech/Frontline-Survival/actions/runs/45451680377), commit 384d473: 39/41 casos aprovados, dois erros de triângulo degenerado em interseção. A dissolução coplanar isolada não resolveu. Nova tentativa: limpeza BMesh de duplicatas e fragmentos degenerados **somente na saída CSG**, tolerância proporcional limitada a 0,1 micrômetro, dissolução de partições coplanares e triangulação explícita BEAUTY. A limpeza exige preservação de bounds e volume assinado dentro de tolerâncias declaradas; rejeita bordas não-manifold, faces degeneradas e vértices órfãos; MeshSpec mantém os critérios anteriores. Diagnósticos de coordenadas e métricas são incluídos em falha do resultado. Novo caso de interseção com operando rotacionado, sem reduzir os testes originais. Corrigido também o filtro de paths do workflow para cobrir alterações em todos os testes paramétricos. Resultado aguardando CI. Limite: limpeza conservadora não prova ausência de toda autointerseção nem preservação de detalhes menores que a tolerância. Nenhuma alteração no gameplay ou nos assets de produção; não é homologação visual.

### Quarta correção — otimização de regiões planas

[Run 45452796093](https://github.com/TPollTech/Frontline-Survival/actions/runs/45452796093), commit 52f60af: 41/42 casos Blender real aprovados. Interseções, inclusive operando rotacionado, passaram em topologia, volume e bounds; único erro é a exigência de malha mínima de 8 vértices (14 retornados). Não houve nova falha de triângulo degenerado. Acrescentada simplificação determinística da superfície já validada em coplanar.py: agrupamento de triângulos por plano de referência fixo, extração de contornos orientados e remoção de pontos colineares somente quando todas as regiões incidentes concordam. Retriangulação com ear clipping existente e verificação de área, volume, bounds e topologia; regiões com furos ou múltiplos contornos preservam a malha válida original. Sem alterar tolerância de MeshSpec nem afrouxar teste de 8 vértices/12 triângulos. Três testes Python adicionais para centros de faces, pontos intermediários em arestas e anel com furo. A suíte passa a 45 casos e precisa de nova execução real. Nenhum recurso de produção modificado, sem homologação visual.

## Encerramento das geometrias avançadas

[CI 45453292708](https://github.com/TPollTech/Frontline-Survival/actions/runs/45453292708), commit 79e7baa9c8df7b26723e5919a265cc609bfdeb20: 45/45 testes aprovados com Blender 3.0.1 real, sem skips, em 11,066 s. Sem Blender: 35 aprovados, 10 skips esperados. Interseção mínima de 8 vértices/12 triângulos aprovada. Manifesto 18 testes aprovado. [Artefato 14949246767](https://github.com/TPollTech/Frontline-Survival/actions/runs/45453292708/artifacts/14949246767), SHA-256 do ZIP informado pelo Actions: 84a53b491eb9d81088f3dcb7e36cc7feab1607938d03983df3ef746942ef611f. Concluída a etapa de biblioteca, não homologação de modelos.

## Curvas, superfícies orgânicas e topologia personalizada

O módulo organic.py acrescenta BezierCurve (segmentos cúbicos conectados, avaliação de Casteljau, derivada, amostragem e continuidade C1 opcional), BezierPatch (superfície bicúbica aberta, amostragem U/V), LoftSection e OrganicLoft (anéis elípticos em alturas estritamente crescentes, centro, raios e twist, interpolação smoothstep, tampas e costura indexada), CustomTopology (triângulos e quads convexos, triangulação determinística). As receitas de malha usam PythonBackend.build e BlenderBackend.build; a curva é uma fonte de pontos, não uma malha. Verificações de bordas, orientação e conectividade do fan de cada vértice; sólidos fechados exigem volume positivo. Não se certifica ausência de toda autointerseção, anatomia, deformação, UV ou normais; loft não é sweep por caminho arbitrário e quads não convexos exigem triangulação explícita. Fixtures neutras apenas; nenhum asset de produção substituído. 12 testes Python e 2 de roundtrip Blender adicionais. Revalidação CI necessária antes de concluir esta etapa.

## Encerramento de curvas e superfícies

[CI 45454861861](https://github.com/TPollTech/Frontline-Survival/actions/runs/45454861861), commit a9ddb346dc2eb5a77c31cf0694a81a59b074b1d2: 59/59 testes aprovados com Blender 3.0.1 real, sem skips, em 7,030 s; sem Blender 47 aprovados, 12 skips esperados. Manifesto 18 testes aprovado. [Artefato 14951190629](https://github.com/TPollTech/Frontline-Survival/actions/runs/45454861861/artifacts/14951190629); SHA-256 informado pelo Actions: 44a0c8a04b2f48730889bc1bacc8e73716ed27c0b5a1a4427b43d77e77f6c53a. Fundação de curvas concluída; sem homologação de modelos.

## Normais, UV e tangentes

shading.py separa MeshSpec topológico de RenderMesh com buffers indexados de posição, normal, UV0, tangent XYZW e source_vertices. Normais por canto: componentes conectados por arestas suavizadas, peso uniforme/área/ângulo/área×ângulo, limite de crease e arestas duras explícitas. UV autoral por canto, projeção planar em metros por tile e atlas automático por triângulo com padding sem sobreposição entre células (não é unwrap de produção otimizado). Triângulos UV degenerados rejeitados. Tangentes Python por derivadas UV ponderadas por ângulo, Gram-Schmidt e sinal de handedness; não é implementação de referência MikkTSpace. shading_blender.py oferece execução opcional real de calc_tangents no Blender (MikkTSpace), UVs e normais customizadas por loop, checagem de ordem, unidade e normal quantizada, reortogonalização na normal canônica. Use build_render_mesh(mesh, tangent_backend=blender_tangents) para produção futura com Mikk. Não há fallback silencioso. Costuras UV e espelhamento podem separar vértices de render sem mudar topologia original. RenderMesh valida reconstrução dos índices fonte e frames ortonormais. Nenhuma integração ainda com SceneSpec/GLB, baking, unwrap avançado, Godot ou Studio; materiais e exportação ficam nas etapas próprias. 10 novos testes Python e 2 reais Blender, aguardando CI. Nenhum asset de produção alterado.

## Encerramento de normais, UV e tangentes

[CI 45456153062](https://github.com/TPollTech/Frontline-Survival/actions/runs/45456153062), commit 23d90a696e0e0694b3ac9f35793333fe13221905: 71/71 aprovados com Blender 3.0.1, zero skips, 14,914 s. Sem Blender: 57 aprovados, 14 skips esperados. Manifesto 18 testes aprovado. [Artefato 14949733546](https://github.com/TPollTech/Frontline-Survival/actions/runs/45456153062/artifacts/14949733546), SHA-256 informado pelo Actions 175d002d11aa0621f20d993b1c0344fd0a54e98cbe3921f8e12950a45b730d41. Concluída a biblioteca de atributos; sem homologação visual.

## Biblioteca PBR e texturas

pbr.py contém PBRMaterial (subclasse compatível de MaterialSpec), TextureData RGB8 e MaterialLibrary imutáveis, com validação de fatores, funções de textura, cores e referências. Fatores são lineares; base color/emissive sRGB; normal e ORM lineares; R=AO, G=roughness, B=metallic; normal tangent-space +Y. Geração inicial de metal escovado, aço pintado, borracha, concreto, madeira e tecido: 6 materiais e 18 mapas originais CC0 declarados, semente e parâmetros rastreáveis. AO neutro (255), não é AO baked. PNG RGB8 determinístico com DEFLATE armazenado, CRC e SHA-256; sem dependências externas no gerador. Mesma receita/ambiente reproduz o resultado; não se garante identidade matemática de sin/cos entre plataformas. Gerar explicitamente em diretório vazio: `python -m tools.asset_pipeline.parametric.generate_materials /tmp/frontline-pbr --size 128 --seed 9133`. Verificação compara manifesto e hashes dos arquivos. Texturas externas RGB8 podem ser fornecidas como pixels decodificados com procedência/licença explícitas; não há importador de arquivos externos nesta etapa. PBRMaterial cabe em SceneSpec; resolução de IDs de textura é responsabilidade de MaterialLibrary e futura exportação. A biblioteca não altera baseline/recursos atuais. 12 testes Python e 1 Blender real verificam geração, integridade, canais, normal maps, resolução de referências e decodificação/wiring Principled BSDF de 18 imagens/6 materiais; a ponte é uma fixture de teste, não render/exportador de produção. Sem baking, alpha por textura, compressão de GPU, render de aprovação ou integração Godot/Studio nesta entrega. Resultados pendentes de CI.

## Hierarquias, pivôs, encaixes e rigging

rig.py acrescenta inversão afim, rotação axis-angle, transformação em torno do pivô e reparent preservando mundo. SocketSpec possui owner node/bone e transform local; attachment_local resolve alinhamento integral (posição e orientação). BoneSpec: eixo longitudinal local +Y, transform rígido, comprimento métrico. SkeletonSpec: raiz única, ordenação pai-primeiro, ciclos e referências validados, pose = rest_local * delta local, matriz de skin = pose_world * inverse(rest_world). SkinSpec: 1 a 4 influências positivas únicas por vértice, soma 1, LBS de posições, remapeamento por RenderMesh.source_vertices. RigSpec liga cena, skeleton, anchor, skin e sockets, com serialização canônica e SHA-256. A malha skinned deve estar no frame de bind do anchor; offsets/instâncias ambíguas são rejeitados. Não é IK, rig anatômico, skinning dual-quaternion, animação por keyframes, exportação GLB, deformação de normais ou integração runtime. A ponte rig_bridge.py é fixture real de armature e deformação Blender, comparando posição de vértices e matrizes de pose com o Python. 11 testes Python e 1 Blender adicionais; CI pendente. Sem alteração de modelo de produção ou homologação visual.

### Compatibilidade de espaços de cor no CI PBR

[CI 45458582573](https://github.com/TPollTech/Frontline-Survival/actions/runs/45458582573) no commit 77297e0: 83/84 casos com Blender 3.0.1; a configuração OCIO fallback do ambiente só disponibiliza Linear e sRGB, rejeitando Non-Color. Corrigida a ponte de teste: preferir Non-Color para dados, usar Linear somente se o enum não estiver disponível, verificar e registrar o espaço efetivo por imagem. Base color continua sRGB; a suíte confere as 18 atribuições. A geração e os testes Python passaram. Não equivale a homologação visual, nem certificação de outras configurações OCIO. Revalidação pendente.

## Encerramento PBR e rigging

[CI 45459161051](https://github.com/TPollTech/Frontline-Survival/actions/runs/45459161051), commit 36672dea8e8d90fa357f50ab75851d2340b2bc7c: 96/96 testes com Blender 3.0.1, zero skips, 17,089 s; sem Blender 80 aprovados e 16 skips. test_real_decode_and_shader_links e test_actual_armature_skin aprovados. Manifesto 18 testes. [Artefato 14950559824](https://github.com/TPollTech/Frontline-Survival/actions/runs/45459161051/artifacts/14950559824), SHA-256 informado pelo Actions 45d956ae3fb7df706ecc523dcdff6b900125cfcfd64615ec14bf0cc56ab13198. Encerradas as fundações PBR e rig; nenhum modelo homologado.

## Colisões e LOD

lod.py: ColliderSpec independente do visual (box, sphere, capsule com altura total, convex proxy fechado e teste de planos, concave proxy estático), transform rígido local, owner node, tipo de corpo e layer/mask. AssetLOD mantém três SceneSpec com distâncias crescentes, redução estrita de triângulos, invariância da hierarquia, pivôs e materiais, bounds locais por peça e globais dentro de tolerância, colisões únicas e independentes. Seleção por distância em metros com histerese; não é ainda seleção runtime integrada. Resampling determinístico de Cylinder, Revolution, OrganicLoft e BezierPatch; outras receitas exigem LOD autoral. Não decima automaticamente malhas com UV/skin; atributos, skin weights e exportação por LOD devem ser reconstruídos na etapa de integração. Convexidade testada por planos; não prova ausência de toda autointerseção. Colisão pode ser aproximada por autoria, não há teste universal de cobertura/silhueta. Orçamentos iniciais BUDGETS por categoria/instância (mapa/terreno por chunk), triângulos, slots por instância, contagem de colisores e triângulos físicos; vértices de render reportados como limite superior 3*triângulos, não medição do buffer. Categorias não geométricas explicitamente excluídas. Valores escolhidos como ponto de partida, não benchmark Ryzen 5 7530U/8 GB; revisão no hardware obrigatório. 10 testes Python adicionais. Workflow isolado Collision and LOD Godot QA gera fixture de coluna neutra e testa real ArrayMesh e raycast com mesmo BoxShape3D ao trocar três LODs. Não é integração no jogo nem inspeção visual. CI pendente; nenhuma alteração nos assets/gameplay existentes.

### Evidência de colisões e LOD

[Godot QA 45460210552](https://github.com/TPollTech/Frontline-Survival/actions/runs/45460210552), commit 95bbffaed20be52fb6018af3136e674dd1e8dfe0, Godot 4.4.1: três níveis (256, 128, 64 triângulos) importados como ArrayMesh; mesmo BoxShape3D e raycast hit_z=0,5 em todos. [Artefato 14952572078](https://github.com/TPollTech/Frontline-Survival/actions/runs/45460210552/artifacts/14952572078), SHA-256 informado pelo Actions f4df75fd1ac082d3278a7a04f4a440b4e976da89b073d73b9e9030c3340de0a6. [CI paramétrico 45460210492](https://github.com/TPollTech/Frontline-Survival/actions/runs/45460210492): Python sem Blender aprovado; regressão completa com Blender ainda não confirmada. Sem benchmark no hardware-alvo, sem validação de desempenho e sem homologação visual. Mantém-se parcial até validar os orçamentos exigidos e a suíte completa. Não houve alteração nos 90 hashes da baseline. Teste Godot cobre somente box estático e troca explícita de malha; outros tipos de collider e histerese testados no Python, não homologados em runtime.

## Exportação GLB/glTF 2.0

exporter.py serializa SceneSpec, RenderMesh, MaterialLibrary e RigSpec em GLB binário e glTF JSON com buffer data URI. Mesma representação, buffers little-endian alinhados a 4 bytes, índices 16/32 bits, POSITION min/max em float32, normal/tangente/UV, materiais metallic-roughness, PNG embutido, ORM compartilhado, skeleton/JOINTS_0/WEIGHTS_0/inverse bind, hierarquia e sockets. Coordenadas canônicas Y-up RH preservadas; V invertido, tangent.w invertido e canal verde do normal map invertido juntos na conversão V-up para V-down. Transformações com shear rejeitadas. Fonte: source_manifest calcula hashes de arquivos reais, caminhos relativos seguros, revisão explícita; export.json registra hashes dos arquivos, IR, buffers de render, biblioteca e rig. Sem timestamp nem caminho absoluto. Reprodução byte a byte para entradas idênticas e mesmo ambiente; gerador de fontes deve incluir dependências transitivas e fixar ambiente. Teste de fixture neutra exporta dois bundles, compara bytes e importa ambos pelo GLTFDocument Godot 4.4.1. 9 testes Python adicionais. Não há ainda export de animação, empacotamento LOD/colisão (contratos separados), catálogo vivo, validação Khronos integral, integração de gameplay ou inspeção visual. Nenhum asset de produção alterado; CI pendente.

### Regressão LOD

[CI 45460210492](https://github.com/TPollTech/Frontline-Survival/actions/runs/45460210492): 106/106 aprovados com Blender 3.0.1, 10,080 s, 90 Python aprovados e 16 skips esperados sem Blender. Artefato 14952043438, SHA-256 informado ccc9e7440ad8ec547eef1497ffc1ebee8728ceca0cf5294569f6af67bf8517fd. Benchmark permanece pendente.

### Estado da exportação

CI 45466926545: 115/115 testes com Blender real, 99 Python e 16 skips sem Blender; 16,803 s com Blender. CI 45466926460: dois bundles idênticos, importação GLB chegou à verificação de atributos e falhou; diagnóstico ampliado sem reduzir critérios. Exportação permanece parcial.


## Revisão 00-10 e 00-11 — 24/11/2026

AssetLOD.budget_report() informa métricas e folgas estáticas por nível e contabiliza colisores independentes, com limites explicitamente provisórios e hardware_validated=false. O CI [45500828834](https://github.com/TPollTech/Frontline-Survival/actions/runs/45500828834) confirma a fixture Godot 4.4.1: 256/128/64 triângulos e hit_z=0,5 em todos os níveis. Não é benchmark de FPS, integração de LOD no gameplay ou homologação dos assets de produção; 00-10 permanece parcial.

O exportador agora normaliza e valida o manifesto de fontes antes de serializar GLB/glTF: ordem canônica, caminhos locais, SHA-256 e rejeição de duplicatas. O teste novo confirma igualdade dos bundles com a lista de fontes invertida e rejeita entradas inválidas. O CI [45500882660](https://github.com/TPollTech/Frontline-Survival/actions/runs/45500882660) aprovou 117/117 testes com Blender real (101 aprovados + 16 skips esperados sem Blender), incluindo os dois testes novos.

No Godot, o locator filho do joint foi promovido a osso auxiliar (bone_root, bone_tip, socket_tip_socket); o teste antigo supunha exatamente dois ossos, embora a skin tenha dois binds. O QA agora verifica a identidade, parentesco, posição de repouso e pesos dos joints e do helper sem dispensar índices, tangentes, UV, material e texturas. O [CI 45501055855](https://github.com/TPollTech/Frontline-Survival/actions/runs/45501055855), commit e1fa71f, confirmou reprodução dos bundles e importação dos dois formatos, 2 joints autorais, 1 helper e 2 binds, sem peso no helper. A fundação de exportação 00-11 foi validada no escopo da fixture técnica. Animação por keyframes, empacotamento de colisões/LOD, dependências transitivas completas declaradas pelo chamador, reprodução entre ambientes distintos e migração de assets reais ainda não são homologados. Nenhum modelo de produção foi alterado; não há revisão visual de modelo novo nem release Windows aprovada.
