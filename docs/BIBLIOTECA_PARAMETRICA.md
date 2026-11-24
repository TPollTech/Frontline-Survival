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
