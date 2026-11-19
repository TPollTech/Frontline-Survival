# Etapa 4 — evidência renderizada das armas em primeira pessoa

O CI gera uma montagem OpenGL real em `viewmodel_current.png` (1920 × 1440), usando o Godot 4 Compatibility com Xvfb. Cada quadro representa uma pose estática do rig do jogo, reduzida a 640 × 360, sem HUD.

| Posição | Quadro |
| --- | --- |
| Superior esquerdo | Pistola, repouso |
| Superior central | SMG, repouso |
| Superior direito | Fuzil, repouso |
| Meio esquerdo | Escopeta, repouso |
| Meio central | LMG, repouso |
| Meio direito | Fuzil, mira ADS aproximada |
| Inferior esquerdo | Fuzil, recarga em 45% do ciclo: mão de apoio e carregador |
| Inferior central | Escopeta, recarga em 70%: mecanismo da bomba e mão de apoio |
| Inferior direito | Pistola disparando: recuo e clarão de boca |
| Quarta linha, esquerda | MRS-7 sniper com iron sight em ADS |
| Quarta linha, centro | Sniper com luneta 2x em ADS |
| Quarta linha, direita | Sniper com luneta 4x em ADS |

As cenas são capturadas em Godot com a mesma estrutura e as mesmas animações procedurais do jogador, mas **não são um vídeo** e não demonstram continuidade temporal. Precisamos ainda testar o enquadramento ao correr, as transições completas, o encaixe dos dedos e o desempenho no Windows.

Reprodução em Linux com Godot 4.4.1 e Xvfb:
`xvfb-run -a -s '-screen 0 1280x720x24' godot --path . --rendering-driver opengl3 --script res://tests/viewmodel_qa_snapshot.gd`
