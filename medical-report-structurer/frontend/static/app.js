const { createApp } = Vue;

createApp({
  components: {
    "empty-state": {
      props: ["text"],
      template: `<div class="empty-state">{{ text }}</div>`,
    },
  },
  data() {
    return {
      text: "患者发绕发绕3天，咳嗦2周，体温 38.6，白细胞 12.5，中性粒细胞80%，CRP 35。考虑急性上呼吸道感染。",
      result: null,
      activeView: "report",
      selectedEvidence: "",
      selectedSentence: "",
      generatedAt: "",
      reportNo: "",
      loading: false,
      copied: false,
      error: "",
      appReady: false,
    };
  },
  computed: {
    prettyJson() {
      return this.result ? JSON.stringify(this.result.extracted, null, 2) : "";
    },
    summary() {
      if (!this.result) {
        return { symptoms: 0, indicators: 0, diagnoses: 0, total: 0 };
      }
      const symptoms = this.result.extracted.symptoms.length;
      const indicators = this.result.extracted.indicators.length;
      const diagnoses = this.result.extracted.diagnoses.length;
      return { symptoms, indicators, diagnoses, total: symptoms + indicators + diagnoses };
    },
    highlightedText() {
      if (!this.result) return "";
      const text = this.result.preprocessing.standardized;
      if (!this.selectedEvidence) return text;
      return text.includes(this.selectedEvidence) ? text.replace(this.selectedEvidence, `【${this.selectedEvidence}】`) : text;
    },
  },
  methods: {
    fillSample(type) {
      const samples = {
        fever:
          "患者发烧3天，咳嗦咳嗦2周，体温39度，白细胞15.2，CRP 42mg/L，血氧饱和度95%。诊断：急性上呼吸道感染。",
        gastro:
          "患者拉肚子2日，腹痛1天，恶心想吐，血压 138/86，心率 102，血糖 7.8。考虑急性胃肠炎。",
      };
      this.text = samples[type] || samples.fever;
      this.parseReport();
    },
    clearAll() {
      this.text = "";
      this.result = null;
      this.error = "";
      this.selectedEvidence = "";
      this.selectedSentence = "";
    },
    selectEvidence(source) {
      this.selectedEvidence = this.selectedEvidence === source ? "" : source;
    },
    toggleSentence(sentence) {
      this.selectedSentence = this.selectedSentence === sentence ? "" : sentence;
      this.selectedEvidence = sentence;
    },
    confidenceLabel(value) {
      return value === "high" ? "高" : "中";
    },
    updateReportMeta() {
      const now = new Date();
      this.generatedAt = now.toLocaleString("zh-CN", { hour12: false });
      this.reportNo = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}-${String(now.getHours()).padStart(2, "0")}${String(now.getMinutes()).padStart(2, "0")}`;
    },
    async copyJson() {
      if (!this.result) return;
      await navigator.clipboard.writeText(this.prettyJson);
      this.copied = true;
      window.setTimeout(() => {
        this.copied = false;
      }, 1200);
    },
    printReport() {
      this.activeView = "report";
      this.$nextTick(() => window.print());
    },
    async parseReport() {
      this.error = "";
      this.loading = true;
      this.selectedEvidence = "";
      this.selectedSentence = "";

      try {
        const response = await fetch("/api/parse", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: this.text }),
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "解析失败");
        }
        this.result = data;
        this.activeView = "report";
        this.updateReportMeta();
      } catch (err) {
        this.error = err.message || "解析失败";
      } finally {
        this.loading = false;
      }
    },
  },
  mounted() {
    window.setTimeout(() => {
      this.appReady = true;
    }, 120);
    this.parseReport();
  },
}).mount("#app");
