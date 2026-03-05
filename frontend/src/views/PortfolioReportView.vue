<template>
  <div>
    <h2 class="page-title">项目整体报告</h2>

    <!-- ── 操作区 ── -->
    <div class="page-card" style="margin-bottom:20px">
      <div class="gen-desc">
        <el-icon style="color:#4472C4;font-size:18px"><InfoFilled /></el-icon>
        <span>生成面向 PMO 和管理层的项目整体报告，包含执行摘要、重点关注项目、全局风险问题、里程碑跟踪和项目状态一览。</span>
      </div>
      <div class="gen-form">
        <div class="gen-form-item">
          <label>报告标题</label>
          <el-input v-model="reportTitle" style="width:260px" placeholder="PMO项目整体报告" />
        </div>
        <div class="gen-form-item">
          <label>报告日期</label>
          <el-date-picker v-model="reportDate" type="date" value-format="YYYY-MM-DD"
            placeholder="默认今日" style="width:160px" />
        </div>
        <div style="display:flex;gap:10px;margin-left:auto;flex-shrink:0">
          <el-button type="primary" :loading="dlWord" @click="downloadWord">
            <el-icon><Download /></el-icon> 生成并下载报告 (Word)
          </el-button>
          <el-button :loading="dlExcel" @click="downloadExcel">
            <el-icon><Document /></el-icon> 数据汇总 (Excel)
          </el-button>
        </div>
      </div>
    </div>

    <!-- ── 报告内容预览 ── -->
    <div class="page-card" v-loading="loading">
      <h3 style="margin-bottom:20px;font-size:17px;color:#2E4057">报告内容预览</h3>

      <!-- 第一行：执行摘要 + 重点关注项目 -->
      <el-row :gutter="20" style="margin-bottom:20px">
        <!-- 一、执行摘要 -->
        <el-col :xs="24" :md="12">
          <div class="preview-section">
            <div class="preview-section-title">一、执行摘要</div>
            <div class="summary-table">
              <div class="summary-row"><span>项目总数</span><span class="sv">{{ s.total }} 个</span></div>
              <div class="summary-row"><span>进行中</span><span class="sv">{{ s.inProgress }} 个</span></div>
              <div class="summary-row"><span>已完成</span><span class="sv">{{ s.done }} 个</span></div>
              <div class="summary-row"><span>正常状态</span><span class="sv">{{ s.normal }} 个</span></div>
              <div class="summary-row">
                <span>预警状态</span>
                <span class="sv" :class="s.warn > 0 ? 'sv-warn' : ''">{{ s.warn }} 个</span>
              </div>
              <div class="summary-row">
                <span>延期状态</span>
                <span class="sv" :class="s.delay > 0 ? 'sv-danger' : ''">{{ s.delay }} 个</span>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 二、重点关注项目 -->
        <el-col :xs="24" :md="12">
          <div class="preview-section">
            <div class="preview-section-title">二、重点关注项目</div>
            <el-table :data="attentionProjects" size="small" style="width:100%"
              :show-header="attentionProjects.length > 0" :border="false">
              <el-table-column prop="name" label="项目名称" min-width="140">
                <template #default="{ row }">
                  <el-link type="primary" @click="$router.push(`/projects/${row.id}`)">{{ row.name }}</el-link>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="72" align="center">
                <template #default="{ row }">
                  <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="manager" label="项目经理" width="90" />
            </el-table>
            <div v-if="attentionProjects.length === 0" class="empty-hint">🎉 当前无需关注项目</div>
          </div>
        </el-col>
      </el-row>

      <!-- 第二行：高优先级问题 + 高影响风险 -->
      <el-row :gutter="20" style="margin-bottom:20px">
        <!-- 三、高优先级问题 -->
        <el-col :xs="24" :md="12">
          <div class="preview-section">
            <div class="preview-section-title">三、高优先级问题</div>
            <el-table :data="highIssues" size="small" style="width:100%"
              :show-header="highIssues.length > 0" :border="false">
              <el-table-column prop="projectName" label="项目" width="110" show-overflow-tooltip />
              <el-table-column prop="title" label="问题标题" min-width="150" show-overflow-tooltip />
              <el-table-column prop="status" label="状态" width="75" align="center">
                <template #default="{ row }">
                  <el-tag :type="issueStatusType(row.status)" size="small">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="highIssues.length === 0 && !loading" class="empty-hint">🎉 暂无高优先级问题</div>
          </div>
        </el-col>

        <!-- 四、高影响风险 -->
        <el-col :xs="24" :md="12">
          <div class="preview-section">
            <div class="preview-section-title">四、高影响风险</div>
            <el-table :data="highRisks" size="small" style="width:100%"
              :show-header="highRisks.length > 0" :border="false">
              <el-table-column prop="projectName" label="项目" width="110" show-overflow-tooltip />
              <el-table-column prop="title" label="风险描述" min-width="150" show-overflow-tooltip />
              <el-table-column prop="status" label="状态" width="75" align="center">
                <template #default="{ row }">
                  <el-tag :type="riskStatusType(row.status)" size="small">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="highRisks.length === 0 && !loading" class="empty-hint">🎉 暂无高影响风险</div>
          </div>
        </el-col>
      </el-row>

      <!-- 第三行：逾期里程碑 + 资源消耗 -->
      <el-row :gutter="20">
        <!-- 五、逾期里程碑 -->
        <el-col :xs="24" :md="12">
          <div class="preview-section">
            <div class="preview-section-title">五、逾期里程碑</div>
            <el-table :data="overdueMilestones" size="small" style="width:100%"
              :show-header="overdueMilestones.length > 0" :border="false">
              <el-table-column prop="projectName" label="项目" width="110" show-overflow-tooltip />
              <el-table-column prop="name" label="里程碑" min-width="140" show-overflow-tooltip />
              <el-table-column prop="plan_date" label="计划日期" width="110" />
              <el-table-column label="逾期" width="70" align="center">
                <template #default="{ row }">
                  <span style="color:#FF4444;font-weight:600">{{ row.overdueDays }}天</span>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="overdueMilestones.length === 0 && !loading" class="empty-hint">🎉 无逾期里程碑</div>
          </div>
        </el-col>

        <!-- 六、资源消耗概览 -->
        <el-col :xs="24" :md="12">
          <div class="preview-section">
            <div class="preview-section-title">六、资源消耗概览</div>
            <div class="summary-table">
              <div class="summary-row">
                <span>总预算人天</span>
                <span class="sv">{{ resource.totalBudget.toFixed(1) }} 人天</span>
              </div>
              <div class="summary-row">
                <span>累计消耗</span>
                <span class="sv">{{ resource.totalUsed.toFixed(1) }} 人天</span>
              </div>
              <div class="summary-row">
                <span>本月消耗</span>
                <span class="sv">{{ resource.thisMonth.toFixed(1) }} 人天</span>
              </div>
              <div class="summary-row">
                <span>预算使用率</span>
                <span class="sv"
                  :class="resource.totalBudget > 0 && resource.usageRate >= 80 ? 'sv-danger' : ''">
                  {{ resource.totalBudget > 0 ? resource.usageRate.toFixed(1) + '%' : 'N/A' }}
                </span>
              </div>
            </div>
            <div style="padding:12px 16px" v-if="resource.totalBudget > 0">
              <el-progress
                :percentage="Math.min(resource.usageRate, 100)"
                :color="resource.usageRate >= 100 ? '#FF4444' : resource.usageRate >= 80 ? '#FFC000' : '#70AD47'"
                :stroke-width="14"
                :show-text="true"
              />
            </div>
          </div>
        </el-col>
      </el-row>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { projectApi, reportApi, riskApi, issueApi, milestoneApi, mandayApi, downloadBlob } from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const dlWord = ref(false)
