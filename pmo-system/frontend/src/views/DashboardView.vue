<template>
  <div>
    <h2 class="page-title">项目总览看板</h2>

    <!-- ── 统计卡片（可点击） ── -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="(s, i) in stats" :key="i">
        <div class="stat-card clickable" @click="openDrawer(i)">
          <div class="icon" :style="{ background: s.bg }">
            <el-icon :style="{ color: '#fff', fontSize: '22px' }">
              <component :is="s.icon" />
            </el-icon>
          </div>
          <div>
            <div class="value" :style="{ color: s.color }">{{ s.value }}</div>
            <div class="label">{{ s.label }}</div>
          </div>
          <el-icon class="arrow-icon"><ArrowRight /></el-icon>
        </div>
      </el-col>
    </el-row>

    <!-- ── 整体报告（仅 pmo/admin） ── -->
    <div v-if="canSeePortfolioReport" class="page-card" style="margin-bottom:20px;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <h3 style="margin:0 0 4px 0;">📊 项目组合整体报告</h3>
          <span style="color:#888;font-size:13px;">涵盖所有项目：执行摘要 · 重点关注 · 全局风险问题 · 里程碑跟踪 · 状态一览</span>
        </div>
        <div style="display:flex;gap:10px;">
          <el-button type="primary" @click="downloadPortfolioWord" :loading="dlWord">
            <el-icon><Document /></el-icon> 下载整体报告 (Word)
          </el-button>
          <el-button @click="downloadPortfolioExcel" :loading="dlExcel">
            <el-icon><Download /></el-icon> 下载数据汇总 (Excel)
          </el-button>
        </div>
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
        <el-table-column prop="name" label="项目名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push(`/projects/${row.id}`)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="client" label="客户" width="140" />
        <el-table-column prop="manager" label="项目经理" width="110" />
        <el-table-column prop="phase" label="阶段" width="90" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="plan_end" label="计划结束" width="110" />
        <el-table-column prop="open_issue_count" label="未关闭问题" width="100" align="center">
          <template #default="{ row }">
            <el-badge :value="row.open_issue_count" :type="row.open_issue_count > 0 ? 'danger' : 'info'" />
          </template>
        </el-table-column>
        <el-table-column prop="open_risk_count" label="开放风险" width="90" align="center">
          <template #default="{ row }">
            <el-badge :value="row.open_risk_count" :type="row.open_risk_count > 0 ? 'warning' : 'info'" />
          </template>
        </el-table-column>
        <el-table-column label="人天使用" width="130" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="row.budget_mandays > 0 ? Math.min(Math.round(row.used_mandays / row.budget_mandays * 100), 100) : 0"
              :color="row.used_mandays > row.budget_mandays ? '#FF4444' : '#70AD47'"
              style="min-width:100px"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/projects/${row.id}`)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ══════════ 详情 Drawer ══════════ -->
    <el-drawer v-model="drawerVisible" :title="drawerTitle" size="55%" direction="rtl">
      <div class="drawer-body">

        <!-- 0: 项目总数 / 1: 进行中 -->
        <template v-if="drawerType === 0 || drawerType === 1">
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
            <el-table-column prop="plan_end" label="计划结束" width="110" />
            <el-table-column label="里程碑" width="70" align="center">
              <template #default="{ row }">{{ row.milestone_count }}</template>
            </el-table-column>
          </el-table>
        </template>

        <!-- 2: 未关闭问题 -->
        <template v-if="drawerType === 2">
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
                <el-table-column prop="due_date" label="截止日期" width="110" />
              </el-table>
            </div>
            <el-empty v-if="issueByProject.length === 0" description="暂无未关闭问题 🎉" />
          </template>
        </template>

        <!-- 3: 开放风险 -->
        <template v-if="drawerType === 3">
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
                <el-table-column prop="probability" label="概率" width="70" />
                <el-table-column prop="impact" label="影响" width="70" />
                <el-table-column prop="level" label="风险级别" width="90">
                  <template #default="{ row }">
                    <el-tag :type="{ '极高':'danger','高':'warning','中':'','低':'success' }[row.level]" size="small">{{ row.level }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="assignee" label="负责人" width="90" />
                <el-table-column prop="status" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="{ '开放':'danger','已缓解':'warning','已关闭':'info' }[row.status]" size="small">{{ row.status }}</el-tag>
                  </template>
                </el-table-column>
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
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const dictStore = useDictStore()
const auth = useAuthStore()
const canSeePortfolioReport = computed(() => ['admin', 'pmo'].includes(auth.user?.role))

const projects = ref([])
const loading = ref(false)
const downloading = ref(false)
const dlWord = ref(false)
const dlExcel = ref(false)

// ── Drawer 状态 ──────────────────
const drawerVisible = ref(false)
const drawerType = ref(0)      // 0=总数 1=进行中 2=问题 3=风险
const issueLoading = ref(false)
const riskLoading = ref(false)
const issueByProject = ref([]) // [{ id, code, name, issues:[] }]
const riskByProject = ref([])  // [{ id, code, name, risks:[] }]

const drawerTitles = ['所有项目详情', '进行中项目详情', '未关闭问题详情', '开放风险详情']
const drawerTitle = computed(() => drawerTitles[drawerType.value] || '')

const drawerProjects = computed(() => {
  if (drawerType.value === 0) return projects.value
  if (drawerType.value === 1) return projects.value.filter(p => ['正常', '预警'].includes(p.status))
  return []
})

onMounted(async () => {
  dictStore.fetchDicts()
  loading.value = true
  try { projects.value = await projectApi.list() } finally { loading.value = false }
})

const stats = computed(() => {
  const ps = projects.value
  return [
    { label: '项目总数', value: ps.length, icon: 'FolderOpened', bg: '#4472C4', color: '#4472C4' },
    { label: '进行中', value: ps.filter(p => ['正常', '预警'].includes(p.status)).length, icon: 'Loading', bg: '#70AD47', color: '#70AD47' },
    { label: '未关闭问题', value: ps.reduce((s, p) => s + p.open_issue_count, 0), icon: 'Warning', bg: '#FF4444', color: '#FF4444' },
    { label: '开放风险', value: ps.reduce((s, p) => s + p.open_risk_count, 0), icon: 'Bell', bg: '#FFC000', color: '#FFC000' },
  ]
})

function statusType(s) {
  const c = dictStore.getDictItem('project_status', s).color
  return c || { '正常': 'success', '预警': 'warning', '延期': 'danger', '已完成': 'info', '暂停': '' }[s] || ''
}

function goProject(id) {
  drawerVisible.value = false
  router.push(`/projects/${id}`)
}

async function openDrawer(type) {
  drawerType.value = type
  drawerVisible.value = true

  // 未关闭问题
  if (type === 2 && issueByProject.value.length === 0) {
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
    } finally {
      issueLoading.value = false
    }
  }

  // 开放风险
  if (type === 3 && riskByProject.value.length === 0) {
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
    } finally {
      riskLoading.value = false
    }
  }
}

async function downloadOverview() {
  downloading.value = true
  try {
    const res = await reportApi.statusOverview()
    downloadBlob(res, '项目状态一览.xlsx')
    ElMessage.success('导出成功')
  } finally {
    downloading.value = false
  }
}

async function downloadPortfolioWord() {
  dlWord.value = true
  try {
    const today = new Date().toISOString().slice(0, 10)
    const res = await reportApi.portfolioWord()
    downloadBlob(res, `PMO项目组合综合报告_${today}.docx`)
    ElMessage.success('整体报告（Word）下载成功')
  } catch (e) {
    ElMessage.error('报告生成失败，请稍后重试')
  } finally {
    dlWord.value = false
  }
}

async function downloadPortfolioExcel() {
  dlExcel.value = true
  try {
    const today = new Date().toISOString().slice(0, 10)
    const res = await reportApi.portfolioExcel()
    downloadBlob(res, `PMO项目组合数据汇总_${today}.xlsx`)
    ElMessage.success('数据汇总（Excel）下载成功')
  } catch (e) {
    ElMessage.error('报告生成失败，请稍后重试')
  } finally {
    dlExcel.value = false
  }
}
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; color: #2E4057; margin-bottom: 20px; }

/* 统计卡片 */
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,.06);
}
.stat-card.clickable {
  cursor: pointer;
  position: relative;
  transition: transform .15s, box-shadow .15s;
}
.stat-card.clickable:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,.12);
}
.stat-card .icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stat-card .value { font-size: 28px; font-weight: 700; line-height: 1; }
.stat-card .label { font-size: 13px; color: #888; margin-top: 4px; }
.arrow-icon {
  margin-left: auto;
  color: #C0C4CC;
  font-size: 16px;
  transition: color .15s;
}
.stat-card.clickable:hover .arrow-icon { color: #409EFF; }

/* Drawer */
.drawer-body { padding: 0 4px; }
.drawer-loading { text-align: center; padding: 60px 0; color: #888; }
.proj-group { margin-bottom: 24px; }
.proj-group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0 10px;
  border-bottom: 2px solid #f0f0f0;
  margin-bottom: 8px;
}
.proj-group-title { font-size: 14px; font-weight: 600; }
</style>
