<template>
  <div>
    <v-data-table
      v-if="roles"
      :headers="headers"
      :items="roles"
      item-key="id"
      @click:row="openDetail"
      class="clickable-row"
    >
      <template
        v-slot:item.name="{ item }"
      >
        <span class="role-name">{{item.name}}</span>
      </template>
    </v-data-table>
  </div>
</template>

<script>

import RoleService from '@/services/role.service.js'

export default {

    name: 'List',
    data(){
        return {
            roles: null,
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
    computed: {
      headers () {
        return [
          {
            text: 'Name',
            align: 'start',
            sortable: false,
            value: 'name',
            width: '100%',
          },
        ]
      },
    },
    methods: {
        openDetail(val, context){
            this.$router.push('/roles/'+context.item.pk)
        },
    },

}

</script>

<style scoped=true>
    .clickable-row{
        cursor: pointer;
    }

</style>