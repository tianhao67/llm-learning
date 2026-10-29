# 评测目录

```
evals/
├── cases/              # 评测集（jsonl，一行一条）
│   ├── classify.jsonl  # 情感分类 30 条
│   ├── survey.jsonl    # 问卷建议 12 条
│   └── rag.jsonl       # 课程笔记问答 15 条
├── results/            # 运行结果（markdown，会提交到仓库作为记录）
└── run_eval.py         # 评测入口
```

运行方式：

```bash
python evals/run_eval.py --task classify
python evals/run_eval.py --task survey --variants v1,v2,v3
python evals/run_eval.py --task rag --top-k 3 --generate
```

指标定义、样本设计思路和复现步骤见 [docs/evaluation.md](../docs/evaluation.md)。
每次跑完把 `results/` 下的文件一起提交，方便对比历史版本。
