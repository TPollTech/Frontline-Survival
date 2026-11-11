# Executável Windows — compilação e testes

**Projeto:** Frontline Survival  
**Versão de desenvolvimento:** 0.9  
**Entrega esperada:** arquivo ZIP contendo FrontlineSurvival.exe, FrontlineSurvival.pck (se o exportador usar pacote separado) e LEIA-ME.md.  
**Status:** a [execução 0.9](https://github.com/TPollTech/Frontline-Survival/actions/runs/42941790033) concluiu importação, smoke test, integridade e exportação Windows; a experiência visual/jogabilidade no notebook ainda está em validação.

## Como baixar sem instalar o Godot

1. Acesse **Actions > Windows playable build** no [repositório](https://github.com/TPollTech/Frontline-Survival/actions/workflows/windows-build.yml).
2. Abra uma execução com **marca verde (success)**, da branch **main**.
3. Em **Artifacts**, baixe **FrontlineSurvival-0.9-Windows**.
4. Extraia o ZIP inteiro numa pasta nova. **Não execute o EXE dentro do ZIP**, e mantenha o arquivo PCK ao lado do EXE, caso esteja presente.
5. Abra **FrontlineSurvival.exe** no Windows. Não é necessário instalar ou abrir o editor Godot.

**Não confundir:** uma execução com erro ou cancelada **não** é uma build pronta. O arquivo ZIP só deve ser enviado ao usuário como jogável quando o workflow estiver concluído com sucesso.

## Como gerar builds futuras

- O workflow `.github/workflows/windows-build.yml` executa automaticamente quando scripts, cenas, assets, configuração do projeto ou arquivos de exportação são alterados na branch main.
- Atualizações de planejamento Markdown, por si sós, não disparam compilação.
- Também é possível executar o workflow manualmente na aba Actions, usando **Run workflow**.
- O workflow instala Godot 4.4.1 e templates, importa recursos, executa verificação estática, exporta o Windows Desktop em modo release e envia os arquivos como artifact.
- Artifacts têm retenção de 30 dias; para distribuição permanente, publicar posteriormente uma Release versionada.

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
