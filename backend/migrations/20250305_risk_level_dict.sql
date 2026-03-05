-- 风险等级字典化迁移脚本
-- 执行时间: 2026-03-05
-- 备份文件: pmo.db.backup.20250305_2149

-- 1. 添加风险等级字典
INSERT INTO sys_dicts (category, code, label, sort_order, color, is_active) VALUES 
  ('risk_level', 'rl_h', '高', 1, 'danger', 1),
  ('risk_level', 'rl_m', '中', 2, 'warning', 1),
  ('risk_level', 'rl_l', '低', 3, 'success', 1);

-- 2. 迁移风险等级数据：中文 -> 英文代码
UPDATE risks SET level = 'rl_h' WHERE level = '高';
UPDATE risks SET level = 'rl_m' WHERE level = '中';
UPDATE risks SET level = 'rl_l' WHERE level = '低';

-- 3. 验证迁移结果
-- SELECT DISTINCT level FROM risks;
