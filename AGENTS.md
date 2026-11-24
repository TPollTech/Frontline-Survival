# Frontline Survival

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
