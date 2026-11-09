# 对话问答回避检测与跨场景迁移分析 (QEvasion Clarity Classification & Cross-Scenario Transfer)

深圳大学《自然语言处理》课程实验 + 期末大作业配套代码。

基于 [QEvasion](https://huggingface.co/datasets/ailsntua/QEvasion) 数据集
（Thomas et al., 2024, *"I Never Said That": A dataset, taxonomy and baselines on
response clarity classification*, Findings of EMNLP 2024）完成回答清晰度三分类
（Clear Reply / Ambivalent / Clear Non-Reply），并将统一字段适配器迁移到
[QNLI](https://huggingface.co/datasets/nyu-mll/glue)（GLUE）数据集，比较零样本
直接复用与目标域再训练的差距，同时给出数据效率（10% / 30% / 100%标注数据）
与粗细粒度标签层级一致性两组扩展分析。

## 仓库结构

```
├── data/                    # 统一字段适配器输出（text_a, text_b, label）
├── src/
│   ├── prepare_data.py      # 下载并适配 QEvasion / QNLI 到统一 schema
│   ├── eda.py               # 标签分布、长度分布图 + 统计
│   ├── train_tfidf.py       # 多数类基线 + TF-IDF + Logistic Regression
│   ├── train_sbert.py       # 预训练句向量 (all-MiniLM-L6-v2) + LR
│   ├── train_bert.py        # BERT-base-uncased 句对微调
│   ├── transfer.py          # 零样本迁移 + QNLI 再训练 + 数据效率实验
│   └── analyze.py           # 混淆矩阵、模型对比图、误判样本、层级一致性
├── results/                 # 指标 json、预测文件、图表
└── requirements.txt
```

## 复现步骤

```bash
pip install -r requirements.txt
python src/prepare_data.py                      # 数据下载与适配
python src/eda.py                               # EDA 图表
python src/train_tfidf.py --task qev_coarse     # 基线（三分类，官方测试集）
python src/train_tfidf.py --task qev_fine       # 基线（9 类，90/10 划分）
python src/train_tfidf.py --task qnli           # 基线（迁移任务）
python src/train_sbert.py  --task qev_coarse    # 冻结句向量 + LR
python src/train_bert.py   --train data/qev_train.csv --test data/qev_test.csv \
    --num_labels 3 --names "Clear Reply|Ambivalent|Clear Non-Reply" \
    --run_name bert_qev_coarse --save_model
python src/train_bert.py   --train data/qev_train.csv --label_col fine \
    --num_labels 9 --names "Explicit|Dodging|Implicit|General|Deflection|Partial/half-answer|Declining to answer|Claims ignorance|Clarification" \
    --run_name bert_qev_fine --dev_split 0.1
python src/transfer.py     # 零样本迁移 + QNLI 10/30/100% 数据效率
python src/analyze.py      # 汇总图表与错误分析
```

默认超参数：`bert-base-uncased`，max_len=384（问题+回答 longest-first 截断），
epochs=4，batch=16，lr=2e-5，AdamW(wd=0.01)，warmup=10%，fp16，seed=42。
迁移运行（QNLI）使用 max_len=256、batch=32、epochs=3。

## 主要结果

**QEvasion 粗粒度三分类（官方测试集 n=308，seed=42）**

| 模型 | Accuracy | Macro-F1 |
|---|---|---|
| 多数类基线 | 0.669 | 0.267 |
| TF-IDF + LR | 0.545 | 0.416 |
| SBERT + LR（冻结） | 0.513 | 0.420 |
| **BERT 微调（最佳）** | **0.714** | **0.556** |

细粒度 9 类（训练集 90/10 划分）：BERT Macro-F1 0.307；
粗→细层级投影一致率 0.519，双模型一致率 0.354（详见 `results/hierarchy_consistency.json`）。

**迁移到 QNLI（统一评估集 n=3000）**

| 设置 | Accuracy | Macro-F1 |
|---|---|---|
| TF-IDF + LR（再训练） | 0.574 | 0.572 |
| SBERT + LR（再训练） | 0.730 | 0.730 |
| BERT 零样本直接复用（标签投影） | 0.491 | 0.329 |
| BERT 再训练 10%（2,000 条） | 0.755 | 0.755 |
| BERT 再训练 30%（6,000 条） | 0.819 | 0.819 |
| BERT 再训练 100%（20,000 条） | 0.855 | 0.855 |

结论：字段适配器与训练流水线可零成本复用，但决策边界必须由目标域数据重学；
10% 标注数据即可恢复大部分性能。

> 注：QEvasion 官方 train/test 划分存在 39 个重叠访谈 URL（涉及测试集 118 条，
> 38.3%），绝对数值可能被轻微高估，但不影响模型间的相对排序。