const dlExcel = ref(false)
const reportTitle = ref('PMO项目整体报告')
const reportDate = ref('')

const projects = ref([])
const highIssues = ref([])    // 高严重等级未关闭问题
const highRisks = ref([])     // 高影响开放风险
const overdueMilestones = ref([])  // 逾期里程碑
const resource = ref({ totalBudget: 0, totalUsed: 0, thisMonth: 0, usageRate: 0 })

// ── 执行摘要 ──────────────────────────────────────────
const s = computed(() => {
  const ps = projects.value
  return {
    total: ps.length,
    inProgress: ps.filter(p => ['正常', '预警'].includes(p.status)).length,
    done: ps.filter(p => p.status === '已完成').length,
    normal: ps.filter(p => p.status === '正常').length,
    warn: ps.filter(p => p.status === '预警').length,
    delay: ps.filter(p => p.status === '延期').length,
  }
})

// ── 重点关注项目（预警+延期+暂停） ──────────────────
const attentionProjects = computed(() =>
  projects.value
    .filter(p => ['预警', '延期', '暂停'].includes(p.status))
    .sort((a, b) => {
      const order = { '延期': 0, '预警': 1, '暂停': 2 }
      return (order[a.status] ?? 9) - (order[b.status] ?? 9)
    })
)

function statusType(s) {
  return { '正常': 'success', '预警': 'warning', '延期': 'danger', '暂停': 'info', '已完成': '' }[s] || ''
}
function issueStatusType(s) {
  return { '待处理': 'danger', '处理中': 'warning', '已关闭': 'success' }[s] || ''
}
function riskStatusType(s) {
  return { '开放': 'danger', '已缓解': 'warning', '已关闭': 'success' }[s] || ''
}

