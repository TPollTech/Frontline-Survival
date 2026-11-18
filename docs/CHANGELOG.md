# Frontline Survival — Histórico de versões

## Estabilização funcional — movimento de esquadrões em passagens estreitas

- Inimigos agora consideram a proximidade de companheiros vivos durante o avanço para reduzir congestionamentos no mesmo corredor.
- O vetor de afastamento é horizontal, limitado e calculado em intervalos de 0,16–0,24 s para preservar desempenho com até 12 inimigos simultâneos.
- A direção para contornar paredes mantém prioridade; cobertura, recarga e ataque continuam regidos pelas mecânicas existentes.
- Teste Godot com seis inimigos e paredes físicas verifica a separação dos lados, ausência de vetores inválidos e desconsideração de mortos.
- **Limitação:** é separação local, não um navmesh global nem um teste real de percurso completo. Corredores longos e ondas prolongadas no Windows ainda precisam de aprovação.

## Estabilização funcional — inimigos desviam de paredes sem oscilar

- O inimigo mantém o mesmo flanco enquanto o obstáculo continua no caminho; as verificações frequentes deixam de sortear novos lados e de cancelar o desvio antes de passar pelo bloqueio.
- A navegação também identifica obstáculos quando o jogador está próximo, mas fora da linha de visão (mesmo dentro da distância desejada de ataque).
- O desvio agora se combina uma única vez com o alvo tático; recargas legítimas não são classificadas como travamento.
- Se uma rota de cobertura ou peek realmente travar, o NPC abandona aquele waypoint e volta ao avanço com um novo desvio; não é teletransportado, eliminado ou recompensado.
- Teste com parede física, persistência da direção e recuperação de cobertura no Godot.
- **Ainda parcial:** isto é direção local, não navegação completa por navmesh; testar cenários com múltiplos contêineres, corredores e 15 ondas no Windows.

## Estabilização funcional — contadores confiáveis das ondas

- Durante combate, o controlador reconcilia periodicamente o contador de inimigos vivos com os NPCs realmente presentes e ativos na cena.
- Evita duas falhas: encerrar uma onda prematuramente quando um inimigo ainda está vivo e manter uma onda travada após remoção inesperada de um NPC sem sinal de derrota.
- Cadáveres, NPCs de outras cenas e elementos de suporte não entram na contagem. A reconciliação **não concede dinheiro nem abates**, preservando a economia.
- Teste integrado Godot cobre contagem zerada com inimigo real, contagem inflada e remoção de inimigo sem recompensa.
- **Não resolve, por si só, inimigos vivos presos atrás de paredes**; IA/rotas e 15 ondas no Windows continuam pendentes.

## Estabilização funcional — compras sem desperdício de créditos

- Estação de equipamentos não cobra por munição, vida ou colete quando seus respectivos recursos já estão no máximo.
- A interface identifica esses três itens como `CHEIO` e desativa o botão, enquanto compras parciais permanecem disponíveis.
- As rotas por teclado/controle de compra também verificam recursos cheios antes de retirar dinheiro; callbacks antigos após fechar a loja não podem comprar.
- Regressão no Godot testa UI, compras cheias, parciais, repetidas e loja fechada com saldo e inventário.
- **Validação Windows pendente**: itens visuais da etapa 4 ficam adiados em favor da estabilidade do loop.

## 0.9.25 — Correção de dedos projetados e antebraços esticados (Windows)

- Corrigido o defeito visual observado no jogo real na v0.9.24: falanges muito projetadas pelo cano e antebraços longos e grossos próximos da câmera.
- Redimensionados ombro, cotovelo, punho, palma e dedos, com ombros ancorados à distância de cada arma para impedir deformações de proporção no FPS.
- As falanges agora curvam de volta à palma; polegares foram recolhidos e afinados mantendo articulações e resposta ao disparo/recarga.
- Testes Godot de proporção por arma, cinco classes, além do QA de integração e montagem OpenGL com nove poses.
- **Etapa 4 continua PARCIAL:** o encaixe visual de dedos e recarga ainda depende de teste no Windows; estes são modelos procedurais.

[Notas de versão e roteiro de comparação](releases/v0.9.25.md)

---

## Etapa 4 — correção visual após captura real do jogador

- Corrigida geometria do rig FPS: falanges deixaram de apontar em direção ao cano e agora dobram de volta para a palma; polegares também recolhidos.
- Reduzido o comprimento e a espessura desproporcionais dos antebraços; os ombros passam a seguir a posição real do punho de cada arma, em vez de ficar num Z fixo distante da câmera.
- Testes de regressão Godot verificam, nas cinco classes, comprimento dos braços e distância dos dedos à palma, evitando reaparecimento dos segmentos projetados.
- Mantidos recarga sincronizada, troca de arma, ADS e munição; aspecto final ainda depende de jogo real no Windows.
- **Status: correção dirigida ao problema visível no screenshot; não é aprovação final de anatomia.**

## 0.9.24 — Teste Windows: anatomia e recarga das mãos FPS

