<template>
    <v-app id="inspire">
    <v-app-bar
      app
      color="white"
      flat
    >
      <v-container class="py-0 fill-height">
        <img src="/logo.png" style="height:60px;"/>
        <template>
            <v-btn to="/users"
              plain rounded
            >
              Users
            </v-btn>
            <v-btn to="/roles"
              plain rounded
            >
              Roles
            </v-btn>

            <v-btn to="/app"
              plain rounded
            >
              EXAMPLE APP
            </v-btn>
        </template>
        <v-spacer></v-spacer>
      </v-container>
    </v-app-bar>

    <v-main class="grey lighten-3">
      <v-container>
        <v-row>
          <v-col>
            <v-sheet
              min-height="70vh"
              rounded="lg"
              class="container"
            >
                  <router-view></router-view>
            </v-sheet>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>


export default {
  name: 'App',
}
</script>

<style lang="scss">


#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  /*margin-top: 60px;*/
}


#header {
    border-bottom: 1px solid lightgrey;
    height: 50px;
    max-height: 50px;
    > a {
        text-decoration: none;
        color: #2c3e50;
    }
    a img{
        width: 35px;
        height: 35px;
    }
    display: flex;
    align-items: center;
    //justify-content: space-around;
    margin-bottom: 30px;

    #home-link{
        margin-left: 5px;
        display: flex;
        align-items: center;
        width: 110px;
        justify-content: space-between;
        > span {
            text-decoration: none;
            font-size: 20px;
        }
    }
}

#app div{
    margin-bottom: 20px;
}

</style>
