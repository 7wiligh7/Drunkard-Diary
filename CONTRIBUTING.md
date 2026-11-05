# 参与贡献

欢迎补充酒款、修正参数、或者纯粹来吵架（关于哪款更好喝）。

## 快速开始

```bash
git clone <你的仓库地址>
cd beer-tasting-notes
pip install -r requirements.txt
python scripts/build.py
```

## 新增一条品鉴

在 `data/beers.yml` 的 `beers:` 列表里追加一条，然后运行 `python scripts/build.py`，README 会自动更新。

```yaml
  - id: rochefort-8
    name: 罗斯福8号
    brand: 罗斯福
    style: trappist
    origin: 比利时
    abv: 9.2
    plato: 20
    price: 3
    rating: 4
    tags: [焦糖, 果香, 酒精感]
    notes: "入口偏甜，果香明显，收尾带一点酒花的苦，比10号好入口。"
```

## 字段说明

| 字段 | 必填 | 类型 | 说明 |
| --- | :---: | --- | --- |
| `id` | ✅ | string | 唯一标识，小写字母/数字/连字符，例如 `rochefort-8` |
| `name` | ✅ | string | 展示名称 |
| `brand` | | string \| null | 品牌或酒厂 |
| `style` | ✅ | enum | 风格 key，见下表 |
| `origin` | | string \| null | 产地国家 / 地区 |
| `abv` | | number \| null | 酒精度（%），只填包装标注值 |
| `plato` | | number \| null | 原麦汁浓度（°P），只填包装标注值 |
| `price` | | 1 \| 2 \| 3 \| null | 1=平价 2=适中 3=偏贵 |
| `rating` | ✅ | 1-5 | 主观评分 |
| `tags` | | string[] | 风味关键词，2-5 个即可 |
| `notes` | ✅ | string | 品鉴记录，用中文，写具体味道而不是「好喝」两个字 |

### 风格 key

| key | 中文名 |
| --- | --- |
| `draft` | 鲜啤 / 原浆 |
| `pale-lager` | 淡色拉格 |
| `dark-lager` | 黑拉格 |
| `pilsner` | 皮尔森 |
| `wheat` | 小麦白啤 |
| `witbier` | 比利时白啤 |
| `belgian-ale` | 比利时艾尔 |
| `trappist` | 修道院啤酒 |
| `ipa` | IPA |
| `stout` | 世涛 / 黑啤 |
| `sour` | 酸啤 / 果啤 |
| `ale` | 艾尔（其他） |
| `non-alcoholic` | 无醇啤酒 |

需要新风格时，请同时修改 `scripts/build.py` 的 `STYLES`、`schema/beer.schema.json` 的 `enum` 和本表格。

## 评分标准

| 评分 | 含义 |
| :---: | --- |
| 5 | 会主动回购，愿意推荐给朋友 |
| 4 | 好喝，值得再买 |
| 3 | 一般，能喝但不惦记 |
| 2 | 不太行，喝完不会想第二瓶 |
| 1 | 踩雷 |

同一款酒允许出现多条记录（不同批次 / 不同年份），用 `id` 区分，例如 `rochefort-10-2024`。但请优先在原有条目上修正，避免重复。

## 提交前检查

```bash
python scripts/build.py --check   # README 是否与数据同步
```

CI 会对每个 PR 跑同样的命令：

- YAML 语法错误；
- `id` 重复或格式不合法；
- `rating` 不在 1-5；
- 未知的 `style`；
- README 忘记重新生成。

## 提交 PR

1. 从 `main` 切一个分支，例如 `feat/add-rochefort-8`；
2. 只改 `data/beers.yml` 和自动生成的 `README.md`；
3. 一个 PR 聚焦一件事（加酒 / 纠错 / 改样式），方便 review；
4. Commit message 建议使用 `feat: 新增罗斯福8号`、`fix: 修正泰象产地` 这类格式。

## 数据声明

- 所有品鉴内容均为个人主观感受，不代表客观品质；
- 酒精度、麦汁浓度等硬参数请以包装或官方资料为准，没把握就写 `null`，不要猜；
- 请勿上传他人未授权的整篇文章或评测，引用请注明来源。