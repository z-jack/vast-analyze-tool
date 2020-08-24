<template>
  <div style="display:flex;flex-direction:column;height:100%">
    <div style="display:flex;align-items:center">
      <div style="margin-left:12px">
        <span>Cluster by:</span>
        <Select v-model="clusterMode">
          <Option
            v-for="option in clusterOptions"
            :key="option"
            :value="option"
            :label="option"
          ></Option>
        </Select>
      </div>
      <div style="margin-left:12px">
        <span>Color by:</span>
        <Select v-model="colorMode">
          <Option
            v-for="option in groupOptions"
            :key="option.key"
            :value="option.key"
            :label="option.label || option.key"
          ></Option>
        </Select>
      </div>
      <div style="flex-grow:1"></div>
      <div>{{ colorLabel }}:</div>
      <div
        v-for="value in colorValues"
        :key="value"
        style="text-align:center;margin-left:8px"
      >
        <div
          style="width:24px;height:24px;border-radius:50%;margin:0 auto"
          :style="{ background: colorMap(value) }"
        ></div>
        <p>{{ value }}</p>
      </div>
    </div>
    <div style="flex-grow:1;position:relative">
      <Poptip
        v-for="paper in paperPosition"
        :key="paper.doi"
        :title="paper.title"
        trigger="hover"
        class="paper-poptip"
        :width="380"
        :word-wrap="true"
        placement="bottom"
        style="position:absolute"
        :style="{
          left: (paper.position[0] + 1) * 49 + '%',
          top: (paper.position[1] + 1) * 49 + '%',
        }"
      >
        <div
          style="border-radius:50%;width:5px;height:5px"
          :style="{ background: colorMap(paper[colorMode]) }"
        ></div>
        <div slot="content" style="display:flex">
          <div
            style="width:180px;height:120px;position:relative;border:1px solid transparent"
          >
            <div
              v-for="(view, i) in getViewsPosition(paper)"
              :key="i"
              style="position:absolute;border:1px solid black"
              :style="{
                left: view[0] + '%',
                top: view[1] + '%',
                width: view[2] + '%',
                height: view[3] + '%',
              }"
            ></div>
          </div>
          <div style="margin-left:8px;width:0;flex-grow:1">
            <p>{{ paper.venue }} - {{ paper.year }}</p>
            <p><b>Authors: </b>{{ paper.author }}</p>
            <a href="#" @click="openUrl(paper.url)"
              ><b>DOI: </b>{{ paper.doi }}</a
            >
            <p><b>Views: </b>{{ getViewTypes(paper) }}</p>
            <!-- <p><b>Vector: </b>{{ paper.vector }}</p> -->
          </div>
        </div>
      </Poptip>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from "vuex";
import path from "path";
import fs from "fs";
import { shell } from "electron";
import TSNE from "tsne-js";
import PCA from "../assets/pca";
import MDS from "../assets/mds";

const { app } = require("electron").remote;
const { dialog, BrowserWindow } = require("electron").remote;

const model = new TSNE({
  dim: 2,
  perplexity: 5.0,
  earlyExaggeration: 4.0,
  learningRate: 100.0,
  nIter: 1000,
  metric: "euclidean",
});

function bluesColorMap(value) {
  if (value <= 0) return "#cfe1f2";
  if (value >= 1) return "#0a4a90";
  const colormap = [
    [207, 225, 242],
    [190, 216, 236],
    [168, 206, 229],
    [143, 193, 222],
    [116, 178, 215],
    [91, 163, 207],
    [69, 146, 198],
    [49, 129, 189],
    [32, 111, 178],
    [18, 92, 164],
    [10, 74, 144],
  ];
  const stop = Math.floor(value * 10);
  const ratio = value * 10 - stop;
  const blendValue = colormap[stop].map((v, i) =>
    Math.round(v * (1 - ratio) + colormap[stop + 1][i] * ratio)
  );
  return `#${blendValue.map((x) => x.toString(16).padStart(2, "0")).join("")}`;
}

function redsColorMap(value) {
  if (value <= 0) return "#fdc9b4";
  if (value >= 1) return "#970b13";
  const colormap = [
    [253, 201, 180],
    [252, 180, 154],
    [252, 158, 128],
    [252, 135, 103],
    [250, 112, 81],
    [246, 87, 63],
    [236, 63, 47],
    [220, 42, 37],
    [200, 27, 29],
    [178, 18, 24],
    [151, 11, 19],
  ];
  const stop = Math.floor(value * 10);
  const ratio = value * 10 - stop;
  const blendValue = colormap[stop].map((v, i) =>
    Math.round(v * (1 - ratio) + colormap[stop + 1][i] * ratio)
  );
  return `#${blendValue.map((x) => x.toString(16).padStart(2, "0")).join("")}`;
}

function getColorMap(type, values) {
  if (type === "categorical") {
    if (values.length <= 8) {
      return (input) =>
        [
          "#808080",
          "#7fc97f",
          "#beaed4",
          "#fdc086",
          "#ff0000",
          "#386cb0",
          "#f0027f",
          "#bf5b17",
          "#666666",
        ][values.indexOf(input) + 1];
    }
    if (values.length <= 10) {
      return (input) =>
        [
          "#808080",
          "#1f77b4",
          "#ff7f0e",
          "#2ca02c",
          "#d62728",
          "#9467bd",
          "#8c564b",
          "#e377c2",
          "#7f7f7f",
          "#bcbd22",
          "#17becf",
        ][values.indexOf(input) + 1];
    }
    return (input) =>
      values.includes(input)
        ? [
            "#1f77b4",
            "#aec7e8",
            "#ff7f0e",
            "#ffbb78",
            "#2ca02c",
            "#98df8a",
            "#d62728",
            "#ff9896",
            "#9467bd",
            "#c5b0d5",
            "#8c564b",
            "#c49c94",
            "#e377c2",
            "#f7b6d2",
            "#7f7f7f",
            "#c7c7c7",
            "#bcbd22",
            "#dbdb8d",
            "#17becf",
            "#9edae5",
          ][values.indexOf(input) % 20]
        : "#808080";
  }
  if (type === "numerical") {
    const min = Math.min(...values);
    const max = Math.max(...values);
    return (input) => redsColorMap((input - min) / (max - min));
  }
  return () => "#808080";
}

