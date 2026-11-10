// dom-branches: a read-only right-hand pane that shows the DOM claim branches
// (branch tree, claims, unfinished candidates, delivery state).
//
// Plain ESM loaded uncompiled through the app's disk-plugin door: only
// '@hermes/plugin-sdk', 'react' and 'react/jsx-runtime' resolve, and the tree
// is written with jsx()/jsxs(). Every colour resolves through the app's theme
// tokens (theme variables); no literal colours. Every figure comes from the sibling
// backend (dashboard/plugin_api.py) through ctx.rest('/overview'), which reaches
// /api/plugins/dom-branches/overview inside the gateway; nothing is computed
// here beyond formatting. The pane never writes and never approves anything.
import { Badge, host, PANES_AREA, Skeleton, StatusDot, Tip, useQuery, usePluginI18n, useValue } from '@hermes/plugin-sdk'
import { useState } from 'react'
import { jsx, jsxs } from 'react/jsx-runtime'

export const PLUGIN_ID = 'dom-branches'
export const PANE_ID = 'tree'
export const POLL_MS = 5000
export const STYLE_ID = 'dom-branches-pane-style'
export const PANE_WIDTH = '340px'

// Bound in register(); ctx.rest is scoped to this plugin's namespace.
let rest = null

function fetchOverview() {
  if (!rest) return Promise.reject(new Error('dom-branches plugin context is not registered'))
  return rest('/overview')
}

// ---------------------------------------------------------------------------
// Pure helpers
// ---------------------------------------------------------------------------

export const shortId = value => String(value ?? '').slice(0, 8)
export const clip = (value, max) => {
  const text = String(value ?? '')
  return text.length > max ? `${text.slice(0, max - 1)}\u2026` : text
}

// review_level is shown only when the reader carries it; otherwise a dash.
export function levelView(level) {
  if (level === 'self') return { text: 'self', variant: 'warn' }
  if (level === 'independent') return { text: 'independent', variant: 'default' }
  return { text: '\u2014', variant: 'muted' }
}

// What the pane renders from one poll: the payload when the reader answered
// with data, otherwise the one state it must say.
//   gateway closed        -> status is the gateway state
//   {error}               -> 'reader error' + the message as notice
//   status NO_DATABASE... -> the status itself, shown as an empty state
export function paneModel({ gateway, data, error }) {
  if (gateway !== 'open') return { payload: null, kind: 'gateway', status: gateway, notice: '', loading: false }
  if (data && data.error) return { payload: null, kind: 'reader_error', status: 'reader error', notice: String(data.error), loading: false }
  if (error) {
    const message = error.message || String(error)
    return { payload: data || null, kind: data ? 'ok' : 'unavailable', status: data ? '' : 'unavailable', notice: message, loading: false }
  }
  if (!data) return { payload: null, kind: 'loading', status: '', notice: '', loading: true }
  if (data.status && data.status !== 'OK') return { payload: null, kind: 'status', status: String(data.status), notice: '', loading: false }
  return { payload: data, kind: 'ok', status: '', notice: '', loading: false }
}

export function claimsOfBranch(payload, branch) {
  return (Array.isArray(payload.claims) ? payload.claims : []).filter(claim => claim.branch === branch)
}

export function pendingOfBranch(payload, branch) {
  return (Array.isArray(payload.pending) ? payload.pending : []).filter(item => item.branch === branch)
}

export function deliveryText(delivery) {
  const d = delivery || { pending: 0, ambiguous: 0, ack: 0 }
  return `${d.pending ?? 0}/${d.ambiguous ?? 0}/${d.ack ?? 0}`
}

// ---------------------------------------------------------------------------
// Styles: prefixed classes only; tokens, not literals.
// ---------------------------------------------------------------------------

