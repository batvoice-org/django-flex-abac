<template>

    <div>
        <v-menu
        transition="scale-transition"
        origin="left bottom"
        offset-y
        bottom
        v-if="actions"
        >
            <template v-slot:activator="{ on }">
                <div v-on="on">
                   <div v-if="this_policy.actions.length">
                    <span v-for="action in this_policy.actions" :key="action.id">{{action.name}} </span>
                    </div>
                    <div v-else>
                        <a>+ Add actions</a>
                    </div>
                </div>
            </template>
            <v-select
                @click.stop
                return-object
                v-model="this_policy.actions"
                :items="actions"
                item-text="name"
                flat
                solo
                :multiple="true"
                :placeholder="'Select actions'"
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

import ActionService from '@/services/action.service.js'
import PolicyService from '@/services/policy.service.js'

export default {
    name: 'PolicyActions',
    props: {
        policy: {
            type: Object,
            required: true,
        },
    },
    data(){
        return  {
            this_policy: this.policy,
            actions: null,
        }
    },
    created(){
        ActionService.list()
            .then(
                (res) => {
                    this.actions = res.data
                }
            )

    },

    watch: {
        'this_policy.actions'(){
            let updated_policy = JSON.parse(JSON.stringify(this.this_policy))
            updated_policy.actions = updated_policy.actions.map(x => x.pk)
            PolicyService.update(this.policy.pk, updated_policy)
        },
    },
}

</script>