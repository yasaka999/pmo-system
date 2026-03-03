<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <h2 class="page-title">项目列表</h2>
      <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon> 新建项目</el-button>
    </div>

    <!-- 筛选 -->
    <div class="page-card" style="padding:12px 20px">
      <el-row :gutter="12" align="middle">
        <el-col :span="7">
          <el-input
            v-model="search"
            placeholder="搜索项目名称/编号/客户"
            prefix-icon="Search"
            clearable
            @input="filterProjects"
          />
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="filterStatuses"
            placeholder="状态筛选（可多选）"
            multiple
            collapse-tags
            collapse-tags-tooltip
            clearable
            style="width:100%"
            @change="filterProjects"
          >
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.label" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="filterPhases"
            placeholder="阶段筛选（可多选）"
            multiple
            collapse-tags
            collapse-tags-tooltip
            clearable
            style="width:100%"
            @change="filterProjects"
          >
            <el-option v-for="p in phaseOptions" :key="p.value" :label="p.label" :value="p.label" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-button @click="resetFilter" plain>重置</el-button>
          <span style="margin-left:12px;color:#888;font-size:13px">共 {{ filtered.length }} 个项目</span>
        </el-col>
      </el-row>
    </div>

    <div class="page-card">
      <el-table :data="filtered" stripe border v-loading="loading" style="width:100%">
        <el-table-column prop="code" label="项目编号" width="130" />
        <el-table-column prop="name" label="项目名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push(`/projects/${row.id}`)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="client" label="客户" width="150" />
        <el-table-column prop="manager" label="项目经理" width="110" />
        <el-table-column prop="phase" label="阶段" width="90" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="plan_end" label="计划结束" width="110" />
        <el-table-column label="人天" width="110" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="row.budget_mandays > 0 ? Math.min(Math.round(row.used_mandays / row.budget_mandays * 100), 100) : 0"
              :color="row.used_mandays > row.budget_mandays ? '#FF4444' : '#70AD47'"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/projects/${row.id}`)">详情</el-button>
            <!-- 编辑/删除仅对有权限的用户显示 -->
            <template v-if="canManage(row)">
              <el-button size="small" type="warning" @click="openDialog(row)">编辑</el-button>
              <el-popconfirm title="确认删除该项目？" @confirm="deleteProject(row.id)">
                <template #reference>
                  <el-button size="small" type="danger">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑项目' : '新建项目'" width="640px">
      <el-form :model="form" label-width="100px" label-position="right">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="项目编号" required><el-input v-model="form.code" :disabled="!!editId" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目状态"><el-select v-model="form.status" style="width:100%">
              <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.label" />
            </el-select></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="项目名称" required><el-input v-model="form.name" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="客户/甲方"><el-input v-model="form.client" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目经理"><el-input v-model="form.manager" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="项目阶段"><el-select v-model="form.phase" style="width:100%">
              <el-option v-for="p in phaseOptions" :key="p.value" :label="p.label" :value="p.label" />
            </el-select></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预算人天"><el-input-number v-model="form.budget_mandays" :min="0" :precision="1" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="计划开始"><el-date-picker v-model="form.plan_start" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计划结束"><el-date-picker v-model="form.plan_end" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="项目描述"><el-input type="textarea" v-model="form.description" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveProject">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { projectApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useDictStore } from '@/stores/dict'
import { useAuthStore } from '@/stores/auth'

const dictStore = useDictStore()
const auth = useAuthStore()

const projects = ref([])
const filtered = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const search = ref('')
const filterStatuses = ref([])   // 多选状态
const filterPhases = ref([])     // 多选阶段
const editId = ref(null)

// 字典选项（getOptions 已返回 { label, value, color } 对象，label 是显示文字，label 也是与 p.status 匹配的值）
const statusOptions = computed(() => dictStore.getOptions('project_status'))
const phaseOptions = computed(() => dictStore.getOptions('project_phase'))

const defaultForm = () => ({
  code: '', name: '', client: '', manager: '', phase: '实施',
  status: '正常', plan_start: null, plan_end: null, budget_mandays: 0, description: ''
})
const form = ref(defaultForm())

// 判断当前用户是否有权限管理某个项目
function canManage(row) {
  const role = auth.user?.role
  if (role === 'admin' || role === 'pmo') return true
  return row.created_by === auth.user?.id
}

async function load() {
  loading.value = true
  try {
    projects.value = await projectApi.list()
    filterProjects()
  } finally {
    loading.value = false
  }
}

function filterProjects() {
  filtered.value = projects.value.filter(p => {
    const q = search.value.trim().toLowerCase()
    const matchText = !q || p.name.toLowerCase().includes(q) || p.code.toLowerCase().includes(q) || (p.client || '').toLowerCase().includes(q)
    const matchStatus = filterStatuses.value.length === 0 || filterStatuses.value.includes(p.status)
    const matchPhase = filterPhases.value.length === 0 || filterPhases.value.includes(p.phase)
    return matchText && matchStatus && matchPhase
  })
}

function resetFilter() {
  search.value = ''
  filterStatuses.value = []
  filterPhases.value = []
  filterProjects()
}

function openDialog(row = null) {
  editId.value = row?.id || null
  form.value = row ? { ...row } : defaultForm()
  dialogVisible.value = true
}

async function saveProject() {
  if (!form.value.code || !form.value.name) { ElMessage.warning('项目编号和名称为必填项'); return }
  saving.value = true
  try {
    if (editId.value) await projectApi.update(editId.value, form.value)
    else await projectApi.create(form.value)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    await load()
  } catch {
    // 错误已在拦截器中处理
  } finally {
    saving.value = false
  }
}

async function deleteProject(id) {
  try {
    await projectApi.remove(id)
    ElMessage.success('已删除')
    await load()
  } catch {
    // 错误已在拦截器中处理
  }
}

function statusType(s) {
  const item = dictStore.getDictItem('project_status', s)
  return item.color || (
    { '正常': 'success', '预警': 'warning', '延期': 'danger', '已完成': 'info', '暂停': '' }[s] || ''
  )
}

onMounted(() => {
  dictStore.fetchDicts()
  load()
})
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; color: #2E4057; }
</style>
