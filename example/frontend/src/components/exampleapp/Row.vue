<template>
    <div>
        <div class="docrow">
            <div  v-if="!editing">
                {{doc.filename}} - Desk: {{doc.desk.name}} - Brand: {{doc.brand.name}}
            </div>
            <div>
                <v-btn v-if="!editing" @click="editing=true">Rename</v-btn>
                <div v-else>
                    <input type="text" v-model="doc.filename" />
                    <v-btn @click="edit">Confirm</v-btn>
                </div>
            </div>
        </div>
    </div>
</template>

<script>

import DocumentService from '@/services/document.service.js'

export default {
    name: 'Row',
    props: {
        document: {
            type: Object,
            required: true,
        },
        username: {
            type: String,
        },
    },
    data(){
        return {
            doc: this.document,
            editing: false,
        }
    },
    methods: {
        edit(){
            DocumentService.update(this.doc.pk, this.doc, this.username)
            .then(
                () => {
                    this.editing = false
                }
            )
            .catch(
                (err) => {
                    if(err.response.status == 403) alert('not allowed, sorry !')
                }
            )
        },
    },
}

</script>