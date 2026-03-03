<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">人天管理</h2>
      <div style="display:flex;gap:8px;flex-shrink:0">
        <el-button @click="downloadMd" :loading="downloading" class="hide-mobile"><el-icon><Download /></el-icon> 导出报表</el-button>
        <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon> 记录人天</el-button>
      </div>
    </div>

    <!-- 统计汇总 -->
    <el-row :gutter="16" style="margin-bottom:16px" v-if="stats">
      <el-col :xs="12" :sm="6">
        <div class="stat-card"><div class="icon" style="background:#4472C4"><el-icon style="color:#fff;font-size:22px"><Timer /></el-icon></div>
          <div><div class="value" style="color:#4472C4">{{ stats.total_days }}</div><div class="label">累计人天</div></div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card"><div class="icon" style="background:#70AD47"><el-icon style="color:#fff;font-size:22px"><Money /></el-icon></div>
          <div><div class="value" style="color:#70AD47">{{ stats.billable_days }}</div><div class="label">计费人天</div></div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card"><div class="icon" style="background:#FFC000"><el-icon style="color:#fff;font-size:22px"><Clock /></el-icon></div>
          <div><div class="value" style="color:#FFC000">{{ stats.non_billable_days }}</div><div class="label">非计费人天</div></div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card"><div class="icon" style="background:#2E4057"><el-icon style="color:#fff;font-size:22px"><DataBoard /></el-icon></div>
          <div><div class="value" :style="{ color: stats.total_days > stats.budget_mandays ? '#FF4444' : '#2E4057' }">
            {{ stats.budget_mandays }}</div><div class="label">预算人天</div></div>
        </div>
      </el-col>
    </el-row>

    <!-- 人员汇总 -->
    <div class="page-card" style="margin-bottom:12px" v-if="stats?.staff_breakdown?.length">
      <h4 style="margin-bottom:10px">人员人天汇总</h4>
      <el-table :data="stats.staff_breakdown" size="small" border>
        <el-table-column prop="staff_name" label="人员姓名" width="130" />
        <el-table-column prop="role" label="角色" width="130" />
        <el-table-column prop="total" label="合计人天" width="110" align="center" />
      </el-table>
    </div>

    <!-- 權明细 PC 表格 -->
    <div class="page-card hide-mobile">
      <h4 style="margin-bottom:10px">人天明细</h4>
      <el-table :data="mandays" stripe border v-loading="loading" style="width:100%">
        <el-table-column prop="work_date" label="日期" width="110" />
        <el-table-column prop="staff_name" label="人员" width="100" />
        <el-table-column prop="role" label="角色" width="120" />
        <el-table-column prop="days" label="人天数" width="90" align="center" />
        <el-table-column prop="is_billable" label="计费" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_billable ? 'success' : ''" size="small">{{ row.is_billable ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="work_content" label="工作内容" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="110" align="center">
          <template #default="{ row }">
            <el-button size="small" type="warning" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确认删除？" @confirm="remove(row.id)">
              <template #reference><el-button size="small" type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 手机端人天明细卡片 -->
    <div class="show-mobile" v-loading="loading">
      <div v-if="mandays.length === 0 && !loading" style="text-align:center;padding:40px;color:#aaa;">暂无数据</div>
      <div class="mobile-card-list">
        <div class="m-card" v-for="row in mandays" :key="row.id">
          <div class="m-card-header">
            <div class="m-card-title">{{ row.staff_name }}</div>
            <el-tag :type="row.is_billable ? 'success' : ''" size="small">{{ row.is_billable ? '计费' : '非计费' }}</el-tag>
          </div>
          <div class="m-card-body">
            <div class="m-field"><span class="m-field-label">日期</span><span class="m-field-value">{{ row.work_date }}</span></div>
            <div class="m-field"><span class="m-field-label">人天数</span><span class="m-field-value">{{ row.days }} 天</span></div>
            <div class="m-field"><span class="m-field-label">角色</span><span class="m-field-value">{{ row.role || '-' }}</span></div>
            <div class="m-field" style="grid-column:1/-1">
              <span class="m-field-label">工作内容</span>
              <span class="m-field-value">{{ row.work_content || '-' }}</span>
            </div>
          </div>
          <div class="m-card-footer">
            <el-button size="small" type="warning" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确认删除？" @confirm="remove(row.id)">
              <template #reference><el-button size="small" type="danger">删除</el-button></template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="dlg" :title="editId ? '编辑人天记录' : '新建人天记录'" width="min(520px, 95vw)">
      <el-form :model="form" label-width="90px">
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="人员姓名"><el-input v-model="form.staff_name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="角色"><el-input v-model="form.role" placeholder="如：实施顾问" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="工作日期"><el-date-picker v-model="form.work_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="投入人天"><el-input-number v-model="form.days" :min="0.5" :step="0.5" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="是否计费"><el-switch v-model="form.is_billable" active-text="计费" inactive-text="不计费" /></el-form-item>
        <el-form-item label="工作内容"><el-input v-model="form.work_content" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { mandayApi, reportApi, downloadBlob } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const pid = route.params.id
const mandays = ref([])
const stats = ref(null)
const loading = ref(false)
const downloading = ref(false)
const dlg = ref(false)
const editId = ref(null)
const df = () => ({ staff_name:'', role:'', work_date:null, days:1, is_billable:true, work_content:'' })
const form = ref(df())

async function load() {
  loading.value = true
  try {
    [mandays.value, stats.value] = await Promise.all([mandayApi.list(pid), mandayApi.stats(pid)])
  } finally { loading.value = false }
}
function openDialog(row = null) {
  editId.value = row?.id || null
  form.value = row ? { ...row } : df()
  dlg.value = true
}
async function save() {
  if (!form.value.staff_name || !form.value.work_date) { ElMessage.warning('人员姓名和日期必填'); return }
  if (editId.value) await mandayApi.update(editId.value, form.value)
  else await mandayApi.create(pid, { ...form.value, project_id: Number(pid) })
  ElMessage.success('保存成功'); dlg.value = false; await load()
}
async function remove(id) {
  await mandayApi.remove(id); ElMessage.success('已删除'); await load()
}
async function downloadMd() {
  downloading.value = true
  try { const res = await reportApi.mandays(pid); downloadBlob(res, '人天统计.xlsx'); ElMessage.success('导出成功') }
  finally { downloading.value = false }
}
onMounted(load)
</script>
<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
</style>
