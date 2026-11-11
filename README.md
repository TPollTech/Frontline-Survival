# Frontline Survival 0.9 — Campo de Testes

**Projeto Godot 4.x Standard, FPS 3D offline para Windows**, com renderizador **Compatibility** e alvo inicial Ryzen 5 7530U / 8 GB RAM. Projeto original inspirado em mecânicas do gênero *Survival por ondas*. **Não contém modelos, áudio ou outros arquivos do Call of Duty.**

A versão **0.9** concentra-se nas correções visuais reportadas na build 0.8: faces ocultas nas armas, enquadramento das armas longas e postura de empunhadura dos soldados. O usuário já conseguiu iniciar a 0.8 no Windows e alcançar a preparação para a onda 2. **A build 0.9 precisa de validação visual e testes de gameplay antes de ser considerada final.**

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
2. Abra a versão mais recente, inicialmente `v0.9.0` (pré-lançamento de testes).
3. Na seção **Assets**, baixe **FrontlineSurvival-v0.9.0-Windows.zip** (o nome acompanha o número da versão futura).
4. Extraia o ZIP inteiro para uma pasta, mantendo `FrontlineSurvival.exe` e `FrontlineSurvival.pck` juntos.
5. Execute `FrontlineSurvival.exe`. **Não é necessário abrir o editor Godot.**

**Plano B:** o [GitHub Actions](https://github.com/TPollTech/Frontline-Survival/actions/workflows/windows-build.yml) continua disponível para builds intermediárias que ainda não tiveram nova versão lançada. Não considere uma execução com erro ou cancelada como build válida. Detalhes em [BUILD_WINDOWS.md](docs/BUILD_WINDOWS.md).

### Para desenvolver pelo Godot

1. Clone este repositório e abra `project.godot` no **Godot 4.x Standard**, aguardando a importação das malhas e WAVs.
2. Pressione F5 e entre na partida.
3. Teste mira, recarga, compra por F, as ondas contínuas e a indicação direcional de ataques.

### Correções visuais da 0.9

- Malhas 3D regeneradas com orientação correta das superfícies e anéis do cano, para evitar aparência transparente/incompleta.
- Escopeta, SMG, fuzil e LMG redimensionadas/reposicionadas na câmera para evitar clipping da coronha.
- Mãos do jogador alinhadas aos pontos de gatilho e guarda-mão de cada arma.
- Soldados e aliados com armas centralizadas e braços que acompanham dois pontos de empunhadura.
- Retidos os indicadores de dano, headshot âmbar e retícula dinâmica introduzidos na 0.8.
- [Checklist visual e regressão da 0.9](docs/TESTES_0_9.md).
- [CHANGELOG.md](docs/CHANGELOG.md) especifica a situação de cada incremento.

**As correções da 0.9 representam implementação parcial das Etapas 1 e 2 (apresentação de soldados).** A estabilidade geral e a postura visual só serão consideradas concluídas após teste real no Windows.

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
