<template>
  <Layout>
    <Layout>
      <Sider hide-trigger :width="240" class="root-sider">
        <!-- <Input icon="ios-search" placeholder="在此页面搜索..." style="width: 100%" @on-change="searchUpdate" @on-focus="activeSearch" @on-blur="deactiveSearch"></Input> -->
        <Menu :theme="app_config.theme || 'light'" mode="vertical" @on-select="menuNavi" :active-name="activeName || 'index'">
          <MenuItem name="index" ><Icon type="ios-home-outline"></Icon>home</MenuItem>
          <MenuItem name="detail" ><Icon type="ionic"></Icon>dataset</MenuItem>
          <MenuItem name="cluster" ><Icon type="ionic"></Icon>cluster</MenuItem>
          <!-- <MenuItem name="settings"><Icon type="ios-toggle-outline"></Icon></MenuItem> -->
        </Menu>
      </Sider>
      <Content class="root-content">
        <router-view></router-view>
      </Content>
    </Layout>
    <!-- <Footer style="text-align:center">Copyright &copy; 2015-2020 jackz.cn All Rights Reserved.</Footer> -->
  </Layout>
</template>

<script>
import { mapState, mapActions } from "vuex";

export default {
  name: "main-layout",
  data() {
    return {
      activeName: null
    };
  },
  computed: {
    ...mapState({
      app_config: state => state.Config.app_config
    })
  },
  methods: {
    menuNavi(item) {
      this.$router.push(`/${item}`);
    },
    searchUpdate(e) {
      this.setSearchContent(e.target.value);
    },
    ...mapActions([
      "activeSearch",
      "deactiveSearch",
      "toggleSearch",
      "setSearchContent"
    ])
  },
  watch: {
    $route(r) {
      this.$set(this, "activeName", r.path.slice(1));
    }
  },
  mounted() {
    this.$set(this, "activeName", this.$route.path.slice(1));
  }
};
</script>

<style lang="scss">
.root-sider {
  position: fixed;
  left: 0;
  top: 0;
  overflow: hidden;
  background: #fff;
  // height: calc(100vh - 69px);
  height: 100vh;
  cursor: default;
}

.root-content {
  padding: 12px;
  padding-left: 252px;
  height: 100vh;
  overflow: auto;
  cursor: default;
}

h1, h2, h3, h4, h5, p, span, li {
  user-select: none;
  cursor: inherit;
}
</style>

