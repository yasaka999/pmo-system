-- 风险等级字典化迁移脚本
-- 执行时间: 2026-03-05
-- 备份文件: pmo.db.backup.20250305_2149

-- 1. 添加风险等级字典
INSERT INTO sys_dicts (category, code, label, sort_order, color, is_active) VALUES 
  ('risk_level', 'rl_h', '高', 1, 'danger', 1),
  ('risk_level', 'rl_m', '中', 2, 'warning', 1),
  ('risk_level', 'rl_l', '低', 3, 'success', 1);

-- 2. 转换概率：中文 -> 英文代码
UPDATE risks SET probability = 'rp_h' WHERE probability = '高';
UPDATE risks SET probability = 'rp_m' WHERE probability = '中';
UPDATE risks SET probability = 'rp_l' WHERE probability = '低';

-- 3. 转换影响：中文 -> 英文代码
UPDATE risks SET impact = 'ri_h' WHERE impact = '高';
UPDATE risks SET impact = 'ri_m' WHERE impact = '中';
UPDATE risks SET impact = 'ri_l' WHERE impact = '低';

-- 4. 根据风险矩阵重新计算风险等级
-- 得分 = 概率分 × 影响分 (高=3, 中=2, 低=1)
-- >=6: 高(rl_h), >=2: 中(rl_m), <2: 低(rl_l)

-- 高风险 (得分 >= 6)
UPDATE risks SET level = 'rl_h' WHERE 
  (probability = 'rp_h' AND impact IN ('ri_h', 'ri_m')) OR
  (probability = 'rp_m' AND impact = 'ri_h');

-- 低风险 (得分 < 2)
UPDATE risks SET level = 'rl_l' WHERE 
  probability = 'rp_l' AND impact = 'ri_l';

-- 其余为中风险
UPDATE risks SET level = 'rl_m' WHERE level NOT IN ('rl_h', 'rl_l') OR level IS NULL;

-- 5. 验证结果
-- SELECT id, title, probability, impact, level FROM risks ORDER BY id;
