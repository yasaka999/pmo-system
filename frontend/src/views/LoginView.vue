<template>
  <div class="login-bg">
    <div class="login-card">
      <div class="login-header">
        <el-icon class="login-logo"><DataBoard /></el-icon>
        <h1>PMO项目管理系统</h1>
        <p>实施项目全生命周期管理</p>
      </div>
      <el-form :model="form" @submit.prevent="handleLogin" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" prefix-icon="User" placeholder="请输入用户名" size="large" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" prefix-icon="Lock" placeholder="请输入密码" size="large" show-password @keyup.enter="handleLogin"/>
        </el-form-item>
        <el-button type="primary" size="large" style="width:100%;margin-top:8px" :loading="loading" @click="handleLogin">
          登 录
        </el-button>
      </el-form>
      <p class="login-tip">默认账号：admin / admin123</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const loading = ref(false)
const form = ref({ username: '', password: '' })

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a2840 0%, #2E4057 50%, #4472C4 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-card {
  background: #fff;
  border-radius: 16px;
  padding: 48px 40px;
  width: 420px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.login-header { text-align: center; margin-bottom: 32px; }
.login-logo { font-size: 48px; color: #4472C4; }
.login-header h1 { font-size: 22px; font-weight: 700; color: #2E4057; margin: 12px 0 4px; }
.login-header p  { color: #888; font-size: 14px; }
.login-tip { text-align: center; color: #aaa; font-size: 12px; margin-top: 16px; }
</style>
