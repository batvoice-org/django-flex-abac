import Vue from 'vue'
import App from './App.vue'

import router from "./router"
import vuetify from './plugins/vuetify'

Vue.config.productionTip = false

/* START auto global component registration */

// TODO: DRY

import upperFirst from 'lodash/upperFirst'
import camelCase from 'lodash/camelCase'


const requireComponent = require.context(
          // The relative path of the components folder
          './components/roles/attribute_filters/',
          // Whether or not to look in subfolders
          false,
          // The regular expression used to match base component filenames
          /[A-Z]\w+\.(vue|js)$/
        )


        requireComponent.keys().forEach(fileName => {

          console.log("&filename", fileName)
          // Get component config
          const componentConfig = requireComponent(fileName)

          // Get PascalCase name of component
          const componentName = upperFirst(
            camelCase(
              // Gets the file name regardless of folder depth
              fileName
                .split('/')
                .pop()
                .replace(/\.\w+$/, '')
            )
          )

          // Register component globally
          Vue.component(
            componentName,
            // Look for the component options on `.default`, which will
            // exist if the component was exported with `export default`,
            // otherwise fall back to module's root.
            componentConfig.default || componentConfig
          )
        })


/* END auto global component registration */

// TODO: auto registration
import CategoricalAttributeUserFilter from './components/exampleapp/filters/attribute_filters/CategoricalAttributeUserFilter.vue'
Vue.component('CategoricalAttributeUserFilter', CategoricalAttributeUserFilter)


new Vue({
  vuetify,
  router,
  render: h => h(App)
}).$mount('#app')
