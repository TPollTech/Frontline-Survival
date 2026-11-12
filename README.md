# Frontline Survival 0.9.17 — Campo de Testes

**Andamento auditado:** as Etapas 0–6 estão acompanhadas por checklists com marcações de implementação, CI e pendências reais. [Resumo atualizado](ROADMAP.md#8-estado-real-das-etapas-06--auditoria-12112026) · [Auditoria detalhada](docs/AUDITORIA_CHECKLISTS_2026_11_12.md). Nenhuma etapa está homologada integralmente no Windows.


**Projeto Godot 4.x Standard, FPS 3D offline para Windows**, com renderizador **Compatibility** e alvo inicial Ryzen 5 7530U / 8 GB RAM. Projeto original inspirado em mecânicas do gênero *Survival por ondas*. **Não contém modelos, áudio ou outros arquivos do Call of Duty.**

A versão **0.9.17** corrige três problemas visuais relatados na v0.9.16: a Red Dot deixou de ser uma caixa opaca e passou a ter aro vazado/lente/ponto emissivo durante ADS; o relatório de ondas e os avisos foram reduzidos a toasts compactos, sem painel vazio no centro; e o **protótipo Quaternius sem animações foi retirado das ondas públicas** (ainda disponível isoladamente para desenvolvimento). As mecânicas, armas e sons gravados continuam preservados. **A qualidade visual depende de aprovação jogando no Windows.**

[Release v0.9.17](docs/releases/v0.9.17.md) · [QA](docs/QA_V0_9_17.md)

## Histórico da v0.9.16

A versão **0.9.16** aperfeiçoa o **Campo de Testes**, sem criar mapas nem ondas extras: soldados comuns passam a procurar cobertura, recarregar, agachar e eventualmente deitar; inimigos agressivos continuam avançando. O menu inicial e a pausa foram preservados, com configurações divididas em **Gráficos, Áudio, Controles e Jogabilidade**, e o HUD recebeu acabamento mais consistente. Os recursos da 0.9.15 (perks, acessórios, Última Chance, 30s entre ondas, recompensas e relatórios) permanecem. **Avaliação real no Windows ainda pendente.**

## v0.9.16 — IA e interface

- **IA:** cobertura atrás de containers/obstáculos com sondas físicas, esconder/espiar/retornar, agachar/deitar e recargas WAV por classe; limite de 12 inimigos mantido.
- **Menu:** iniciar, pausar e retomar; opções por abas, com VSync, escala 3D, sensibilidade/inversão do mouse e feedback de jogo.
- **HUD:** cartões mais alinhados, painéis arredondados, vida crítica em destaque, interação contextual e opções de hitmarker/direção do dano.
- **Estabilidade:** carregadores finitos e tiros dependentes da linha de visão; registros automatizados e teste de jogo real ainda necessários.

[Notas v0.9.16](docs/releases/v0.9.16.md) · [QA](docs/QA_V0_9_16.md).

## Histórico da v0.9.15

A versão **0.9.15** implementa os recursos centrais pedidos: **perks, Última Chance, recompensas de metas, relatório estatístico ao concluir ondas, 30 segundos de intervalo padrão, Red Dot/Silenciador compráveis em todas as cinco armas, agachar e deitar**. Os modelos e WAVs gravados anteriores foram preservados. O soldado Quaternius continua experimental; esta versão acrescenta uma **captura renderizada de QA** para verificar a malha além das coordenadas dos ossos. **A jogabilidade real e o visual ainda precisam de avaliação no Windows.**

## Novidades da 0.9.15 — Núcleo Survival

- **Preparação entre ondas:** 30 segundos padrão em novas instalações; preferência antiga (como 75 s) continua salva; N antecipa.
- **Relatório:** abates pessoais, headshots fatais, precisão por disparo, tempo, dano e dinheiro por fonte.
- **Metas:** Rampage, Killstreak, Headshots, Quad Kill; duas por onda, +$500 cada quando alcançada.
- **Armas:** Red Dot, Holográfica, Silenciador e Compensador, adquiridos na estação **Armas** por arma, sem acessórios no início. Silenciador filtra o WAV gravado, sem efeitos sintetizados.
- **Perks:** Recarga Ágil, Mira Firme, Reação Rápida, Mobilidade e Resistência na estação de Suporte; um ativo por vez.
- **Última Chance:** cair, usar pistola de emergência por dez segundos e tentar eliminar um inimigo para se levantar; Kit de Reanimação pode ser comprado em Equipamentos.
- **Posturas:** C/Ctrl agacha e Z deita; colisão e altura da câmera acompanham o movimento.
- **Lojas paginadas:** teclas Q/E ou botões Anterior/Próxima para acessar todos os itens.
- **Quaternius:** ainda um único soldado por onda, com captura visual renderizada no CI e fallback ao modelo anterior se o rig falhar.
- **Sem novos mapas nem ondas:** prioridade em aperfeiçoar o Campo de Testes.

[Notas v0.9.15](docs/releases/v0.9.15.md) · [Checklist de QA](docs/QA_V0_9_15.md).

## Histórico: Hotfix 0.9.14 — Esqueleto humano corrigido

- Corrigidas rotações dos ossos: a animação agora parte da pose original, sem torcer braços, pernas e tronco.
- Adicionados testes estruturais de posição das mãos e das articulações, e fallback ao soldado antigo se o modelo deformar.
- A 0.9.13 falhou na inspeção visual do jogador e não deve ser usada para comparar personagens.
- **Nenhum mapa, arma, áudio ou regra de ondas foi alterado.**
- [Correção técnica e QA](docs/QA_V0_9_14.md) · [Release Windows](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.14).

## Histórico da 0.9.13

- **Um soldado humanoide por onda:** malha do Quaternius com esqueleto de 65 ossos em vez de primitivas geométricas.
- **Visual militar original:** colete, capacete, máscara/visor e bolsas discretos no modelo.
- **Caminhada/arma:** pose básica usando os ossos, mantendo a arma e a IA anteriores.
- **Comparação A/B:** o restante dos soldados continua com o modelo anterior. Falha de carregamento retorna ao modelo antigo.
- **Sem expansão:** os mapas, ondas, som PCM e demais sistemas não foram alterados.
- [Documentação da licença e do asset](docs/ASSET_QUATERNIUS_CC0.md) · [QA da 0.9.13](docs/QA_V0_9_13.md).

## Histórico da 0.9.12

- **Corrida tática:** arma baixa/inclinada e suporte do braço esquerdo se afasta; transição suave ao voltar ao combate.
- **Hitmarker sem crosshair:** confirmação mínima por 0,16 s ao acertar, headshot âmbar, sem apito.
- **Gore leve:** sangue nos impactos, corpos sem colisão que desaparecem após cerca de 17 s; limites para FPS.
- **Loot:** inimigos deixam arma e podem deixar munição; pegue com **F** próximo ao item, antes que desapareça.
- **Dano recebido:** arcos vermelhos curvos substituem barras quadradas.
- **Personagens:** coletes, ombros e mochilas mais arredondados; rig humanoide profissional ainda pendente.
- **Escopo:** NÃO ampliar mapas/ondas/transporte nesta rodada. [Plano de polimento](docs/M0_POLIMENTO_CAMPO_TESTES.md).

## Histórico da 0.9.11

- **Ondas especiais:** ameaças blindadas anunciadas por texto (sem apitos), com progressão mais justa.
- **Regras separadas:** scripts próprios para composição, quantidade e limites das ondas.
- **Mais QA:** 50 ondas simuladas e duas ondas reais no teste automatizado, preservando o limite simultâneo de 12 inimigos.
- **Áudio preservado:** cinco disparos e cinco recargas com gravações WAV/PCM da versão 0.9.10, sem ressuscitar sons antigos.
- **Objetivo v1.0:** continuar M0 (estabilização) e M2 (diretor de ondas) mantendo o mapa de testes e o hardware-alvo.

## Histórico da 0.9.3

- **Suporte aliado:** cabeça, capacete e máscara conectados ao torso com pescoço/gola.
- **Armas texturizadas:** metal e polímero com mapas procedurais, preservando cores originais e o desempenho.
- **Mais detalhes 3D:** pequenas peças acrescentadas às cinco categorias.
- **Recarga:** WAV mecânico próprio de cada arma, com volume menor e sem o apito genérico.
- **IA:** inimigos e aliados sondam obstáculos e tentam se recuperar quando presos.
- **Build Windows:** GitHub Releases continua sendo a forma principal de baixar.

## Melhorias da 0.9.2

- **Spawns com verificação física:** o jogo analisa pontos candidatos e rejeita áreas ocupadas e próximas do jogador ou das estações.
- **Distribuição menos previsível:** preferência por entradas fora da visão frontal quando existem opções seguras.
- **Sem nascimento forçado:** caso nenhum ponto seja válido, o sistema aguarda e tenta novamente.
- **Teste de integração Godot:** 100 spawns simulados e duas ondas completas com contadores verificados, como pré-requisito de build.
- **Lembrete:** o teste automatizado não equivale a jogar 15 ondas no notebook.

## Mudanças da 0.7

### Armas em primeira pessoa
- **Cinco armas com modelos 3D modulares**: corpo, carregador (quando aplicável) e mecanismo móvel (ferrolho/corrediça ou pump). São arquivos GLB gerados do zero, leves, e não cópias de outras franquias.
- **Recarga em estágios**: inclina o conjunto, desloca o carregador, reinsere e movimenta o mecanismo. A escopeta movimenta o guarda-mão/pump. Ainda é uma animação procedural simplificada, não captura de movimento profissional.
- **Animações contextuais**: troca de arma, recuo por disparo, balanço ao andar, arma abaixada ao correr, movimento de mão durante a recarga e golpe corpo a corpo.
- **Áudio atual:** cinco disparos e cinco recargas gravados em WAV PCM (atualizados nas versões 0.9.4–0.9.10). Os sons sintetizados anteriores foram substituídos; fontes e licenças das gravações estão documentadas nas notas da v0.9.5. Volumes continuam ajustáveis no menu.

### Soldados e feedback de combate
- Inimigos com **quadril, joelhos, ombros e cotovelos animados**: caminhada com flexão de joelho, arma posicionada à frente, recuo, breve reação a impactos e queda ao morrer.
- **Uniformes, coletes, bolsas e capacetes distintos** por tipo de arma e pela classe do inimigo. O soldado pesado tem proteção visual extra.
- Aliados chamados pelo suporte também têm pernas e braços articulados e **identificação azul** nos ombros.
- Rastros luminosos longos substituídos por **traços curtos e ocasionais**. Clarões pequenos e cônicos. Impactos transitórios dissipam com alpha, compatível com o renderizador Compatibility.

### Funcionalidades intencionalmente mantidas
- **Campo de Testes permanente**, incluindo **a textura original do asfalto** e as três estações físicas.
- **Sem menu rápido pelo B**: use **F perto da estação** de armas, equipamentos ou suporte.
- **Ondas sucessivas/infinitas**, sem encerrar automaticamente depois da primeira. Entre ondas, **30 s** por padrão em novas instalações, configuráveis de 30 a 120 s (preferências antigas preservadas); tecla **N** opcional para antecipar.
- **Modo de testes com reanimação**, mantendo número da onda, armas, dinheiro e abates. Modo de uma vida continua disponível nas configurações.
- **$1.200** iniciais no Campo de Testes para experimentar armas.
- Inimigos mudam de armamento por faixa de ondas (escopeta → SMG → fuzil → LMG).
- Reforços adquiridos na estação, chamados por **3** (esquadrão) e **4** (ataque aéreo).
- Configurações de volume geral/SFX/UI, sensibilidade, FOV, FPS e tela cheia.

## Baixar e jogar sem instalar o Godot (Windows)

**Download principal: [Releases do Frontline Survival](https://github.com/TPollTech/Frontline-Survival/releases).** Versões publicadas possuem número, changelog e ZIP próprio.

1. Entre em **[Releases](https://github.com/TPollTech/Frontline-Survival/releases)**.
2. Abra a versão mais recente **efetivamente publicada** em Releases. A `v0.9.15` é a versão em desenvolvimento; até o CI publicá-la, a última versão confirmada é a `v0.9.14`.
3. Na seção **Assets**, baixe o ZIP Windows correspondente à tag publicada, por exemplo **FrontlineSurvival-v0.9.17-Windows.zip** quando a v0.9.15 aparecer.
4. Extraia o ZIP inteiro para uma pasta, mantendo `FrontlineSurvival.exe` e `FrontlineSurvival.pck` juntos.
5. Execute `FrontlineSurvival.exe`. **Não é necessário abrir o editor Godot.**

**Plano B:** o [GitHub Actions](https://github.com/TPollTech/Frontline-Survival/actions/workflows/windows-build.yml) continua disponível para builds intermediárias que ainda não tiveram nova versão lançada. Não considere uma execução com erro ou cancelada como build válida. Detalhes em [BUILD_WINDOWS.md](docs/BUILD_WINDOWS.md).

### Para desenvolver pelo Godot

1. Clone este repositório e abra `project.godot` no **Godot 4.x Standard**, aguardando a importação das malhas e WAVs.
2. Pressione F5 e entre na partida.
3. Teste mira, recarga, compra por F, as ondas contínuas e a indicação direcional de ataques.

### Correções da 0.9.1

- Armas agora aplicam as **cores COLOR_0 existentes** nos modelos GLB por meio de material Godot opaco. Corrige a aparência branca da 0.9.0.
- Braços de aliados e inimigos com posicionamento de cotovelo em dois segmentos e proporções mais naturais, mantendo colete e distintivos azuis.
- **Sem crosshair de HUD**: alinhamento da mira pelo visor 3D ao centro da câmera; recuo apenas depois de calcular o tiro.
- Visores com abertura real e poste fino 3D, sem lente sólida bloqueando a visão.
- Removido o som agudo a cada acerto; conclusão da onda com batida grave curta e compra mais discreta.
- [Checklist visual e regressão da 0.9.1](docs/TESTES_0_9_1.md).
- [CHANGELOG.md](docs/CHANGELOG.md) especifica a situação de cada incremento.

**As correções da 0.9.1 representam implementação parcial das Etapas 1 (armas/mira), 2 (soldados) e 5 (HUD/áudio).** A estabilidade completa e a aprovação visual exigem teste real no Windows.

## Controles

| Tecla / botão | Ação |
|---|---|
| WASD / mouse | Andar e olhar |
| Mouse esquerdo / direito | Atirar / mirar |
| Shift / C ou Ctrl / Espaço | Correr / agachar / pular |
| F | Acessar/fechar a estação de compra ao alcance |
| 1 / 2 ou roda do mouse | Arma principal / pistola |
| R | Recarregar |
| E | Corpo a corpo |
| G | Granada |
| 3 / 4 | Chamar esquadrão comprado / utilizar ataque aéreo comprado |
| N | Antecipar a próxima onda apenas na preparação |
| Esc | Pausa e configurações |

## Arquitetura e desempenho

- `scripts/player.gd`: FPS, combate e animação procedural das peças das armas.
- `scripts/enemy.gd`: IA básica, kits por onda, animação articular e impactos.
- `scripts/ally.gd`: IA de aliados e rig leve.
- `scripts/main.gd`: mapa de testes, ondas, compras, HUD, efeitos e reforços.
- `assets/models/*.glb`: cinco armas inteiras para NPCs e 14 grupos modulares para a câmera em primeira pessoa.
- `assets/audio/weapons/*.wav`: cinco arquivos de som novos.
- `tools/build_weapons.py`: gerador editável de armas; requer Python + NumPy + Trimesh apenas **para regenerar modelos**, não para jogar.
- `tools/verify_project.py`: checagens estáticas de integridade, referências, WAVs, modelos e mecânicas principais.

**Limites de fidelidade:** os rostos, mãos e soldados ainda são geometria procedural relativamente simples. Não são personagens realistas com rig profissional, animações capturadas ou texturas PBR de alta resolução. O foco é avançar a qualidade visual sem perder desempenho no notebook.

**Verificação:** o projeto possui testes estáticos e uma rotina de importação/exportação na seção Actions. A conclusão de uma execução confirma apenas a compilação, **não** uma partida real no Windows nem o desempenho no notebook. A Etapa 0 permanece em validação até o checklist ser executado.

Leia `docs/TESTES_0_7.md` para uma sequência rápida de testes e como identificar eventuais erros.

## Planejamento das próximas versões

As melhorias propostas, etapas, prioridades, critérios de aceite e regras de desenvolvimento estão em **[ROADMAP.md](ROADMAP.md)**. Antes de programar novas funcionalidades, validar a etapa correspondente neste planejamento.
