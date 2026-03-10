<template>
  <div class="user-view">
    <div class="header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="openDialog()">新增用户</el-button>
    </div>

    <el-table :data="tableData" border style="width: 100%; margin-top: 15px;" v-loading="loading">
      <el-table-column prop="username" label="用户名 (账号)" width="150" />
      <el-table-column prop="full_name" label="姓名" width="150" />
      <el-table-column prop="role" label="角色" width="120">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : (row.role === 'pmo' ? 'warning' : '')">
            {{ row.role === 'admin' ? '系统管理员' : (row.role === 'pmo' ? 'PMO' : (row.role === 'member' ? '项目成员' : '只读用户')) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-switch v-model="row.is_active" @change="toggleStatus(row)" :disabled="row.id === currentUserId" />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">
          {{ new Date(row.created_at).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right" align="center">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="openDialog(row)">编辑/重置密码</el-button>
          <el-popconfirm v-if="row.id !== currentUserId" title="确定删除此用户吗？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button type="danger" link size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 用户编辑弹窗 -->
    <el-dialog :title="dialog.isEdit ? '编辑用户' : '新增用户'" v-model="dialog.visible" width="500px">
      <el-form :model="dialog.form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="登录账号" prop="username">
          <el-input v-model="dialog.form.username" :disabled="dialog.isEdit" placeholder="唯一英文字母/数字" />
        </el-form-item>
        <el-form-item label="密码" :prop="dialog.isEdit ? '' : 'password'">
          <el-input v-model="dialog.form.password" type="password" show-password :placeholder="dialog.isEdit ? '留空表示不修改' : '初始密码'" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="dialog.form.full_name" placeholder="用户真实姓名" />
        </el-form-item>
        <el-form-item label="系统角色" prop="role">
          <el-select v-model="dialog.form.role" placeholder="选择角色" style="width:100%">
            <el-option label="系统管理员 (admin)" value="admin" />
            <el-option label="PMO (pmo)" value="pmo" />
            <el-option label="项目成员 (member)" value="member" />
            <el-option label="只读用户 (viewer)" value="viewer" />
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="dialog.form.email" placeholder="可选" />
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
import { userApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

const loading = ref(false)
const tableData = ref([])

async function fetchData() {
  loading.value = true
  try {
    tableData.value = await userApi.list()
  } finally {
    loading.value = false
  }
}

async function toggleStatus(row) {
  try {
    await userApi.updateStatus(row.id, row.is_active)
    ElMessage.success('状态已更新')
  } catch (e) {
    row.is_active = !row.is_active // 恢复
  }
}

async function handleDelete(id) {
  try {
    await userApi.remove(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) {}
}

// ---- 表单相关 ----
const formRef = ref(null)
const dialog = reactive({
  visible: false,
  isEdit: false,
  loading: false,
  form: { username: '', password: '', full_name: '', role: 'member', email: '' }
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入初始密码', trigger: 'blur' }],
  full_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

function openDialog(row) {
  dialog.isEdit = !!row
  if (row) {
    dialog.form = { ...row, password: '' }
  } else {
    dialog.form = { username: '', password: '', full_name: '', role: 'member', email: '' }
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
          // 如果没有填新密码，就去掉 password 字段不修改
          const dataToUpdate = { ...dialog.form }
          if (!dataToUpdate.password) {
            delete dataToUpdate.password
          }
          await userApi.update(dialog.form.id, dataToUpdate)
          ElMessage.success('更新成功')
        } else {
          await userApi.create(dialog.form)
          ElMessage.success('创建成功')
        }
        dialog.visible = false
        fetchData()
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
