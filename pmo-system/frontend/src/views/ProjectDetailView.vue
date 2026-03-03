<template>
  <div>
    <div v-if="project" class="page-card" style="margin-bottom:16px">
      <el-descriptions :title="project.name" :column="3" border>
        <el-descriptions-item label="项目编号">{{ project.code }}</el-descriptions-item>
        <el-descriptions-item label="合同编号">{{ project.contract_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="区域">{{ project.region || '-' }}</el-descriptions-item>
        <el-descriptions-item label="客户/甲方">{{ project.client || '-' }}</el-descriptions-item>
        <el-descriptions-item label="项目经理">{{ project.manager || '-' }}</el-descriptions-item>
        <el-descriptions-item label="预算人天">{{ project.budget_mandays }} 天</el-descriptions-item>
        <el-descriptions-item label="项目阶段">{{ project.phase }}</el-descriptions-item>
        <el-descriptions-item label="项目状态">
          <el-tag :type="statusType(project.status)">{{ project.status }}</el-tag>
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
      <div style="margin-top:12px;display:flex;gap:8px">
        <el-button size="small" @click="$router.push(`/projects/${id}/milestones`)"><el-icon><Calendar /></el-icon> 里程碑进度</el-button>
        <el-button size="small" @click="$router.push(`/projects/${id}/issues`)"><el-icon><Warning /></el-icon> 问题台账</el-button>
        <el-button size="small" @click="$router.push(`/projects/${id}/risks`)"><el-icon><Bell /></el-icon> 风险台账</el-button>
        <el-button size="small" @click="$router.push(`/projects/${id}/mandays`)"><el-icon><Timer /></el-icon> 人天管理</el-button>
        <el-button size="small" type="success" @click="$router.push(`/projects/${id}/reports`)"><el-icon><Document /></el-icon> 生成报告</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { projectApi } from '@/api'

const route = useRoute()
const id = route.params.id
const project = ref(null)

onMounted(async () => {
  project.value = await projectApi.get(id)
})

function statusType(s) {
  return { '正常': 'success', '预警': 'warning', '延期': 'danger', '已完成': 'info', '暂停': '' }[s] || ''
}
</script>
