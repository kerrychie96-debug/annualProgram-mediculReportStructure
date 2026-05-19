# 医学报告结构化系统

一个纯规则 + 正则 + jieba 分词实现的医学报告结构化演示系统。

## 功能

- 文本预处理：清理无效字符、语气词、重复词、常见错别字
- 智能分句与分词：使用 jieba，并加载医学词典避免术语被拆分
- 术语标准化：将口语表达转换为标准医学术语
- 信息提取：症状、时长、检查指标、数值、单位、诊断
- 单位补全：根据指标自动补全常见默认单位

## 运行

```bash
cd medical-report-structurer
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

浏览器打开：

```text
http://127.0.0.1:5000
```

如果 Windows 提示从 Microsoft Store 安装 Python，说明当前没有可用的真实 Python 解释器。安装 Python 3.10+ 后重新执行上面的命令即可。

## 示例文本

```text
患者发绕发绕3天，咳嗦2周，体温 38.6，白细胞 12.5，中性粒细胞80%，CRP 35。考虑急性上呼吸道感染。
```