export default {
  name: "cluster-page",
  data() {
    return {
      groupOptions: [
        { key: "year", type: "categorical" },
        { key: "venue", type: "categorical" },
        { key: "view_num", label: "Num. of Views", type: "numerical" },
      ],
      clusterOptions: ["tSNE", "MDS", "PCA"],
      colorMode: "venue",
      clusterMode: "MDS",
    };
  },
  computed: {
    ...mapState({
      mv_config: (s) => s.Config.mv_config,
    }),
    rawPaperVectors() {
      return this.mv_config.papers.filter((paper) => ![].includes(paper.doi)); // filter out some outlier to beautify result
      // .map((paper) => this.parseViewObject(paper.views.result.views));
    },
    chartTypes() {
      return [
        ...new Set(
          this.rawPaperVectors
            .map((paper) => Object.keys(paper))
            .reduce((p, v) => p.concat(v), [])
        ),
      ];
    },
    paperVectors() {
      return this.rawPaperVectors.map(
        (paper) =>
          // this.chartTypes.map((type) => paper[type] || 0)
          paper.viewMatrix
      );
    },
    paperPosition() {
      let output;
      // switch (this.clusterMode) {
      //   case "tSNE":
      //     model.init({
      //       data: this.paperVectors,
      //       type: "dense",
      //     });
      //     console.log(model.run());
      //     output = model.getOutputScaled();
      //     console.log(output);
      //     return output.map((position, i) => ({
      //       ...this.mv_config.papers[i],
      //       position,
      //       vector:this.paperVectors[i]
      //     }));
      //   case "MDS":
      //     output = MDS(this.paperVectors);
      //     console.log(output);
      //     return output.map((position, i) => ({
      //       ...this.mv_config.papers[i],
      //       position,
      //       vector:this.paperVectors[i]
      //     }));
      //   case "PCA":
      //     output = PCA(this.paperVectors);
      //     console.log(output);
      //     return output.map((position, i) => ({
      //       ...this.mv_config.papers[i],
      //       position,
      //       vector:this.paperVectors[i]
      //     }));
      // }
      output = JSON.parse(fs.readFileSync("static/data/tsne.json"));
      return output.map((position, i) => ({
        ...this.mv_config.papers[i],
        position,
        vector: this.paperVectors[i],
      }));
      // return [];
    },
    colorValues() {
      return [
        ...new Set(
          this.mv_config.papers.reduce(
            (p, v) => p.concat([v[this.colorMode]]),
            []
          )
        ),
      ].sort((a, b) =>
        this.colorType === "numerical"
          ? parseFloat(a) - parseFloat(b)
          : a < b
          ? -1
          : 1
      );
    },
    colorMap() {
      return getColorMap(this.colorType, this.colorValues);
    },
    colorLabel() {
      const colorOption = this.groupOptions.find(
        (option) => option.key === this.colorMode
      );
      return colorOption.label || colorOption.key;
    },
    colorType() {
      return this.groupOptions.find((option) => option.key === this.colorMode)
        .type;
    },
  },
  methods: {
    parseViewObject(views) {
      return Object.entries(
        Object.values(views)
          .map((view) => [
            view.viewType.map((v) => ({
              ...v,
              probability:
                parseFloat(v.probability || "1") *
                parseFloat(view.cWidth) *
                parseFloat(view.cHeight),
            })),
            ...this.parseViewObject(view.mid_view || {}).map((v) => ({
              ...v,
              probability:
                parseFloat(v.probability || "1") *
                parseFloat(view.cWidth) *
                parseFloat(view.cHeight),
            })),
          ])
          .reduce((p, v) => p.concat(...v), [])
          .filter((v) => v.Type !== "small multiple")
          .reduce(
            (p, v) => ({
              ...p,
              [v.Type]: (p[v.Type] || 0) + v.probability,
            }),
            {}
          )
      ).map(([Type, probability]) => ({ Type, probability }));
    },
    getViewsPosition(paper) {
      return this.parseViewPosObject(paper.views.result.views);
    },
    parseViewPosObject(views) {
      return Object.values(views)
        .map((view) => [
          [
            view.cX - view.cWidth / 2,
            view.cY - view.cHeight / 2,
            view.cWidth,
            view.cHeight,
          ].map((n) => parseFloat(n) * 100),
          ...this.parseViewPosObject(view.mid_view || {}),
        ])
        .reduce((p, v) => p.concat(v), []);
    },
    getViewTypes(paper) {
      return this.parseTypes(paper.views.result.views).join(", ");
    },
    parseTypes(views) {
      return Object.values(views)
        .map((view) => {
          const childrenTypes = this.parseTypes(view.mid_view || {});
          return childrenTypes.length
            ? childrenTypes
            : view.viewType.map((x) => x.Type);
        })
        .reduce((p, v) => p.concat(v), []);
    },
    openUrl(url) {
      shell.openExternal(url);
    },
  },
};
</script>

<style lang="scss">
.paper-poptip {
  .ivu-poptip-rel {
    width: 100%;
  }

  .ivu-poptip-inner {
    white-space: unset;
  }
}
</style>
