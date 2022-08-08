<template>

    <div>
        <div
            v-for="(attributes, name) in grouped_attributes"
             :key="name"
        >
            <b>Model: {{name}}</b>
            <div
                v-for="attribute in attributes"
                :key="attribute.pk"
            >
                <component
                    :is="getFilterForAttribute(attribute)"
                    :attribute="attribute"
                    v-model="this_policy"
                />
                <!--:policy="this_policy"-->
            </div>
        </div>

    </div>

</template>

<script>
import _ from 'lodash';

export default {
    name: 'PolicyScope',
    props: {
        policy: {
            type: Object,
            required: true,
        },
        attributes: {
            type: Array,
            required: true,
        },
    },
    data(){
        return {
            this_policy: this.policy,
        }
    },
    methods: {
        getFilterForAttribute(a){
            return a.resourcetype+'Filter'
        },
    },
    computed: {
        grouped_attributes(){

            let grouped = _.groupBy(this.attributes, 'class_name')

            console.log(grouped)
            /*
            .map((x) => {return {...x, name: x.class_name}});
            */
            return grouped
        },
    },
}

</script>