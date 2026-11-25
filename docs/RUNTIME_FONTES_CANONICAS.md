# 00-32 — Escopos canônicos de objetos, colisores e efeitos em runtime

Data 25/11/2026. Base dc501c291f1c6c799c785fe626e3838428594446, descendente de b6f1d43. Estado parcial. Sem Actions; [skip ci]. Preservados mapa, WorldLOD, benchmark e regras de gameplay.

## Migração de rastreabilidade

O inventário anterior já associa as famílias históricas a receitas reais, mas a associação de uma família a uma amostra inteira (por exemplo combat_visual_event) não isola os nós do efeito. Acrescentado contrato asset_scope_schema 1 e escopos por amostra em inventory_qa.gd. Captura os caminhos dos nós reais antes/depois do callback existente, ou referências diretas do objeto, sem criar preview independente nem alterar produção. Inventário integral, buffers, hierarquias e IDs históricos permanecem. A contagem de amostras continua prevista em 86; não declarar nova execução.

13 papéis em 10 famílias:
- player:collision: cápsula real, corpo CharacterBody3D, camada 2/máscara 1; não confundir com consulta temporária de postura.
- effect:muzzle e effect:scope_overlay: malha real e CanvasItem com shader real; distinguir presença e visibilidade, não afirmar efeito ativo apenas por existir.
- object:turret: duas malhas e luz, sem colisor próprio; object:loot: arma GLB original ou duas malhas de munição, sem colisor; object:grenade: três malhas, SphereShape3D independente, corpo RigidBody3D camada 8/máscara 1.
- effect:grenade: somente filhos recém-criados pelo callback, 24 malhas e uma luz; excluir corpo e colisor da granada. Callback visual isolado, não detonação completa.
- effect:blood: sete malhas; effect:enemy_tracer: traçador real.
- effect:combat: três malhas novas da chamada visual da escopeta (traçador, estojo e impacto), marcador e impacto aéreo em amostras separadas.

runtime_asset_scopes.py valida papéis por ID, família, raízes existentes, ausência de sobreposição, contagens de componentes, classe/camada/máscara de colisão e identidade do shader; escopos são seleção de QA, não dedução automática de todos os estados. Dados históricos sem marcador não recebem propriedade inferida. Catálogo vivo vincula runtime_scopes às famílias existentes, com aprovação falsa. Studio exibe métricas e raízes específicas junto das métricas da subárvore inteira. A composição visual continua sendo a amostra inteira, não isolamento de geometria, e a interface WebGL não foi testada nesta revisão. Consultas de spawn, cobertura e torreta seguem marcadas source_review para parâmetros e resultados amostrados; não atribuir-lhes malhas ou colisores persistentes.

## Evidências e limitações

9/9 testes Python sintéticos realmente executados no container Python 3.13.5: escopo do tiro exclui mapa, rejeita toda a cena, raízes inexistentes, sobreposição, papel ausente, camada incorreta, shader incorreto, conserva colisão e visibilidade da sobreposição, distingue inventário antigo de cobertura incompleta. Hashes Git dos dois arquivos testados conferidos antes de publicar. Conferência estática das chamadas e contratos com as receitas reais da base. Não equivale à execução de GDScript, inventário completo, browser ou revisão visual. Nenhuma alteração de script de gameplay, modelo, material, colisão, duração ou LOD. Godot não localizado no PATH; git ls-remote falha por DNS nesta sessão. Sem capturas novas, sem release/ZIP.

Validação restante: executar inventário real Godot e catálogo vivo da mesma revisão, verificar os 13 papéis, seus caminhos e estados, executar suite Python integral e Studio WebGL, inspecionar efeitos em movimento e pós-limpeza, testar estados de colisores durante gameplay e medir custo no hardware-alvo. A ampliação de efeitos e colisões de outros estados e a homologação continuam pendentes; não confundir os escopos iniciais com cobertura integral de instâncias. Preservar os demais IDs.

Teste local isolado:
```sh
python -m unittest discover -s tests -p test_runtime_asset_scopes.py -v
```
Para captura e construção do Studio, seguir docs/INVENTARIO_RUNTIME.md e docs/ASSET_STUDIO.md com perfil de QA isolado, revisão correta e importação Compatibility. Não disparar workflows.
