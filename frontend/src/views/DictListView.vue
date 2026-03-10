<template>
  <div class="dict-view">
    <div class="header">
      <h2>数据字典配置</h2>
      <el-button type="primary" @click="openDialog()">新增字典项</el-button>
    </div>

    <!-- 过滤器面板 -->
    <el-card shadow="never" class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="字典类别">
          <el-select v-model="filters.category" placeholder="全部类别" clearable @change="fetchData">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="tableData" border style="width: 100%; margin-top: 15px;" v-loading="loading">
      <el-table-column prop="category" label="类别 (Category)" width="180" />
      <el-table-column prop="code" label="字典编码 (Code)" width="180" />
      <el-table-column prop="label" label="显示名称 (Label)" width="200" />
      <el-table-column prop="color" label="显示颜色" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.color" :type="['success','warning','danger','info'].includes(row.color) ? row.color : ''" :color="row.color.startsWith('#') ? row.color : ''" effect="dark">
            {{ row.color }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="sort_order" label="排序" width="80" align="center" />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-switch v-model="row.is_active" @change="toggleStatus(row)" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right" align="center">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确定删除此字典项吗？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button type="danger" link size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 字典编辑弹窗 -->
    <el-dialog :title="dialog.isEdit ? '编辑字典项' : '新增字典项'" v-model="dialog.visible" width="500px">
      <el-form :model="dialog.form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="字典类别" prop="category">
          <el-input v-model="dialog.form.category" placeholder="如: project_phase" />
        </el-form-item>
        <el-form-item label="字典编码" prop="code">
          <el-input v-model="dialog.form.code" placeholder="如: phase_impl，须唯一" />
        </el-form-item>
        <el-form-item label="显示名称" prop="label">
          <el-input v-model="dialog.form.label" placeholder="页面上显示的中文名称" />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="dialog.form.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="显示样式" prop="color">
          <el-select v-model="dialog.form.color" placeholder="可选项" clearable allow-create filterable>
            <el-option label="主色 (primary)" value="primary" />
            <el-option label="成功 (success)" value="success" />
            <el-option label="警告 (warning)" value="warning" />
            <el-option label="危险/红色 (danger)" value="danger" />
            <el-option label="置灰 (info)" value="info" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="dialog.loading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { dictApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useDictStore } from '@/stores/dict'

const dictStore = useDictStore()
const loading = ref(false)
const rawData = ref([])
const filters = reactive({ category: '' })

// 提取所有唯一种类用于过滤下拉框
const categories = computed(() => {
  const set = new Set(rawData.value.map(item => item.category))
  return Array.from(set)
})

const tableData = computed(() => {
  let res = rawData.value
  if (filters.category) {
    res = res.filter(item => item.category === filters.category)
  }
  return res
})

async function fetchData() {
  loading.value = true
  try {
    rawData.value = await dictApi.list()
  } finally {
    loading.value = false
  }
}

async function toggleStatus(row) {
  try {
    await dictApi.update(row.id, { is_active: row.is_active })
    ElMessage.success('状态已更新')
    dictStore.fetchDicts() // 更新全局store
  } catch (e) {
    row.is_active = !row.is_active // 恢复
  }
}

async function handleDelete(id) {
  try {
    await dictApi.remove(id)
    ElMessage.success('删除成功')
    fetchData()
    dictStore.fetchDicts()
  } catch (e) { }
}

// ---- 下拉/表单相关 ----
const formRef = ref(null)
const dialog = reactive({
  visible: false,
  isEdit: false,
  loading: false,
  form: { category: '', code: '', label: '', sort_order: 0, color: '', is_active: true }
})

const rules = {
  category: [{ required: true, message: '请输入类别', trigger: 'blur' }],
  code: [{ required: true, message: '请输入唯一代码', trigger: 'blur' }],
  label: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
}

function openDialog(row) {
  dialog.isEdit = !!row
  if (row) {
    dialog.form = { ...row }
  } else {
    dialog.form = { category: filters.category || '', code: '', label: '', sort_order: 0, color: '', is_active: true }
  }
  dialog.visible = true
}

async function submitForm() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      dialog.loading = true
      try {
        if (dialog.isEdit) {
          await dictApi.update(dialog.form.id, dialog.form)
          ElMessage.success('修改成功')
        } else {
          await dictApi.create(dialog.form)
          ElMessage.success('创建成功')
        }
        dialog.visible = false
        fetchData()
        dictStore.fetchDicts() // 更新前端缓存
      } finally {
        dialog.loading = false
      }
    }
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
