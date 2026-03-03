<template>
  <div>
    <h2 class="page-title">项目整体报告</h2>

    <!-- ── 说明 & 生成区 ── -->
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
          <el-date-picker
            v-model="reportDate"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="默认今日"
            style="width:160px"
          />
        </div>
        <div style="display:flex;gap:10px;margin-left:auto">
          <el-button type="primary" :loading="dlWord" @click="downloadWord">
            <el-icon><Download /></el-icon> 生成并下载报告 (Word)
          </el-button>
          <el-button :loading="dlExcel" @click="downloadExcel">
            <el-icon><Document /></el-icon> 下载数据汇总 (Excel)
          </el-button>
        </div>
      </div>
    </div>

    <!-- ── 报告内容预览 ── -->
    <div class="page-card" v-loading="loading">
      <h3 style="margin-bottom:20px;font-size:17px;color:#2E4057">报告内容预览</h3>

      <el-row :gutter="20">
        <!-- 一、执行摘要 -->
        <el-col :xs="24" :sm="12">
          <div class="preview-section">
            <div class="preview-section-title">一、执行摘要</div>
            <div class="summary-table">
              <div class="summary-row"><span>项目总数</span><span class="summary-val">{{ summary.total }} 个</span></div>
              <div class="summary-row"><span>进行中</span><span class="summary-val">{{ summary.inProgress }} 个</span></div>
              <div class="summary-row"><span>已完成</span><span class="summary-val">{{ summary.done }} 个</span></div>
              <div class="summary-row"><span>正常状态</span><span class="summary-val">{{ summary.normal }} 个</span></div>
              <div class="summary-row">
                <span>预警状态</span>
                <span class="summary-val" :class="summary.warn > 0 ? 'warn-val' : ''">{{ summary.warn }} 个</span>
              </div>
              <div class="summary-row">
                <span>延期状态</span>
                <span class="summary-val" :class="summary.delay > 0 ? 'danger-val' : ''">{{ summary.delay }} 个</span>
              </div>
              <div class="summary-row"><span>未关闭问题</span><span class="summary-val">{{ summary.openIssues }} 条</span></div>
              <div class="summary-row"><span>开放风险</span><span class="summary-val">{{ summary.openRisks }} 条</span></div>
            </div>
          </div>
        </el-col>

        <!-- 二、重点关注项目 -->
        <el-col :xs="24" :sm="12">
          <div class="preview-section">
            <div class="preview-section-title">二、重点关注项目</div>
            <div v-if="attentionProjects.length === 0" style="padding:20px;text-align:center;color:#aaa;">
              🎉 当前无需关注项目
            </div>
            <el-table v-else :data="attentionProjects" size="small" :show-header="true"
              style="width:100%" :border="false">
              <el-table-column prop="name" label="项目名称" min-width="150">
                <template #default="{ row }">
                  <el-link type="primary" @click="$router.push(`/projects/${row.id}`)">{{ row.name }}</el-link>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="70" align="center">
                <template #default="{ row }">
                  <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="manager" label="项目经理" width="90" />
            </el-table>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top:20px">
        <!-- 三、开放风险 TOP -->
        <el-col :xs="24" :sm="12">
          <div class="preview-section">
            <div class="preview-section-title">三、开放风险（前 5 条）</div>
            <div v-if="topRisks.length === 0" style="padding:20px;text-align:center;color:#aaa;">
              暂无开放风险
            </div>
            <el-table v-else :data="topRisks" size="small" style="width:100%" :border="false">
              <el-table-column prop="projectName" label="所属项目" min-width="120" />
              <el-table-column prop="title" label="风险标题" min-width="150" show-overflow-tooltip />
              <el-table-column prop="level" label="等级" width="60" align="center">
                <template #default="{ row }">
                  <span :class="`risk-${row.level}`" style="font-weight:600">{{ row.level }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>

        <!-- 四、项目人天消耗 -->
        <el-col :xs="24" :sm="12">
          <div class="preview-section">
            <div class="preview-section-title">四、人天预算消耗概览</div>
            <div class="budget-list">
              <div class="budget-row" v-for="p in budgetProjects" :key="p.id">
                <span class="budget-name" :title="p.name">{{ p.name }}</span>
                <el-progress
                  :percentage="p.pct"
                  :color="p.pct >= 100 ? '#FF4444' : p.pct >= 80 ? '#FFC000' : '#70AD47'"
                  :stroke-width="10"
                  style="flex:1;margin:0 10px"
                />
                <span class="budget-pct" :style="{ color: p.pct >= 100 ? '#FF4444' : '#555' }">
                  {{ p.usedDays }}/{{ p.budgetDays }}天
                </span>
              </div>
              <div v-if="budgetProjects.length === 0" style="text-align:center;color:#aaa;padding:20px">
                暂无人天数据
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { projectApi, reportApi, riskApi, downloadBlob } from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const dlWord = ref(false)
const dlExcel = ref(false)
const reportTitle = ref('PMO项目整体报告')
const reportDate = ref('')
const projects = ref([])
const topRisks = ref([])  // [{projectName, title, level}]

// ── 统计摘要 ──
const summary = computed(() => {
  const ps = projects.value
  return {
    total: ps.length,
    inProgress: ps.filter(p => ['正常', '预警'].includes(p.status)).length,
    done: ps.filter(p => p.status === '已完成').length,
    normal: ps.filter(p => p.status === '正常').length,
    warn: ps.filter(p => p.status === '预警').length,
    delay: ps.filter(p => p.status === '延期').length,
    openIssues: ps.reduce((s, p) => s + (p.open_issue_count || 0), 0),
    openRisks: ps.reduce((s, p) => s + (p.open_risk_count || 0), 0),
  }
})

// ── 重点关注项目（预警+延期+暂停） ──
const attentionProjects = computed(() =>
  projects.value.filter(p => ['预警', '延期', '暂停'].includes(p.status))
    .sort((a, b) => {
      const order = { '延期': 0, '预警': 1, '暂停': 2 }
      return (order[a.status] ?? 9) - (order[b.status] ?? 9)
    })
)

// ── 人天消耗（只展示有预算的项目，按消耗%降序） ──
const budgetProjects = computed(() =>
  projects.value
    .filter(p => p.budget_mandays > 0)
    .map(p => ({
      id: p.id,
      name: p.name,
      budgetDays: p.budget_mandays,
      usedDays: p.used_mandays || 0,
      pct: Math.min(Math.round((p.used_mandays || 0) / p.budget_mandays * 100), 100),
    }))
    .sort((a, b) => b.pct - a.pct)
    .slice(0, 6)
)

function statusType(s) {
  return { '正常': 'success', '预警': 'warning', '延期': 'danger', '暂停': 'info', '已完成': '' }[s] || ''
}

async function loadData() {
  loading.value = true
  try {
    projects.value = await projectApi.list()

    // 加载有开放风险的项目风险（取前5条高优先级）
    const riskProjects = projects.value.filter(p => p.open_risk_count > 0)
    const allRisks = []
    await Promise.all(
      riskProjects.map(p =>
        riskApi.list(p.id).then(risks => {
          risks.filter(r => r.status === '开放').forEach(r => {
            allRisks.push({ ...r, projectName: p.name })
          })
        })
      )
    )
    const levelOrder = { '极高': 0, '高': 1, '中': 2, '低': 3, '极低': 4 }
    topRisks.value = allRisks
      .sort((a, b) => (levelOrder[a.level] ?? 9) - (levelOrder[b.level] ?? 9))
      .slice(0, 5)
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
  } catch {
    ElMessage.error('报告生成失败，请稍后重试')
  } finally {
    dlWord.value = false
  }
}

async function downloadExcel() {
  dlExcel.value = true
  try {
    const today = reportDate.value || new Date().toISOString().slice(0, 10)
    const res = await reportApi.portfolioExcel()
    downloadBlob(res, `PMO项目组合数据汇总_${today}.xlsx`)
    ElMessage.success('数据汇总（Excel）下载成功')
  } catch {
    ElMessage.error('报告生成失败，请稍后重试')
  } finally {
    dlExcel.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
/* 说明 & 生成区 */
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
  color: #333;
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
  height: 100%;
}
.preview-section-title {
  background: #f4f7fd;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #2E4057;
  border-bottom: 1px solid #e8edf3;
}

/* 摘要表 */
.summary-table { padding: 4px 0; }
.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 16px;
  font-size: 13px;
  border-bottom: 1px solid #f5f5f5;
}
.summary-row:last-child { border-bottom: none; }
.summary-val { font-weight: 600; color: #333; }
.warn-val { color: #FFC000 !important; }
.danger-val { color: #FF4444 !important; }

/* 人天消耗 */
.budget-list { padding: 8px 12px; }
.budget-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.budget-row:last-child { margin-bottom: 0; }
.budget-name {
  font-size: 12px;
  color: #555;
  width: 90px;
  flex-shrink: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.budget-pct {
  font-size: 12px;
  width: 70px;
  text-align: right;
  flex-shrink: 0;
}
</style>
