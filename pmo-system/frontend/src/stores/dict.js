import { defineStore } from 'pinia'
import { dictApi } from '@/api'

export const useDictStore = defineStore('dict', {
    state: () => ({
        // 存储所有字典数据，格式 { category: [ { code, label, color, sort_order }, ... ] }
        dicts: {}
    }),
    actions: {
        async fetchDicts() {
            try {
                // 获取所有已启用的字典项
                const res = await dictApi.list()
                const grouped = {}
                res.forEach(item => {
                    if (!item.is_active) return
                    if (!grouped[item.category]) {
                        grouped[item.category] = []
                    }
                    grouped[item.category].push({
                        label: item.label,
                        value: item.code, // 前端习惯用 value
                        color: item.color,
                        sort_order: item.sort_order
                    })
                })
                // 对每组按 sort_order 排序
                for (let key in grouped) {
                    grouped[key].sort((a, b) => a.sort_order - b.sort_order)
                }
                this.dicts = grouped
            } catch (err) {
                console.error("加载字典失败", err)
            }
        },

        // 获取某个分类的下拉选项
        getOptions(category) {
            return this.dicts[category] || []
        },

        // 取特定值的对应字典对象（用于展示带有颜色的 Tag）
        getDictItem(category, value) {
            const options = this.getOptions(category)
            return options.find(o => o.value === value) || { label: value, value, color: '' }
        }
    }
})
