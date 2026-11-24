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
