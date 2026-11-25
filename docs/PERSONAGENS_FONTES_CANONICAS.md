# 00-29 — Fontes canônicas de personagens, mãos e equipamentos

Data 25/11/2026. Base preservada ca2033711b25e391bb7d422bc0ff8a89d4aea488 (descendente de c1d56a4). Estado parcial. A cota de GitHub Actions está esgotada, conforme o responsável; não disparar CI nesta entrega.

## Migração incremental da geometria real

`scripts/character_geometry.gd` centraliza cinco receitas: joint, padded, capsule, box e sleeve. Consumidores reais: player.gd (sleeve), enemy.gd e ally.gd (joint, padded, capsule), quaternius_soldier_visual.gd (capsule, box). As funções de montagem existentes continuam canônicas para hierarquia, transformações, nomes, materiais, cache por cor da mão, poses, animações, física e gameplay. A geometria da manga (SurfaceTool, anéis, perfil, índices, normais) foi movida sem alterar a receita, passando o comprimento do eixo por parâmetro. As cápsulas NPC mantêm 10 segmentos/2 rings; equipamento Quaternius 12/3. Sem novos GLBs, sem alterar texturas, sem substituir a anatomia ou mudar o Skeleton3D. As funções _ready e o gameplay subsequente dos NPCs são idênticos aos da base; a montagem e animação FPS e o rig experimental também permanecem iguais. O humanoide experimental continua desativado por padrão em main.gd. O GLB Quaternius é importado, não fonte editável confirmada; procedência em ASSET_QUATERNIUS_CC0.md. Os pilotos anatômicos da suíte QA não foram ativados em produção.

O catálogo vivo liga as quatro famílias históricas às receitas compartilhadas e ao fingerprint atual, sem editar a baseline nem criar modelo de preview independente. Não confundir as quatro famílias consumidoras com quatro personagens completos homologados. O helper é excluído dos candidatos de preview somente quando o contrato das quatro famílias está presente e as referências/funções foram encontradas. O teste Python cobre vínculo, fingerprint, determinismo e referência faltante.

## Evidência desta revisão

10/10 verificações estáticas em V8 sobre os arquivos reais e as alterações propostas: equivalência da receita da manga, montagem/anim FPS inalteradas, _ready/gameplay NPCs intactos, materiais NPCs intactos, ordem dos joints, tesselação, rig/animação/equipamento Quaternius intactos, equivalência do material e montagem Quaternius, quatro referências reais, contrato de catálogo. Não são execução Python, GDScript ou renderização. Novo teste Python incluído mas não executado nesta sessão. A execução local de Godot/Blender e renderização do Studio não está disponível neste fluxo; não foram inspecionadas capturas novas nem gerado ZIP. Sem CI, conforme solicitação. Não atribuir ganho de FPS ou aprovação visual.

## Próximos passos

Executar `python -m unittest discover -s tests -p 'test_live_catalog.py' -v`, inventário runtime e Studio no mesmo commit; verificar importação GDScript e equivalência dos buffers, transformações, materiais, colisores, hierarquia e poses em todos os casos. Comparar capturas de mãos em repouso/mira/recarga, soldado/runner/heavy, aliado e Quaternius experimental. Migrar composição/anatomia e rig de produção por lotes, preservar comportamento e medir orçamento/desempenho. Recuperar fonte editável upstream ou registrar lacuna de procedência do importado. Tarefa 00-29 permanece parcial até paridade real e homologação.