export const PANE_CSS = `
.dom-pane{display:flex;flex-direction:column;height:100%;min-width:0;font-size:12px;line-height:1.35;color:var(--ui-text-primary)}
.dom-mono{font-family:'JetBrains Mono',var(--font-mono,var(--dt-font-mono,monospace));font-variant-numeric:tabular-nums}
.dom-head{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:10px 10px 3px;min-width:0}
.dom-brand{display:flex;align-items:center;gap:6px;min-width:0;font-weight:600;white-space:nowrap}
.dom-work{padding:0 10px 4px;font-size:11px;color:var(--ui-text-quaternary);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dom-rule{flex:none;border-top:1px solid var(--ui-stroke-tertiary);margin-top:5px}
.dom-body{min-height:0;flex:1;overflow-y:auto;overscroll-behavior:contain}
.dom-section{display:flex;align-items:baseline;gap:8px;padding:8px 10px 3px;min-width:0}
.dom-section-label{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--ui-text-quaternary);white-space:nowrap}
.dom-section-count{margin-left:auto;font-size:11px;color:var(--ui-text-quaternary);white-space:nowrap}
.dom-branch{display:flex;align-items:center;gap:6px;width:100%;padding:3px 10px;border:0;background:transparent;color:inherit;text-align:left;cursor:pointer;font:inherit}
.dom-branch:hover{background:var(--chrome-action-hover)}
.dom-branch-name{font-weight:600}
.dom-branch-meta{margin-left:auto;display:flex;gap:6px;color:var(--ui-text-tertiary);white-space:nowrap;font-size:11px}
.dom-claims{margin:0 10px 4px 18px;padding-left:8px;border-left:2px solid var(--ui-stroke-tertiary)}
.dom-claim{padding:3px 0}
.dom-claim-l1{display:flex;align-items:baseline;gap:6px;min-width:0;font-size:11px;color:var(--ui-text-tertiary)}
.dom-claim-text{margin-top:1px;overflow-wrap:anywhere;color:var(--ui-text-primary)}
.dom-fold{padding:1px 0;font-size:11px;color:var(--ui-text-quaternary)}
.dom-pending{padding:2px 10px}
.dom-pending-l1{display:flex;align-items:baseline;gap:6px;font-size:11px;color:var(--ui-text-tertiary)}
.dom-delivery{padding:6px 10px;font-size:11px;color:var(--ui-text-tertiary)}
.dom-empty{padding:16px 10px;color:var(--ui-text-tertiary);overflow-wrap:anywhere}
.dom-empty-title{font-weight:600;color:var(--ui-text-secondary);margin-bottom:2px}
.dom-notice{margin:6px 10px 8px;border-radius:6px;background:var(--chrome-action-hover);padding:6px 8px;font-size:11px;color:var(--ui-text-tertiary);overflow-wrap:anywhere}
.dom-skeleton{height:10px;margin:6px 10px}
.dom-warn{color:var(--ui-yellow)}
.dom-muted{color:var(--ui-text-quaternary)}
`

export function injectStyle() {
  if (typeof document === 'undefined') return () => {}
  const existing = document.getElementById(STYLE_ID)
  if (existing) existing.remove()
  const style = document.createElement('style')
  style.id = STYLE_ID
  style.textContent = PANE_CSS
  document.head.append(style)
  return () => style.remove()
}

// ---------------------------------------------------------------------------
// Tree helpers
// ---------------------------------------------------------------------------

const present = child => child !== null && child !== undefined && child !== false && child !== ''
function node(type, props, children, key) {
  const list = (Array.isArray(children) ? children : [children]).filter(present)
  if (list.length === 1) return jsx(type, { ...props, children: list[0] }, key)
  return jsxs(type, { ...props, children: list }, key)
}
const span = (className, children, key) => node('span', { className }, children, key)
const div = (className, children, key) => node('div', { className }, children, key)

function useOverview() {
  const gateway = useValue(host.state.gateway)
  const query = useQuery({
    queryKey: [PLUGIN_ID, 'overview'],
    queryFn: fetchOverview,
    refetchInterval: POLL_MS,
    enabled: gateway === 'open',
    placeholderData: previous => previous
  })
  return { gateway, data: query.data, error: query.error }
}

// ---------------------------------------------------------------------------
// Pane sections
// ---------------------------------------------------------------------------

function Header({ t, payload, model }) {
  const tone = !payload ? 'muted' : 'good'
  return div('dom-head', [
    div('dom-brand', [span('', 'dom'), payload && payload.simulated ? jsx(Badge, { variant: 'warn', size: 'xs', className: 'dom-mono', children: t('simulation') }) : null], 'brand'),
    jsx(StatusDot, { tone }, 'dot')
  ])
}

