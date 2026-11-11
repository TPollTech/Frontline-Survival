# Executável Windows — compilação e testes

**Projeto:** Frontline Survival  
**Versão de desenvolvimento:** 0.9  
**Entrega esperada:** arquivo ZIP contendo FrontlineSurvival.exe, FrontlineSurvival.pck (se o exportador usar pacote separado) e LEIA-ME.md.  
**Status:** a [execução da release 0.9](https://github.com/TPollTech/Frontline-Survival/actions/runs/42943797046) concluiu importação, smoke test, integridade e exportação Windows, e publicou a [Release v0.9.0](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.0). A experiência visual/jogabilidade no notebook ainda está em validação.

## Baixar pelo GitHub Releases (padrão)

1. Acesse **[Releases do Frontline Survival](https://github.com/TPollTech/Frontline-Survival/releases)**.
2. Escolha a versão de testes que deseja baixar (por exemplo, **v0.9.0**).
3. Em **Assets**, clique no arquivo **FrontlineSurvival-v0.9.0-Windows.zip** (o nome muda conforme a versão).
4. Extraia em pasta nova, mantendo o arquivo EXE e o arquivo PCK juntos.
5. Execute **FrontlineSurvival.exe** sem precisar instalar o editor Godot.

O download é público e não depende do link de anexo do ChatGPT. As releases são preservadas como versões numeradas, ao contrário dos artifacts temporários das execuções.

**Builds intermediárias:** a página [Actions > Windows playable build](https://github.com/TPollTech/Frontline-Survival/actions/workflows/windows-build.yml) ainda disponibiliza Artifacts quando houver compilação bem-sucedida, mas não substitui o lançamento numerado.

## Padrão de lançamento das próximas versões

- Alterar `application/product_version` no `export_presets.cfg` para um **novo número** de versão (por exemplo, `0.9.1`), atualizar o número no menu/título e registrar mudanças no `docs/CHANGELOG.md`.
- Opcionalmente criar notas específicas em `docs/releases/v0.9.1.md` antes do commit da versão.
- Ao enviar para a branch `main` uma mudança em scripts/cenas/assets/exportação, o GitHub Actions gera e testa um ZIP Windows.
- **Se o CI passar e ainda não existir a release para essa versão**, a automação cria `v0.9.1` na aba Releases e anexa o ZIP + arquivo SHA-256 de integridade. Se já existir, **não altera uma release antiga**: é necessário incrementar a versão.
- Até a validação final do jogo, as releases são marcadas como **pré-lançamentos de testes**.
- Commits de documentação de planejamento não disparam exportações desnecessárias. O workflow também pode ser iniciado manualmente na aba Actions.
- Não marcar uma etapa do ROADMAP como 100% concluída sem teste real de jogo. CI verde comprova compilação/exportação, não gameplay.

**Publicação confirmada:** a primeira release v0.9.0 foi criada automaticamente pelo GitHub Actions com permissão `contents: write`, contendo ZIP Windows e arquivo SHA-256 de integridade. Novas versões usarão esse mesmo processo quando o número de versão for incrementado e o CI passar.

## O que significa teste concluído

| Etapa | O que confirma | O que NÃO confirma |
| --- | --- | --- |
| Verificação estática | Referências, invariantes, WAVs e modelos | Jogabilidade real |
| Importação Godot headless | Parser e recursos carregam sem erros críticos detectados | Comportamento da câmera/menus |
| Exportação Windows | EXE e pacote são gerados | Execução no Windows |
| Teste no notebook | Armas, lojas, ondas, FPS, áudio e controls reais | Ausência de todos os bugs futuros |

Se a exportação falhar, verificar os logs da execução, corrigir e recompilar. Nunca marcar uma etapa como concluída simplesmente por ter atualizado scripts.

## Checklist mínimo do jogador (versão 0.8)

- [ ] Abre pelo EXE, sem Godot.
- [ ] Menu inicial, configurações e pausa aparecem.
- [ ] Movimento WASD, mouse esquerdo/direito e F em lojas.
- [ ] Na onda 1, eliminar todos os inimigos inicia os 75 segundos de preparação, não encerra a partida.
- [ ] As armas, especialmente a escopeta, estão inteiras e opacas, sem faces vazadas.
- [ ] As mãos do jogador e dos soldados estão próximas das regiões corretas de empunhadura.
- [ ] Ao tomar tiro, aparece brevemente o indicador de direção no centro da tela (frente/direita/trás/esquerda).
- [ ] Headshot destaca a retícula em âmbar e concede bônus.
- [ ] Comprar e equipar arma, recarregar com R e usar suporte com 3/4.
- [ ] Treino reanima sem perder progresso; modo clássico encerra ao morrer.
- [ ] FPS e áudio no notebook são registrados.

**Meta de hardware, não desempenho medido:** Ryzen 5 7530U, 8 GB de RAM, 720p baixo com piso desejado de 30 FPS. O usuário deve confirmar o comportamento em seu Windows.

## Segurança e limitações

O EXE não está assinado digitalmente. O Windows pode apresentar aviso de reputação. Verificar se a origem é o repositório oficial antes de executar; não desativar antivírus por causa de um aviso. O jogo é offline, sem instalador e não requer permissões de administrador.

**Regra de entrega:** sempre anexar link de build Windows de execução bem-sucedida e manter status **concluído/parcial/pendente** no ROADMAP. A [0.9](TESTES_0_9.md) está disponível para teste real. Se o build falhar, apresentar erro e não chamar de jogável.
