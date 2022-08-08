<template>
  <div>

    <v-menu
        transition="scale-transition"
        origin="left bottom"
        offset-y
        bottom
        v-if="roles"
    >
        <template v-slot:activator="{ on }">
            <div v-on="on">
               <div v-if="this_user.roles.length">
                <span v-for="role in this_user.roles" :key="role.id">{{role.name}} </span>
                </div>
                <div v-else>
                    <a>+ Add a role</a>
                </div>
            </div>
        </template>
        <v-select
            @click.stop
            return-object
            v-model="this_user.roles"
            :items="roles"
            item-text="name"
            flat
            solo
            :multiple="true"
            :placeholder="'Select roles'"
            append-icon=mdi-chevron-down
            hide-details="auto"
        >
            <template v-slot:selection="{ parent, item }">
                    {{item.name}}
            </template>
        </v-select>
      </v-menu>
  </div>

</template>

<script>

import RoleService from '@/services/role.service.js'
import UserService from '@/services/user.service.js'


export default {

    name: 'UserRoles',
    props: {
        user: {
            type: Object,
            required: true
        },
    },
    data(){
        return {
            readMode: true,
            roles: null,
            this_user: this.user,
        }
    },
    created(){
        RoleService.list()
            .then(
                (res) => {
                    this.roles = res.data
                }
            )
    },
    watch: {
        'this_user.roles'(){
            UserService.update(this.user.pk, this.this_user)
        },
    },
}

</script>