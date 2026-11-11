# ADR-P1-05. `dom_claim_versions` и `dom_diff`

- Статус: Accepted
- Дата: 2026-11-11
- Ветка: `arch/p1-version-baseline`
- Долг: TD-DOM-22.6
- Аудит: `docs/AUDIT_2026-11-11_ARCHITECTURE_ANALYSIS.md` §P1.5

## Контекст

Нужна навигация по replacement-цепочке и сравнение двух веток без смешения
версий одного логического claim с разными claim_id.

## Решение

- `dom_claim_versions(claim_id)` возвращает цепочку от корня к листу:
  `claim_id, version, supersedes, raw_sha256, revision, is_current`.
  `is_current` = claim не архивирован; `logical_claim_id` = корень.
- `dom_diff(branch_a, branch_b)` сравнивает текущие (не архивные) claims,
  выровненные по `logical_claim_id`:
  - `only_a`/`only_b` — логические id, присутствующие только в одной ветке;
  - `identical` — одинаковый `raw_sha256`;
  - `changed` — разные `raw_sha256`, с claim_id/version/sha каждой стороны;
  - `common_ancestor` — самый глубокий общий логический claim (по max
    version); при отсутствии общих — `null`;
  - `comparable=false`, если общих логических claims нет.
- Возвращается `read_snapshot` с обеими ветками.

## Последствия

- Diff не путает версии: одна и та же запись в двух версиях — `changed`,
  а не `only_a` + `only_b`.
- `common_ancestor` — логический claim, не `branch_forks.fork_point`
  (таблицы fork появятся в P3).
- Глобальная карта replacement-событий используется и здесь; независимые
  fork-replacements требуют branch-aware карты в P3.

## Проверка

- `test_claim_versions_follow_the_replacement_chain`: `A v1` (не current) →
  `B v2` (current), `supersedes=A`.
- `test_diff_aligns_by_logical_claim_id`: AA `B v2` vs AB `A v1` → один
  `changed`, `common_ancestor=A`, `only_*` пусты.
- `test_diff_without_a_shared_logical_claim_is_not_comparable`: нет общего
  логического claim → `comparable=false`, `only_a/only_b` заполнены.
