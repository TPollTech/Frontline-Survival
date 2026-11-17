# Etapa 4 — evidência renderizada das armas em primeira pessoa

O CI gera uma montagem OpenGL real em `viewmodel_current.png` (1920 × 720), usando o jogo atual no Godot 4 Compatibility com Xvfb. Cada quadro é uma captura reduzida a 640 × 360, sem HUD.

| Posição | Quadro |
| --- | --- |
| Superior esquerdo | Pistola, posição de descanso |
| Superior central | SMG, posição de descanso |
| Superior direito | Fuzil, posição de descanso |
| Inferior esquerdo | Escopeta, posição de descanso |
| Inferior central | LMG, posição de descanso |
| Inferior direito | Fuzil, mira ADS aproximada |

**Limitação:** essas são poses de referência montadas com o mesmo rig, materiais e modelos usados pelo jogo; não demonstram fluidez, clipping durante recarga/troca, desempenho nem aprovação visual no Windows. Essas etapas permanecem pendentes do jogador.

Reprodução no Linux com Godot 4.4.1 e Xvfb: `xvfb-run -a -s '-screen 0 1280x720x24' godot --path . --rendering-driver opengl3 --script res://tests/viewmodel_qa_snapshot.gd`.
