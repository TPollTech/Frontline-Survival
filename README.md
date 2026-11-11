# Frontline Survival 0.9.3 — Campo de Testes

**Projeto Godot 4.x Standard, FPS 3D offline para Windows**, com renderizador **Compatibility** e alvo inicial Ryzen 5 7530U / 8 GB RAM. Projeto original inspirado em mecânicas do gênero *Survival por ondas*. **Não contém modelos, áudio ou outros arquivos do Call of Duty.**

A versão **0.9.3** preserva o sistema de spawns e o ciclo das ondas e corrige três problemas relatados: cabeça solta do suporte aliado, armas visualmente geométricas e som de recarga irritante. Agora há texturas originais, detalhes 3D, cinco sons mecânicos e recuperação de NPCs presos em obstáculos. **O acabamento visual e sonoro ainda precisa de avaliação jogando.**

## Novidades pontuais da 0.9.3

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
- **Cinco sons originais sintetizados** de tiro (pistola, SMG, fuzil, escopeta e metralhadora). São sons provisórios e foram normalizados com margem contra clipping. Volumes continuam ajustáveis no menu.

### Soldados e feedback de combate
- Inimigos com **quadril, joelhos, ombros e cotovelos animados**: caminhada com flexão de joelho, arma posicionada à frente, recuo, breve reação a impactos e queda ao morrer.
- **Uniformes, coletes, bolsas e capacetes distintos** por tipo de arma e pela classe do inimigo. O soldado pesado tem proteção visual extra.
- Aliados chamados pelo suporte também têm pernas e braços articulados e **identificação azul** nos ombros.
- Rastros luminosos longos substituídos por **traços curtos e ocasionais**. Clarões pequenos e cônicos. Impactos transitórios dissipam com alpha, compatível com o renderizador Compatibility.

### Funcionalidades intencionalmente mantidas
- **Campo de Testes permanente**, incluindo **a textura original do asfalto** e as três estações físicas.
- **Sem menu rápido pelo B**: use **F perto da estação** de armas, equipamentos ou suporte.
- **Ondas sucessivas/infinitas**, sem encerrar automaticamente depois da primeira. Entre ondas, **75 s** por padrão, configuráveis de 45 a 120 s; tecla **N** opcional para antecipar.
- **Modo de testes com reanimação**, mantendo número da onda, armas, dinheiro e abates. Modo de uma vida continua disponível nas configurações.
- **$1.200** iniciais no Campo de Testes para experimentar armas.
- Inimigos mudam de armamento por faixa de ondas (escopeta → SMG → fuzil → LMG).
- Reforços adquiridos na estação, chamados por **3** (esquadrão) e **4** (ataque aéreo).
- Configurações de volume geral/SFX/UI, sensibilidade, FOV, FPS e tela cheia.

## Baixar e jogar sem instalar o Godot (Windows)

**Download principal: [Releases do Frontline Survival](https://github.com/TPollTech/Frontline-Survival/releases).** Versões publicadas possuem número, changelog e ZIP próprio.

1. Entre em **[Releases](https://github.com/TPollTech/Frontline-Survival/releases)**.
2. Abra a versão mais recente, atualmente `v0.9.3` (pré-lançamento de testes).
3. Na seção **Assets**, baixe **FrontlineSurvival-v0.9.3-Windows.zip** (o nome acompanha o número da versão futura).
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
