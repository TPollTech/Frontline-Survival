# Frontline Survival 0.7 — Campo de Testes

**Projeto Godot 4.x Standard, FPS 3D offline para Windows**, com renderizador **Compatibility** e alvo inicial Ryzen 5 7530U / 8 GB RAM. Projeto original inspirado em mecânicas do gênero *Survival por ondas*. **Não contém modelos, áudio ou outros arquivos do Call of Duty.**

A versão 0.7 atualiza a base 0.6, sem trocar o mapa nem alterar a economia das ondas. Objetivo: dar mais movimento às armas e aos soldados antes de investir em personagens de alta fidelidade e mapas definitivos.

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

## Instruções para jogar

1. Extraia **todo o ZIP** em uma **pasta nova**, sem mesclar com versões anteriores.
2. No **Godot 4.x Standard**, escolha **Importar** e abra `project.godot`.
3. Espere o editor concluir a importação dos arquivos `.glb` e `.wav`.
4. Pressione **F5** e selecione **Iniciar partida**.
5. Visite a estação **ARMAS**, aperte **F** e teste a metralhadora leve ($650). Recarregue com **R** e observe o tambor e o mecanismo.
6. Elimine os inimigos; a próxima onda deve vir automaticamente depois dos **75 segundos de preparação**.

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

**Limites de verificação:** os arquivos, malhas e sons foram validados por scripts locais, mas o executável do Godot **não está disponível neste ambiente**. Logo, esta versão **não foi executada no Godot aqui** e ainda requer teste no notebook para confirmar compilação dos scripts, importação dos GLBs e jogabilidade. O verificador estático **não substitui esse teste**.

Leia `docs/TESTES_0_7.md` para uma sequência rápida de testes e como identificar eventuais erros.

## Planejamento das próximas versões

As melhorias propostas, etapas, prioridades, critérios de aceite e regras de desenvolvimento estão em **[ROADMAP.md](ROADMAP.md)**. Antes de programar novas funcionalidades, validar a etapa correspondente neste planejamento.
