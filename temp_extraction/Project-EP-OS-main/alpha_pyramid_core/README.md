# 👑 Z17: Apex Core (Alpha Layer)

## Роль в Системе

Высшая точка Пирамиды Z (Вершина). Глобальный реестр модулей и хранитель корня Канона.

## Структура

- **Apex Core**: Логика управления реестром и валидации канонических правил.

## Взаимодействия

- **Вниз (Downstream)**: Через **Z16 Spine Router** передает состояние системы к **Z15 Atlas Generator**.
- **Интент**: Инициирует первичный импульс PEAR, передавая его к **Z13 PEAR Seed**.

## Инфраструктура (Black Door)

- **Z16 Spine Router**: Обеспечивает невидимую маршрутизацию между Вершиной и Структурным Атласом.

## Integration Nodes in Alpha

The following service nodes are now physically manifested in Alpha and discovered by core sync:

- `Z15` `openai_docs_hub` -> `α_Pyramid_Core/PURPLE/15_OPENAI_DOCS_HUB`
- `Z11` `gh_ci_guardian` -> `α_Pyramid_Core/RED/11_GH_CI_GUARDIAN`

Each node is defined by `.node_manifest.json` and participates in the Z-service vertical chain.
