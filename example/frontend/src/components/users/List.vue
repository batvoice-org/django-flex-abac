<template>
  <div>
    <!--{{users}}-->
    <v-data-table
      v-if="users"
      :headers="headers"
      :items="users"
      item-key="id"
    >
          <template
            v-slot:item.roles="{ item }"
          >
            <UserRoles :user="item" />
          </template>
    </v-data-table>
  </div>
</template>

<script>

import UserService from '@/services/user.service.js'
import UserRoles from './UserRoles'

export default {

    name: 'List',
    components: {
        UserRoles,
    },
    data(){
        return {
            users: null,
        }
    },
    created(){
        UserService.list()
            .then(
                (res) => {
                    this.users = res.data
                }
            )
    },
    computed: {
      headers () {
        return [
          {
            text: 'Name',
            align: 'start',
            sortable: false,
            value: 'username',
            width: '40%',
          },
          {
            text: 'Roles',
            value: 'roles',
            sortable: false,
            width: '60%',
          },
        ]
      },
    },

}

</script>