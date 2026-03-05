<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <h2 class="page-title">项目列表</h2>
      <div style="display:flex;gap:8px">
        <el-button @click="colDlgVisible = true" plain size="small">
          <el-icon><Setting /></el-icon> 列设置
        </el-button>
        <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon> 新建项目</el-button>
      </div>
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
        <!-- 动态列（根据 visibleCols 顺序渲染） -->
        <template v-for="col in visibleCols" :key="col.key">
          <!-- 项目名称列（带链接） -->
          <el-table-column v-if="col.key === 'name'" :label="col.label" min-width="180">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/projects/${row.id}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <!-- 状态列（带 Tag） -->
          <el-table-column v-else-if="col.key === 'status'" :label="col.label" width="90">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <!-- 人天使用列（进度条） -->
          <el-table-column v-else-if="col.key === 'mandays'" :label="col.label" width="120" align="center">
            <template #default="{ row }">
              <el-progress
                :percentage="row.budget_mandays > 0 ? Math.min(Math.round(row.used_mandays/row.budget_mandays*100),100) : 0"
                :color="row.used_mandays > row.budget_mandays ? '#FF4444' : '#70AD47'"
                :stroke-width="8"
              />
            </template>
          </el-table-column>
          <!-- 普通文本列 -->
          <el-table-column v-else :prop="col.prop" :label="col.label" :width="col.width" />
        </template>
        <!-- 操作列（始终固定在最后） -->
        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/projects/${row.id}`)">详情</el-button>
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

    <!-- ── 列设置弹窗 ── -->
    <el-dialog v-model="colDlgVisible" title="列设置" width="360px" append-to-body>
      <p style="font-size:12px;color:#999;margin:0 0 12px">开关控制列的显示/隐藏，↑↓ 调整列顺序。</p>
      <div class="col-config-list">
        <div v-for="(col, idx) in colDefs" :key="col.key" class="col-config-row">
          <span class="col-seq">{{ idx + 1 }}</span>
          <span class="col-name">{{ col.label }}</span>
          <div style="display:flex;align-items:center;gap:6px">
            <el-switch v-model="col.visible" :disabled="col.required" />
            <el-button-group size="small">
              <el-button :disabled="idx === 0" @click="moveCol(idx, -1)">↑</el-button>
              <el-button :disabled="idx === colDefs.length - 1" @click="moveCol(idx, 1)">↓</el-button>
            </el-button-group>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button size="small" @click="resetCols">恢复默认</el-button>
        <el-button size="small" @click="colDlgVisible = false">关闭</el-button>
      </template>
    </el-dialog>

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
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="合同编号"><el-input v-model="form.contract_no" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="区域"><el-input v-model="form.region" placeholder="如：华东区" /></el-form-item>
          </el-col>
        </el-row>
        <!-- 交付日期 -->
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="计划交付"><el-date-picker v-model="form.plan_delivery_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实际交付"><el-date-picker v-model="form.actual_delivery_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <!-- 初验日期 -->
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="计划初验"><el-date-picker v-model="form.plan_initial_acceptance_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实际初验"><el-date-picker v-model="form.actual_initial_acceptance_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <!-- 终验日期 -->
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="计划终验"><el-date-picker v-model="form.plan_final_acceptance_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实际终验"><el-date-picker v-model="form.actual_final_acceptance_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
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
import { ref, onMounted, computed, reactive, watch } from 'vue'
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
const colDlgVisible = ref(false)

// ── 列配置：全部可配置列定义 ───────────────────────────────
const DEFAULT_COLS = [
  { key: 'code',        label: '项目编号',   prop: 'code',        width: 130,  visible: true,  required: false },
  { key: 'name',        label: '项目名称',   prop: 'name',        width: null, visible: true,  required: true  },
  { key: 'contract_no', label: '合同编号',   prop: 'contract_no', width: 140,  visible: false, required: false },
  { key: 'region',      label: '区域',       prop: 'region',      width: 100,  visible: false, required: false },
  { key: 'client',      label: '客户',       prop: 'client',      width: 140,  visible: true,  required: false },
  { key: 'manager',     label: '项目经理',   prop: 'manager',     width: 110,  visible: true,  required: false },
  { key: 'phase',       label: '阶段',       prop: 'phase',       width: 90,   visible: true,  required: false },
  { key: 'status',      label: '状态',       prop: 'status',      width: 90,   visible: true,  required: false },
  { key: 'plan_start',  label: '计划开始',   prop: 'plan_start',  width: 105,  visible: false, required: false },
  { key: 'plan_end',    label: '计划结束',   prop: 'plan_end',    width: 105,  visible: true,  required: false },
  { key: 'plan_delivery_date',            label: '计划交付',   prop: 'plan_delivery_date',            width: 105, visible: false, required: false },
  { key: 'actual_delivery_date',          label: '实际交付',   prop: 'actual_delivery_date',          width: 105, visible: false, required: false },
  { key: 'plan_initial_acceptance_date',  label: '计划初验',   prop: 'plan_initial_acceptance_date',  width: 105, visible: false, required: false },
  { key: 'actual_initial_acceptance_date',label: '实际初验',   prop: 'actual_initial_acceptance_date',width: 105, visible: false, required: false },
  { key: 'plan_final_acceptance_date',    label: '计划终验',   prop: 'plan_final_acceptance_date',    width: 105, visible: false, required: false },
  { key: 'actual_final_acceptance_date',  label: '实际终验',   prop: 'actual_final_acceptance_date',  width: 105, visible: false, required: false },
  { key: 'mandays',     label: '人天使用',   prop: null,          width: 120,  visible: true,  required: false },
]

const COL_KEY = 'project_list_cols'

function loadColDefs() {
  try {
    const saved = JSON.parse(localStorage.getItem(COL_KEY) || 'null')
    if (!saved) return DEFAULT_COLS.map(c => ({ ...c }))
    // 将保存的 visible+顺序应用到默认定义，新增字段 fallback 到默认
    const map = Object.fromEntries(saved.map(s => [s.key, s]))
    return saved
      .filter(s => DEFAULT_COLS.some(d => d.key === s.key))
      .map(s => ({ ...DEFAULT_COLS.find(d => d.key === s.key), visible: s.visible }))
      .concat(DEFAULT_COLS.filter(d => !map[d.key]))
  } catch { return DEFAULT_COLS.map(c => ({ ...c })) }
}

const colDefs = reactive(loadColDefs())
watch(colDefs, v => localStorage.setItem(COL_KEY, JSON.stringify(v.map(c => ({ key: c.key, visible: c.visible })))), { deep: true })

const visibleCols = computed(() => colDefs.filter(c => c.visible))

function moveCol(idx, dir) {
  const newIdx = idx + dir
  if (newIdx < 0 || newIdx >= colDefs.length) return
  const tmp = colDefs[idx]
  colDefs[idx] = colDefs[newIdx]
  colDefs[newIdx] = tmp
}

function resetCols() {
  const fresh = DEFAULT_COLS.map(c => ({ ...c }))
  colDefs.splice(0, colDefs.length, ...fresh)
  localStorage.removeItem(COL_KEY)
}

// 字典选项（getOptions 已返回 { label, value, color } 对象，label 是显示文字，label 也是与 p.status 匹配的值）
const statusOptions = computed(() => dictStore.getOptions('project_status'))
const phaseOptions = computed(() => dictStore.getOptions('project_phase'))

const defaultForm = () => ({
  code: '', name: '', client: '', manager: '', phase: '实施',
  status: '正常', plan_start: null, plan_end: null, budget_mandays: 0, description: '',
  contract_no: '', region: '',
  plan_delivery_date: null, actual_delivery_date: null,
  plan_initial_acceptance_date: null, actual_initial_acceptance_date: null,
  plan_final_acceptance_date: null, actual_final_acceptance_date: null,
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

/* 列设置弹窗 */
.col-config-list { display: flex; flex-direction: column; }
.col-config-row {
  display: flex; align-items: center;
  padding: 9px 4px;
  border-bottom: 1px solid #f0f0f0;
  gap: 10px;
}
.col-config-row:last-child { border-bottom: none; }
.col-seq {
  width: 22px; height: 22px; border-radius: 50%;
  background: #eef2fb; color: #4472C4;
  font-size: 11px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.col-name { flex: 1; font-size: 13px; color: #303133; }
</style>
