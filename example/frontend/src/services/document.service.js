import ExampleApiService from '@/services/exampleapi.service'

class DocumentService {
  constructor() {
    this.request = ExampleApiService
  }

  list(params = {}) {
    console.log("params", params)
    return this.request.get('/documents/', params)
  }

  create(data) {
    return this.request.post('/documents/', data)
  }

  update(id, payload, username) {
    console.log("payload", JSON.parse(JSON.stringify(payload)))
    return this.request.patch(`/documents/${id}/`, payload, {params: {as_user: username}})
  }

  get(id) {
    return this.request.get(`/documents/${id}/`)
  }
}

export default new DocumentService()
