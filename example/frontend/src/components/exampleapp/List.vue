<template>
    <div>
        <p>Simulate user: </p>
        <v-select
            v-if="usernames.length"
            @click.stop
            return-object
            v-model="selected_username"
            :items="usernames"
            flat
            solo
            append-icon=mdi-chevron-down
            hide-details="auto"
        ></v-select>
        <div v-if="documents">
        <Filters :username="selected_username" @changed="filter"/>
        <h3>DOCUMENTS: </h3>
        <div v-if="documents.length">
            <div v-for="doc in documents" :key="doc.pk">
                <Row :document="doc" :username="selected_username"/>
            </div>
        </div>
        </div>
        <div v-if="!loading && !documents">
            No documents.
        </div>
    </div>
</template>

<script>

import DocumentService from '@/services/document.service.js'
import Row from './Row'
import Filters from './filters/Filters'

import UserService from '@/services/user.service.js'

export default {
    name: 'List',
    components: {
        Row,
        Filters,
    },
    data(){
        return {
            documents: null,
            loading: true,
            usernames: [],
            selected_username: 'member',
            params: null,
        }
    },
    created(){
        DocumentService.list({params: {as_user: this.selected_username}}).then(
            (res) => {
                this.documents = res.data
                this.loading = false
            }
        )
        UserService.list().then(
            (res) => {
                this.usernames = res.data.map(x => x.username)
            }
        )
    },
    methods: {
        filter(params){
            this.params = params
            this.loading = true
            DocumentService.list(
                {
                    params: {...params, as_user: this.selected_username}
                }
            ).then(
                (res) => {
                    this.documents = res.data
                    this.loading = false
                }
            )
        },
    },
    watch: {
        selected_username(){
            this.filter(this.params)
        },
    },
}

</script>

<style lang="scss" scoped>

.docrow {
    display: flex;
    justify-content: space-between;
}

</style>