function WorkLine({ payload }) {
  const binding = payload.binding || {}
  const ref = binding.work_ref || ''
  if (!ref) return null
  return div('dom-work dom-mono', `${ref} \u00b7 v${binding.user_version ?? '?'}`)
}

function ClaimRow({ t, claim }) {
  const level = levelView(claim.review_level)
  return div(
    'dom-claim',
    [
      div('dom-claim-l1', [
        jsx(Tip, { label: claim.claim_id, children: span('dom-mono', shortId(claim.claim_id)) }),
        span('', claim.content_type),
        span('dom-mono', claim.origin_version ? `${t('originVersion')}: ${clip(claim.origin_version, 24)}` : ''),
        jsx(Badge, { variant: level.variant, size: 'xs', className: 'dom-mono', children: level.text })
      ]),
      div('dom-claim-text', claim.preview)
    ]
  )
}

function BranchNode({ t, payload, branch }) {
  const [open, setOpen] = useState(false)
  const claims = claimsOfBranch(payload, branch.branch)
  const hidden = Math.max(0, (Number(branch.claims_count) || 0) - claims.length)
  const rows = [
    node(
      'button',
      { type: 'button', className: 'dom-branch', onClick: () => setOpen(value => !value), 'aria-expanded': open ? 'true' : 'false' },
      [
        span('dom-mono', open ? '\u25be' : '\u25b8'),
        span('dom-branch-name', branch.branch),
        span('dom-branch-meta dom-mono', [
          span('', `r${branch.head_revision ?? 0}`),
          span('', t('claimsShort', branch.claims_count ?? 0)),
          Number(branch.pending_count) > 0 ? span('dom-warn', t('pendingShort', branch.pending_count)) : null
        ])
      ],
      'row'
    )
  ]
  if (open) {
    rows.push(
      div(
        'dom-claims',
        [
          ...claims.map(claim => jsx(ClaimRow, { t, claim }, claim.claim_id)),
          claims.length === 0 ? div('dom-fold', t('noClaims'), 'none') : null,
          hidden > 0 ? div('dom-fold', t('moreClaims', hidden), 'more') : null
        ],
        'claims'
      )
    )
  }
  return div('', rows)
}

function PendingBlock({ t, payload }) {
  const items = Array.isArray(payload.pending) ? payload.pending : []
  const total = Number(payload.pending_total) || items.length
  const rejected = Number(payload.rejected_count) || 0
  if (total === 0 && rejected === 0) return null
  return [
    div('dom-rule', [], 'pending-rule'),
    div('dom-section', [span('dom-section-label', t('unfinished')), span('dom-section-count dom-mono', `${total}`)], 'pending-head'),
    ...items.map(item =>
      div(
        'dom-pending',
        div('dom-pending-l1 dom-mono', [
          span('', item.branch),
          span('', shortId(item.candidate_id)),
          span('', item.operation || '\u2014'),
          span('', item.state === 'REVIEWED' ? t('reviewed') : t('awaitingReview')),
          Number.isFinite(item.age_seconds) ? span('dom-muted', `${Math.floor(item.age_seconds / 60)} min`) : null
        ]),
        item.candidate_id
      )
    ),
    total > items.length ? div('dom-fold dom-pending', t('moreClaims', total - items.length), 'pending-more') : null,
    div('dom-section', [span('dom-section-label', t('rejected')), span('dom-section-count dom-mono', `${rejected}`)], 'rejected-head')
  ]
}

function EmptyState({ t, model }) {
  const key = model.kind === 'status' ? `state.${model.status}` : model.kind === 'gateway' ? 'state.gateway' : model.kind === 'reader_error' ? 'state.reader_error' : 'state.unavailable'
  const text = t(key, model.status)
  return div('dom-empty', [div('dom-empty-title', model.status || t('state.unavailable'), 'title'), div('', text, 'text')])
}

