<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">风险台账</h2>
      <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon> 新建风险</el-button>
    </div>

    <!-- PC 表格 -->
    <div class="page-card hide-mobile">
      <el-table :data="risks" stripe border v-loading="loading" style="width:100%">
        <el-table-column prop="title" label="风险标题" min-width="200" />
        <el-table-column prop="probability" label="概率" width="80" align="center">
          <template #default="{ row }">
            {{ getDictLabel('risk_prob', row.probability) }}
          </template>
        </el-table-column>
        <el-table-column prop="impact" label="影响" width="80" align="center">
          <template #default="{ row }">
            {{ getDictLabel('risk_impact', row.impact) }}
          </template>
        </el-table-column>
        <el-table-column prop="level" label="风险等级" width="100" align="center">
          <template #default="{ row }">
            <span :class="`risk-${row.level}`" style="font-weight:600">{{ row.level || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="assignee" label="负责人" width="100" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="riskStatusType(row.status)" size="small">{{ getDictLabel('risk_status', row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="mitigation" label="应对措施" min-width="180" show-overflow-tooltip />
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
      <div v-if="risks.length === 0 && !loading" style="text-align:center;padding:40px;color:#aaa;">暂无数据</div>
      <div class="mobile-card-list">
        <div class="m-card" v-for="row in risks" :key="row.id">
          <div class="m-card-header">
            <div class="m-card-title">{{ row.title }}</div>
            <span :class="`risk-${row.level}`" style="font-weight:600;font-size:13px">{{ row.level || '-' }}</span>
          </div>
          <div class="m-card-body">
            <div class="m-field"><span class="m-field-label">状态</span>
              <el-tag :type="riskStatusType(row.status)" size="small">{{ getDictLabel('risk_status', row.status) }}</el-tag>
            </div>
            <div class="m-field"><span class="m-field-label">负责人</span><span class="m-field-value">{{ row.assignee || '-' }}</span></div>
            <div class="m-field"><span class="m-field-label">概率</span><span class="m-field-value">{{ getDictLabel('risk_prob', row.probability) }}</span></div>
            <div class="m-field"><span class="m-field-label">影响</span><span class="m-field-value">{{ getDictLabel('risk_impact', row.impact) }}</span></div>
            <div class="m-field" style="grid-column:1/-1">
              <span class="m-field-label">应对措施</span>
              <span class="m-field-value" style="white-space:pre-wrap">{{ row.mitigation || '-' }}</span>
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
    <el-dialog v-model="dlg" :title="editId ? '编辑风险' : '新建风险'" width="min(560px, 95vw)">
      <el-form :model="form" label-width="90px">
        <el-form-item label="风险标题"><el-input v-model="form.title" /></el-form-item>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="8">
            <el-form-item label="概率">
              <el-select v-model="form.probability" style="width:100%" @change="calcRiskLevel">
                <el-option v-for="s in probOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="8">
            <el-form-item label="影响">
              <el-select v-model="form.impact" style="width:100%" @change="calcRiskLevel">
                <el-option v-for="s in impactOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="8">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width:100%">
                <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="24">
            <el-form-item label="风险等级">
              <div style="display:flex;align-items:center;height:32px">
                <el-tag :type="riskLevelType(form.level)" size="large" effect="dark">{{ form.level || '-' }}</el-tag>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="负责人"><el-input v-model="form.assignee" /></el-form-item>
        <el-form-item label="风险描述"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="应对措施"><el-input v-model="form.mitigation" type="textarea" :rows="2" /></el-form-item>
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
import { riskApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useDictStore } from '@/stores/dict'

const dictStore = useDictStore()
const route = useRoute()
const pid = route.params.id
const risks = ref([])
const loading = ref(false)
const dlg = ref(false)
const editId = ref(null)

const probOptions = computed(() => dictStore.getOptions('risk_prob'))
const impactOptions = computed(() => dictStore.getOptions('risk_impact'))
const statusOptions = computed(() => dictStore.getOptions('risk_status'))

// 字典值转中文标签
function getDictLabel(category, value) {
  const item = dictStore.getDictItem(category, value)
  return item?.label || value
}

// 计算风险等级（根据概率和影响）
// 兼容中英文两种格式的数据
function calcRiskLevel() {
  // 支持英文代码和中文两种格式
  const probMap = { 
    'rp_h': 3, '高': 3,
    'rp_m': 2, '中': 2, 
    'rp_l': 1, '低': 1
  }
  const impactMap = { 
    'ri_h': 3, '高': 3,
    'ri_m': 2, '中': 2, 
    'ri_l': 1, '低': 1
  }
  
  const probVal = form.value.probability || ''
  const impactVal = form.value.impact || ''
  
  const probScore = probMap[probVal] || 0
  const impactScore = impactMap[impactVal] || 0
  const totalScore = probScore * impactScore
  
  // 风险矩阵：得分 >= 6 为高，>= 2 为中，否则为低
  if (totalScore >= 6) {
    form.value.level = '高'
  } else if (totalScore >= 2) {
    form.value.level = '中'
  } else {
    form.value.level = '低'
  }
}

const df = () => ({ title:'', probability:'rp_m', impact:'ri_m', level:'中', assignee:'', status:'rs_open', description:'', mitigation:'' })
const form = ref(df())

async function load() {
  loading.value = true
  try { risks.value = await riskApi.list(pid) } finally { loading.value = false }
}
function openDialog(row = null) {
  editId.value = row?.id || null
  form.value = row ? { ...row } : df()
  calcRiskLevel()  // 计算风险等级
  dlg.value = true
}
async function save() {
  if (!form.value.title) { ElMessage.warning('风险标题必填'); return }
  if (editId.value) await riskApi.update(editId.value, form.value)
  else await riskApi.create(pid, { ...form.value, project_id: Number(pid) })
  ElMessage.success('保存成功'); dlg.value = false; await load()
}
async function remove(id) {
  await riskApi.remove(id); ElMessage.success('已删除'); await load()
}
function riskStatusType(s) {
  const item = dictStore.getDictItem('risk_status', s)
  const c = item?.color
  return c || { 'rs_open': 'danger', 'rs_mitig': 'warning', 'rs_closed': 'success', '开放': 'danger', '已缓解': 'warning', '已关闭': 'success' }[s] || 'info'
}

function riskLevelType(level) {
  const map = { '高': 'danger', '中': 'warning', '低': 'success' }
  return map[level] || 'info'
}

onMounted(() => { dictStore.fetchDicts(); load() })
</script>

<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
</style>
