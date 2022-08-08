<template>
    <div>
        <div v-if="role">
            <h3> {{role.name}} </h3>
            <h4> Policies: </h4>
            <div
                v-for="policy in role.policies" :key="policy.pk"
            >
                <Policy :policy="policy" />
            </div>
            <div v-if="!role.policies.length">
                No policies.
            </div>
            <div id="add-policy">
                <div v-if="addingPolicy">
                    <input type="text" v-model="addedPolicy.name">
                    <v-btn @click="addPolicy"><v-icon>mdi-check</v-icon></v-btn>
                </div>
                <div v-else>
                    <v-btn @click="addingPolicy=true">Add policy</v-btn>
                </div>
            </div>
        </div>
    </div>
</template>

<script>

import RoleService from '@/services/role.service.js'
import PolicyService from '@/services/policy.service.js'
import Policy from './Policy'

export default {
    name: 'Detail',
    components: {
        Policy,
    },
    props: {
        id: {
            type: String || Number,
            required: true,
        },
    },
    data(){
        return {
            role: null,
            addingPolicy: false,
            addedPolicy: {
                actions: [],
                scopes: [],

            },
        }
    },
    created(){
        RoleService.get(this.id).then(
            (res) => {
                this.role = res.data
                this.addedPolicy.name = this.getDefaultNewPolicyName(this.role)
            }
        )
    },
    methods: {
        getDefaultNewPolicyName(role){
            return "Policy #"+ (role.policies.length + 1)
        },
        addPolicy(){
            PolicyService.create(this.addedPolicy)
                .then(
                    (res) => {
                        var added = res.data
                        this.role.policies.push(added)
                        let updated_role = JSON.parse(JSON.stringify(this.role))
                        updated_role.policies = updated_role.policies.map(x => x.pk)
                        RoleService.update(this.role.pk, updated_role).then(
                            () => {
                                this.addingPolicy = false
                                this.addedPolicy = {actions: [], scopes: [], name: this.getDefaultNewPolicyName(updated_role)}
                            }
                        )
                    }
                ).catch(err => alert(err))
        },
    },
}

</script>