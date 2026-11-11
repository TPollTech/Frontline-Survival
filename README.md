# Frontline Survival 0.8 — Campo de Testes

**Projeto Godot 4.x Standard, FPS 3D offline para Windows**, com renderizador **Compatibility** e alvo inicial Ryzen 5 7530U / 8 GB RAM. Projeto original inspirado em mecânicas do gênero *Survival por ondas*. **Não contém modelos, áudio ou outros arquivos do Call of Duty.**

A versão **0.8** preserva o núcleo da 0.7 e traz **aviso direcional de dano** e **feedback âmbar para headshots**. Há agora um workflow de exportação Windows para baixar o jogo pronto em ZIP, sem precisar instalar o editor Godot. **A execução no Windows real e a campanha de QA permanecem pendentes até o teste do jogador.**

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

## Como jogar sem abrir o Godot (Windows)

1. Vá em **[Actions > Windows playable build](https://github.com/TPollTech/Frontline-Survival/actions/workflows/windows-build.yml)**.
2. Escolha a execução mais recente da branch `main` que esteja **verde / success**.
3. Baixe o arquivo da área **Artifacts** chamado `FrontlineSurvival-0.8-Windows`.
4. Extraia todo o ZIP em uma pasta vazia, mantendo `FrontlineSurvival.exe` e o pacote `.pck` juntos (se exportado separadamente).
5. Abra **FrontlineSurvival.exe**. O editor Godot NÃO é necessário.

**Se não houver execução verde ou artifact disponível, a build não está pronta.** Nunca considerar uma execução vermelha ou cancelada como entrega. Leia [BUILD_WINDOWS.md](docs/BUILD_WINDOWS.md).

### Para desenvolver pelo Godot

1. Clone este repositório e abra `project.godot` no **Godot 4.x Standard**, aguardando a importação das malhas e WAVs.
2. Pressione F5 e entre na partida.
3. Teste mira, recarga, compra por F, as ondas contínuas e a indicação direcional de ataques.

### Novidades pontuais da 0.8

- Dano do inimigo agora aciona uma indicação curta de direção do ataque (frente/lados/trás).
- Headshot recebe destaque âmbar na retícula, preservando a recompensa existente.
- [CHANGELOG.md](docs/CHANGELOG.md) especifica a situação de cada incremento.

**Essas alterações representam implementação parcial das Etapas 1 e 5; estabilidade completa só após QA real.**

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
