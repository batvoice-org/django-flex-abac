<template>
  <div>
    <!--{{users}}-->
    <v-data-table
      v-if="users"
      :headers="headers"
      :items="users"
      :loading="loading"
      :hide-default-footer="true"
      item-key="id"
    >
    <template v-slot:top>
        <v-text-field
          v-model="search"
          label="Search users by username"
          class="mx-4"
          @input="searchUsers"
        ></v-text-field>
      </template>
          <template
            v-slot:item.roles="{ item }"
          >
            <UserRoles :user="item" />
          </template>
    </v-data-table>
    <v-pagination  @input="getUsers" v-model="page" :length="totalPages"></v-pagination>
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
            page: 1,
            totalPages: null,
            users: null,
            search: "",
            loading: false,
            headers: [
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
        }
    },
    created(){
        this.getUsers()
    },
    methods :{
      getUsers(){
        console.log(this.page)
        this.loading = true
        let params = {
          page: this.page,
          ...(this.search) && {search: this.search}
        }
        UserService.list(params)
            .then(
                (res) => {
                    this.users = res.data.results
                    this.totalPages = res.data.total_pages
                    this.loading = false
                }
            )

      },
      searchUsers(){
        if (this.search.length > 3 || this.search.length === 0){
          this.page = 1
          this.getUsers()
        }
      }
    }

}

</script>