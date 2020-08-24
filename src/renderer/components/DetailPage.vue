<template>
  <div style="display:flex;flex-direction:column;height:100%">
    <div style="display:flex;align-items:center">
      <div>
        <span>Views type:</span>
        <Select multiple v-model="selectedViewTypes">
          <Option
            v-for="option in viewTypes"
            :key="option"
            :value="option"
            :label="option"
          ></Option>
        </Select>
      </div>
      <div style="margin-left:12px">
        <span>Num. of views:</span>
        <Select multiple v-model="selectedNumOfViews">
          <Option
            v-for="option in numOfViews"
            :key="option"
            :value="option"
            :label="option"
          ></Option>
        </Select>
      </div>
      <div style="margin-left:12px">
        <span>Group by:</span>
        <Select v-model="groupMode">
          <Option
            v-for="option in groupOptions"
            :key="option.key"
            :value="option.key"
            :label="option.label || option.key"
          ></Option>
        </Select>
      </div>
      <div style="margin-left:12px">
        <span>Color by:</span>
        <Select v-model="colorMode">
          <Option
            v-for="option in colorOptions"
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
    <div
      style="display:flex;flex-grow:1;align-items:stretch;justify-content:center;margin-top:4px"
    >
      <div
        v-for="(group, i) in sortedItem"
        style="width:0;flex-grow:1;display:flex;flex-direction:column;padding:4px;max-width:30%"
        :style="{
          borderRight:
            i === sortedItem.length - 1 ? 'none' : '1px dashed #808080',
        }"
        :key="group.name"
      >
        <p style="text-align:center;background:lightgray;margin-bottom:4px">
          {{ group.name }}
        </p>
        <div
          style="display:grid;grid-template-columns:repeat(auto-fill,minmax(35px,1fr))"
        >
          <Poptip
            v-for="paper in group.items"
            :key="paper.doi"
            :title="paper.title"
            trigger="hover"
            class="paper-poptip"
            :width="380"
            :word-wrap="true"
            :placement="i === sortedItem.length - 1 ? 'bottom-end' : 'bottom'"
            style="width:90%;margin:0 5%"
          >
            <div
              style="border-radius:50%;width:100%;padding-top:100%"
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
              </div>
            </div>
          </Poptip>
        </div>
        <div style="flex-grow:1"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from "vuex";
import path from "path";
import fs from "fs";
import { shell } from "electron";
const { app } = require("electron").remote;
const { dialog, BrowserWindow } = require("electron").remote;

function viewString2Num(num) {
  const base = parseInt(num);
  let end = base;
  if (num.endsWith("+")) {
    end = Infinity;
  }
  return [base, end];
}

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

function getColorMap(type, values) {
  if (type === "categorical") {
    if (values.length <= 8) {
      return (input) =>
        [
          "#808080",
          "#7fc97f",
          "#beaed4",
          "#fdc086",
          "#ffff99",
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
    return (input) => bluesColorMap((input - min) / (max - min));
  }
  return () => "#808080";
}

export default {
  name: "mv-page",
  data() {
    return {
      viewTypes: [
        "Area",
        "Bar",
        "Circle",
        "Diag.",
        "Distri.",
        "Net.",
        "Grid",
        "Line",
        "Map",
        "Point",
        "Table",
        "Text",
        "SciVis",
        "Panel",
      ],
      numOfViews: ["2", "3", "4", "5", "6", "7", "8", "9", "10", "11+"],
      selectedViewTypes: [],
      selectedNumOfViews: [],
      groupOptions: [
        { key: "year", type: "categorical" },
        { key: "venue", type: "categorical" },
        { key: "view_num", label: "Num. of Views", type: "numerical" },
      ],
      groupMode: "view_num",
      colorMode: "year",
    };
  },
  computed: {
    filteredItem() {
      return this.mv_config.papers
        .filter(
          (paper) =>
            !this.selectedViewTypes.find(
              (viewType) => !paper.view_type.includes(viewType)
            )
        )
        .filter((paper) =>
          this.selectedNumOfViews.length
            ? !!this.selectedNumOfViews.find((numOfViews) => {
                const range = viewString2Num(numOfViews);
                return paper.view_num >= range[0] && paper.view_num <= range[1];
              })
            : true
        );
    },
    groupedItem() {
      const preresult = {};
      this.filteredItem.forEach((paper) => {
        let paperKey = paper[this.groupMode];
        if (this.groupType === "numerical") {
          paperKey = Math.round(paperKey);
        }
        preresult[paperKey] = preresult[paperKey] || [];
        preresult[paperKey].push(paper);
      });
      const result = [];
      Object.entries(preresult)
        .sort((a, b) =>
          this.groupType === "numerical"
            ? parseFloat(a[0]) - parseFloat(b[0])
            : a[0] < b[0]
            ? -1
            : 1
        )
        .forEach(([name, items], i, arr) => {
          if (i >= 9 && this.groupType === "numerical" && arr.length > 10) {
            if (i === 9) {
              result.push({ name: `${name}+`, items });
            } else {
              result[9].items = result[9].items.concat(items);
            }
          } else {
            result.push({ name, items });
          }
        });
      return result;
    },
    sortedItem() {
      return this.groupedItem.map((group) => {
        return {
          ...group,
          items: group.items
            .slice()
            .sort((a, b) =>
              a[this.colorMode] < b[this.colorMode]
                ? -1
                : a[this.colorMode] > b[this.colorMode]
                ? 1
                : a.doi < b.doi
                ? -1
                : 1
            ),
        };
      });
    },
    groupType() {
      return this.groupOptions.find((option) => option.key === this.groupMode)
        .type;
    },
    colorValues() {
      return [
        ...new Set(
          this.sortedItem.reduce(
            (p, v) => p.concat(v.items.map((x) => x[this.colorMode])),
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
    colorOptions() {
      return this.groupOptions.filter(
        (option) => option.key !== this.groupMode
      );
    },
    ...mapState({
      mv_config: (s) => s.Config.mv_config,
    }),
  },
  watch: {
    colorOptions(v) {
      if (!v.find((option) => option.key === this.colorMode)) {
        this.colorMode = v[0].key;
      }
    },
  },
  methods: {
    getViewsPosition(paper) {
      return this.parseViewObject(paper.views.result.views);
    },
    parseViewObject(views) {
      return Object.values(views)
        .map((view) => [
          [
            view.cX - view.cWidth / 2,
            view.cY - view.cHeight / 2,
            view.cWidth,
            view.cHeight,
          ].map((n) => parseFloat(n) * 100),
          ...this.parseViewObject(view.mid_view || {}),
        ])
        .reduce((p, v) => p.concat(v), []);
    },
    getViewTypes(paper) {
      return this.parseTypes(paper.views.result.views).join(', ');
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
