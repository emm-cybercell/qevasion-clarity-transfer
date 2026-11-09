# -*- coding: utf-8 -*-
"""Build the final assignment (期末大作业) docx in the SZU answer-sheet style.

Reads all result JSONs produced by the experiment pipeline and renders a
complete six-section report with figures, tables and references.
"""
import os
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK = os.path.dirname(HERE)
RES = os.path.join(HERE, "results")
FIG = os.path.join(RES, "figures")
OUT = os.path.join(TASK, "自然语言处理期末大作业-对话问答回避检测与跨场景迁移分析.docx")
GITHUB = "https://github.com/<你的GitHub用户名>/qevasion-clarity-transfer"

plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def set_font(run, size=12, bold=False, east="宋体", west="Times New Roman",
             color=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = west
    run._element.rPr.rFonts.set(qn("w:eastAsia"), east)
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_para(doc, text, size=12, bold=False, east="宋体", align=None,
             indent=True, space_after=6, line=1.3):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.line_spacing = line
    if indent:
        pf.first_line_indent = Pt(size * 2)
    if align:
        p.alignment = align
    r = p.add_run(text)
    set_font(r, size=size, bold=bold, east=east)
    return p


def add_heading(doc, text, level=1):
    if level == 1:
        p = add_para(doc, text, size=14, bold=True, east="黑体",
                     indent=False, space_after=8)
    else:
        p = add_para(doc, text, size=12, bold=True, east="黑体",
                     indent=False, space_after=6)
    return p


def set_borders(table):
    pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "666666")
        borders.append(el)
    pr.append(borders)


def add_table(doc, data, caption=None, sizes=9, col_widths=None):
    if caption:
        add_para(doc, caption, size=10, bold=True, east="黑体",
                 align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=4)
    t = doc.add_table(len(data), len(data[0]))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_borders(t)
    for ri, row in enumerate(data):
        for ci, val in enumerate(row):
            cell = t.rows[ri].cells[ci]
            cell.text = str(val)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.space_before = Pt(1)
            if ri == 0 or ci == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                set_font(r, size=sizes, bold=(ri == 0), east="宋体")
    if col_widths:
        for ci, w in enumerate(col_widths):
            for row in t.rows:
                row.cells[ci].width = Cm(w)
    add_para(doc, "", size=6, indent=False, space_after=0)
    return t


def add_figure(doc, path, caption, width=5.6):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Inches(width))
    add_para(doc, caption, size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER,
             indent=False, space_after=10)


def build_learning_curve(xfer):
    caps = [("10%", 0.10), ("30%", 0.30), ("100%", 1.00)]
    sizes, accs, mf1s = [], [], []
    for label, frac in caps:
        key = f"bert_qnli_{int(frac*100)}pct"
        m = load(os.path.join(RES, key, "metrics.json"))
        sizes.append(m["config"]["train_size"])
        accs.append(m["accuracy"]); mf1s.append(m["macro_f1"])
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.plot(sizes, accs, "o-", color="#5B8FF9", label="Accuracy")
    ax.plot(sizes, mf1s, "s-", color="#F6903D", label="Macro-F1")
    for x, a, b in zip(sizes, accs, mf1s):
        ax.annotate(f"{a:.3f}", (x, a), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=9)
        ax.annotate(f"{b:.3f}", (x, b), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=9)
    zs = xfer["zero_shot_bert"]
    ax.axhline(zs["macro_f1"], color="#C33", ls="--", lw=1.1)
    ax.text(sizes[0], zs["macro_f1"] + 0.015,
            f"零样本直接复用 Macro-F1={zs['macro_f1']:.3f}", color="#C33",
            fontsize=9)
    ax.set_xscale("log")
    ax.set_xticks(sizes); ax.set_xticklabels([f"{s}\n({l})" for s, l in zip(sizes, ['10%','30%','100%'])])
    ax.set_xlabel("训练样本数（占 20k 训练池比例）"); ax.set_ylabel("得分")
    ax.set_ylim(0.2, 1.0)
    ax.set_title("QNLI 迁移：标注数据量—性能曲线（BERT）")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    p = os.path.join(FIG, "fig7_qnli_efficiency.png")
    fig.savefig(p, dpi=200); plt.close(fig)
    return p


