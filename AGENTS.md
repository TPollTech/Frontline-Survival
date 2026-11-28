# Frontline Survival

## Coordenação dos subagentes do Frontline Survival

O agente principal coordena cada pedido e delega a execução a pelo menos um especialista, inclusive nas tarefas pequenas, salvo orientação expressa do usuário. Cada subagente executa sua atribuição diretamente e devolve resultados ao coordenador. Os perfis de projeto estão em `.codex/agents/`. Se a sessão disponibilizar apenas o agente genérico, o coordenador lê o perfil correspondente e repassa suas instruções na delegação. Se a ferramenta de subagentes estiver indisponível, informa o bloqueio e pede autorização antes de executar sozinho.

Escolha os especialistas a partir do resultado pedido e do componente que o produz. Delegue uma tarefa indivisível inteira ao perfil adequado. Quando o pedido cruzar disciplinas, passe a cada agente o mesmo caso reproduzível, o ID do checklist quando houver, a parte que lhe compete, as dependências e a evidência esperada. Para tarefas fora das especialidades abaixo, atribua a função necessária a um subagente de propósito geral.

| Especialista | Responsabilidade |
| --- | --- |
| `modelagem_armas` | Modelagem 3D das armas e acessórios visíveis no jogo. |
| `modelagem_personagens` | Malhas dos personagens, mãos, luvas, vestuário e equipamento usado no corpo. |
| `rig_animacao` | Rig, poses e transições do personagem e da animação em primeira pessoa. |
| `movimento_jogador` | Programação de controles, locomoção, posturas, colisão e câmera do jogador. |
| `combate_jogador` | Regras de combate do jogador, estados do arsenal, inventário de combate e itens utilizáveis. |
| `ia_navegacao` | Comportamento de inimigos e aliados, movimento dos NPCs, navegação e seleção de spawn. |
| `sistemas_survival` | Ondas, economia, lojas, progressão, estatísticas e checkpoints. |
| `mundo_cenarios` | Mapas, layout, objetos de cenário, colisão e LOD do mundo. |
| `materiais_texturas` | Materiais, texturas PBR e acabamento de superfícies de personagens, armas e mundo. |
| `interface_jogo` | HUD, menus, configurações, acessibilidade e interação com telas do jogo. |
| `audio_efeitos` | Áudio, efeitos visuais de eventos e feedback audiovisual em jogo. |
| `pipeline_studio` | Importação e exportação de assets, biblioteca paramétrica, catálogo e Asset Studio WebGL. |
| `qa_desempenho_build` | Reprodução independente, revisão visual, desempenho, regressões e exportação Windows. |

Trabalhe na frente já autorizada. Paralelize investigações e alterações independentes; combine a ordem das mudanças que dependem umas das outras. Designe um único editor por vez para cada arquivo, gerador e seus derivados ou interface compartilhada. Isso inclui `scripts/player.gd`, `scripts/main.gd`, o Godot e o Asset Studio. O responsável pela fonte regenera seus derivados antes de entregá-los ao próximo especialista.

Por exemplo, se a mão atravessa um objeto ao correr, movimento reproduz a entrada e informa o estado, animação localiza o instante em que a pose se desvia e modelagem confere os pontos de contato. O coordenador dirige a correção ao dono da causa e combina quem edita os arquivos compartilhados. A verificação final repete a sequência na câmera do jogador.

Cada especialista relata o que observou, as fontes e arquivos alterados e a verificação feita. O coordenador reúne os resultados na mesma revisão, solicita verificação independente quando pertinente e confere o critério de aceite da tarefa. A atualização do checklist e a publicação seguem as regras abaixo e ficam centralizadas no coordenador.

## Trabalho na main

- Use a branch `main` como destino de todas as alterações deste projeto. Antes de editar, sincronize com `origin/main` e preserve as mudanças já publicadas.
- Faça commit e push na `main` a cada entrega. Se outra alteração entrar durante o trabalho, integre-a e repita os testes afetados. Preserve o histórico e use push sem força.
- Se precisar de uma cópia de trabalho temporária, integre o resultado à `main` antes de entregar. Verifique o commit no remoto.
- Gere o ZIP de Windows a partir do commit integrado. Confira o conteúdo do pacote e execute os testes aplicáveis no jogo exportado.