// ── 加载数据 ──────────────────────────────────────────
async function loadData() {
  loading.value = true
  try {
    projects.value = await projectApi.list()

    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const thisYear = today.getFullYear()
    const thisMonth = today.getMonth()

    const issueList = [], riskList = [], msList = []
    let totalBudget = 0, totalUsed = 0, thisMonthDays = 0

    // 遍历每个项目并发拉取
    await Promise.all(projects.value.map(async p => {
      totalBudget += p.budget_mandays || 0
      totalUsed += p.used_mandays || 0

      // 高优先级问题（高严重等级、未关闭）
      if (p.open_issue_count > 0) {
        const issues = await issueApi.list(p.id)
        issues
          .filter(i => i.severity === '高' && i.status !== '已关闭')
          .forEach(i => issueList.push({ ...i, projectName: p.name }))
      }

      // 高影响风险（影响=高 或 等级极高/高，状态=开放）
      if (p.open_risk_count > 0) {
        const risks = await riskApi.list(p.id)
        risks
          .filter(r => r.status === '开放' && ['极高', '高'].includes(r.level))
          .forEach(r => riskList.push({ ...r, projectName: p.name }))
      }

      // 逾期里程碑（计划日期已过、非已完成）
      const milestones = await milestoneApi.list(p.id)
      milestones
        .filter(ms => {
          if (!ms.plan_date || ms.status === 'ms_done') return false
          const planDate = new Date(ms.plan_date)
          planDate.setHours(0, 0, 0, 0)
          return planDate < today
        })
        .forEach(ms => {
          const planDate = new Date(ms.plan_date)
          const diffDays = Math.floor((today - planDate) / 86400000)
          msList.push({ ...ms, projectName: p.name, overdueDays: diffDays })
        })

      // 本月人天消耗
      try {
        const mandays = await mandayApi.list(p.id)
        mandays.forEach(m => {
          if (!m.work_date) return
          const d = new Date(m.work_date)
          if (d.getFullYear() === thisYear && d.getMonth() === thisMonth) {
            thisMonthDays += Number(m.days) || 0
          }
        })
      } catch { /* 忽略人天加载错误 */ }
    }))

    // 排序
    const levelOrder = { '极高': 0, '高': 1, '中': 2, '低': 3 }
    highIssues.value = issueList.sort((a, b) => (levelOrder[a.severity] ?? 9) - (levelOrder[b.severity] ?? 9))
    highRisks.value = riskList.sort((a, b) => (levelOrder[a.level] ?? 9) - (levelOrder[b.level] ?? 9))
    overdueMilestones.value = msList.sort((a, b) => b.overdueDays - a.overdueDays)

    resource.value = {
      totalBudget,
      totalUsed,
      thisMonth: thisMonthDays,
      usageRate: totalBudget > 0 ? (totalUsed / totalBudget) * 100 : 0,
    }
  } finally {
    loading.value = false
  }
}

async function downloadWord() {
  dlWord.value = true
  try {
    const today = reportDate.value || new Date().toISOString().slice(0, 10)
    const res = await reportApi.portfolioWord()
    downloadBlob(res, `PMO项目组合综合报告_${today}.docx`)
    ElMessage.success('整体报告（Word）下载成功')
  } catch { ElMessage.error('报告生成失败，请稍后重试') }
  finally { dlWord.value = false }
}

async function downloadExcel() {
  dlExcel.value = true
  try {
    const today = reportDate.value || new Date().toISOString().slice(0, 10)
    const res = await reportApi.portfolioExcel()
    downloadBlob(res, `PMO项目组合数据汇总_${today}.xlsx`)
    ElMessage.success('数据汇总（Excel）下载成功')
  } catch { ElMessage.error('报告生成失败，请稍后重试') }
  finally { dlExcel.value = false }
}

onMounted(loadData)
</script>

<style scoped>
/* 操作区 */
.gen-desc {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #f4f7fd;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 13px;
  color: #555;
  margin-bottom: 16px;
}
.gen-form {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}
.gen-form-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}
@media (max-width: 768px) {
  .gen-form { flex-direction: column; align-items: flex-start; }
  .gen-form > div:last-child { margin-left: 0 !important; }
}

/* 预览区块 */
.preview-section {
  border: 1px solid #e8edf3;
  border-radius: 10px;
  overflow: hidden;
  min-height: 160px;
  margin-bottom: 4px;
}
.preview-section-title {
  background: #f4f7fd;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #2E4057;
  border-bottom: 1px solid #e8edf3;
}
.empty-hint {
  text-align: center;
  color: #aaa;
  padding: 30px;
  font-size: 13px;
}

/* 摘要表 */
.summary-table { }
.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 16px;
  font-size: 13px;
  border-bottom: 1px solid #f5f5f5;
  color: #555;
}
.summary-row:last-child { border-bottom: none; }
.sv { font-weight: 600; color: #333; }
.sv-warn { color: #FFC000 !important; }
.sv-danger { color: #FF4444 !important; }
</style>
