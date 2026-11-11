# Executável Windows — compilação e testes

**Projeto:** Frontline Survival  
**Versão de desenvolvimento:** 0.9.2  
**Entrega esperada:** arquivo ZIP contendo FrontlineSurvival.exe, FrontlineSurvival.pck (se o exportador usar pacote separado) e LEIA-ME.md.  
**Status:** v0.9.2 avança o sistema de spawns e inclui um teste de integração obrigatório com 100 escolhas e duas ondas; [Releases](https://github.com/TPollTech/Frontline-Survival/releases) continua sendo o canal de download. O visual, a mira, a IA e o desempenho exigem validação no Windows.

## Baixar pelo GitHub Releases (padrão)

1. Acesse **[Releases do Frontline Survival](https://github.com/TPollTech/Frontline-Survival/releases)**.
2. Escolha a versão de testes que deseja baixar (por exemplo, **v0.9.2**).
3. Em **Assets**, clique no arquivo **FrontlineSurvival-v0.9.2-Windows.zip** (o nome muda conforme a versão).
4. Extraia em pasta nova, mantendo o arquivo EXE e o arquivo PCK juntos.
5. Execute **FrontlineSurvival.exe** sem precisar instalar o editor Godot.

O download é público e não depende do link de anexo do ChatGPT. As releases são preservadas como versões numeradas, ao contrário dos artifacts temporários das execuções.

**Builds intermediárias:** a página [Actions > Windows playable build](https://github.com/TPollTech/Frontline-Survival/actions/workflows/windows-build.yml) ainda disponibiliza Artifacts quando houver compilação bem-sucedida, mas não substitui o lançamento numerado.

## Padrão de lançamento das próximas versões

- Alterar `application/product_version` no `export_presets.cfg` para um **novo número** de versão (por exemplo, `0.9.3`), atualizar o número no menu/título e registrar mudanças no `docs/CHANGELOG.md`.
- Opcionalmente criar notas específicas em `docs/releases/v0.9.3.md` antes do commit da versão.
- Ao enviar para a branch `main` uma mudança em scripts/cenas/assets/exportação, o GitHub Actions gera e testa um ZIP Windows.
- **Se o CI passar e ainda não existir a release para essa versão**, a automação cria a nova tag numerada na aba Releases e anexa o ZIP + arquivo SHA-256 de integridade. Se já existir, **não altera uma release antiga**: é necessário incrementar a versão.
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
- [ ] Na onda 1, eliminar todos os inimigos inicia 30 segundos de preparação por padrão (ou o intervalo salvo no menu), sem encerrar a partida. Conferir resumo de onda e metas sem bloquear a loja.
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

## Integração de duas ondas na 0.9.2

A partir da 0.9.2, o workflow exige `tests/runtime_wave_qa.gd` antes de exportar: abre o Campo de Testes em modo headless, verifica pontos de spawn, bloqueios e duas transições de onda com sinais de abate. Uma falha interrompe o ZIP e a release. O teste é automatizado e **não substitui sessão real de 15 ondas nem validação de FPS/qualidade visual**.


## QA acrescentada na v0.9.15 — Núcleo Survival e Quaternius renderizado

A pipeline agora executa \`tests/survival_features_qa.gd\` para validar dinheiro por kills/challenges, precisão e headshot, além da integração de lojas, attachments, perks, prone e Última Chance. Um estágio Xvfb renderiza um humanoide Quaternius para produzir \`docs/qa/humanoid_current.png\`. **O teste de ossos da v0.9.14 não bastou para garantir aparência correta**; inspecionar o PNG gerado e solicitar avaliação em Windows.

- Não publicar release se GDScript não importar ou teste falhar.
- Conferir log \`QA_SURVIVAL_FEATURES_PASS\`, \`QA_RUNTIME_PASS\`, \`QA_HUMANOID_SNAPSHOT_PASS\` e exportação Windows.
- A captura de imagem verifica a malha real, mas não garante animação profissional, FPS ou mãos corretamente empunhando em todas as poses.
- Entregar sempre ZIP Windows/EXE/PCK/SHA256 em Releases numeradas.
- Após lançar, testar 15 ondas com configuração 30 s e também 75 s já salva, combinando perks, acessórios, compras de kit e Last Stand.
