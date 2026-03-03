<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2 class="page-title">问题台账</h2>
      <div>
        <el-button @click="downloadIssueRisk" :loading="downloading"><el-icon><Download /></el-icon> 导出Excel</el-button>
        <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon> 新建问题</el-button>
      </div>
    </div>

    <div class="page-card" style="padding:12px 20px;margin-bottom:12px">
      <el-row :gutter="12">
        <el-col :span="4">
          <el-select v-model="filterStatus" placeholder="状态" clearable @change="load">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterSeverity" placeholder="严重等级" clearable @change="load">
            <el-option v-for="s in severityOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <div class="page-card">
      <el-table :data="issues" stripe border v-loading="loading">
        <el-table-column prop="title" label="问题" min-width="220" />
        <el-table-column prop="severity" label="等级" width="80">
          <template #default="{ row }">
            <el-tag :type="sevType(row.severity)" size="small">{{ dictLabel('issue_severity', row.severity) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="90">
          <template #default="{ row }">{{ dictLabel('issue_source', row.source) }}</template>
        </el-table-column>
        <el-table-column prop="assignee" label="负责人" width="100" />
        <el-table-column prop="raised_date" label="提出日期" width="110" />
        <el-table-column prop="due_date" label="期望解决" width="110" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ dictLabel('issue_status', row.status) }}</el-tag>
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

    <el-dialog v-model="dlg" :title="editId ? '编辑问题' : '新建问题'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="问题标题"><el-input v-model="form.title" /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="严重等级">
              <el-select v-model="form.severity" style="width:100%">
                <el-option v-for="s in severityOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="来源">
              <el-select v-model="form.source" style="width:100%">
                <el-option v-for="s in sourceOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width:100%">
                <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="8"><el-form-item label="负责人"><el-input v-model="form.assignee" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="提出日期"><el-date-picker v-model="form.raised_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="期望解决"><el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="实际解决"><el-date-picker v-model="form.resolved_date" type="date" value-format="YYYY-MM-DD" style="width:200px" /></el-form-item>
        <el-form-item label="问题描述"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="解决措施"><el-input v-model="form.resolution" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { issueApi, reportApi, downloadBlob } from '@/api'
import { ElMessage } from 'element-plus'
import { useDictStore } from '@/stores/dict'

const dictStore = useDictStore()
const route = useRoute()
const pid = route.params.id
const issues = ref([])
const loading = ref(false)
const downloading = ref(false)
const dlg = ref(false)
const editId = ref(null)
const filterStatus = ref('')
const filterSeverity = ref('')

const statusOptions = computed(() => dictStore.getOptions('issue_status'))
const severityOptions = computed(() => dictStore.getOptions('issue_severity'))
const sourceOptions = computed(() => dictStore.getOptions('issue_source'))

const df = () => ({ title:'', severity:'中', source:'内部', assignee:'', raised_date:null, due_date:null, resolved_date:null, status:'待处理', description:'', resolution:'' })
const form = ref(df())

async function load() {
  loading.value = true
  const params = {}
  if (filterStatus.value) params.status = filterStatus.value
  if (filterSeverity.value) params.severity = filterSeverity.value
  try { issues.value = await issueApi.list(pid, params) } finally { loading.value = false }
}

function openDialog(row = null) {
  editId.value = row?.id || null
  form.value = row ? { ...row } : df()
  dlg.value = true
}

async function save() {
  if (!form.value.title) { ElMessage.warning('问题标题必填'); return }
  if (editId.value) await issueApi.update(editId.value, form.value)
  else await issueApi.create(pid, { ...form.value, project_id: Number(pid) })
  ElMessage.success('保存成功'); dlg.value = false; await load()
}

async function remove(id) {
  await issueApi.remove(id); ElMessage.success('已删除'); await load()
}

async function downloadIssueRisk() {
  downloading.value = true
  try { const res = await reportApi.issueRisk(pid); downloadBlob(res, '问题风险台账.xlsx'); ElMessage.success('导出成功') }
  finally { downloading.value = false }
}

function dictLabel(cat, val) {
  return dictStore.getDictItem(cat, val).label || val
}

function sevType(s) {
  const c = dictStore.getDictItem('issue_severity', s).color
  return c || { '高': 'danger', '中': 'warning', '低': 'success' }[s] || ''
}
function statusType(s) {
  const c = dictStore.getDictItem('issue_status', s).color
  return c || { '待处理': 'danger', '处理中': 'warning', '已关闭': 'success' }[s] || ''
}

onMounted(() => {
  dictStore.fetchDicts()
  load()
})
</script>
<style scoped>
.page-title { font-size: 20px; font-weight: 600; color: #2E4057; }
</style>