function DomPane() {
  const t = usePluginI18n(PLUGIN_ID)
  const data = useOverview()
  const model = paneModel(data)
  const payload = model.payload
  const body = []
  if (model.loading) {
    body.push(jsx(Skeleton, { className: 'dom-skeleton', style: { width: '70%' } }, 'sk1'))
    body.push(jsx(Skeleton, { className: 'dom-skeleton', style: { width: '45%' } }, 'sk2'))
  } else if (payload) {
    const branches = Array.isArray(payload.branches) ? payload.branches : []
    body.push(div('dom-section', [span('dom-section-label', t('branches')), span('dom-section-count dom-mono', `${branches.length}`)], 'branches-head'))
    if (branches.length === 0) body.push(div('dom-fold dom-pending', t('noBranches'), 'nobranches'))
    for (const branch of branches) body.push(jsx(BranchNode, { t, payload, branch }, branch.branch))
    body.push(jsx(PendingBlock, { t, payload }, 'pending'))
    const total = (payload.delivery && payload.delivery.total) || null
    body.push(div('dom-rule', [], 'delivery-rule'))
    body.push(div('dom-delivery dom-mono', `${t('delivery')}: ${deliveryText(total)}`, 'delivery'))
    if (Array.isArray(payload.warnings) && payload.warnings.length) {
      body.push(div('dom-notice', payload.warnings.map(String).join(' \u00b7 '), 'warnings'))
    }
  } else {
    body.push(jsx(EmptyState, { t, model }, 'empty'))
  }
  return div('dom-pane', [
    jsx(Header, { t, payload, model }, 'head'),
    payload ? jsx(WorkLine, { payload }, 'work') : null,
    div('dom-rule', [], 'head-rule'),
    div('dom-body', body, 'body'),
    model.notice ? div('dom-notice', `dom backend: ${model.notice}`, 'notice') : null
  ])
}

const EN = {
  simulation: 'SIMULATION',
  branches: 'Branches',
  noBranches: 'No branches',
  claimsShort: count => `${count} claims`,
  pendingShort: count => `${count} pending`,
  noClaims: 'No claims on this branch',
  moreClaims: count => `\u2026 ${count} more`,
  originVersion: 'origin',
  unfinished: 'Unfinished',
  rejected: 'Rejected',
  reviewed: 'reviewed, not admitted',
  awaitingReview: 'awaiting review',
  delivery: 'Delivery pending/ambiguous/ack',
  'state.NO_DATABASE': 'No DOM database in the configured directory yet.',
  'state.EMPTY_DATABASE': 'The DOM database exists but has no tables.',
  'state.gateway': status => `The gateway is ${status}.`,
  'state.reader_error': 'The DOM reader failed; see the message below.',
  'state.unavailable': 'The dom backend did not answer.'
}

const RU = {
  simulation: 'SIMULATION',
  branches: 'Ветки',
  noBranches: 'Веток нет',
  claimsShort: count => `клаймов: ${count}`,
  pendingShort: count => `не завершено: ${count}`,
  noClaims: 'На этой ветке нет клаймов',
  moreClaims: count => `\u2026 ещё ${count}`,
  originVersion: 'версия',
  unfinished: 'Не завершено',
  rejected: 'Отклонено',
  reviewed: 'проверен, не допущен',
  awaitingReview: 'ждёт проверки',
  delivery: 'Доставка ожидает/неясно/подтверждена',
  'state.NO_DATABASE': 'В указанном каталоге ещё нет базы DOM.',
  'state.EMPTY_DATABASE': 'База DOM есть, но в ней нет таблиц.',
  'state.gateway': status => `Шлюз: ${status}.`,
  'state.reader_error': 'Читатель DOM завершился ошибкой; сообщение ниже.',
  'state.unavailable': 'Бэкенд dom не ответил.'
}

export default {
  id: PLUGIN_ID,
  name: 'DOM branches',
  description: 'Read-only view of DOM claim branches, unfinished candidates and delivery state.',
  defaultEnabled: false,
  register(ctx) {
    rest = ctx.rest
    const removeStyle = injectStyle()
    ctx.onDispose(() => {
      removeStyle()
      rest = null
    })
    ctx.i18n.register({ en: EN, ru: RU })
    ctx.registerMany([
      {
        id: PANE_ID,
        area: PANES_AREA,
        title: 'dom',
        data: { placement: 'right', width: PANE_WIDTH },
        render: () => jsx(DomPane, {})
      }
    ])
  }
}