- Atualizado o rig procedural com polegares articulados em duas juntas, acompanhando gatilho e abertura/fechamento da mão de apoio durante recarga.
- SMG, fuzil e LMG usam contatos individuais com seus carregadores e tambor; escopeta acompanha a transformação real da bomba.
- Mantidos os refinamentos de recuo visual específico por arma, poses ADS, entrada/saída da troca, respiração e proteção do cano perto de paredes desde v0.9.23.
- Testes de regressão para cinco classes, verificação de distância entre mão e mecanismo, capturas renderizadas de nove poses e QA Godot integrados.
- **Etapa 4 permanece PARCIAL** até verificar visualmente anatomia, contato dos dedos, recarga contínua e FPS no Windows.

[Notas e roteiro de teste](releases/v0.9.24.md)

---

## Etapa 4 — polegares articulados e empunhadura

- Polegares das luvas FPS agora têm juntas independentes na base e na ponta, acompanhando as outras falanges.
- O polegar do gatilho reage ao disparo; o de apoio abre e fecha durante recarga, mantendo a pegada da escopeta.
- Regressão para as cinco armas verifica criação, movimento e retorno das juntas; não altera mecânicas de tiro.
- **Parcial:** aprovação visual do encaixe entre dedos e peças e do desempenho depende do Windows.

## Etapa 4 — escopeta: mão acompanha a bomba física

- Mão esquerda da escopeta agora acompanha o contato real da peça `action` (bomba), inclusive posição e rotação durante recarga e ciclo do mecanismo.
- Reposicionada a pegada de repouso para a superfície inferior da bomba; removido deslocamento genérico que não considerava o modelo.
- QA no Godot verifica distância entre palma e a bomba animada.
- **Parcial:** textura, clip de dedos e fluidez real no Windows ainda precisam de avaliação.

## Etapa 4 — encaixe da mão de apoio nos carregadores

- SMG, fuzil e LMG agora têm pontos de pega definidos nas coordenadas das malhas originais do carregador e tambor, em vez do mesmo deslocamento fixo.
- A mão acompanha a transformação real do carregador animado (posição/rotação/escala), compensando a posição do rig e voltando para o apoio quando a recarga acaba.
- QA físico no Godot mede a distância entre a palma e o ponto de contato em cada arma, incluindo maior deslocamento necessário para o tambor da LMG.
- **Status parcial:** referência geométrica aproximada ainda exige avaliação visual dos dedos, da mão, da recarga e do acabamento no Windows.

## Etapa 4 — QA renderizado das animações

- Montagem de QA OpenGL ampliada para nove quadros: cinco armas em repouso, fuzil ADS, recarga do fuzil, bomba da escopeta e disparo da pistola.
- As poses usam peças e dedos articulados atuais, sem introduzir arquivos de animação externos ou alterar gameplay.
- **Parcial:** poses estáticas não substituem vídeo de transições reais nem homologação visual no Windows.

## Etapa 4 — articulação funcional dos dedos das luvas

- Substituídos os dedos estáticos de duas peças por duas juntas por dedo, preservando os nomes das malhas e a estrutura de ombro/cotovelo/punho.
- O indicador da mão do gatilho dobra brevemente durante o tiro; as outras falanges fecham durante corpo a corpo.
- A mão de apoio abre os dedos durante a retirada do carregador e fecha novamente no retorno à empunhadura, evitando dedos rígidos durante o movimento.
- QA verifica os pivôs e a abertura/fechamento no Godot para todas as cinco armas, inclusive ausência de mão extra na pistola.
- **Etapa ainda parcial:** contato real entre dedos e armas, arte anatômica e desempenho no Windows permanecem para aprovação.

## Etapa 4 — recuo animado por classe de arma

- Recuo visual da pistola, SMG, fuzil, escopeta e LMG agora tem amplitudes distintas no viewmodel e nas articulações do braço, preservando dano, dispersão e cadência originais.
- Em ADS, o movimento do modelo é atenuado; o mecanismo (ferrolho/slide) mantém o ciclo existente.
- Testes de regressão verificam amplitude relativa e retorno ao repouso nas cinco classes.
- **Status parcial:** avaliação de realismo, sensação e FPS no Windows continua necessária.

## Etapa 4 — inspeção renderizada de armas e mãos

- O workflow agora produz montagem OpenGL das cinco armas em hipfire e do fuzil em ADS, mostrando os modelos e o rig de mãos efetivamente usados pelo Godot.
- Montagem e layout documentados em `docs/qa/viewmodel_layout.md` com artefato próprio no GitHub Actions. Isso facilita identificar proporções e clipping nas mãos sem afirmar homologação visual.
- **Etapa 4 permanece parcial:** ainda é necessário avaliar animações dinâmicas e o jogo no Windows.

## 0.9.23 — Testes da etapa 4: troca de armas e proteção contra paredes (Windows)

