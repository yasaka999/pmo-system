<template>
  <div>
    <!-- 基本信息卡 -->
    <div v-if="project" class="page-card" style="margin-bottom:16px">
      <el-descriptions :title="project.name" :column="3" border>
        <el-descriptions-item label="项目编号">{{ project.code }}</el-descriptions-item>
        <el-descriptions-item label="合同编号">{{ project.contract_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="区域">{{ project.region || '-' }}</el-descriptions-item>
        <el-descriptions-item label="客户/甲方">{{ project.client || '-' }}</el-descriptions-item>
        <el-descriptions-item label="项目经理">{{ project.manager || '-' }}</el-descriptions-item>
        <el-descriptions-item label="预算人天">{{ project.budget_mandays }} 天</el-descriptions-item>
        <el-descriptions-item label="项目阶段">{{ phaseLabel(project.phase) }}</el-descriptions-item>
        <el-descriptions-item label="项目状态">
          <el-tag :type="statusType(project.status)">{{ statusLabel(project.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label=""> </el-descriptions-item>
        <el-descriptions-item label="计划开始">{{ project.plan_start || '-' }}</el-descriptions-item>
        <el-descriptions-item label="计划结束">{{ project.plan_end || '-' }}</el-descriptions-item>
        <el-descriptions-item label="实际开始">{{ project.actual_start || '-' }}</el-descriptions-item>
        <el-descriptions-item label="计划交付">{{ project.plan_delivery_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="实际交付">{{ project.actual_delivery_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label=""> </el-descriptions-item>
        <el-descriptions-item label="计划初验">{{ project.plan_initial_acceptance_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="实际初验">{{ project.actual_initial_acceptance_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label=""> </el-descriptions-item>
        <el-descriptions-item label="计划终验">{{ project.plan_final_acceptance_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="实际终验">{{ project.actual_final_acceptance_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label=""> </el-descriptions-item>
        <el-descriptions-item label="项目描述" :span="3">{{ project.description || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">
        <el-button size="small" @click="$router.push(`/projects/${id}/milestones`)"><el-icon><Calendar /></el-icon> 里程碑进度</el-button>
        <el-button size="small" @click="$router.push(`/projects/${id}/issues`)"><el-icon><Warning /></el-icon> 问题台账</el-button>
        <el-button size="small" @click="$router.push(`/projects/${id}/risks`)"><el-icon><Bell /></el-icon> 风险台账</el-button>
        <el-button size="small" @click="$router.push(`/projects/${id}/mandays`)"><el-icon><Timer /></el-icon> 人天管理</el-button>
        <el-button size="small" @click="$router.push(`/projects/${id}/weekly-progress`)"><el-icon><Document /></el-icon> 周报进展</el-button>
        <el-button size="small" type="success" @click="$router.push(`/projects/${id}/reports`)"><el-icon><Document /></el-icon> 生成报告</el-button>
      </div>
    </div>

    <!-- 甘特图 -->
    <div v-if="project" class="page-card">
      <div class="gantt-title-bar">
        <h3 style="margin:0;font-size:16px;color:#2E4057">📊 项目甘特图</h3>
        <el-radio-group v-model="dayPxMode" size="small">
          <el-radio-button label="compact">紧凑</el-radio-button>
          <el-radio-button label="normal">标准</el-radio-button>
          <el-radio-button label="wide">宽松</el-radio-button>
        </el-radio-group>
      </div>
      <div v-loading="ganttLoading" style="min-height:120px">
        <GanttChart
          v-if="!ganttLoading"
          :project="project"
          :milestones="milestones"
          :tasks="tasks"
          :day-px="dayPxValue"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { projectApi, milestoneApi, taskApi } from '@/api'
import GanttChart from '@/components/GanttChart.vue'
import { useDictStore } from '@/stores/dict'

const dictStore = useDictStore()

// ── 字典转换函数 ─────────────────────────────────────────
function statusLabel(s) {
  return dictStore.getDictItem('project_status', s).label || s
}
function phaseLabel(p) {
  return dictStore.getDictItem('project_phase', p).label || p
}

const route = useRoute()
const id = route.params.id
const project = ref(null)
const milestones = ref([])
const tasks = ref([])
const ganttLoading = ref(false)
const dayPxMode = ref('normal')

const dayPxValue = computed(() => ({ compact: 10, normal: 14, wide: 20 }[dayPxMode.value])  )

onMounted(async () => {
  project.value = await projectApi.get(id)
  ganttLoading.value = true
  try {
    const [ms, ts] = await Promise.all([milestoneApi.list(id), taskApi.list(id)])
    milestones.value = ms
    tasks.value = ts
  } finally {
    ganttLoading.value = false
  }
})

function statusType(s) {
  return { 'st_normal': 'success', 'st_warn': 'warning', 'st_delay': 'danger', 'st_done': 'info', 'st_pause': '' }[s] || ''
}
</script>

<style scoped>
.gantt-title-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
</style>