## Revisão visual de modelagem

Abra uma partida com renderização após cada alteração de modelagem. Observe o objeto pela câmera do jogador, na escala e na iluminação normais. Para armas, confira repouso, mira e recarga com a animação em execução. Compare capturas na mesma posição, corrija defeitos visíveis e repita a inspeção antes de publicar. Informe a plataforma testada e mostre uma captura da versão entregue.

## Sistema obrigatório de modelagem 3D e Asset Studio

- Leia e siga [docs/ASSET_STUDIO_SPEC.md](docs/ASSET_STUDIO_SPEC.md) e mantenha [docs/CHECKLIST_MESTRE.md](docs/CHECKLIST_MESTRE.md) atualizado. A especificação nova rege todo conteúdo 3D, inclusive cenas, mapas, personagens, armas, objetos e assets procedurais; não apenas armas.
- Antes de remodelar em massa, implemente a biblioteca central, o contrato de fontes/manifesto, o Studio e os verificadores. Analise SNC Energies e SNC Adventures e preserve a arquitetura funcional do jogo.
- Cada asset tem fonte editável canônica, em escala real; corrigir a fonte, exportar de forma reproduzível e usar exatamente os recursos do jogo no Studio. Proibido preview com geometria independente. Catálogo, fontes, materiais, texturas, pivôs, animações, colisões e LOD devem ser rastreáveis; mapas/cenas/runtime também.
- Para cada alteração de modelagem, cumprir as 13 etapas da especificação: referências, proporções, silhueta, detalhes, materiais, exportação, verificações, abrir e inspecionar no Studio, corrigir a fonte, integrar, abrir e inspecionar no Godot e registrar evidências.
- Não confundir CI verde ou screenshot gerado com revisão visual realizada. Sem inspeção real, registrar parcial e o bloqueio; não marcar tarefa concluída nem publicar modelo como homologado. Preservar funcionalidade, desempenho no hardware-alvo e o histórico da main.
- Ao entregar uma tarefa do checklist, atualizar somente estados demonstrados por testes/evidências, reportar bloqueios e reenviar o checklist mestre interativo completo quando a interface permitir.
- Siga [docs/ARQUITETURA_ASSET_PIPELINE.md](docs/ARQUITETURA_ASSET_PIPELINE.md), contrato v1 e convenções de coordenadas. O manifesto de baseline é gerado por tools/asset_pipeline/build_manifest.mjs, não editar manualmente nem confundir com catálogo vivo. IDs, fontes e hashes devem ser preservados em migrações; campos não medidos ficam desconhecidos. Não promover aprovação sem evidências.
- Para comandos locais, extensão de categorias, orçamentos e QA, consulte [docs/GUIA_PIPELINE_3D.md](docs/GUIA_PIPELINE_3D.md). Evidência histórica não homologa revisão nova; especificação e contrato v1 continuam obrigatórios.
- Prioridade obrigatória: finalizar todos os 34 IDs da etapa 00 antes de iniciar ou avançar qualquer etapa posterior, conforme [critérios de aceite por ID](docs/CRITERIOS_ACEITE_1_0.md). Fundação = pipeline operacional, Studio WebGL real, pilotos por categoria e migração/paridade técnica; produção artística e otimização final pertencem aos IDs posteriores. Manter os 13 passos de qualidade para modelos alterados e benchmark final no hardware-alvo em 10-08.
- QA é meio, não produto: reutilizar verificadores e evidências de escopo comprovadamente inalterado, executar testes focados e só repetir integração completa quando necessário. [QA All-in-One](docs/QA_ALL_IN_ONE.md) é opcional, não critério de aceite; não desenvolver instaladores/runners redundantes nem exigir comandos manuais no Godot ao responsável. Falhas impeditivas continuam bloqueadoras; débitos não impeditivos exigem evidência e ID responsável. Não promover estado sem evidência, não confundir captura com inspeção ou aceite técnico com homologação artística.
- Entregas exclusivamente documentais não exigem exportação Windows nem disparo de CI; verificar conteúdo, referências, escopo e preservação dos IDs.