- Troca manual com animação de saída da arma antiga antes de montar e animar a nova; equipação forçada por loot/loja permanece imediata.
- Disparo, recarga, melee e ADS respeitam a transição de troca de armamento; cancelamento de troca incluído na regressão.
- Respiração sutil em idle, sway curto durante caminhada, mantendo a animação tática de corrida.
- Raycast físico detecta parede à frente e suaviza retração/inclinação da arma no FPS. Pistola com distância de segurança menor; ADS reticle desativado se a arma estiver perto demais de obstáculo.
- Testes Python e Godot das correções anteriores **passaram** (74 testes e 773 verificações integradas; 2.416 de ondas). A versão 0.9.23 deverá passar novamente pelo CI antes de ser disponibilizada.
- **Status: Etapa 4 PARCIAL.** Clipping visual real de luvas, carregadores e canos e rig 3D definitivo precisam de aprovação no Windows. Android ainda não foi exportado.

[Notas para testar](releases/v0.9.23.md)

---

## Etapa 4 — proteção de arma contra paredes próximas

- O modelo FPS agora recua e inclina suavemente ao aproximar arma/cano de uma parede detectada por raycast físico; o colisor, a câmera e a trajetória dos projéteis permanecem inalterados.
- Pistola tem menor alcance de retração que SMG, fuzil, escopeta e LMG; ADS/retícula física são desativados quando a arma está demasiado próxima de uma parede.
- Regressão com parede física no Godot testa aproximação, diferenças entre pistola e arma longa e retorno ao remover a obstrução.
- **Parcial:** protege contra geometria do mundo à frente da câmera; a aprovação visual de possíveis interseções entre dedos, arma e câmera permanece pendente no Windows.

## Em desenvolvimento após v0.9.22 — Etapa 4, transições e enquadramento

- Troca manual agora tem saída curta da arma antiga antes de montar a nova; compras/loot/recuperação por equipação forçada seguem imediatas.
- Disparo, recarga e corpo a corpo bloqueados durante a troca; ADS aguarda a arma nova terminar de equipar.
- Respiração discreta na posição parada e oscilação própria da caminhada, sem alterar câmera ou trajetória dos tiros.
- QA no Godot verifica saída/entrada da arma, cancelamento, recarga, movimento visual e posição de palmas no enquadramento para as cinco armas.
- **PARCIAL:** estes testes não substituem revisão visual de contato/atravessamentos no Windows nem o modelo de luvas definitivo. A release v0.9.22 antecede esta mudança.

## 0.9.22 — Teste da Etapa 4: animações e mãos (Windows)

- Novo rig procedural leve com ombros, cotovelos e punhos independentes e dedos de duas articulações aparentes nas luvas; cinco armas cobertas.
- Mão de apoio sincronizada com a recarga de SMG, fuzil, LMG e bomba da escopeta; retorno à empunhadura após concluir/cancelar.
- Transições procedurais de recuo, equipar, corrida, corpo a corpo e recarga agora movimentam articulações locais. ADS não permanece ativo durante recarga.
- Testes de regressão e integração no Godot aprovados na execução anterior: 58 testes Python, 744 asserções Godot, 2.416 de ondas e 23 Survival.
- **Status da Etapa 4: PARCIAL.** Rig criado em código, não um modelo anatômico GLB final. Ainda falta avaliar clipping, mãos/dedos, transições e visual em Windows real.

[Notas e roteiro de teste](releases/v0.9.22.md)

---

## Registro de implementação da Etapa 4 após v0.9.21

- Mão de apoio dos três armamentos longos com carregador (SMG, fuzil e LMG) acompanha o ciclo visual do carregador durante a recarga, voltando suavemente à empunhadura ao finalizar/cancelar.
- Escopeta: mão de apoio segue a bomba móvel durante a animação de recarga, em vez de simular troca de carregador.
- Entrada em ADS deixa de permanecer ativa durante a recarga; preservados FOV, mira física e ausência de crosshair 2D permanente.
- Regressão em Godot verifica offsets e retorno das mãos em cada tipo de arma, sem alterar cadência, dano, WAV ou geometria de modelos.
- **Status:** refinamento parcial; ainda falta rig anatômico de mãos e avaliação visual real de empunhadura/recarga/ADS no Windows. Sem nova build Windows nesta rodada.

## 0.9.21 — CT-03: postura física e câmera (build para homologação Windows)

- Corrigida a câmera para não ultrapassar o topo da cápsula durante a transição de agachar/deitar.
- Corrida e salto só reativam depois que o colisor voltou à altura ereta; cenário de QA agora valida quadros intermediários a 60 FPS.
- Sob teto baixo, recuperar-se da Última Chance conserva a postura física deitado (não mantém um estado `downed` obsoleto).
- QA de integração com teto físico: bloqueio de levantar, rastejar/voltar ao agachamento, posição dos pés, câmera e recuperação sob cobertura.
- 13 contratos Python de regressão para postura, salto, sprint, ADS e colisão.
- **Status:** testes Python e Godot integrados passaram no CI; homologação real do jogador no Windows permanece pendente.
- **Release:** v0.9.21 com ZIP Windows exportado somente após os gates de QA.

[Notas da versão](releases/v0.9.21.md)

---

## 0.9.20 — Build de testes atualizada: FPS e combate

