<template>
  <div>
    <!-- <Select v-model="selpath" style="width:calc(100% - 80px)">
      <Option value="all">全部视频文件</Option>
      <OptionGroup v-for="volume in volumes" :key="volume.volume" :label="volume.volume">
        <Option :value="volume.volume + '@root$all'">此盘全部视频</Option>
        <Option v-for="dir in volume.directories" :key="dir.path" :value="volume.volume + dir.path" class="overflow-option">{{ dir.path ? dir.path : '/' }}</Option>
      </OptionGroup>
    </Select> -->
    <!-- <Button type="ghost" shape="circle" icon="ios-plus-empty" @click="addPath"></Button> -->
    <span>{{ filteredItem.length }} papers</span>
    <Button
      :type="onlyV ? 'info' : 'ghost'"
      shape="circle"
      icon="ios-glasses-outline"
      @click="onlyV = !onlyV"
    ></Button>
    <Page
      v-if="filteredItem.length > 40"
      :total="filteredItem.length"
      :page-size="40"
      @on-change="page = $event"
      style="text-align: center; margin-top: 20px; margin-bottom: 10px;"
      :current="page"
    ></Page>
    <waterfall line="h" :line-gap="200" :min-line-gap="180" :max-line-gap="220">
      <waterfall-slot
        v-for="(item, index) in filteredItem.slice((page - 1) * 40, page * 40)"
        :width="400"
        :height="400"
        :order="index"
        :key="item.DOI"
        class="thumbshow"
        style="padding: 10px;"
      >
        <div
          class="thumbview"
          :style="{
            'background-image': 'url(/static/images/' + item.image + ')',
          }"
        >
          {{ item.image ? "" : "No teaser available" }}
        </div>
        <div class="thumbinfo">
          <div class="namectner">
            <p style="font-weight:bold" :title="item.Title">{{ item.Title }}</p>
            <p :title="item.AuthorKeywords">{{ item.AuthorKeywords }}</p>
          </div>
          <div class="btngroup">
            <Button
              :type="item.hasViewed ? 'success' : 'ghost'"
              shape="circle"
              :icon="
                item.hasViewed ? 'ios-checkmark-empty' : 'ios-glasses-outline'
              "
              @click="toggleItem(item)"
            ></Button>
            <!-- <Button
              type="ghost"
              shape="circle"
              icon="ios-more"
            ></Button> -->
          </div>
        </div>
      </waterfall-slot>
    </waterfall>
    <Page
      v-if="filteredItem.length > 40"
      :total="filteredItem.length"
      :page-size="40"
      @on-change="page = $event"
      style="text-align: center; margin-top: 20px;"
      :current="page"
    ></Page>
  </div>
</template>

<script>
import { mapState, mapActions } from "vuex";
import path from "path";
import fs from "fs";
import { shell } from "electron";
import Waterfall from "vue-waterfall/lib/waterfall";
import WaterfallSlot from "vue-waterfall/lib/waterfall-slot";
const { app } = require("electron").remote;
const { dialog, BrowserWindow } = require("electron").remote;

export default {
  name: "index-page",
  data() {
    return {
      selpath: "all",
      refdig: 0,
      onlyV: false,
      page: 1,
    };
  },
  computed: {
    totalItem() {
      console.log(this.app_config);
      if (!this.app_config.papers) return [];
      return this.app_config.papers;
    },
    filteredItem() {
      return (() => {
        if (this.selpath == "all") return this.totalItem;
        if (this.selpath.endsWith("@root$all"))
          return this.totalItem.filter(
            (x) => x.volume == this.selpath.slice(0, -9)
          );
        return this.totalItem.filter((x) => x.pk == this.selpath);
      })().filter((x) => !this.onlyV || x.hasViewed);
      // .map((x, i, a) => {
      //   if (this.search_content) {
      //     return {
      //       block: x,
      //       fuzzy: fuzzy.filter(this.search_content, slice).map((y) => {
      //         return {
      //           x_index: y.original.indexOf(this.search_content[0]),
      //           ...y,
      //         };
      //       }),
      //     };
      //   } else
      //     return {
      //       block: x,
      //       fuzzy: [{ score: a.length - i, x_index: i }],
      //     };
      // })
      // .filter((x) => x.fuzzy.length > 0)
      // .sort(
      //   (i, j) =>
      //     j.fuzzy[0].score - i.fuzzy[0].score ||
      //     i.fuzzy[0].x_index - j.fuzzy[0].x_index
      // )
      // .map((x) => x.block);
    },
    ...mapState({
      app_config: (s) => s.Config.app_config,
      search_content: (s) => s.SearchBar.search_content,
    }),
  },
  methods: {
    toggleItem(fb) {
      let f = this.app_config.papers.find((x) => x.DOI == fb.DOI);
      if (f) {
        let k = this.app_config.papers.indexOf(f);
        this.setByPath([["papers", k, "hasViewed"], !fb.hasViewed]);
      }
    },
    ...mapActions(["setByPath"]),
  },
  watch: {
    page() {
      this.$el.parentElement.scrollTop = 0;
    },
    search_content() {
      this.$set(this, "page", 1);
    },
    onlyV() {
      this.$set(this, "page", 1);
    },
  },
  components: {
    Waterfall,
    WaterfallSlot,
  },
};
</script>

<style lang="scss">
.overflow-option {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
  direction: rtl;
  text-align: left;
}

.thumbshow {
  padding: 10px;
  transition: 0.3s ease-in-out;

  &:hover {
    background: rgba(128, 132, 143, 0.3);
  }

  .thumbview {
    width: 100%;
    height: 56.25%;
    background-size: cover;
    background-position: center center;
    cursor: pointer;
    text-align: center;
    background-color: gainsboro;
  }

  .thumbload {
    width: 100%;
    height: 56.25%;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    background: #bbbec4;
  }

  .thumbinfo {
    width: 100%;
    height: 43.75%;

    .namectner {
      display: flex;
      justify-content: left;
      flex-direction: column;
      align-items: center;
      width: 100%;
      height: 50%;

      p {
        width: 100%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        text-align: left;
        cursor: pointer;
      }
    }

    .btngroup {
      width: 100%;
      height: 50%;
      margin: 0;
      position: relative;

      .ivu-btn.ivu-btn-circle.ivu-btn-icon-only {
        width: 20%;
        height: 0;
        padding-top: 20%;
        margin: 4%;
        font-size: width;
        position: relative;

        .ivu-icon {
          position: absolute;
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
        }
      }
    }
  }
}
</style>
