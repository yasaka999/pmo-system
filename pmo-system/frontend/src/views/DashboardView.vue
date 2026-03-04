<template>
  <div>
    <h2 class="page-title">项目总览看板</h2>

    <!-- ── 统计看板（动态，从字典读取配置） ── -->
    <div class="widgets-grid" style="margin-bottom:20px">
      <div
        v-for="w in activeWidgets"
        :key="w.code"
        class="stat-card clickable"
        @click="openDrawer(w.code)"
      >
        <div class="icon" :style="{ background: w.bg }">
          <el-icon style="color:#fff;font-size:22px"><component :is="w.icon" /></el-icon>
        </div>
        <div class="card-content">
          <!-- 普通单数 -->
          <div v-if="!w.splitValue" class="value" :style="{ color: w.color }">{{ w.value }}</div>
          <!-- 双数：逾期（红）+ 正常（蓝） -->
          <div v-else class="value split-value">
            <span class="sv-overdue">{{ w.splitValue.overdue }}</span>
            <span class="sv-sep">+</span>
            <span class="sv-normal">{{ w.splitValue.normal }}</span>
          </div>
          <div class="label">{{ w.label }}</div>
          <div v-if="w.splitValue" class="split-hint">
            <span class="sv-overdue">逾期</span>&nbsp;+&nbsp;<span class="sv-normal">未到期</span>
          </div>
        </div>
        <el-icon class="arrow-icon"><ArrowRight /></el-icon>
      </div>
    </div>

    <!-- ── 项目状态一览表 ── -->
    <div class="page-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <h3>项目状态一览</h3>
        <el-button size="small" @click="downloadOverview" :loading="downloading">
          <el-icon><Download /></el-icon> 导出Excel
        </el-button>
      </div>
      <el-table :data="projects" stripe border style="width:100%" v-loading="loading">
        <el-table-column prop="code" label="项目编号" width="120" />
        <el-table-column prop="name" label="项目名称" min-width="180">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push(`/projects/${row.id}`)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="client" label="客户" width="130" />
        <el-table-column prop="manager" label="项目经理" width="100" />
        <el-table-column prop="phase" label="阶段" width="80" />
        <el-table-column prop="status" label="状态" width="85">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="plan_end" label="计划结束" width="105" />
        <el-table-column prop="open_issue_count" label="未关闭问题" width="90" align="center">
          <template #default="{ row }">
            <el-badge :value="row.open_issue_count" :type="row.open_issue_count > 0 ? 'danger' : 'info'" />
          </template>
        </el-table-column>
        <el-table-column prop="open_risk_count" label="开放风险" width="85" align="center">
          <template #default="{ row }">
            <el-badge :value="row.open_risk_count" :type="row.open_risk_count > 0 ? 'warning' : 'info'" />
          </template>
        </el-table-column>
        <el-table-column label="人天使用" width="120" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="row.budget_mandays > 0 ? Math.min(Math.round(row.used_mandays/row.budget_mandays*100),100) : 0"
              :color="row.used_mandays > row.budget_mandays ? '#FF4444' : '#70AD47'"
              style="min-width:90px"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/projects/${row.id}`)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ══════════ 详情 Drawer ══════════ -->
    <el-drawer v-model="drawerVisible" :title="drawerTitle" size="55%" direction="rtl">
      <div class="drawer-body">
        <!-- 项目列表型看板 -->
        <template v-if="['total','in_progress','done','pending_delivery','delivered','pending_acceptance','accepted'].includes(drawerCode)">
          <el-table :data="drawerProjects" stripe border style="width:100%">
            <el-table-column prop="code" label="项目编号" width="120" />
            <el-table-column prop="name" label="项目名称" min-width="160">
              <template #default="{ row }">
                <el-link type="primary" @click="goProject(row.id)">{{ row.name }}</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="client" label="客户" width="120" />
            <el-table-column prop="manager" label="项目经理" width="100" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="交付日期" width="100">
              <template #default="{ row }">
                <span :style="isOverdue(row.plan_delivery_date, row.actual_delivery_date) ? 'color:#FF4444;font-weight:600' : ''">
                  {{ row.plan_delivery_date || '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="验收日期" width="100">
              <template #default="{ row }">
                <span :style="isOverdue(row.plan_final_acceptance_date, row.actual_final_acceptance_date) ? 'color:#FF4444;font-weight:600' : ''">
                  {{ row.plan_final_acceptance_date || '-' }}
                </span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="drawerProjects.length === 0" description="暂无数据" />
        </template>

        <!-- 未关闭问题 -->
        <template v-if="drawerCode === 'open_issues'">
          <div v-if="issueLoading" class="drawer-loading">
            <el-icon class="is-loading" style="font-size:28px"><Loading /></el-icon>
            <p>正在加载…</p>
          </div>
          <template v-else>
            <div v-for="proj in issueByProject" :key="proj.id" class="proj-group">
              <div class="proj-group-header">
                <el-link type="primary" @click="goProject(proj.id)" class="proj-group-title">
                  {{ proj.code }} · {{ proj.name }}
                </el-link>
                <el-tag size="small" type="danger">{{ proj.issues.length }} 条</el-tag>
              </div>
              <el-table :data="proj.issues" stripe size="small" style="width:100%">
                <el-table-column prop="title" label="问题标题" min-width="180" />
                <el-table-column prop="severity" label="严重等级" width="90">
                  <template #default="{ row }">
                    <el-tag :type="{ '高':'danger','中':'warning','低':'success' }[row.severity]" size="small">{{ row.severity }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="{ '待处理':'danger','处理中':'warning','已关闭':'info' }[row.status]" size="small">{{ row.status }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="assignee" label="负责人" width="90" />
              </el-table>
            </div>
            <el-empty v-if="issueByProject.length === 0" description="暂无未关闭问题 🎉" />
          </template>
        </template>

        <!-- 开放风险 -->
        <template v-if="drawerCode === 'open_risks'">
          <div v-if="riskLoading" class="drawer-loading">
            <el-icon class="is-loading" style="font-size:28px"><Loading /></el-icon>
            <p>正在加载…</p>
          </div>
          <template v-else>
            <div v-for="proj in riskByProject" :key="proj.id" class="proj-group">
              <div class="proj-group-header">
                <el-link type="primary" @click="goProject(proj.id)" class="proj-group-title">
                  {{ proj.code }} · {{ proj.name }}
                </el-link>
                <el-tag size="small" type="warning">{{ proj.risks.length }} 条</el-tag>
              </div>
              <el-table :data="proj.risks" stripe size="small" style="width:100%">
                <el-table-column prop="title" label="风险标题" min-width="180" />
                <el-table-column prop="level" label="风险级别" width="90">
                  <template #default="{ row }">
                    <el-tag :type="{ '极高':'danger','高':'warning','中':'','低':'success' }[row.level]" size="small">{{ row.level }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="{ '开放':'danger','已缓解':'warning','已关闭':'info' }[row.status]" size="small">{{ row.status }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="assignee" label="负责人" width="90" />
              </el-table>
            </div>
            <el-empty v-if="riskByProject.length === 0" description="暂无开放风险 🎉" />
          </template>
        </template>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { projectApi, reportApi, downloadBlob, issueApi, riskApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useDictStore } from '@/stores/dict'

const router = useRouter()
const dictStore = useDictStore()

const projects = ref([])
const loading = ref(false)
const downloading = ref(false)
const drawerVisible = ref(false)
const drawerCode = ref('')
const issueLoading = ref(false)
const riskLoading = ref(false)
const issueByProject = ref([])
const riskByProject = ref([])

const TODAY = new Date()
TODAY.setHours(0, 0, 0, 0)

// ── 工具函数 ─────────────────────────────────────────
function isOverdue(planDate, actualDate) {
  if (actualDate) return false   // 已完成，不算逾期
  if (!planDate) return false
  return new Date(planDate) < TODAY
}

// ── 所有看板定义（固定，code 对应字典配置） ──────────
const WIDGET_DEFS = {
  total:              { label: '项目总数',   icon: 'FolderOpened',       bg: '#4472C4', color: '#4472C4' },
  in_progress:        { label: '进行中',     icon: 'Loading',            bg: '#4CAF50', color: '#4CAF50' },
  done:               { label: '已完成',     icon: 'CircleCheck',        bg: '#909399', color: '#909399' },
  open_issues:        { label: '未关闭问题', icon: 'Warning',            bg: '#FF4444', color: '#FF4444' },
  open_risks:         { label: '开放风险',   icon: 'Bell',               bg: '#FFC000', color: '#FFC000' },
  pending_delivery:   { label: '待交付',     icon: 'Van',                bg: '#4472C4', color: '#4472C4', split: true },
  delivered:          { label: '已交付',     icon: 'Checked',            bg: '#70AD47', color: '#70AD47' },
  pending_acceptance: { label: '待验收',     icon: 'DocumentChecked',    bg: '#E6820E', color: '#E6820E', split: true },
  accepted:           { label: '已验收',     icon: 'Medal',              bg: '#70AD47', color: '#70AD47' },
  // 按项目状态细分
  status_normal:  { label: '正常',   icon: 'SuccessFilled',      bg: '#67C23A', color: '#67C23A' },
  status_warning: { label: '预警',   icon: 'WarnTriangleFilled', bg: '#E6A23C', color: '#E6A23C' },
  status_delayed: { label: '延期',   icon: 'Clock',              bg: '#F56C6C', color: '#F56C6C' },
  status_paused:  { label: '暂停',   icon: 'VideoPause',         bg: '#909399', color: '#909399' },
  status_done:    { label: '已完成(状态)', icon: 'CircleCheck',  bg: '#409EFF', color: '#409EFF' },
}

// ── 统计计算 ─────────────────────────────────────────
const computed_stats = computed(() => {
  const ps = projects.value
  const pendingDel = ps.filter(p => p.plan_delivery_date && !p.actual_delivery_date)
  const pendingAcc = ps.filter(p => p.actual_delivery_date && !p.actual_final_acceptance_date)
  return {
    total: ps.length,
    in_progress: ps.filter(p => !['暂停', '已完成'].includes(p.status)).length,
    done: ps.filter(p => p.status === '已完成').length,
    open_issues: ps.reduce((s, p) => s + (p.open_issue_count || 0), 0),
    open_risks: ps.reduce((s, p) => s + (p.open_risk_count || 0), 0),
    delivered: ps.filter(p => p.actual_delivery_date).length,
    accepted: ps.filter(p => p.actual_final_acceptance_date).length,
    pending_delivery: {
      overdue: pendingDel.filter(p => isOverdue(p.plan_delivery_date, p.actual_delivery_date)).length,
      normal: pendingDel.filter(p => !isOverdue(p.plan_delivery_date, p.actual_delivery_date)).length,
    },
    pending_acceptance: {
      overdue: pendingAcc.filter(p => isOverdue(p.plan_final_acceptance_date, p.actual_final_acceptance_date)).length,
      normal: pendingAcc.filter(p => !isOverdue(p.plan_final_acceptance_date, p.actual_final_acceptance_date)).length,
    },
    // 按状态细分
    status_normal:  ps.filter(p => p.status === '正常').length,
    status_warning: ps.filter(p => p.status === '预警').length,
    status_delayed: ps.filter(p => p.status === '延期').length,
    status_paused:  ps.filter(p => p.status === '暂停').length,
    status_done:    ps.filter(p => p.status === '已完成').length,
  }
})

// ── 从字典读取启用的看板，按 sort_order 排序 ──────────
const activeWidgets = computed(() => {
  const widgetOptions = dictStore.getOptions('dashboard_widget')
  // getOptions 已按 sort_order 排序，且只返回 is_active=true 的
  return widgetOptions.map(opt => {
    const def = WIDGET_DEFS[opt.value] || { label: opt.label, icon: 'Grid', bg: '#aaa', color: '#aaa' }
    const st = computed_stats.value
    const val = st[opt.value]
    const isSplit = def.split && typeof val === 'object'
    return {
      code: opt.value,
      label: def.label,
      icon: def.icon,
      bg: def.bg,
      color: def.color,
      value: isSplit ? (val.overdue + val.normal) : val,
      splitValue: isSplit ? val : null,
    }
  })
})

// ── Drawer ────────────────────────────────────────────
const drawerTitle = computed(() => {
  const def = WIDGET_DEFS[drawerCode.value]
  return def ? `${def.label} — 项目列表` : '详情'
})

const drawerProjects = computed(() => {
  const ps = projects.value
  const code = drawerCode.value
  if (code === 'total') return ps
  if (code === 'in_progress') return ps.filter(p => !['暂停', '已完成'].includes(p.status))
  if (code === 'done') return ps.filter(p => p.status === '已完成')
  if (code === 'delivered') return ps.filter(p => p.actual_delivery_date)
  if (code === 'accepted') return ps.filter(p => p.actual_final_acceptance_date)
  if (code === 'pending_delivery') return ps.filter(p => p.plan_delivery_date && !p.actual_delivery_date)
  if (code === 'pending_acceptance') return ps.filter(p => p.actual_delivery_date && !p.actual_final_acceptance_date)
  // 按状态拆分
  const STATUS_MAP = {
    status_normal: '正常', status_warning: '预警',
    status_delayed: '延期', status_paused: '暂停', status_done: '已完成'
  }
  if (STATUS_MAP[code]) return ps.filter(p => p.status === STATUS_MAP[code])
  return []
})

async function openDrawer(code) {
  drawerCode.value = code
  drawerVisible.value = true

  if (code === 'open_issues' && issueByProject.value.length === 0) {
    issueLoading.value = true
    try {
      const proj = projects.value.filter(p => p.open_issue_count > 0)
      const results = await Promise.all(
        proj.map(p => issueApi.list(p.id).then(issues => ({
          id: p.id, code: p.code, name: p.name,
          issues: issues.filter(i => i.status !== '已关闭')
        })))
      )
      issueByProject.value = results.filter(r => r.issues.length > 0)
    } finally { issueLoading.value = false }
  }

  if (code === 'open_risks' && riskByProject.value.length === 0) {
    riskLoading.value = true
    try {
      const proj = projects.value.filter(p => p.open_risk_count > 0)
      const results = await Promise.all(
        proj.map(p => riskApi.list(p.id).then(risks => ({
          id: p.id, code: p.code, name: p.name,
          risks: risks.filter(r => r.status === '开放')
        })))
      )
      riskByProject.value = results.filter(r => r.risks.length > 0)
    } finally { riskLoading.value = false }
  }
}

function goProject(id) {
  drawerVisible.value = false
  router.push(`/projects/${id}`)
}

function statusType(s) {
  return { '正常': 'success', '预警': 'warning', '延期': 'danger', '已完成': 'info', '暂停': '' }[s] || ''
}

onMounted(async () => {
  dictStore.fetchDicts()
  loading.value = true
  try { projects.value = await projectApi.list() } finally { loading.value = false }
})

async function downloadOverview() {
  downloading.value = true
  try {
    const res = await reportApi.statusOverview()
    downloadBlob(res, '项目状态一览.xlsx')
    ElMessage.success('导出成功')
  } finally { downloading.value = false }
}
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; color: #2E4057; margin-bottom: 20px; }

/* 看板网格：自适应宽度，每张最小 200px */
.widgets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 16px;
}

/* 统计卡片 */
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 16px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,.06);
  cursor: pointer;
  transition: transform .15s, box-shadow .15s;
  position: relative;
  min-width: 0;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,.12);
}
.stat-card .icon {
  width: 46px; height: 46px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.card-content { flex: 1; min-width: 0; }
.value { font-size: 26px; font-weight: 700; line-height: 1.1; }
.label { font-size: 12px; color: #888; margin-top: 3px; }
.arrow-icon { color: #C0C4CC; font-size: 15px; transition: color .15s; }
.stat-card:hover .arrow-icon { color: #409EFF; }

/* 双数展示 */
.split-value { display: flex; align-items: baseline; gap: 3px; }
.sv-overdue { color: #FF4444; font-size: 22px; font-weight: 700; }
.sv-normal  { color: #4472C4; font-size: 22px; font-weight: 700; }
.sv-sep     { color: #aaa; font-size: 16px; }
.split-hint { font-size: 11px; color: #aaa; margin-top: 2px; }
.split-hint .sv-overdue { font-size: 11px; }
.split-hint .sv-normal  { font-size: 11px; }

/* Drawer */
.drawer-body { padding: 0 4px; }
.drawer-loading { text-align: center; padding: 60px 0; color: #888; }
.proj-group { margin-bottom: 24px; }
.proj-group-header {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 0 10px;
  border-bottom: 2px solid #f0f0f0;
  margin-bottom: 8px;
}
.proj-group-title { font-size: 14px; font-weight: 600; }

/* 手机端：单列 */
@media (max-width: 768px) {
  .widgets-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .stat-card { padding: 14px 10px; gap: 10px; }
  .value { font-size: 22px; }
  .sv-overdue, .sv-normal { font-size: 18px; }
}
</style>