- Corrigido o salto no Godot 4.4: `Input.is_key_just_pressed()` não existe; o código agora detecta a transição de Space pressionado para solto, sem auto-bunny-hop.
- Consolidadas as alterações posteriores à 0.9.19: captura/foco do mouse, câmera, FOV e animação de corrida proporcional ao movimento real, e transições ADS.
- Tiro e recarga: impedir disparos durante equipar/corpo a corpo, manter cooldown entre trocas, impedir munição criada após recarga cancelada, proteger menus/lojas e Última Chance.
- Troca de armas: lembrar a última primária realmente equipada; pistola e lojas permanecem funcionais.
- Suíte Python de regressão integrada ao workflow e novos cenários de QA do Godot para combate, recarga e troca.
- **Finalidade:** build Windows para teste do jogador. QA em Godot/CI e desempenho/jogabilidade no Windows precisam ser observados antes de marcar a etapa como concluída.

[Notas da versão](releases/v0.9.20.md)

---

## 0.9.19 — Reconstrução estrutural do HUD de combate

- Removidos os polígonos grandes preenchidos dos quatro instrumentos de combate; somente rótulos e linhas leves nas bordas da tela.
- Novo layout ancorado por região (topo esquerdo, centro, topo direito, baixo esquerdo e baixo direito), independente de coordenadas rígidas 1280×720.
- Créditos, número de onda, vida e munição em fontes grandes; recarga, reservas, acessórios e recursos em fontes menores.
- Banner, relatório de onda e notificação simples disputam a mesma área de eventos por prioridade, sem aparecer sobrepostos.
- Centro para mira/ADS e hitmarker ancorado; desafio completo exibido somente durante TAB e prompt F reduzido.
- Screenshot de QA em Godot OpenGL/Xvfb para análise visual; nada muda nas regras de combate e compras.
- **Status inicial:** código implementado, CI e revisão visual aguardando resultados.

[QA v0.9.19](QA_V0_9_19.md) · [Release](releases/v0.9.19.md)

---

## 0.9.18 — HUD tático, animação original de sprint, empunhadura dos NPCs e granada física

- Instrumentos do HUD do combate convertidos de caixas opacas para componentes angulares com linhas finas, bordas de tela e menor obstrução visual.
- Corrida militar procedural com arma recolhida/abaixada, inclinação e balanço do braço de apoio com transições suavizadas; não reproduz arquivos de COD.
- Rifle de inimigos e aliados agora posicionado em altura de peito/ombro, com pontos de apoio adequados ao IK existente.
- `G` lança projétil `RigidBody3D` físico com arco, ricochete e fusível 2,45 s; explosão com fumaça, choque, iluminação, dano com oclusão por cobertura.
- Gravação real de explosão `Kenney CC0` (OGG) baixada/checada no CI e copiada para o jogo; modelos e WAVs anteriores preservados.
- **STATUS:** implementação concluída em código; CI e teste visual Windows determinarão o aceite. Testar desempenho do Ryzen 5 7530U.

[QA v0.9.18](QA_V0_9_18.md) · [Release](releases/v0.9.18.md)

---

## 0.9.17 — Red Dot vazada, HUD compacto e rollback visual dos NPCs

- Acessórios Red Dot/Holo têm visor físico vazado, lente translúcida e ponto emissivo, visível apenas em ADS. Nenhuma retícula 2D permanente.
- O relatório de onda virou toast de 2 linhas com resultados, bônus, headshots e precisão (4 segundos), no alto, sem caixa preta central.
- Removidos os avisos duplicados de fim de onda; banners de combate e prompts de interação foram reduzidos.
- Desabilitado o soldado experimental Quaternius nos spawns das partidas públicas, até haver rig/animações homologados.
- Nenhuma alteração dos WAV/PCM, sistemas de compras, perks, IA ou progressão. **CI não substitui inspeção visual.**

[QA v0.9.17](QA_V0_9_17.md) · [Notas da release](releases/v0.9.17.md)

---

## 0.9.16 — IA tática, menus por categoria e HUD refinado

