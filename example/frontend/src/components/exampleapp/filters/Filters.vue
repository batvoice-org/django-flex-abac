<template>
    <div>
        <h3>FILTERS</h3>
        <div v-if="attributes_with_values && attributes">
            <!--<div
                v-for="(attribute_values, pk) in attributes_with_values"
                 :key="pk"
            >
                <component
                    :is="getFilterForAttribute(attribute_values[0].attribute_type)"
                    :values="attribute_values"
                    @changed="filterChanged"
                    @unselected="filterUnselected"
                />
            </div>
            -->
            <div
                v-for="attribute in attributes"
                 :key="attribute.pk"
            >
                <component
                    :is="getFilterForAttribute(attribute)"
                    :values="getAllowedValuesForAttribute(attribute)"
                    :attribute="attribute"
                    @changed="filterChanged"
                    @unselected="filterUnselected"
                />
            </div>
        </div>
    </div>
</template>

<script>

import AllowedValueService from '@/services/allowed-value.service.js'
import AttributeTypeService from '@/services/attribute-type.service.js'

import _ from 'lodash';
export default {
    name: 'Filters',
    props: {
        username: {
            type: String,
            required: true,
        },
    },
    data(){
        return {
            attributes: null,
            attributes_with_values: null,
            query_params: {},
        }
    },
    created(){
        this.getAllowedValues()
    },
    methods: {
        getAllowedValues(){
            AllowedValueService.list(this.username).then(
                (res) => {
                    let ordered = _.orderBy(res.data, 'attribute_type.class_name')
                    let grouped = _.groupBy(ordered, 'attribute_type.pk')
                    this.attributes_with_values = grouped
                }
            )
            AttributeTypeService.list().then(res => this.attributes = res.data)
        },
        getFilterForAttribute(a){
            return a.resourcetype+'UserFilter'
        },
        filterChanged(filter_value){
            //TODO: generalize to multiselect
            console.log(filter_value)
            if (filter_value){
                this.query_params[filter_value.attribute_type.field_name] = filter_value.value
                this.$emit('changed', this.query_params)
            }
        },
        filterUnselected(attribute){
            delete this.query_params[attribute.field_name]
            this.$emit('changed', this.query_params)
        },
        getAllowedValuesForAttribute(attribute){
            console.log("ATTR with vals", this.attributes_with_values)
            if (this.attributes_with_values[attribute.pk]){
                return this.attributes_with_values[attribute.pk]
            }
            return []
        }
    },
    watch: {
        username(){
            this.getAllowedValues()
        },
    },
}

</script>