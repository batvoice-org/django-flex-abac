import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

let router = new VueRouter({
    mode: "history",
    base: process.env.BASE_URL,
    routes: [
        {
            path: '/users',
            name: 'users',
            component: () =>
                import("./components/users/List.vue")
        },
        {
            path: '/roles',
            name: 'roles',
            component: () =>
                import("./components/roles/List.vue")
        },

        {
            path: '/roles/:id',
            component: () =>
                import(/* webpackChunkName: "Task" */ "./components/roles/Detail.vue"),
            props: route => ({ id: route.params.id })
        },
        {
            path: '/app',
            name: 'exampleapp',
            component: () =>
                import("./components/exampleapp/List.vue")
        },

    ]
})

export default router