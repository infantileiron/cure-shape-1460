# 滩原材料 · 固化曲线形态归并

把完整等距模拟养护曲线，转成可追溯的 DTW 配对路径、complete-link 合并层级和人工命名版本。

滩原材料养护组是一个模拟的 11 人材料工作室。上游交付 `tanyuan_cure_20261112.json`，包含48件养护样各64个反应指数，固定2分钟采样。原先研究员在电子表格按终值分组：时移掩盖同形，尖峰拖动相似性判断，合并层级没有证据。本项目承接完整性检查到形态归并的一段；下游是研究员复核稿与负责人批准的 CSV，不是材料强度检测、质量合格或工艺控制系统。

## 一天的复核工作

1. 09:00 分析员导入模拟固化曲线，逐条检查64点与同一时间轴。
2. 09:05 打开48曲线总览，确认延迟上升、快慢升温和尖峰。
3. 09:10 选择原始量级或每曲线 zscore；锁定 Sakoe–Chiba 窗口和阈值。
4. 09:15 冻结任务，保存完整曲线与口径快照。
5. 09:20 提交 Redis worker，计算1128个独立配对、距离矩阵、完整47次归并和切树。
6. 09:25 点击矩阵单元，核对具体曲线的累计平方差、最优路径长度与完整索引。
7. 09:30 查看 complete-link 树及最大距离见证，为每簇人工命名并提交接受/待补充版本。
8. 09:40 负责人从版本清单明确选择当前最新的接受版本批准，冻结名称、版本与校验和的归档快照；旧名称和旧归档保留原版本。

## 启动

```sh
cp .env.example .env
docker compose config --quiet
docker compose up -d --build --wait --wait-timeout 180
# 可显式再跑，幂等且不覆盖用户编辑
docker compose exec backend python -m scripts.seed_demo
```

访问前端 `http://localhost:18232`，API文档 `http://localhost:19232/docs`，PostgreSQL `localhost:17732`。首次启动自动建立初始表并 seed；本地演示环境账号如下，密码统一为 `Curve2026!`。

| 角色 | 账号 | 主要页面和动作 |
|---|---|---|
| analyst | analyst@tanyuan.demo | 导入曲线、保存对齐口径、冻结任务、运行、人工命名与复核 |
| admin | admin@tanyuan.demo | 全部分析功能，批准最新接受复核版本归档 |
| viewer | viewer@tanyuan.demo | 读取全部结果与审计，下载已批准CSV，不能写入或批准 |

演示凭据与 JWT 默认密钥仅用于本地模拟环境。写接口由服务端 JWT 角色控制，隐藏按钮不是权限边界；所有写入与拒绝记录到审计表，错误中间件保留可恢复的错误信息。

## 计算口径

`backend/src/services/dtw.py::dtw(x, y, window)` 使用局部平方差，三方向递推求**最小累计代价**；仅允许 `|i-j| <= window`。同累计代价先取较短路径，再按对角、上、左确定唯一回溯。配对按曲线ID排序；显示距离为 `sqrt(累计代价 / 该最优路径长度)`，**不是最小平均代价路径，也不保证三角不等式**。保存完整最优路径、累计代价、长度、矩阵和输入校验和。

`backend/src/services/clustering.py::complete_link(ids, matrix, threshold)` 每次取簇间成员两两距离的最大值，同分按已排序成员ID字典序确定合并，内部节点ID与全部叶ID隔离。返回完整合并树、最大距离见证和包含等号的阈值切树；每个输出簇的成员两两最大距离不超过阈值。合并后距离不被重算成均值，也没有假定 DTW 归一距离满足度量公理。

数据集必须有2至64条曲线，各64个有限值，共用64个严格递增、固定间隔分钟时间点。重复时间、缺点、非等距、重复曲线ID和无穷值拒绝；不重采样、不填零。曲线ID是唯一英数短ID。`raw` 保留反应指数的量级；`zscore` 按每曲线总体标准差标准化，常量或近常量使任务明确失败，不生成伪零曲线。两个口径的距离/阈值单位不同，需要分别定义。

六实体为 CurveDataset、AlignmentPolicy、ShapeStudy、ShapeRun、ClusterReview、Report，贯穿表、schema、service、route、前端 API 与页面。研究任务冻结数据/口径；运行结果持久化到 PostgreSQL JSON。复核每次新增不可变版本，必须覆盖当前所有簇。保存时携带页面打开时的基线版本 `base_version`：服务端在事务内锁定运行行再取号，只有基线等于当前最新版本才写入 `version+1`；版本号连续且 `(run_id, version)` 唯一，旧页面重复保存返回 409 `review_version_conflict`（含基线/最新版本号）并保留用户填写内容，不会静默覆盖他人提交。Report 必须显式绑定 `review_id`，只允许批准所选的最新接受版本；所选版本已有更新复核或结论为待补充时拒绝。归档时冻结快照（名称、复核版本、校验和、簇成员与口径），后续新复核或重跑都不改变旧CSV中的名称、版本、校验和和簇归属；复核页标出本页基线版本、库中最新版本及冲突原因。

## 技术与目录

| 部分 | 技术 |
|---|---|
| 前端 | React18、TypeScript、Vite、SVG真结果图表 |
| API | Python3.11、FastAPI、SQLAlchemy、JWT |
| 后台 | Redis真实队列、独立Python worker、心跳健康检查 |
| 数据库 | PostgreSQL16 |
| 容器 | 恰好 frontend/backend/worker/db/redis 五服务，全部健康检查 |

`frontend/src` 按 api/stores/types/pages/components/hooks/router/utils/constants 分工，六领域页加登录，曲线图/口径条/簇清单跨页共享。`backend/src` 按 models/schemas/services/controllers/routes/middlewares/config/utils/constants 分工；`backend/scripts/seed_demo.py` 仅在自然键不存在时插入，连跑不覆盖编辑。`backend/migrations` 说明初始schema来源。测试、截图、日志和验收报告位于批根的 `test-artifacts/gb-2403`，源码中不混入测试产物。

环境变量在 `.env.example`：COMPOSE_PROJECT_NAME=cure-shape，FRONTEND_PORT=18232，BACKEND_PORT=19232，DB_PORT=17732，SEED_DEMO=true，JWT_SECRET。容器内DATABASE_URL/REDIS_URL由compose注入。数据库、Redis和worker产物使用独立命名卷；Nginx `/api/` 代理FastAPI并处理SPA回落。开发时前端 `npm ci && npm run dev`，API `uvicorn src.main:app --host 0.0.0.0`，worker `python -m src.worker`，并配置可连接的DATABASE_URL/REDIS_URL。

共享枚举 role、normalization、run_status、review_decision 分别定义在 `backend/src/constants/enums.py` 与 `frontend/src/constants/enums.ts`，同时受后端对应schema Literal和状态服务约束。

## 边界与清理

模拟反应指数不是强度单位；归并仅比较给定输入/窗口/归一口径，不自动去除尖峰，不判定材料合格或异常因果。阈值改变需新建口径与任务，避免覆盖既有结果。所有配对路径保留，演示规模限制64曲线；单worker未实现生产级分布式租约。初始建表不含生产迁移回滚；审计供本地演示，没有多租户隔离。

```sh
docker compose down -v --remove-orphans
```

License: MIT。数据均为固定seed生成的模拟养护样。
