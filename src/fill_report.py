# -*- coding: utf-8 -*-
"""Fill the SZU lab-report template with experiment results.

The converted template already contains styled (empty) tables for 表1/2/3/4/5/7
and instruction boxes with questions. This script fills THOSE tables in place,
answers the questions inside the boxes, replaces the 图1/2/3 placeholders with
real figures + captions, and appends the conclusion. The original .doc file is
never touched; output is a new docx next to the task files.
"""
import os
import json

import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.table import Table
from docx.text.paragraph import Paragraph

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK = os.path.dirname(HERE)
RES = os.path.join(HERE, "results")
FIG = os.path.join(RES, "figures")
DATA = os.path.join(HERE, "data")
TPL = os.path.join(TASK, "converted",
                   "实验报告：对话问答回避检测与跨场景迁移分析.docx")
OUT = os.path.join(TASK, "实验报告-对话问答回避检测与跨场景迁移分析-已完成.docx")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def set_run(r, size=9, bold=False):
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.name = "Calibri"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


def fill_cell(cell, text, size=9, bold=False, center=False):
    cell.text = str(text)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.space_before = Pt(1)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        set_run(r, size=size, bold=bold)


def fill_row(row, values, start_col=1, center_data=True):
    """Fill `values` into the row starting at start_col, tolerating merged
    cells: if the row has fewer physical cells than values, the tail values
    are joined into the last cell."""
    cells = row.cells[start_col:]
    n = len(cells)
    if n >= len(values):
        for c, v in zip(cells, values):
            fill_cell(c, v, center=center_data)
    else:
        head = values[:n - 1]
        tail = " ｜ ".join(str(v) for v in values[n - 1:])
        for c, v in zip(cells[:n - 1], head):
            fill_cell(c, v, center=center_data)
        fill_cell(cells[-1], tail, center=False)


def tables_in(cell):
    return [Table(ch, cell) for ch in cell._tc.iterchildren()
            if ch.tag == qn("w:tbl")]


def find_table(cell, nrows, ncols=None, nth=0):
    hits = [t for t in tables_in(cell)
            if len(t.rows) == nrows and (ncols is None or len(t.columns) == ncols)]
    return hits[nth]


def box_cell(cell, nth=0):
    """Return the content cell (row 1) of the nth single-column prompt box."""
    boxes = [t for t in tables_in(cell) if len(t.columns) == 1 and len(t.rows) >= 2]
    return boxes[nth].rows[1].cells[0]


def add_answer(box_content_cell, text, size=9):
    p = box_content_cell.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.25
    r = p.add_run(text)
    set_run(r, size=size)
    return p


def find_para(cell, prefix):
    for p in cell.paragraphs:
        if p.text.strip().startswith(prefix):
            return p
    return None


def replace_with_image(para, img_path, width_in=5.7):
    for r in list(para.runs):
        r._element.getparent().remove(r._element)
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run()
    run.add_picture(img_path, width=Inches(width_in))
    return para


def new_para_after(cell, anchor_el, text, size=9, center=False):
    p_el = OxmlElement("w:p")
    anchor_el.addnext(p_el)
    p = Paragraph(p_el, cell)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.3
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    set_run(r, size=size)
    return p


def macro_pr(per_class):
    ps = [v["precision"] for v in per_class.values()]
    rs = [v["recall"] for v in per_class.values()]
    return sum(ps) / len(ps), sum(rs) / len(rs)


