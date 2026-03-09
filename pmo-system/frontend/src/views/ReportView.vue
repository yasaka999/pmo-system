<template>
  <div>
    <h2 class="page-title" style="margin-bottom:20px">报告生成</h2>

    <el-row :gutter="16">
      <!-- 周报 -->
      <el-col :span="12">
        <div class="page-card report-card">
          <div class="report-icon" style="background:#4472C4">📄</div>
          <h3>项目周报</h3>
          <p>包含里程碑进度、本周工作、下周计划、问题与风险</p>
          <el-form label-position="top" style="margin-top:12px">
            <el-form-item label="周报日期（可选）">
              <el-date-picker v-model="weeklyDate" type="date" value-format="YYYY-MM-DD" placeholder="默认今日" style="width:100%" />
            </el-form-item>
          </el-form>
          <el-button type="primary" style="width:100%" @click="download('weekly')" :loading="loading.weekly">
            <el-icon><Download /></el-icon> 下载周报 (Word)
          </el-button>
        </div>
      </el-col>

      <!-- 月报 -->
      <el-col :span="12">
        <div class="page-card report-card">
          <div class="report-icon" style="background:#70AD47">📊</div>
          <h3>项目月报</h3>
          <p>包含里程碑完成情况、本月人天投入、问题与风险汇总</p>
          <el-form label-position="top" style="margin-top:12px">
            <el-form-item label="选择年月">
              <el-date-picker v-model="monthlyDate" type="month" value-format="YYYY-MM" placeholder="如：2024-03" style="width:100%" />
            </el-form-item>
          </el-form>
          <el-button type="success" style="width:100%" @click="download('monthly')" :loading="loading.monthly">
            <el-icon><Download /></el-icon> 下载月报 (Word)
          </el-button>
        </div>
      </el-col>

      <!-- 问题风险台账 -->
      <el-col :span="12" style="margin-top:16px">
        <div class="page-card report-card">
          <div class="report-icon" style="background:#FF4444">⚠️</div>
          <h3>问题与风险台账</h3>
          <p>导出全部问题/风险明细，包含颜色标注的优先级</p>
          <div style="height:60px" />
          <el-button type="danger" style="width:100%" @click="download('issueRisk')" :loading="loading.issueRisk">
            <el-icon><Download /></el-icon> 下载台账 (Excel)
          </el-button>
        </div>
      </el-col>

      <!-- 人天报表 -->
      <el-col :span="12" style="margin-top:16px">
        <div class="page-card report-card">
          <div class="report-icon" style="background:#FFC000">⏱️</div>
          <h3>人天统计报表</h3>
          <p>人员投入明细及汇总，含计费/非计费分类统计</p>
          <div style="height:60px" />
          <el-button type="warning" style="width:100%" @click="download('mandays')" :loading="loading.mandays">
            <el-icon><Download /></el-icon> 下载报表 (Excel)
          </el-button>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { reportApi, downloadBlob } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const pid = route.params.id
const weeklyDate = ref('')
const monthlyDate = ref('')

const loading = ref({ weekly: false, monthly: false, issueRisk: false, mandays: false })

async function download(type) {
  loading.value[type] = true
  try {
    let res, filename
    if (type === 'weekly') {
      res = await reportApi.weekly(pid, weeklyDate.value || null)
      filename = `周报_${weeklyDate.value || '今日'}.docx`
    } else if (type === 'monthly') {
      if (!monthlyDate.value) { ElMessage.warning('请选择年月'); return }
      const [y, m] = monthlyDate.value.split('-')
      res = await reportApi.monthly(pid, y, m)
      filename = `月报_${monthlyDate.value}.docx`
    } else if (type === 'issueRisk') {
      res = await reportApi.issueRisk(pid)
      filename = '问题风险台账.xlsx'
    } else if (type === 'mandays') {
      res = await reportApi.mandays(pid)
      filename = '人天统计报表.xlsx'
    }
    downloadBlob(res, filename)
    ElMessage.success('下载成功')
  } finally { loading.value[type] = false }
}
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; color: #2E4057; }
.report-card { text-align: center; padding: 28px 24px; }
.report-icon { width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 26px; margin: 0 auto 12px; }
.report-card h3 { font-size: 16px; font-weight: 600; margin-bottom: 6px; }
.report-card p  { color: #888; font-size: 13px; line-height: 1.5; }
</style>