**Escopo:** Campo de Testes, sem novos mapas ou ondas. **Status: implementação e CI aprovados** ([run 43166124429](https://github.com/TPollTech/Frontline-Survival/actions/runs/43166124429)), **homologação visual e de gameplay pendente.**

- NPCs soldados comuns analisam cobertura estática, procuram proteção, agacham/deitam e alternam exposição para disparar. A decisão é limitada para não elevar demais a CPU integrada.
- Carregadores reais por classe: 8 escopeta, 30 SMG/fuzil e 60 LMG; recarga com WAVs já gravados, sem tiros infinitos.
- Reação a dano e precisão menos automática; corredor continua agressivo e pesado segue pressionando.
- Gráficos, Áudio, Controles e Jogabilidade agora têm abas separadas no menu já existente de início/pausa.
- Persistência de escala de renderização 3D, VSync, mouse invertido, hitmarker e arcos de dano, além dos controles existentes.
- HUD com painéis consistentes, relatório mais legível, interação contextual e saúde crítica destacada.
- Testes de menus, escala 3D, recarga/postura e pontos de cobertura incluídos na integração.
- **Preservados:** perks, desafios, attachments, Last Stand, 30 s padrão, WAV PCM, Quaternius A/B, campo de testes e três lojas F.

[QA v0.9.16](QA_V0_9_16.md) · [Release](releases/v0.9.16.md)

---

## 0.9.15 — Survival Core: perks, metas, attachments, prone e autorreanimação

**Estado:** CT-01 a CT-06 implementados em código; CI e visual Windows obrigatórios antes de afirmar conclusão. **Sem mapas/ondas/veículos novos.**

- Tempo entre ondas **30 s padrão**, opções 30–120 no menu; configurações antigas preservadas.
- Motor independente de estatísticas: tiros por disparo (escopeta sem multiplicar pellets), precisão, headshots, dano, tempo e créditos por fonte; relatório temporário após onda.
- Desafios Rampage (quatro kills rápidas), Killstreak (cinco sem sofrer dano), Headshots (cinco abates na cabeça) e Quad Kill (mesma explosão). Duas metas por onda, +$500 por meta, sem duplicidades.
- Lojas paginadas: red dot/holográfica e silenciador/compensador para **cada uma das cinco armas**, comprados sem acessórios iniciais; acessórios em 3D, com som gravado filtrado quando suprimido.
- Cinco perks compráveis no suporte (um ativo por vez), com efeitos reais de velocidade de recarga, dispersão, ADS, mobilidade e dano recebido.
- Agachar/deitar com altura de câmera e cápsula, checagem de teto para não atravessar o mapa.
- Última Chance: estado ferido, pistola com oito tiros de emergência, dez segundos para um abate pessoal; Kit de Reanimação de um uso comprado em equipamentos.
- Teste determinístico de recompensas e testes Godot de compras/perks/armas/postura/queda adicionados.
- Novo teste visual renderiza o Quaternius em Xvfb, guarda PNG de QA e preserva fallback. Isto **não valida profissionalmente** a animação.

[Notas v0.9.15](releases/v0.9.15.md) · [QA v0.9.15](QA_V0_9_15.md)

---

## 0.9.14 — Correção do humanoide deformado (hotfix)

**Motivo:** o screenshot real do jogador **reprovou** a aparência do protótipo da v0.9.13: braços levantados, antebraços cruzados e malha distorcida. **Correção estrutural**, não adição de conteúdo.

- Corrigido o erro de manipular `Skeleton3D`: antes a animação sobrescrevia as rotações originais dos ossos do Quaternius; agora preserva a **pose base** e compõe apenas deltas pequenos.
- Os braços e a coluna mantêm sua orientação nativa, e o movimento das pernas também parte do repouso correto.
- Novo critério de sanidade visual no runtime: mãos abaixo da cabeça, cabeça acima do quadril, pés abaixo do quadril e altura humana plausível. Em falha, o soldado antigo aparece automaticamente.
- Testes Godot bloqueiam rotações de ossos excessivas. Na versão defeituosa a altura das mãos era **2,279/2,287**, com a cabeça em **2,200**; após a correção, as mãos estão em **1,979/1,990**, com a cabeça em **2,200**.
- CI aprovado, Windows ZIP publicado e SHA256 disponíveis no [GitHub Releases v0.9.14](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.14).
- **PENDENTE:** inspeção visual do jogador no Windows antes de migrar outros soldados; ainda faltam animações profissionais do Quaternius.

**Evitar a v0.9.13:** ela falhou na validação visual.

[QA v0.9.14](QA_V0_9_14.md) · [Notas de correção](releases/v0.9.14.md)

---

## 0.9.13 — Protótipo de soldado humanoide Quaternius (CC0)

**Estado:** integração do modelo, skeleton e testes automatizados **CONCLUÍDOS (CI)** após compilação; **visual/animação: PARCIAL**, aguardando aprovação jogando.

- Integração de um GLB humanoide skinned (Quaternius Universal Base Characters, CC0, ~741 KB, 65 ossos) com a origem documentada em [ASSET_QUATERNIUS_CC0.md](ASSET_QUATERNIUS_CC0.md).
- Apenas o primeiro soldado comum de cada onda recebe o novo corpo, preservando os demais NPCs para comparação direta.
- Equipamento tático próprio (colete, capacete, visor, bolsos), material de tecido verde e pose procedural de empunhadura/caminhada no esqueleto.
- O corpo procedural antigo fica oculto apenas nesse soldado; o modelo antigo é mantido automaticamente se o importador não encontrar um esqueleto válido.
- IA, mira, colisão, arma, morte, loot, sangue, ondas, lojas, assets sonoros PCM, desempenho alvo e Campo de Testes preservados.
- QA da cena com verificação de ossos, corpo oculto, arma visível e integração com mortes/ondas.
- **Não** inclui animações da Universal Animation Library nem substitui todos os soldados/aliados. Próxima decisão depende de teste real no Windows.

[Notas da release](releases/v0.9.13.md) · [QA](QA_V0_9_13.md)

---

## 0.9.12 — Corrida tática, acertos, sangue, corpos e coleta

**Prioridade:** polimento do Campo de Testes (M0/M1). Usuário confirma ter alcançado a onda 10; expansões de mapas, ondas e transporte ficam em espera até o protótipo ficar convincente. **Estado da jogabilidade: PARCIAL**, ainda que CI passe.

- Corrida com arma inclinada/baixada, sway mais marcado e mão esquerda de suporte afastada; interpolação para não parecer caminhada acelerada.
- Hitmarker branco/âmbar com quatro traços pequenos e duração 160 ms, **sem mira estática nem sinal sonoro**.
- Pequenos efeitos transitórios de sangue nos impactos (limite de 14).
- Inimigos deixam corpos sem colisão por até 17 s (máximo 12), arma e ocasional munição coletáveis por F. Loot limitado a 18 itens por 20 s.
- Quatro indicadores curvos e discretos de direção de dano substituem barras retas.
- Silhuetas de coletes e mochilas arredondadas; armas de soldados posicionadas mais à frente. Isso não substitui rig humanoide profissional.
- QA de runtime ampliada para corrida sem disparo, hitmarker, drops, sangue, corpo após morte, 2 ondas e integridade do áudio gravado.
- **Sem alteração** dos arquivos de áudio gravado, das armas do jogador ou da economia/arquitetura de ondas anterior.

[Plano de polimento](M0_POLIMENTO_CAMPO_TESTES.md) • [QA 0.9.12](QA_V0_9_12.md) • [Notas da release](releases/v0.9.12.md)

---

## 0.9.11 — Ondas especiais com aviso e testes de progressão

**Avanço:** M0 (qualidade/CI) e M2 (diretor de ondas, **PARCIAL**). Builds anteriores v0.9.4–v0.9.10, gravações de áudio, materiais e alterações das armas permanecem intactas.

- Nova `scripts/wave_rules.gd`: limites de quantidade, composição de tipos e ameaças blindadas anunciadas.
- Primeira onda com **um pesado na 10**; um pesado na onda 15; dois nas ondas-marco a partir da 20. Fora desses marcos, sem pesado aleatório inesperado.
- Aviso visual de ameaça blindada, **sem áudio novo ou apitos**.
- `tests/wave_rules_qa.gd` simula 50 composições, 2.416 assertions, 2.150 inimigos planejados e 16 pesados de marco (não são 50 ondas jogadas).
- `tests/runtime_wave_qa.gd`: duas ondas com inimigos reais + conferência do HUD da onda 10.
- Pipeline do GitHub Actions passa a exigir o novo teste antes de gerar o executável.
- Revisão do README: áudio atual é **gravado e importado sem perdas (PCM)**, não os efeitos sintetizados da versão antiga.

**QA:** [checklist v0.9.11](QA_V0_9_11.md). O teste de 15 ondas no Windows, desempenho real, rig e modelos continuam pendentes; não considerar M0/M2 100% concluídos.

---

## 0.9.10 — Áudio PCM sem perdas

- WAVs de disparo e recarga importados como PCM de 16 bits, sem QOA. O teste em Godot compara os dados das amostras importadas com os WAVs de origem.

---

## 0.9.9 — Som restrito a disparo e recarga

- Removidos os efeitos antigos de fim de onda, compra e explosão. A pasta de áudio contém apenas os dez WAVs de disparo e recarga.

---

## 0.9.8 — Áudio somente por WAV

- Aviso de fim de onda carregado de WAV, sem geração de áudio durante o jogo.

---

## 0.9.7 — Limpeza de áudio legado

- Removidos os WAVs genéricos de disparo, impacto e recarga. Disparos e recargas usam os WAVs próprios de cada arma.

---

## 0.9.6 — Disparos gravados

- Gravações carregadas explicitamente por classe, incluindo uma aproximação de 5,56 mm para a LMG.
- Tiros do jogador mais presentes e disparos posicionais para inimigos e aliados.

---

## 0.9.5 — Recargas com gravações mecânicas

- Substituídas as cinco recargas sintetizadas por sequências de gravações de manuseio. Fontes e licenças nas [notas da versão](releases/v0.9.5.md).
- O som de recarga é interrompido ao trocar de arma, reabastecer ou morrer.

---

## 0.9.4 — Armas e mira

- Pistola e AK-47 remodeladas, com alinhamento das miras e da boca do cano atualizado.
- Alça da LMG deslocada do eixo da mira.
- Quatro disparos gravados com reprodução polifônica. Créditos e teste manual nas [notas da versão](releases/v0.9.4.md).

---

## 0.9.3 — Suporte articulado, materiais, foley e IA local

**Estado:** implementação submetida aos testes do Godot; apresentação de armas/aliados e IA permanecem **PARCIAIS** até validação jogando.

- Cabeça e capacete dos aliados presos ao mesmo pivô, com pescoço e gola conectando a silhueta do torso. Este item responde ao efeito de cabeça solta da captura.
- Metal e polímero com mapas de textura/normal procedurais originais, projeção triplanar e paleta GLB preservada.
- Mais pequenos detalhes nas cinco classes de armas; peças ainda estilizadas e econômicas para GPU integrada.
- Recargas mecânicas originais separadas por arma (pistola, SMG, fuzil, escopeta, LMG), com menor volume.
- Etapa 2: sondas leves de obstáculos e recuperação de perseguição quando NPCs ou aliados ficam presos; sem teleportes.
- Gerador determinístico em Python, exportação automática Windows e sincronização de GLBs, texturas e WAVs na branch main.
- Testes estáticos e de duas ondas ampliados com checagens de sons, materiais, cabeça dos aliados e resistência básica de integração.

**CI/Release:** [v0.9.3](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.3). A existência da Release com ZIP e SHA-256 confirma exportação; o teste real no Windows continua necessário.

---

## 0.9.2 — Spawn seguro e teste integrado de ondas

**Estado:** melhoria implementada; homologação em jogo **PARCIAL**. Integração headless verifica o fluxo de duas ondas e pelo menos 100 escolhas de spawn; teste prolongado de 15 ondas permanece pendente.

- **Etapa 2B:** seletor reutilizável de spawns, respeitando distância mínima de 10m do jogador, 4,75m das estações e raio de ocupação física de 0,72m. Os números são provisórios para Campo de Testes.
- Preferência suave por entradas fora da direção de visão do jogador, sem tornar spawn totalmente previsível.
- Se o ponto não for seguro, não cria NPC: aguarda 0,6s e tenta novamente. Log de advertência após tentativas recorrentes; sem descartar inimigos da fila.
- Geração de inimigos movida do processamento de quadros para **_physics_process**, necessário para consultar o espaço de colisão de maneira correta.
- **Etapa 2A / QA:** cenário automatizado `tests/runtime_wave_qa.gd` no GitHub Actions carrega a cena, inicia partidas, examina os pontos de entrada e verifica duas transições de onda com mortes reais dos NPCs e contadores coerentes.
- Nenhuma alteração gráfica em armas ou soldados neste incremento: os defeitos/ajustes visuais da v0.9.1 ainda precisam de avaliação do jogador.

**Release e CI: CONCLUÍDOS** — [v0.9.2](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.2) com ZIP Windows e SHA-256, [workflow 42949035024 aprovado](https://github.com/TPollTech/Frontline-Survival/actions/runs/42949035024), incluindo material das armas, aliados, duas ondas e 100+ escolhas seguras. **Status de gameplay: PARCIAL** até sessão real e feedback.

---

## 0.9.1 — Paleta de armas, aliados, mira real e som de onda (em validação)

**Origem:** na v0.9.0, uma captura real mostrou armas brancas, aliados com poses deformadas e mira desalinhada; houve relato de apitos irritantes. O trabalho da 0.9.1 implementa correções, mas **não está homologado visualmente** até teste em Windows.

**Alterações de código:**
- GLBs armazenam cores no atributo `COLOR_0`. Novo material Godot configura `vertex_color_use_as_albedo`, usado por jogador, inimigos e aliados. Corrige o problema de cores que persistiu após inverter as faces da v0.9.0.
- Criada uma solução compartilhada para braços com geometria de dois segmentos e cotovelos posicionados segundo comprimento de braço e distância até a empunhadura. Reduz poses invertidas de soldados e aliados.
- Colete, mochila e ombreiras dos aliados receberam proporções menores para uma silhueta mais limpa.
- Retirados a crosshair 2D e o hitmarker sonoro agudo; tiro na cabeça continua recompensado pelo texto/créditos.
- Ao mirar, o visor/ferrolho frontal da arma é alinhado ao eixo central da câmera; as ópticas do fuzil/SMG/LMG têm abertura e poste 3D, sem disco opaco.
- Aplicação do recuo deslocada para **depois do raycast**, mantendo o primeiro tiro no ponto de mira antes da subida da câmera.
- Fim de onda recebe dois toques graves suaves sintetizados no próprio jogo; volume do efeito de compra reduzido.
- Preservados Campo de Testes, textura do asfalto, compras por F, intervalo padrão de 75 segundos, ondas contínuas, modos treino/clássico e reforços.

**Etapas do ROADMAP:** Etapa 1 (armas/mira), Etapa 2 (representação dos aliados e inimigos) e Etapa 5 (HUD e áudio) **PARCIAIS** até validação jogando. Etapa 0 (estabilidade) também **PARCIAL**; sessão de 15 ondas ainda pendente.

**QA:** [TESTES_0_9_1.md](TESTES_0_9_1.md). **Exportação: CONCLUÍDA (CI + RELEASES)** — [compilação aprovada](https://github.com/TPollTech/Frontline-Survival/actions/runs/42945928310), ZIP Windows + SHA-256 publicados na [release v0.9.1](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.1). **Visual, mira, sons e aliados: PARCIAIS**, aguardando teste no Windows real.

---

## 0.9 — Correção visual de armas e empunhadura (em validação)

**Estado de entrega:** **CI CONCLUÍDO** na [execução Windows 0.9](https://github.com/TPollTech/Frontline-Survival/actions/runs/42941790033): modelos regenerados, importação Godot 4.4.1, smoke test headless, integridade estática, exportação e artifact ZIP aprovados. Os 19 GLBs corrigidos foram [commitados no GitHub](https://github.com/TPollTech/Frontline-Survival/commit/680a86643ac51841cbe835d8dd8e194b4079c8f7). **Etapas 1 e 2: PARCIAIS**, pois visual, animação e jogabilidade real ainda precisam de aprovação do jogador.

**Correções:**
- Corrigida a orientação invertida das faces dos blocos chanfrados e dos anéis da boca do cano no gerador 3D: faces antes ocultas pelo backface culling devem voltar a aparecer.
- Regeneração integral das cinco armas e dos seus subconjuntos GLB, preservando geometria original de baixo custo e as funcionalidades de recarga.
- Armas longas com escala e profundidade adaptadas para evitar que a coronha ultrapasse o plano próximo da câmera, especialmente a escopeta.
- Mãos do jogador referenciadas ao gatilho e ao guarda-mão de cada classe, acompanhando a posição e escala do modelo.
- Armas de inimigos e aliados centralizadas, clarão alinhado ao cano e braços posicionados por duas metas de empunhadura com cálculo leve por quadro.
- Verificador estático com guarda de orientação externa de faces e presença das novas rotinas de empunhadura.

**Preservado:** Campo de Testes, textura original do asfalto, ondas contínuas, intervalo padrão de 75 s, lojas físicas via F, aliados, ataque aéreo, HUD e controles.

**Avaliação obrigatória:** [TESTES_0_9.md](TESTES_0_9.md): verificar armas opacas e inteiras, recarga e transições, duas mãos realmente sobre a arma, aliados/inimigos em movimento e disparo, ondas 1–5 e performance.

**Evidência de base:** o jogador executou a 0.8 no Windows e enviou captura da preparação para a onda 2, com 138 FPS naquele momento. Esse valor não é um benchmark de sessão prolongada e não homologa a 0.9.

---

## 0.8 — Feedback tático e pipeline Windows (em validação)

**Status técnico:** recursos implementados e exportados com êxito pelo Godot 4.4.1 no GitHub Actions; importação, smoke test headless e integridade estática aprovados. **Etapas 1 e 5: PARCIAIS (teste real pendente). Etapa 0: PARCIAL (CI aprovado, sessão de 15 ondas pendente). Exportação Windows: CONCLUÍDA (CI).** [Execução validada](https://github.com/TPollTech/Frontline-Survival/actions/runs/42936566841).

### Entregas neste incremento
- Indicadores de direção do tiro recebido: frente, direita, trás e esquerda, temporários, sem ocupar permanentemente o HUD.
- O inimigo informa sua posição ao causar dano; aviso só aparece se o ataque efetivamente causar dano.
- Headshot realça por instantes a retícula em âmbar; o bônus existente permanece.
- Mira ADS com deslocamento mais cauteloso e redução moderada do recuo.
- Retícula com expansão dinâmica conforme dispersão das rajadas e retorno ao centro.
- Atualização da identificação de versão no jogo.
- Novo workflow de importação, verificação estática e exportação do Windows em GitHub Actions.
- Instruções de teste sem abrir o Godot em [BUILD_WINDOWS.md](BUILD_WINDOWS.md).

### Preservado
- Ondas contínuas, preparação de 75 s com N opcional, Campo de Testes e asfalto original.
- Estações físicas com F, sem loja global no B.
- Treino com reanimação, suporte com 3/4, 1/2 para armas, menus e áudio ajustável.
- A própria versão 0.7 anterior continua registrada no histórico do GitHub.

### Ainda NÃO concluído
- Teste completo de 15 ondas no notebook e medições de FPS/RAM.
- Rig de mãos profissional, revisão de todas as armas e IA avançada.
- Avaliação do funcionamento no Windows real e eventuais correções depois do feedback.
- Etapas 0–6 do GDD como um todo.

### Lista curta de testes para a versão 0.8
1. Iniciar pelo EXE, sem Godot, abrir menus/pausa.
2. Tomar tiros de frente, dos lados e de trás; conferir indicador correto e temporário.
3. Fazer headshot; verificar flash âmbar e recompensa.
4. Comprar fuzil, usar F na loja, mirar e disparar sem travar controles.
5. Completar onda 1, aguardar 75 segundos e avançar à onda 2.
6. Testar apoio com 3/4 e reanimação no modo de treino.
7. Registrar erro, vídeo, FPS e RAM em eventual falha.

## 0.7 — Armas modulares e soldados articulados

- Cinco classes de armas com corpos/magazines/mecanismos GLB originais.
- Recargas e animações procedurais, braços em primeira pessoa.
- Soldados inimigos e aliados articulados.
- Efeitos curtos de tiro, traços e impactos com transparência.
- Verificador estático e roteiro de testes.

**Observação:** versões em pré-produção têm status explícito. A existência de um arquivo EXE não prova que uma etapa foi validada 100%.
