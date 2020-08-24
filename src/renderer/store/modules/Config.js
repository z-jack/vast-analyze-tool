import Vue from "vue";
import fs from "fs";

function loadMVConfig() {
  const config = JSON.parse(
    fs.readFileSync("static/data/mv_data.json").toString("utf8")
  );
  config.papers.forEach((paper) => {
    paper.views = JSON.parse(
      fs.readFileSync(`static/data/mv_data/${paper.json}`).toString("utf8")
    );
  });
  return config;
}

const state = {
  app_config: JSON.parse(
    fs.readFileSync("static/data/config.json").toString("utf8")
  ),
  tmp_config: {},
  mv_config: loadMVConfig(),
};

const mutations = {
  SET_CONFIG(state, cfg) {
    state.app_config = cfg;
    fs.writeFileSync(
      "static/data/config.json",
      JSON.stringify(state.app_config)
    );
  },
  SET_KV(state, arr) {
    let [k, v] = arr;
    Vue.set(state.app_config, k, v);
    fs.writeFileSync(
      "static/data/config.json",
      JSON.stringify(state.app_config)
    );
  },
  SET_DEP(state, arr) {
    let [p, v] = arr;
    let cfg = state.app_config;
    for (let i = 0; i < p.length - 1; i++) {
      let key = p[i];
      cfg = cfg[key];
      if (!cfg && i < p.length - 1) return;
    }
    Vue.set(cfg, p.pop(), v);
    fs.writeFileSync(
      "static/data/config.json",
      JSON.stringify(state.app_config)
    );
  },
  SET_TMP(state, arr) {
    let [k, v] = arr;
    Vue.set(state.tmp_config, k, v);
  },
};

const actions = {
  setConfig({ commit }, cfg) {
    commit("SET_CONFIG", cfg);
  },
  setByKeyValue({ commit }, arr) {
    if (!(arr instanceof Array) || arr.length != 2) return;
    commit("SET_KV", arr);
  },
  setByPath({ commit }, arr) {
    if (
      !(arr instanceof Array) ||
      arr.length != 2 ||
      !(arr[0] instanceof Array)
    )
      return;
    commit("SET_DEP", arr);
  },
  saveToTmp({ commit }, arr) {
    if (!(arr instanceof Array) || arr.length != 2) return;
    commit("SET_TMP", arr);
  },
};

export default {
  state,
  mutations,
  actions,
};
