<template>
    <div>
        {{attribute.name}}:
        <div v-if="possibleValues && scopes">
                <v-select
                    @click.stop
                    return-object
                    v-model="scopes"
                    :items="possibleValues"
                    :item-text="possibleValueName"
                    flat
                    solo
                    :multiple="true"
                    :placeholder="'All'"
                    append-icon=mdi-chevron-down
                    hide-details="auto"
                >
                    <template v-slot:selection="{ parent, item }">
                            {{item.extra.name}}
                    </template>
                </v-select>

        </div>

    </div>
</template>

<script>

import PolicyService from '@/services/policy.service.js'
import PossibleValueService from '@/services/possible-value.service.js'

export default {
    name: 'CategoricalAttributeFilter',
    props: {
        attribute: {
            type: Object,
            required: true,
        },
        value: { //policy
            type: Object,
            required: true,
        },
    },
    data(){
        return {
            scopes: null,
            this_policy: this.value,
            possibleValues: null,
        }
    },
    created(){
        
        this.this_policy.actions = this.this_policy.actions.map((x) => {
                if (x.pk) {
                    return x.pk
                }
                return x
            }
        )
        PossibleValueService.list(this.attribute.pk).then((res) => {
            this.possibleValues = res.data.possible_values
        })
        this.scopes = this.this_policy.scopes.filter(s => s.attribute_type.pk == this.attribute.pk)
    },
    methods: {
        possibleValueName(val){
            return val.extra.name
        },
    },
    watch: {
        'scopes'(){
            console.log("policy scopes changed!")
            //TODO: this causes PATCH requests with missing attributes
            // because this.this_policy does not reflect changes for other attributes
            let updated_policy = JSON.parse(JSON.stringify(this.this_policy))
            console.log("updated_policy.scopes before", JSON.parse(JSON.stringify(updated_policy.scopes)))
            updated_policy.scopes = updated_policy.scopes.filter(
                (s) => {
                    if (s.attribute_type.pk == this.attribute.pk) return false
                    return true
                }
            )
            updated_policy.scopes = updated_policy.scopes.concat(this.scopes)
            PolicyService.update(this.this_policy.pk, updated_policy)
            this.this_policy.scopes = updated_policy.scopes
            this.$emit('change', this.this_policy)
        },
    },
}

</script>