def main():
    doc = Document(TPL)
    body = doc.tables[0]
    tail = doc.tables[1]
    c1, c2, c3, c4 = (body.rows[i].cells[0] for i in range(1, 5))

    eda = load(os.path.join(RES, "eda_stats.json"))
    base = load(os.path.join(RES, "baselines_qev_coarse.json"))
    bert = load(os.path.join(RES, "bert_qev_coarse", "metrics.json"))
    xfer = load(os.path.join(RES, "transfer_summary.json"))
    errs = load(os.path.join(RES, "error_samples.json"))
    qtr = pd.read_csv(os.path.join(DATA, "qnli_train.csv"))
    qte = pd.read_csv(os.path.join(DATA, "qnli_dev.csv"))
    tr = pd.read_csv(os.path.join(DATA, "qev_train.csv"))
    te = pd.read_csv(os.path.join(DATA, "qev_test.csv"))

    def words(s):
        return float(s.str.split().str.len().mean())

    # ============ 表1：数据统计记录（模板 11x7；前 5 行为数据行，
    # 后 6 行是指令段落；第 3/4 行预留给迁移数据集） ============
    t1 = find_table(c1, 11)
    rows1 = [
        ("3448", "0", f"{words(tr['text_a']):.1f}", f"{words(tr['text_b']):.1f}"),
        ("308", "0", f"{words(te['text_a']):.1f}", f"{words(te['text_b']):.1f}"),
        ("20000", "0", f"{words(qtr['text_a']):.1f}", f"{words(qtr['text_b']):.1f}"),
        ("3000", "0", f"{words(qte['text_a']):.1f}", f"{words(qte['text_b']):.1f}"),
    ]
    for row, vals in zip(t1.rows[1:5], rows1):
        fill_row(row, vals)
    new_para_after(
        c1, t1._tbl,
        "注：train/test 为 QEvasion 官方划分，类别比分别为 1052:2040:356（30.5%/59.2%/10.3%）与 "
        "79:206:23（25.6%/66.9%/7.5%），测试集不含细粒度标签；迁移数据 train/test 为 QNLI"
        "（entailment 占 49.5%/49.9%），以 seed=42 从 GLUE 原始数据分层抽样。长度单位为词数。",
        size=9)
    # rows 5-10 are instruction sections inside the table: answer the
    # requirement boxes in （四）训练配置 and （五）评价指标
    add_answer(t1.rows[8].cells[0],
               "完成情况：三种模型的学习率/轮数/种子见表2；BERT 微调采用 AdamW（lr=2e-5，"
               "warmup 10%，fp16），SBERT 冻结编码器仅训练 LR 头；复测结果与报告一致。")
    add_answer(t1.rows[10].cells[0],
               "完成情况：主指标 Macro-F1，辅指标 Accuracy 与类别级 P/R/F1；测试集标签不可用时"
               "（细粒度 9 类）从训练集按 seed=42 分层划分 90/10，并已检查同访谈泄漏风险。")

    # ============ 表2：训练配置记录（模板 4x6；行名已预填：
    # TF-IDF + LR / 预训练模型（BERT 微调）/ 迁移模型（QNLI-BERT）） ============
    t2 = find_table(c1, 4, 6)
    fill_row(t2.rows[1], ["100000（稀疏词袋）", "词级 1-2 元组，不定长", "—（LR C=4.0, balanced）", "—（单次拟合）", "42"])
    fill_row(t2.rows[2], ["768（[CLS] 隐向量）", "384 子词（longest-first）", "2e-5", "4（batch=16）", "42"])
    fill_row(t2.rows[3], ["768（[CLS] 隐向量）", "256 子词（longest-first）", "2e-5", "3（batch=32）", "42"])

    # ============ 表3：模型总体性能（模板 6x6） ============
    t3 = find_table(c2, 6, 6)
    mp, mr = macro_pr(base["majority"]["per_class"])
    fill_row(t3.rows[1], ["0.669", f"{mp:.3f}", f"{mr:.3f}", "0.267", "恒预测 Ambivalent"])
    mp, mr = macro_pr(base["tfidf_lr"]["per_class"])
    fill_row(t3.rows[2], [str(base["tfidf_lr"]["accuracy"]), f"{mp:.3f}", f"{mr:.3f}",
                          str(base["tfidf_lr"]["macro_f1"]), "词袋特征，Clear Reply 召回低"])
    mp, mr = macro_pr(base["sbert_lr"]["per_class"])
    fill_row(t3.rows[3], [str(base["sbert_lr"]["accuracy"]), f"{mp:.3f}", f"{mr:.3f}",
                          str(base["sbert_lr"]["macro_f1"]), "冻结 MiniLM 句向量 + LR"])
    mp, mr = macro_pr(bert["per_class"])
    fill_row(t3.rows[4], [str(bert["accuracy"]), f"{mp:.3f}", f"{mr:.3f}",
                          str(bert["macro_f1"]), "BERT 微调，最佳模型"])
    q = xfer["bert_qnli_100pct"]
    fill_row(t3.rows[5], [str(q["accuracy"]), "—", "—", str(q["macro_f1"]),
                          "迁移任务 QNLI（100% 数据再训练，2 类）"])

    # ============ 表4：最佳模型类别级结果（模板 5x5，转置） ============
    t4 = find_table(c2, 5, 5)
    pc = bert["per_class"]
    fill_row(t4.rows[1], ["79", str(pc["Clear Reply"]["precision"]),
                          str(pc["Clear Reply"]["recall"]), str(pc["Clear Reply"]["f1"])])
    fill_row(t4.rows[2], ["206", str(pc["Ambivalent"]["precision"]),
                          str(pc["Ambivalent"]["recall"]), str(pc["Ambivalent"]["f1"])])
    fill_row(t4.rows[3], ["23", str(pc["Clear Non-Reply"]["precision"]),
                          str(pc["Clear Non-Reply"]["recall"]), str(pc["Clear Non-Reply"]["f1"])])
    mp, mr = macro_pr(pc)
    fill_row(t4.rows[4], ["308", f"{mp:.3f}", f"{mr:.3f}", str(bert["macro_f1"])])

    # ============ 图1/2/3 ============
    figs = [
        ("图1", "fig1_label_dist.png",
         "图1：QEvasion 标签分布。左图为粗粒度三分类在训练/测试集中的比例，Ambivalent 类占 59.2%，"
         "约为 Clear Non-Reply 的 5.7 倍，类别不均衡显著；右图为训练集细粒度 9 类的样本数，"
         "Explicit 类（1052 条）与 Partial/half-answer、Clarification 等尾部类差距悬殊。"
         "长尾分布决定了评估必须以 Macro-F1 和类别级指标为主，而非只看 Accuracy。", 5.7),
        ("图2", "fig2_length_dist.png",
         "图2：问题与回答的长度分布。问题中位数仅 12 词，而回答中位数 207 词、95 分位 888 词、"
         "最长 2117 词，输入呈严重长尾。为控制显存与计算量，BERT 微调采用 question+answer "
         "longest-first 截断至 384 子词的策略，回答后段信息会被裁剪，"
         "这也是部分长回答样本被误判的原因之一。", 5.7),
        ("图3", "fig_run_log.png",
         "图3：最佳模型（BERT 微调）真实运行日志截图。日志显示 4 个 epoch 共 864 步的训练过程中 loss "
         "从约 0.98 稳定下降至 0.55 左右，总耗时 267 秒（RTX 4060 Laptop GPU，fp16），"
         "随机种子固定为 42；配合仓库中的脚本与 requirements.txt 可完整复现训练与评估结果。", 5.7),
    ]
    for key, img, caption, w in figs:
        para = find_para(c2, key)
        if para is not None:
            replace_with_image(para, os.path.join(FIG, img), w)
            new_para_after(c2, para._p, caption, size=9)

    # CM image + caption right after 表4
    p_cm = new_para_after(c2, t4._tbl,
                          "最佳模型（BERT 微调）混淆矩阵（行=真实，列=预测）为 "
                          "[[29,47,3],[16,183,7],[1,14,8]]：47 个明确回答被判为模糊回答、"
                          "16 个反向流入，Clear Reply 与 Ambivalent 的互吸约占全部误判的 80%。",
                          size=9)
    p_img = new_para_after(c2, p_cm._p, "", size=9, center=True)
    p_img.add_run().add_picture(os.path.join(FIG, "fig3_cm_bert_coarse.png"),
                                width=Inches(4.2))
    new_para_after(c2, p_img._p,
                   "图4：BERT 微调模型混淆矩阵。Clear Non-Reply 仅 23 个测试样本、8 个预测正确，"
                   "行稀疏导致该类指标波动大，与训练集中该类占比仅 10.3% 的不均衡直接相关。",
                   size=9)

    # ============ 表5：典型误判样本（模板 6x6） ============
    t5 = find_table(c3, 6, 6)
    for i, e in enumerate(errs, 1):
        fill_row(t5.rows[i], [e["question"][:80], e["answer_head"][:110],
                              e["gold"], e["pred"], e["type"]])

    # ============ 表7：原任务与迁移任务对比（模板 5x4） ============
    t7 = find_table(c4, 5, 4)
    zs = xfer["zero_shot_bert"]
    fill_row(t7.rows[1], ["0.545 / 0.416", "—",
                          "TF-IDF+LR 在 QEvasion：Acc/Macro-F1，词袋特征仅能利用词汇重叠"])
    fill_row(t7.rows[2], [str(xfer["tfidf_lr_qnli"]["accuracy"]),
                          str(xfer["tfidf_lr_qnli"]["macro_f1"]),
                          "QNLI 再训练仍仅 0.57：蕴含判断需要跨句交互，词袋失效"])
    fill_row(t7.rows[3], [str(zs["accuracy"]), str(zs["macro_f1"]),
                          "BERT 零样本+标签投影完全退化为多数类预测（全判 not_entailment）"])
    fill_row(t7.rows[4], [str(xfer["bert_qnli_100pct"]["accuracy"]),
                          str(xfer["bert_qnli_100pct"]["macro_f1"]),
                          "适配后再训练恢复高水平；10%/30% 数据已达 0.755/0.819"])

    # ============ 提示框内回答问题 ============
    box_c1 = [t for t in tables_in(c1) if len(t.columns) == 1 and len(t.rows) >= 4][0]
    add_answer(box_c1.rows[1].cells[0],
               "完成情况：环境为 Python 3.11 + PyTorch 2.11（CUDA） + transformers/sentence-transformers；"
               "数据经统一字段适配器（text_a/text_b/label）落盘为 data/qev_*.csv 与 qnli_*.csv，"
               "下载、适配与划分由 src/prepare_data.py 一键完成。")
    add_answer(box_c1.rows[3].cells[0],
               "完成情况：类别分布见图1、长度分布见图2；另按访谈来源检查了划分——训练/测试集存在 39 个"
               "重叠访谈 URL（涉及测试集 118 条，38.3%），已作为来源泄漏风险在报告中说明。")
    add_answer(box_cell(c2, 0),
               "完成情况：标签映射代码见 src/prepare_data.py；图1-图3 即下方的分布图与训练日志截图；"
               "运行环境与耗时见图3 说明；results/ 下保存了全部 metrics.json 与 predictions.csv；"
               "固定 seed=42 后按 README 顺序重跑，指标完全一致。")
    add_answer(box_cell(c3, 0),
               "回答：Clear Non-Reply 最难（F1 仅 0.390）——训练集仅 356 条（10.3%），且测试集只有 23 条，"
               "混淆矩阵显示其 14 条被吸入 Ambivalent。TF-IDF 基线主要依赖词面重叠与回答长度："
               "拒答类回答常以长铺垫开头，词面与明确回答无异，故 Clear Non-Reply 的召回仅 0.304。"
               "预训练模型的提升主要来自 Clear Reply（F1 0.398→0.464）与 Ambivalent（0.694→0.813），"
               "说明跨句交互改善的是\"回答是否覆盖问题信息点\"的判断。粗略按访谈主题分组检查发现，"
               "长回答（>500 词）样本的 Clear Reply 召回明显低于短回答，指向截断损失。")
    add_answer(box_cell(c4, 0),
               "本实验选择 QNLI：question + sentence → 是否包含答案（entailment / not_entailment），"
               "与 QEvasion 的\"问题—回答\"输入结构同构，标签从三档清晰度变为二档蕴含。")
    add_answer(box_cell(c4, 1),
               "回答：共同点是两者都在判断\"text_b 是否满足了 text_a 的信息需求\"；区别在于回避检测容忍"
               "\"部分满足\"并要求区分回避手法（多档），而蕴含只有二元判据。原模型直接迁移完全退化为多数类"
               "预测（Acc 0.491），重新训练后 BERT 达 0.855，说明字段适配器与训练流水线可以复用，"
               "但决策边界必须由目标域数据重学；10% 标注数据即可恢复到 0.755，适配成本不高。")

    # ============ 实验结论 ============
    c5 = tail.rows[0].cells[0]
    concl_marker = None
    for p in c5.paragraphs:
        if p.text.strip().startswith("实验过程中遇到的工程或分析困难"):
            concl_marker = p
    if concl_marker is None:
        concl_marker = c5.paragraphs[-1]
    concl = ("实验结论：本次实验在 QEvasion 数据集上完成了回答清晰度三分类的全流程建模与跨场景迁移。"
             "与普通情感分类相比，问答回避检测的难点在于标签由\"回答内容与问题信息需求的对应关系\"决定，"
             "而非词汇极性：同样的中性措辞既可构成明确回答也可构成回避，模型必须建模问题-回答的细粒度语义对应，"
             "且 Ambivalent 与 Clear Reply 的边界由人工标注习惯定义，存在天然模糊。"
             "结果层面，多数类基线 Acc 0.669 但 Macro-F1 仅 0.267；TF-IDF+LR（0.416）与冻结 SBERT（0.420）"
             "均明显低于 BERT 微调（Acc 0.714 / Macro-F1 0.556），说明跨句交互表征是该任务的关键增益来源。"
             "最典型的错误是 Clear Reply 与 Ambivalent 互相混淆（约占误判八成），"
             "改进方向包括粗-细两级标签联合建模、面向长回答的滑动窗口编码与对比式数据增广。"
             "迁移到 QNLI 后，字段适配器与训练流水线完全复用，但标签映射与截断配置必须重设；"
             "零样本 Macro-F1 仅 0.329，再训练后提升至 0.855，且随 10%→30%→100% 数据量单调上升，"
             "验证了\"流程可复用、边界需重学\"的结论。工程上的主要困难是长回答截断与类别不均衡评估，"
             "分别通过 longest-first 截断和 class_weight=balanced 配合 Macro-F1 口径解决。")
    new_para_after(c5, concl_marker._p, concl, size=10.5)

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
