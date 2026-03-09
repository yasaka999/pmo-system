<template>
  <div class="config-section">
    <!-- 标题区 -->
    <div class="section-title-row">
      <div>
        <h3 class="section-title">{{ title }}</h3>
        <p class="section-desc">{{ desc }}</p>
      </div>
    </div>

    <!-- 标签展示区 -->
    <div class="tags-area">
      <div v-for="item in items" :key="item.id ?? item.code" class="tag-wrapper">
        <el-tag
          :type="item.color || ''"
          closable
          size="large"
          class="config-tag"
          @close="$emit('remove', item)"
        >
          {{ item.label }}
        </el-tag>
        <!-- 颜色选择点（仅 show-color 时显示） -->
        <div
          v-if="showColor"
          class="color-dot"
          :style="{ background: colorBg(item.color) }"
          :title="'颜色: ' + (item.color || '默认')"
          @click="openColorPicker(item)"
        />
      </div>

      <!-- 新增输入框 -->
      <div class="add-input-wrapper">
        <el-input
          v-model="inputVal"
          size="small"
          :placeholder="'输入新' + title + '后按回车'"
          class="add-input"
          @keyup.enter="submit"
          @blur="submit"
          clearable
        />
      </div>
    </div>
  </div>

  <!-- 颜色选择对话框 -->
  <el-dialog v-model="colorDlgVisible" :title="colorDlgTitle" width="340px" append-to-body>
    <div class="color-picker-grid">
      <div
        v-for="c in colorOptions"
        :key="c.value"
        :class="['color-chip', editingItem && editingItem.color === c.value ? 'active' : '']"
        :style="{ background: c.bg }"
        @click="setColor(c.value)"
      >{{ c.label }}</div>
    </div>
    <template #footer>
      <el-button size="small" @click="colorDlgVisible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  title: String,
  desc: String,
  items: Array,
  showColor: { type: Boolean, default: false },
})
const emit = defineEmits(['add', 'remove'])

const inputVal = ref('')
const colorDlgVisible = ref(false)
const editingItem = ref(null)

const colorDlgTitle = computed(() =>
  editingItem.value ? ('设置 ' + editingItem.value.label + ' 的显示颜色') : '设置颜色'
)

const colorOptions = [
  { label: '默认',   value: '',        bg: '#C0C4CC' },
  { label: '蓝色',   value: 'primary', bg: '#409EFF' },
  { label: '绿色',   value: 'success', bg: '#67C23A' },
  { label: '橙色',   value: 'warning', bg: '#E6A23C' },
  { label: '红色',   value: 'danger',  bg: '#F56C6C' },
  { label: '灰色',   value: 'info',    bg: '#909399' },
]

function colorBg(color) {
  const found = colorOptions.find(c => c.value === color)
  return found ? found.bg : '#C0C4CC'
}

function submit() {
  const val = inputVal.value.trim()
  if (val) {
    emit('add', val)
    inputVal.value = ''
  }
}

function openColorPicker(item) {
  editingItem.value = item
  colorDlgVisible.value = true
}

function setColor(val) {
  if (editingItem.value) {
    editingItem.value.color = val
  }
}
</script>

<style scoped>
.config-section {
  padding: 8px 0 16px;
}
.section-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 14px;
}
.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #2E4057;
  margin: 0 0 4px 0;
}
.section-desc {
  font-size: 12px;
  color: #999;
  margin: 0;
}
.tags-area {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}
.tag-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.config-tag {
  font-size: 13px;
  border-radius: 6px;
}
.color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1px solid #ddd;
  cursor: pointer;
  flex-shrink: 0;
  transition: transform 0.15s;
}
.color-dot:hover { transform: scale(1.4); }

.add-input-wrapper {
  display: inline-flex;
  align-items: center;
}
.add-input {
  width: 180px;
}
.add-input :deep(.el-input__wrapper) {
  border: 1.5px dashed #C0C4CC;
  box-shadow: none;
  border-radius: 6px;
  background: #FAFAFA;
}
.add-input :deep(.el-input__wrapper:hover) {
  border-color: #409EFF;
}

/* 颜色选择器 */
.color-picker-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  padding: 8px 0;
}
.color-chip {
  width: 66px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  border: 3px solid transparent;
  transition: 0.15s;
  user-select: none;
}
.color-chip.active {
  border-color: #2E4057;
  transform: scale(1.1);
}
.color-chip:hover { opacity: 0.85; }
</style>
