<template>
    <div>
        {{attribute.name}}:
        <div v-if="values">
                <v-select
                    @click.stop
                    return-object
                    v-model="selected"
                    :items="values"
                    :item-text="valueName"
                    flat
                    solo
                    :placeholder="'All'"
                    append-icon=mdi-chevron-down
                    hide-details="auto"
                >
                    <template v-slot:selection="{ parent, item }">
                            {{item.extra.name}}
                    </template>
                    <template v-slot:prepend-item>
                        <v-list-item
                          ripple
                          @click="selectAll"
                        >
                          <v-list-item-action>
                          </v-list-item-action>
                          <v-list-item-content>
                            <v-list-item-title>
                              Select All
                            </v-list-item-title>
                          </v-list-item-content>
                        </v-list-item>
                        <v-divider class="mt-2"></v-divider>
                    </template>
                </v-select>

        </div>

    </div>
</template>

<script>

export default {
    name: 'CategoricalAttributeUserFilter',
    props: {
        values: {
            type: Array,
            required: true,
        },
        attribute: {
            type: Object,
            required: true,
        },
    },
    data(){
        return {
            selected: null,
        }
    },
    methods: {
        valueName(val){
            return val.extra.name
        },
        selectAll(){
            this.$nextTick(() => {
                    this.selected = null
                }
            )
            this.$emit('unselected', this.attribute)
        },
    },
    watch: {
        selected(){
            console.log("CHANGED")
            this.$emit('changed', this.selected)
        },
    },
}

</script>