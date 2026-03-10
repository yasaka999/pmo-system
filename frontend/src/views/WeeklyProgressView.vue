<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">周报进展</h2>
      <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon> 添加记录</el-button>
    </div>

    <!-- PC 表格 -->
    <div class="page-card hide-mobile">
      <el-table :data="progressList" stripe border v-loading="loading" style="width:100%">
        <el-table-column prop="record_date" label="记录日期" width="120" align="center">
          <template #default="{ row }">
            {{ formatDate(row.record_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="progress_percent" label="进度" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.progress_percent > 0" :type="progressType(row.progress_percent)" size="small">
              {{ row.progress_percent }}%
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="工作内容" min-width="250" show-overflow-tooltip />
        <el-table-column prop="next_plan" label="下周计划" min-width="180" show-overflow-tooltip />
        <el-table-column prop="issues" label="遇到问题" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.issues" class="text-danger">{{ row.issues }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="creator_name" label="记录人" width="100" align="center">
          <template #default="{ row }">
            {{ row.creator_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button size="small" type="warning" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确认删除？" @confirm="remove(row.id)">
              <template #reference><el-button size="small" type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 手机端卡片列表 -->
    <div class="show-mobile" v-loading="loading">
      <div v-if="progressList.length === 0 && !loading" style="text-align:center;padding:40px;color:#aaa;">暂无数据</div>
      <div class="mobile-card-list">
        <div class="m-card" v-for="row in progressList" :key="row.id">
          <div class="m-card-header">
            <div class="m-card-title">{{ formatDate(row.record_date) }}</div>
            <el-tag v-if="row.progress_percent > 0" :type="progressType(row.progress_percent)" size="small">
              {{ row.progress_percent }}%
            </el-tag>
          </div>
          <div class="m-card-body">
            <div class="m-field" style="grid-column:1/-1">
              <span class="m-field-label">工作内容</span>
              <span class="m-field-value" style="white-space:pre-wrap">{{ row.content || '-' }}</span>
            </div>
            <div class="m-field" style="grid-column:1/-1">
              <span class="m-field-label">下周计划</span>
              <span class="m-field-value" style="white-space:pre-wrap">{{ row.next_plan || '-' }}</span>
            </div>
            <div v-if="row.issues" class="m-field" style="grid-column:1/-1">
              <span class="m-field-label">遇到问题</span>
              <span class="m-field-value text-danger" style="white-space:pre-wrap">{{ row.issues }}</span>
            </div>
            <div class="m-field">
              <span class="m-field-label">记录人</span>
              <span class="m-field-value">{{ row.creator_name || '-' }}</span>
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

    <!-- 对话框 -->
    <el-dialog v-model="dlg" :title="editId ? '编辑周报进展' : '添加周报进展'" width="min(600px, 95vw)">
      <el-form :model="form" label-width="90px" ref="formRef" :rules="rules">
        <el-form-item label="记录日期" prop="record_date">
          <el-date-picker v-model="form.record_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="完成进度" prop="progress_percent">
          <el-slider v-model="form.progress_percent" :max="100" show-stops />
        </el-form-item>
        <el-form-item label="工作内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="4" placeholder="请描述本周工作进展..." />
        </el-form-item>
        <el-form-item label="下周计划" prop="next_plan">
          <el-input v-model="form.next_plan" type="textarea" :rows="2" placeholder="请输入下周工作计划（可选）" />
        </el-form-item>
        <el-form-item label="遇到问题" prop="issues">
          <el-input v-model="form.issues" type="textarea" :rows="2" placeholder="请输入遇到的问题（可选）" />
        </el-form-item>
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
import { weeklyProgressApi } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const pid = route.params.id
const progressList = ref([])
const loading = ref(false)
const dlg = ref(false)
const editId = ref(null)
const formRef = ref()

const rules = {
  record_date: [{ required: true, message: '请选择记录日期', trigger: 'change' }],
  content: [{ required: true, message: '请输入工作内容', trigger: 'blur' }]
}

const df = () => ({ 
  record_date: new Date().toISOString().split('T')[0], 
  content: '', 
  progress_percent: 0, 
  next_plan: '', 
  issues: '' 
})
const form = ref(df())

async function load() {
  loading.value = true
  try { 
    progressList.value = await weeklyProgressApi.list(pid) 
  } finally { 
    loading.value = false 
  }
}

function openDialog(row = null) {
  editId.value = row?.id || null
  form.value = row ? { ...row } : df()
  dlg.value = true
}

async function save() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  if (editId.value) {
    await weeklyProgressApi.update(editId.value, form.value)
  } else {
    await weeklyProgressApi.create(pid, { ...form.value, project_id: Number(pid) })
  }
  ElMessage.success('保存成功')
  dlg.value = false
  await load()
}

async function remove(id) {
  await weeklyProgressApi.remove(id)
  ElMessage.success('已删除')
  await load()
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function progressType(percent) {
  if (percent >= 80) return 'success'
  if (percent >= 50) return 'warning'
  return 'info'
}

onMounted(() => { load() })
</script>

<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.text-danger { color: #f56c6c; }
</style>