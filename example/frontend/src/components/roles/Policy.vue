<template>
    <div>
        <h5>Policy: {{policy.name}}</h5>

        <h6> Actions: </h6>
        <PolicyActions :policy="JSON.parse(JSON.stringify(policy))" />

        <h6> Scope: </h6>
        <PolicyScope
            v-if="attributes"
            :policy="policy"
            :attributes="attributes"
        />
    </div>
</template>

<script>

import PolicyActions from './PolicyActions'
import PolicyScope from './PolicyScope'
import AttributeTypeService from '@/services/attribute-type.service.js'
//import PossibleValueService from '@/services/possible-value.service.js'

export default {
    name: 'Policy',
    components: {

    PolicyActions,

    PolicyScope,
    },
    props: {
        policy: {
            type: Object,
            required: true,
        },
    },
    data(){
        return {
            attributes: null,
        }
    },
    created(){
        AttributeTypeService.list()
            .then(
                (res) => {
                    this.attributes = res.data
                }
            )

    },
}

</script>