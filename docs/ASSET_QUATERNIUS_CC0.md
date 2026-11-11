# Humanoide experimental — Quaternius (CC0)

**Integração:** Frontline Survival, protótipo da versão 0.9.13.

**Pacote original:** [Universal Base Characters — Quaternius](https://quaternius.com/packs/universalbasecharacters.html), lançado em agosto de 2025. Licença **Creative Commons Zero 1.0 Universal (CC0-1.0)**, conforme a página oficial.

**Arquivo utilizado:** `assets/characters/quaternius_base_male.glb`.

**Procedência verificável:** foi obtido de [programasweights/avatar](https://github.com/programasweights/avatar/blob/main/ASSETS.md), que documenta a origem como `Base Characters/Godot - UE/Superhero_Male_FullBody.gltf` do pacote Standard oficial de Quaternius, baixado em setembro de 2026. Esse repositório empacotou a malha e o esqueleto originais em um GLB de aproximadamente 741 KB, preservando pesos de skinning e 65 ossos, mas removeu as texturas originais e aplicou uma aparência uniforme. Não inclui animações externas.

**Alterações próprias do Frontline:** material de tecido verde, equipamento militar de baixo custo (capacete/colete/bolsos), postura e caminhada básicas programadas em `scripts/quaternius_soldier_visual.gd`, sem incorporar ativos de Call of Duty.

**Direitos:** a licença original CC0 permite adaptação e uso inclusive comercial. O arquivo não inclui código, música nem imagens protegidas de Call of Duty. Citação do autor é facultativa na CC0, mas mantemos a procedência por transparência.

## Escopo do experimento

- **Um soldado comum por onda** no Campo de Testes utiliza o humanoide.
- A IA, a colisão, o armamento e as regras de combate continuam as mesmas.
- Os demais inimigos e todos os aliados continuam usando o modelo anterior, permitindo comparação.
- Se a malha ou o esqueleto falhar ao carregar, o sistema mantém o soldado procedimental.
- A animação da versão de teste é procedural, **não equivale às animações profissionais da Universal Animation Library**.
- Importação e presença de ossos devem ser testadas pelo Godot CI; aparência e movimento precisam de aprovação jogando no Windows.

## Próxima avaliação

Verificar altura, pés no chão, giro do personagem, inclinação do fuzil e braço de apoio; se a pose básica não for suficiente, integrar clips de idle/walk/run/aim do [Universal Animation Library (CC0)](https://quaternius.com/packs/universalanimationlibrary.html) com retargeting e testar apenas esse soldado antes de trocar todos os NPCs.

**Não substituir a versão 0.9.12:** manter protótipo A/B isolado até aprovação visual.