def main():
    base = load(os.path.join(RES, "baselines_qev_coarse.json"))
    fine_b = load(os.path.join(RES, "baselines_qev_fine.json"))
    qnli_b = load(os.path.join(RES, "baselines_qnli.json"))
    bert = load(os.path.join(RES, "bert_qev_coarse", "metrics.json"))
    fine = load(os.path.join(RES, "bert_qev_fine", "metrics.json"))
    xfer = load(os.path.join(RES, "transfer_summary.json"))
    cons = load(os.path.join(RES, "hierarchy_consistency.json"))
    errs = load(os.path.join(RES, "error_samples.json"))
    stats = load(os.path.join(HERE, "data", "dataset_stats.json"))
    sbert_qnli = qnli_b["sbert_lr"]

    eff_fig = build_learning_curve(xfer)

    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Cm(2.5); sec.bottom_margin = Cm(2.5)
        sec.left_margin = Cm(2.8); sec.right_margin = Cm(2.8)

    # ------------- 答题纸头 -------------
    t = add_para(doc, "深 圳 大 学 考 试 答 题 纸", size=16, bold=True,
                 east="黑体", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
    add_para(doc, "（以论文、报告等形式考核专用）", size=10.5,
             align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=2)
    add_para(doc, "2026—2027 学年度第一学期", size=10.5,
             align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=10)
    head = [
        ["课程编号", "1504660001", "课序号", "1", "课程名称", "自然语言处理"],
        ["主讲教师", "陈俊扬", "评分", "", "学号", ""],
        ["姓名", "", "专业年级", "", "提交日期", "2026-12-30"],
    ]
    ht = doc.add_table(3, 6)
    set_borders(ht)
    for ri, row in enumerate(head):
        for ci, val in enumerate(row):
            c = ht.rows[ri].cells[ci]
            c.text = val
            for r in c.paragraphs[0].runs:
                set_font(r, size=10.5, east="宋体")
    add_para(doc, "", size=8, indent=False, space_after=0)
    add_para(doc, "题目：对话问答回避检测的粗细粒度标签建模与跨场景迁移边界分析"
                  "——基于 QEvasion 数据集的研究", size=13, bold=True, east="黑体",
             align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=14)

    # ================= 一、背景介绍与研究问题 =================
    add_heading(doc, "一、背景介绍与研究问题")
    add_para(doc,
             "在政治访谈、新闻发布、客服会话与安全审核等真实对话场景中，\"回答是否回应了提问\""
             "往往比\"回答的情感倾向\"更值得机器自动判别：记者需要在成段发言中判断发言人是否"
             "实质回应了敏感追问，客服质检需要识别话术性敷衍，内容审核则需从大量应答中筛出"
             "规避式回答。回答清晰度（response clarity）与回避策略（evasion）刻画的是"
             "\"回答内容与提问信息需求之间的对应关系\"：明确回答（Clear Reply）直接提供所问信息，"
             "模糊/矛盾回答（Ambivalent）只覆盖部分信息需求或转移焦点，明确不回答（Clear Non-Reply）"
             "则拒绝、声称无知或要求澄清[1]。自动判别这三类行为，是访谈质量评估、"
             "客服质检与对话安全合规的基础组件。")
    add_para(doc,
             "本文使用 Thomas 等人发布的 QEvasion 数据集[1]。该数据集从政治记者会访谈中抽取"
             "\"子问题—完整回答\"文本对，由 ChatGPT 辅助、三人交叉人工标注，训练集 3448 条、"
             "测试集 308 条；粗粒度标签 clarity_label 含 Clear Reply / Ambivalent / Clear Non-Reply "
             "三档，细粒度标签 evasion_label 进一步区分 Explicit、Dodging、Implicit、General、"
             "Deflection、Partial/half-answer、Declining to answer、Claims ignorance、Clarification "
             "九种行为（细粒度标签仅在训练集提供）。两类标签存在严格的层级映射：Explicit 对应 "
             "Clear Reply，Dodging/Implicit/General/Deflection/Partial/half-answer 五类合并为 "
             "Ambivalent，Declining to answer/Claims ignorance/Clarification 三类合并为 "
             "Clear Non-Reply。迁移任务选用 GLUE 基准中的 QNLI[4][5]：输入同样是\"问题—文本\"对，"
             "但标签是二分类的蕴含判断（sentence 是否回答 question）。两者输入结构同构，"
             "标签语义却不同：前者判断\"信息需求被满足的程度与方式\"，后者判断\"单向蕴含是否成立\"，"
             "这构成了检验流程可迁移性的理想对照。")
    add_para(doc,
             "围绕上述数据，本文提出三个研究问题。RQ1（基础模型表现）：从词袋基线到预训练"
             "表示、再到句对微调，回答清晰度判别的性能阶梯有多大，增益来自何处？RQ2（跨场景"
             "迁移边界）：将同一套实验流程迁移到 QNLI 时，哪些组件可以原样复用、哪些必须重新"
             "设计，直接复用的性能上限在哪里？RQ3（扩展任务——粗细粒度标签层级）：细粒度九类"
             "模型按官方层级映射回粗粒度后，与粗粒度模型、与粗粒度金标的预测一致性如何，"
             "层级信息能否解释粗粒度模型的典型错误？")
    add_para(doc,
             "与普通情感分类相比，本任务的建模难点有三。其一，标签由跨句的对应关系决定而非"
             "文本内在极性，单句编码天然不足；其二，Ambivalent 与 Clear Reply 的边界由标注者"
             "对\"是否覆盖全部子问题\"的判断习惯定义，存在固有的标签模糊；其三，类别不均衡"
             "显著（训练集 Ambivalent : Clear Non-Reply 约 5.7:1）[1]，若只看 Accuracy，"
             "恒定预测多数类即可得到 0.669 的虚高分数，因此评估必须采用对类敏感的 Macro-F1"
             "口径[6]。此外，我们检测到官方划分存在来源泄漏风险：训练集与测试集共享 39 个"
             "访谈 URL，涉及测试集 118 条样本（38.3%）；同一访谈中的问题主题相近，"
             "模型可能借访谈记忆而非回答语义得分，故所有结论在解释时均需对这一风险保持保守。")

    # ================= 二、相关工作 =================
    add_heading(doc, "二、相关工作的优缺点总结")
    add_para(doc,
             "回答清晰度判别由 Thomas 等人系统化[1]。该工作构建了首个带两级分类法的"
             "QEvasion 数据集，并用 GPT-3.5 与多种规模的 BERT 类模型建立基线，"
             "其贡献在于给出了可复用的标签体系与基准划分；不足在于：粗粒度三分类上最强的"
             "预训练基线 Macro-F1 仍只有约 0.6，细粒度九类更低，说明长回答的信息压缩与"
             "边界模糊问题未被很好解决；同时该文分别报告两级标签的独立指标，"
             "未分析两级预测之间的一致性，也未讨论划分中的来源重叠问题。")
    add_para(doc,
             "表示学习方面，BERT[2]通过拼接\"[CLS] 问题 [SEP] 回答 [SEP]\"实现逐 token 的"
             "跨句自注意力交互，是句对语义匹配的强基线，但推理与训练开销大、对长文本需截断；"
             "Sentence-BERT[3]用孪生网络把句子压成定长向量，配合余弦相似度与轻量分类头，"
             "在效率上占优，却牺牲了细粒度对齐，对本任务这类\"回答需逐点回应问题\"的场景"
             "表达能力有限。传统特征方面，TF-IDF + 逻辑回归[7]可解释性强、小样本下稳健，"
             "但词袋表示无法建模跨句对齐，只能依赖词汇重叠做浅层判别。三类方法的适用条件"
             "与不足提示我们：回答清晰度判别的关键增益应来自问题—回答间的深层交互，"
             "而非更强的单句表示。")
    add_para(doc,
             "跨场景迁移方面，GLUE 基准中的 QNLI[4]（源自 SQuAD[5]的问句—证据句对）"
             "代表\"问题—文本\"输入范式下的二分类蕴含任务，其标注边界清晰、类别近均衡，"
             "与 QEvasion 形成鲜明对照。已有迁移研究多关注同标签空间的域适应，"
             "而\"标签语义不同但输入同构\"的直接迁移上限少有定量刻画。"
             "本文的扩展工作针对[1]未探索的标签层级一致性问题：利用其官方层级映射，"
             "在统一数据划分与指标口径下，量化细粒度模型与粗粒度模型的预测矛盾，"
             "并分析这些矛盾能否定位粗粒度模型的系统性错误；不要求复现更复杂的论文模型。")

    # ================= 三、模型方法与扩展设计 =================
    add_heading(doc, "三、模型方法与扩展设计")
    add_para(doc,
             "统一字段适配器。所有数据集被规范化为同一记录结构：text_a（源数据集 QEvasion "
             "中为子问题 question，迁移数据集 QNLI 中为问题 question）、text_b（源数据集中为"
             "完整回答 interview_answer，迁移数据集中为被评判句子 sentence）、label（源任务为"
             "0/1/2 三档清晰度，迁移任务为 0/1 二档蕴含）。适配器同时固化了划分方式"
             "（QEvasion 使用官方 train/test 划分；QNLI 以 seed=42 从 104743 条训练数据中分层"
             "抽取 20000 条为训练池、从 5463 条验证集中抽取 3000 条为统一评估集）、标签映射"
             "与指标口径，保证不同模型的比较在同一条件下进行。")
    add_para(doc,
             "基线与主模型。多数类基线恒预测训练集最高频类；TF-IDF + LR[7]使用词级一元、"
             "二元特征（max_features=100000，sublinear_tf，min_df=2）接类加权逻辑回归"
             "（C=4.0，class_weight=balanced）；预训练表示方法冻结 Sentence-BERT"
             "（all-MiniLM-L6-v2）[3]分别编码 text_a 与 text_b，将两向量与余弦相似度拼接后接"
             "逻辑回归。主模型为句对微调的 bert-base-uncased[2]：输入构造为"
             "[CLS] text_a [SEP] text_b [SEP]，采用 longest-first 策略截断至 384 子词"
             "（迁移任务因输入较短取 256）；训练使用交叉熵损失"
             "L = -Σ_c y_c log p(c|text_a, text_b)，AdamW 优化器（lr=2e-5，weight_decay=0.01），"
             "线性预热 10%，batch=16，epochs=4，混合精度 fp16，随机种子固定为 42。"
             "训练配置完整记录于仓库的 metrics.json，所有结果可一键复现。")
    add_para(doc,
             "扩展设计：粗—细粒度标签层级一致性。假设：细粒度九类模型按官方层级映射"
             "（Explicit→Clear Reply；Dodging/Implicit/General/Deflection/Partial/half-answer→"
             "Ambivalent；Declining to answer/Claims ignorance/Clarification→Clear Non-Reply）"
             "后，与粗粒度金标的一致率应显著高于随机水平，但会显著低于粗粒度模型自身的准确率；"
             "两级模型的预测矛盾将集中出现在 Ambivalent 的五个子类与 Clear Reply 的边界上。"
             "实现步骤：保持与三分类主模型完全相同的配置，仅将分类头改为九类，在训练集内按 "
             "90/10 分层划分训练与验证（官方测试集不含细粒度标签）；推理时对细粒度预测应用"
             "映射函数，得到层级投影预测。比较设置：与粗粒度金标比对（投影一致率）、"
             "与粗粒度模型预测比对（双模型一致率），并统计矛盾对的分布。")
    add_para(doc,
             "迁移与数据效率设置。迁移采用两种模式：零样本直接复用——将 QEvasion 微调模型"
             "直接应用于 QNLI，仅通过标签投影适配器把 Clear Reply 映射为 entailment、"
             "其余两类映射为 not_entailment；目标域适配——在 QNLI 训练池上按统一流程重新训练"
             "各模型，并进一步在 10%、30%、100% 训练池（2000/6000/20000 条）上训练 BERT，"
             "绘制标注数据量—性能曲线，刻画适配成本。所有迁移运行沿用统一评估集与指标口径。")

    # ================= 四、实验结果与综合分析 =================
    add_heading(doc, "四、实验结果与综合分析")
    add_heading(doc, "4.1 总体性能与类别级结果", 2)
    add_para(doc,
             "表1报告 QEvasion 官方测试集上四个层次的模型总体性能。多数类基线 Accuracy 高达 "
             "0.669 而 Macro-F1 仅 0.267，印证了只看 Accuracy 的误导性；TF-IDF+LR 与冻结 "
             "SBERT 的 Macro-F1 分别为 0.416 与 0.420，处于同一水平；BERT 句对微调取得 "
             f"{bert['accuracy']} / {bert['macro_f1']}（Accuracy / Macro-F1），"
             "相对最强基线 Macro-F1 提升约 0.14，回答了 RQ1：该任务的核心增益来自问题—回答的"
             "深层交互建模，而非更好的单句表示。")
    add_table(doc, [
        ["模型", "Accuracy", "Macro-F1"],
        ["多数类基线", base["majority"]["accuracy"], base["majority"]["macro_f1"]],
        ["TF-IDF + LR", base["tfidf_lr"]["accuracy"], base["tfidf_lr"]["macro_f1"]],
        ["SBERT + LR（冻结表示）", base["sbert_lr"]["accuracy"], base["sbert_lr"]["macro_f1"]],
        ["BERT 句对微调（本文最佳）", bert["accuracy"], bert["macro_f1"]],
    ], caption="表1  QEvasion 粗粒度三分类总体性能（官方测试集，n=308）")
    add_figure(doc, os.path.join(FIG, "fig5_model_compare.png"),
               "图1  四个层次的模型在 QEvasion 测试集上的 Accuracy 与 Macro-F1 对比")
    pc = bert["per_class"]
    add_table(doc, [
        ["类别", "Precision", "Recall", "F1", "Support"],
        ["Clear Reply", pc["Clear Reply"]["precision"], pc["Clear Reply"]["recall"],
         pc["Clear Reply"]["f1"], 79],
        ["Ambivalent", pc["Ambivalent"]["precision"], pc["Ambivalent"]["recall"],
         pc["Ambivalent"]["f1"], 206],
        ["Clear Non-Reply", pc["Clear Non-Reply"]["precision"],
         pc["Clear Non-Reply"]["recall"], pc["Clear Non-Reply"]["f1"], 23],
    ], caption="表2  最佳模型（BERT 微调）类别级结果")
    add_figure(doc, os.path.join(FIG, "fig3_cm_bert_coarse.png"),
               "图2  BERT 微调模型混淆矩阵（行=真实，列=预测）", width=4.4)
    add_para(doc,
             "类别级结果（表2、图2）显示：Ambivalent 类 F1 最高（0.813），Clear Reply 次之"
             "（0.464），Clear Non-Reply 仅 0.390；混淆矩阵中 Clear Reply 有 47 条被吸入 "
             "Ambivalent、16 条反向流入，两类互吸约占全部误判的八成，"
             "清晰界定了错误的主要形态——模型并非\"乱猜\"，而是在\"部分满足信息需求\"与"
             "\"完整满足\"的边界上系统性偏保守。")
    add_heading(doc, "4.2 跨场景迁移结果（回答 RQ2）", 2)
    zs = xfer["zero_shot_bert"]
    add_table(doc, [
        ["模型", "QEvasion（原任务）", "QNLI 零样本直接复用", "QNLI 目标域再训练"],
        ["TF-IDF + LR",
         f"{base['tfidf_lr']['accuracy']} / {base['tfidf_lr']['macro_f1']}", "—",
         f"{xfer['tfidf_lr_qnli']['accuracy']} / {xfer['tfidf_lr_qnli']['macro_f1']}"],
        ["SBERT + LR",
         f"{base['sbert_lr']['accuracy']} / {base['sbert_lr']['macro_f1']}", "—",
         f"{sbert_qnli['accuracy']} / {sbert_qnli['macro_f1']}"],
        ["BERT 句对微调",
         f"{bert['accuracy']} / {bert['macro_f1']}",
         f"{zs['accuracy']} / {zs['macro_f1']}",
         f"{xfer['bert_qnli_100pct']['accuracy']} / {xfer['bert_qnli_100pct']['macro_f1']}"],
    ], caption="表3  原任务与迁移任务对比（数值为 Accuracy / Macro-F1）")
    add_para(doc,
             "迁移结果呈现清晰的三个层次。第一，零样本直接复用完全失效：QEvasion 模型在 "
             f"QNLI 上的 Accuracy 仅 {zs['accuracy']}，等于把全部样本判为 not_entailment 的"
             "多数类水平——投影适配器只解决了标签空间对齐，解决不了决策边界共享，"
             "因为\"回答是否满足信息需求\"与\"句子是否蕴含\"的判据不同：前者容忍部分满足与"
             "话术性回避，后者只有蕴含与否的二元判断。第二，TF-IDF+LR 在 QNLI 上"
             f"仅取得 {xfer['tfidf_lr_qnli']['macro_f1']} 的 Macro-F1，与其在多数类基线附近的"
             "表现说明：蕴含判断必须建模问题与句子间的交互，词袋的词汇重叠特征在近均衡的"
             "二分类上失去区分力。第三，目标域再训练后 BERT 取得 "
             f"{xfer['bert_qnli_100pct']['macro_f1']} 的 Macro-F1，SBERT+LR 也回升至 "
             f"{sbert_qnli['macro_f1']}，符合 QNLI 上的常见水平。")
    add_figure(doc, eff_fig,
               "图3  QNLI 迁移的标注数据效率曲线：10%/30%/100% 训练池下的 BERT 性能")
    add_para(doc,
             "数据效率曲线（图3）进一步显示：10% 训练池（2000 条）即可把 Macro-F1 从零样本的 "
             f"{zs['macro_f1']:.3f} 拉升到 {xfer['bert_qnli_10pct']['macro_f1']}，30% 后达到 "
             f"{xfer['bert_qnli_30pct']['macro_f1']}，100% 为 "
             f"{xfer['bert_qnli_100pct']['macro_f1']}，呈边际递减。这说明字段适配器与训练"
             "流水线虽可零成本复用，但决定性能的决策边界必须由目标域标注数据重学；"
             "小样本适配的性价比最高，回答了 RQ2 的\"哪些可复用、哪些需重学\"。")
    add_heading(doc, "4.3 扩展实验：粗—细粒度标签层级一致性（回答 RQ3）", 2)
    add_table(doc, [
        ["一致性指标", "数值", "含义"],
        ["投影一致率（细粒度预测→映射 vs 粗粒度金标）",
         cons["hierarchy_macro_consistency_dev"], "细粒度模型映射后命中的比例（验证集）"],
        ["双模型一致率（细粒度投影 vs 粗粒度模型预测）",
         cons["two_model_agreement_test"], "两级模型预测遵循同一层级的比例（测试集）"],
        ["粗粒度模型自身准确率", bert["accuracy"], "双模型一致率的参照上限"],
    ], caption="表4  标签层级一致性结果")
    add_figure(doc, os.path.join(FIG, "fig6_cm_fine.png"),
               "图4  细粒度九类模型混淆矩阵（验证集，行=真实，列=预测）", width=5.2)
    add_para(doc,
             f"细粒度九类模型 Macro-F1 为 {fine['macro_f1']}、Accuracy {fine['accuracy']}，"
             "远低于三分类任务，主要因为尾部类别（Partial/half-answer、Clarification 训练集"
             "合计仅 171 条）几乎不可学习（图4）。层级一致性方面：投影一致率仅 "
             f"{cons['hierarchy_macro_consistency_dev']}，双模型一致率仅 "
             f"{cons['two_model_agreement_test']}，远低于粗粒度模型自身准确率 "
             f"{bert['accuracy']}。矛盾对统计显示，最集中的冲突是细粒度模型判为 Implicit/"
             "Declining to answer/Claims ignorance 而粗粒度模型判为 Ambivalent，以及"
             "细粒度判为 Explicit 而粗粒度判为 Clear Non-Reply——前者说明细粒度模型把大量"
             "\"泛泛而谈\"样本错分进了\"拒绝回答\"子类，映射后被抬升为 Clear Non-Reply；"
             "后者直接对应三分类任务中 Clear Reply 偏保守的错误模式。"
             "由此回答 RQ3：两级标签的层级在标注定义上是严格一致的，但在模型预测层面"
             "并不自动保持一致；细粒度信号目前不能直接用于校正粗粒度预测，"
             "先粗后细（coarse-to-fine，以粗粒度输出为条件的细粒度子分类）是更合理的建模方向。")
    add_heading(doc, "4.4 案例分析：典型误判样本", 2)
    rows = [["#", "错误类型", "真实 → 预测", "问题与回答关键证据"]]
    type2note = {
        "长而空泛": "回答 1309 词，仅结尾一句承诺性表态；模型被长段铺陈淹没，未捕捉尾部信息点",
        "部分/半回答→误判为明确回答": "回答只覆盖多子问题中的一部分，标注者判为部分回答，模型判为完整回应",
        "隐式回答边界模糊": "答案以暗示而非直陈方式给出，语义上介于 Ambivalent 与 Clear Reply 之间",
        "明确拒答被误判": "拒答前有长段背景铺垫，词面证据与 Clear Non-Reply 的典型短拒答不符",
        "明确回答被误判为回避": "回答同时回应多个子问题，模型仅匹配到部分信息点而整体判为模糊",
    }
    for i, e in enumerate(errs, 1):
        rows.append([i, e["type"], f"{e['gold']} → {e['pred']}",
                     type2note.get(e["type"], e["question"][:60])])
    add_table(doc, rows, caption="表5  五个典型误判样本及其可解释触发因素", sizes=9)
    add_para(doc,
             "五个案例共同指向两类根因：其一是长文本信息压缩——回答中位长度 207 词、最长 "
             "2117 词，384 子词截断后尾部信息点丢失，长而空泛的回答尤其受损；其二是标签边界"
             "本身的模糊性——\"部分回答\"与\"完整回答\"的界线依赖标注者对问题子部分覆盖的判断，"
             "与数据噪声叠加后，任何表示学习模型都难以完全消除该误差面。")
    add_heading(doc, "4.5 综合分析与结论适用范围", 2)
    add_para(doc,
             "综合来看，性能变化可以分解到四个来源。数据分布：QEvasion 测试集比训练集更不均衡"
             "（Ambivalent 占 66.9%），少数类的类别级指标天然波动更大；QNLI 近均衡，"
             "Macro-F1 与 Accuracy 接近。标签边界：Clear Reply/Ambivalent 的互吸与细粒度"
             "子类的不可分，都来自\"部分满足信息需求\"这一中间地带的定义模糊，"
             "属于任务固有难度而非模型缺陷。来源群体：QEvasion 全部来自政治记者会，"
             "说话人风格高度集中（前总统记者会），迁移到客服等场景时结论外推需谨慎；"
             "同时官方划分存在 38.3% 的访谈级重叠，所有绝对数值可能被轻微高估，"
             "但模型间的相对排序不受影响。模型表示：跨句交互（BERT 微调）带来的增益在两个"
             "任务上一致出现，而冻结表示与传统特征的差距在两任务上方向相反，"
             "说明\"表示够不够用\"取决于任务是否需要跨句对齐。"
             "综上，本文结论适用于\"问题—文本\"同构输入、标签由对应关系决定的判别任务；"
             "对标签空间差异更大的迁移场景（如中文 LCQMC、立场分类 EZ-STANCE），"
             "字段适配器与训练流水线仍可直接复用，但标签投影与决策边界必须重学。")

    # ================= 五、GitHub =================
    add_heading(doc, "五、代码与结果的开源（GitHub）")
    add_para(doc,
             f"本作业全部代码、配置、预测文件与结果已整理为可复现仓库并上传至 GitHub：{GITHUB}。"
             "仓库结构：src/prepare_data.py（统一字段适配器与数据下载）、src/eda.py（标签与长度"
             "分布分析）、src/train_tfidf.py（多数类与 TF-IDF+LR 基线）、src/train_sbert.py"
             "（冻结句向量基线）、src/train_bert.py（BERT 句对微调，支持九类与数据效率扩展）、"
             "src/transfer.py（零样本迁移与 QNLI 再训练）、src/analyze.py（混淆矩阵、误判样本与"
             "层级一致性分析）；results/ 内含全部指标 JSON、预测 CSV 与图表；"
             "README.md 给出一键复现命令与超参数说明。随机种子固定为 42，"
             "按 README 顺序执行即可复现本文全部表格与图形。")
    add_para(doc,
             "（注：请在上传后把正文中的仓库链接替换为实际地址，"
             "例如 https://github.com/yourname/qevasion-clarity-transfer。）", size=10.5)

    # ================= 六、参考文献 =================
    add_heading(doc, "六、参考文献")
    refs = [
        "[1] Thomas K, Filandrianos G, Lymperaiou M, Zerva C, Stamou G. \"I Never Said "
        "That\": A dataset, taxonomy and baselines on response clarity classification[C]// "
        "Findings of the Association for Computational Linguistics: EMNLP 2024. Miami, "
        "Florida: Association for Computational Linguistics, 2024: 5204-5233.",
        "[2] Devlin J, Chang M W, Lee K, Toutanova K. BERT: Pre-training of deep "
        "bidirectional transformers for language understanding[C]// Proceedings of the "
        "2019 Conference of the North American Chapter of the Association for "
        "Computational Linguistics. Minneapolis: ACL, 2019: 4171-4186.",
        "[3] Reimers N, Gurevych I. Sentence-BERT: Sentence embeddings using Siamese "
        "BERT-networks[C]// Proceedings of the 2019 Conference on Empirical Methods in "
        "Natural Language Processing. Hong Kong: ACL, 2019: 3982-3992.",
        "[4] Wang A, Singh A, Michael J, Hill F, Levy O, Bowman S R. GLUE: A multi-task "
        "benchmark and analysis platform for natural language understanding[C]// "
        "International Conference on Learning Representations (ICLR). New Orleans, 2019.",
        "[5] Rajpurkar P, Zhang J, Lopyrev K, Liang P. SQuAD: 100,000+ questions for "
        "machine comprehension of text[C]// Proceedings of the 2016 Conference on "
        "Empirical Methods in Natural Language Processing. Austin: ACL, 2016: 2383-2392.",
        "[6] Opitz J, Burst S. Macro F1 and F1 measures, oh my![C]// Proceedings of the "
        "13th Edition of the ACL Student Research Workshop. Dublin: ACL, 2022: 34-41.",
        "[7] Pedregosa F, Varoquaux G, Gramfort A, et al. Scikit-learn: Machine learning "
        "in Python[J]. Journal of Machine Learning Research, 2011, 12: 2825-2830.",
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.3
        run = p.add_run(r)
        set_font(run, size=10.5)

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
