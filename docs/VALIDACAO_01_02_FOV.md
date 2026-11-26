# 01-02 — Validação do campo de visão

26/11/2026. Revisão consultada: b0b13471d9b67f3f4988400e078ba07958d70e70. Escopo exclusivo 01-02. Critério normativo: variar FOV nos limites suportados, verificar persistência e aplicação na câmera durante gameplay. Fundação 00 preservada.

## Conferência da implementação atual

- scripts/game_settings.gd define FOV_MIN=60.0, FOV_DEFAULT=76.0, FOV_MAX=100.0. _normalize_fov restringe valores numéricos finitos ao intervalo e retorna 76 para tipos inválidos e não finitos. set_value("fov", ...) chama apply() e _save(); _save() grava controls/fov via ConfigFile em settings_path, originalmente user://frontline_settings.cfg; _load() lê a mesma chave e normaliza. O FOV das armas tem chave independente, preservada; a homologação completa da projeção independente é 01-04.
- scripts/game_menu.gd, categoria graphics: HSlider Setting_fov usa as constantes e passo de 1 grau; value_changed é conectado a _on_slider_changed, que atualiza o rótulo e chama GameSettings.set_value. _show_options abre graphics e renderiza novamente. scripts/player.gd inicializa Camera3D com a configuração, conecta GameSettings.changed, atualiza camera.fov se o FOV base mudar e usa o mesmo valor base em get_target_camera_fov durante gameplay, com ADS prioritário ao sprint. Essa é leitura estática, não interação executada.
- tests/fov_settings_qa.gd existente já cobre menu inicial/pausa, 60/100, atualização de rótulo e câmera, gravação temporária, _load, entradas inválidas e alvos hip/ADS/sprint das oito armas e ópticas. O workflow tem execução headless e OpenGL com fov_60.png, fov_100.png, fov_menu.png. Não alterado nem disparado. O teste recarrega ConfigFile na mesma sessão, não constitui por si só teste de reinício de processo. Imagens não versionadas (404 nesta consulta); consulta de workflow por commit 6a4c0d2 retornou lista vazia, que não demonstra falha nem sucesso do CI histórico.

## Evidência numérica de aplicação em Godot real

Análise Python do inventário Windows histórico em evidence.zip/inventory/runtime_inventory.json, Godot 4.4.1-stable official, revisão 95c7ac8c0b32c7c5723ab33cb7a2d4dd29d52968, SHA-256 51f663f01b7dc142de276d92e8a7046c094c3cb758e6979b8a3d74358e5ad4bb (igual ao sha256.json do ZIP). Lista failures vazia. Foram selecionadas as 57 amostras fps_ reais: 24 hip, 25 ads, 8 reload, abrangendo os oito IDs de arma, com uma Camera3D ativa e um adaptador IndependentViewmodelProjection por amostra. Comparadas camera.fov_degrees, context.viewmodel_fov e diagonal do transform local do adaptador com o contrato vigente, base 76 graus, tolerância 1e-4.

| Estado | FOV esperado em graus (base 76) |
|---|---:|
| Hip/recarga | 76 |
| ADS padrão | 53,2 |
| ADS sniper scope_2x | 36,48 |
| ADS sniper scope_4x | 22,04 |
| ADS Sentinela scope4 | 22,10389717282503 |

57/57 valores de câmera, 57/57 valores de viewmodel, 57/57 diagonais e 57/57 câmeras ativas verificados. Erro máximo câmera 9,155273019700871e-7 graus; viewmodel 2,842170943040401e-14 graus; diagonal 4,258175656524088e-8. A diagonal esperada é (tan(camera_fov/2)/tan(viewmodel_fov/2), mesmo fator, 1), ângulos convertidos em radianos. Esta conciliação é nova, sobre capturas reais anteriores; não executa novamente Godot. As amostras são poses preparadas pelo inventário, não trajetória de jogo com slider manipulado; não demonstram limites 60/100, sprint ou persistência. FOV base do cenário e da arma é igual nessas amostras, não homologar 01-04 por esta comparação.

Comparação remota 95c7ac8..b0b13471d9b67f3f4988400e078ba07958d70e70: ancestral confirmado, nenhum arquivo de scripts/, scenes/, project.godot ou tests/fov_settings_qa.gd alterado no diff. Sete blobs conferidos individualmente nas duas revisões, idênticos:
- scripts/game_settings.gd d5d04ecb51851fb3a6383b1d21b4847cfc327c93
- scripts/game_menu.gd 79e517d2937ee93f6887c218099e91ac3c1cc289
- scripts/player.gd 9659ccd4f91b6ddc807a8ea25ece69e5e51a16c6
- scripts/main.gd 73fa98d7bde2c4ebe32a4e5aab097d4caa313911
- project.godot 7a7091acf052ff6720d5348106db39798ae7ecf4
- scenes/main.tscn a5acfcabfa732af0d60af94b8048f690a0c73d8d
- tests/fov_settings_qa.gd 2f5f2132841c04f7f83b164d39d8109518a1fd4c

A evidência numérica segue pertinente ao caminho de configuração/câmera inalterado; assets e materiais mudaram, então não atribuir renderização antiga à revisão atual.

## Decisão

01-02 permanece parcial. Não foi encontrada falha que justifique editar código de FOV. Faltam executar o teste existente na revisão atual, inspecionar 60/100 no jogo, confirmar aplicação em gameplay e persistência real entre sessões (perfil temporário). Godot não instalado/encontrado; tentativa Git ls-remote falhou por DNS. Python disponível para conciliação histórica. Nenhuma nova execução GDScript, captura visual, build Windows ou CI nesta sessão. Não inventar teste de persistência nem repetir fundação. Entrega exclusivamente documental, sem alterações de gameplay ou modelos.
